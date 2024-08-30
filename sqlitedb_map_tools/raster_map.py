from __future__ import annotations

import asyncio
import io
import logging
import sqlite3
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any, Final

import aiohttp
import click
from PIL import Image
from tqdm import tqdm

from .cli import cli
from .const import DEFAULT_HEADERS
from .utils import _remove_file, async_enumerate, coordinates_to_tile_position, to_jpg

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator
    from types import TracebackType

    from PIL.Image import Image as ImageType

logger: Final[logging.Logger] = logging.getLogger(name=__name__)


class RasterMapAPI:
    def __init__(
        self,
        url_mask: str,
        sqlitedb_path: Path,
        timeout: int = 120,
        max_requests_per_second: int | None = None,
        max_retry_count: int = 10,
        chunk_size: int = 2048,
    ) -> None:
        self.url_mask = url_mask
        self.max_retry_count = max_retry_count
        self.chunk_size = chunk_size
        self._session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(timeout),
            connector=aiohttp.TCPConnector(limit=max_requests_per_second)
            if max_requests_per_second is not None
            else None,
            headers=DEFAULT_HEADERS,
        )
        self._create_sqlitedb_file(sqlitedb_path=sqlitedb_path)

    async def download_tiles(
        self,
        zoom: int,
        min_x: int,
        max_x: int,
        min_y: int,
        max_y: int,
    ) -> None:
        x_y_values = [(x, y) for x in range(min_x, max_x + 1) for y in range(min_y, max_y + 1)]
        progress_bar = tqdm(total=len(x_y_values), desc=f"Downloading tiles (zoom {zoom})")
        async for chunk_index, tiles_chunk in async_enumerate(
            self._fetch_tiles(zoom, min_x, max_x, min_y, max_y)
        ):
            previous_chinks_tiles_count = chunk_index * self.chunk_size
            for tile_index, tile in enumerate(tiles_chunk):
                if tile is not None:
                    x, y = x_y_values[previous_chinks_tiles_count + tile_index]
                    self._save_tile(x=x, y=y, z=zoom, image=tile)
                progress_bar.update()
        self._connection.commit()

    def save_min_max_zoom(
        self,
        min_zoom: int,
        max_zoom: int,
    ) -> None:
        self._cursor.execute(
            "INSERT INTO info (maxzoom, minzoom) VALUES(?, ?)", (max_zoom, min_zoom)
        )

    async def _fetch_tiles(
        self, zoom: int, min_x: int, max_x: int, min_y: int, max_y: int
    ) -> AsyncGenerator[list[ImageType | None], None]:
        fetch_tiles_tasks: list[asyncio.Task[ImageType | None]] = []
        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                tile_url = self.url_mask.format(x=x, y=y, z=zoom)
                fetch_tiles_tasks.append(asyncio.create_task(self._get_image(url=tile_url)))

                if len(fetch_tiles_tasks) >= self.chunk_size:
                    tiles: list[ImageType | None] = await asyncio.gather(*fetch_tiles_tasks)
                    yield tiles
                    fetch_tiles_tasks.clear()

        if fetch_tiles_tasks:
            tiles: list[ImageType | None] = await asyncio.gather(  # type: ignore[no-redef]
                *fetch_tiles_tasks
            )
            yield tiles

    def _save_tile(self, x: int, y: int, z: int, image: ImageType) -> None:
        image_bytes = to_jpg(image=image)
        self._cursor.execute(
            "INSERT INTO tiles (x, y, z, s, image) VALUES (?, ?, ?, ?, ?)",
            (x, y, z, 0, sqlite3.Binary(image_bytes)),
        )

    def _create_sqlitedb_file(self, sqlitedb_path: Path) -> None:
        self._connection = sqlite3.connect(sqlitedb_path)
        self._cursor = self._connection.cursor()
        self._cursor.execute(
            "CREATE TABLE tiles (x INT, y INT, z INT, s INT, image BLOB, PRIMARY KEY (x, y, z, s))"
        )
        self._cursor.execute("CREATE TABLE info (maxzoom INT, minzoom INT)")

    async def _get_image(
        self, url: str = "", retry_number: int = 0, **kwargs: Any
    ) -> ImageType | None:
        try:
            async with self._session.request(method="GET", url=url, **kwargs) as response:
                logger.debug("Sent GET request: %d: %s", response.status, str(response.url))
                if response.status == 404:
                    return None
                if response.status != 200:
                    if retry_number == self.max_retry_count:
                        raise RuntimeError(f"Too many retries for {url}")
                    logger.debug(
                        "Retring GET request (%d try): %d: %s",
                        retry_number + 1,
                        response.status,
                        str(response.url),
                    )
                    return await self._get_image(url=url, retry_number=retry_number + 1, **kwargs)
                image_data = await response.read()
                return Image.open(io.BytesIO(image_data))
        except asyncio.exceptions.TimeoutError:
            if retry_number == self.max_retry_count:
                raise RuntimeError(f"Too many retries for {url!s}")  # noqa: B904
            logger.debug(
                "Retring GET request (%d try): %d: %s",
                retry_number + 1,
                response.status,
                str(response.url),
            )
            return await self._get_image(url=url, retry_number=retry_number + 1, **kwargs)

    async def close(self) -> None:
        if not self._session.closed:
            await self._session.close()
        self._connection.close()

    async def __aenter__(self) -> RasterMapAPI:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.close()


def _format_seconds(seconds: int | float) -> str:
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"


async def _download_raster_map(
    output_file: Path,
    url_mask: str,
    replace_file: bool,
    upper_left_coordinates: tuple[float, float],
    bottom_right_coordinates: tuple[float, float],
    min_zoom: int,
    max_zoom: int,
    max_requests_per_second: int,
    timeout: int,
    max_retry_count: int,
    chunk_size: int,
) -> None:
    _remove_file(
        output_file, "Output file %s already exists. Add -f option for overwrite", replace_file
    )
    async with RasterMapAPI(
        url_mask=url_mask,
        sqlitedb_path=output_file,
        timeout=timeout,
        max_requests_per_second=max_requests_per_second,
        max_retry_count=max_retry_count,
        chunk_size=chunk_size,
    ) as raster_map_api:
        raster_map_api.save_min_max_zoom(min_zoom=min_zoom, max_zoom=max_zoom)

        latitude1, longitude1 = upper_left_coordinates
        latitude2, longitude2 = bottom_right_coordinates

        print("Tiles to download:")
        zoom_to_x_y_ranges: dict[int, tuple[int, int, int, int]] = {}
        total_tiles_count = 0
        total_time_to_save_tiles = 0.0
        for zoom in range(min_zoom, max_zoom + 1):
            min_x, min_y = coordinates_to_tile_position(latitude1, longitude1, zoom)
            max_x, max_y = coordinates_to_tile_position(latitude2, longitude2, zoom)
            zoom_to_x_y_ranges[zoom] = (min_x, max_x, min_y, max_y)
            tiles_count = max(max_x - min_x, 1) * max(max_y - min_y, 1)
            if max_requests_per_second:
                time_to_save_tiles = tiles_count / max_requests_per_second
                total_time_to_save_tiles += time_to_save_tiles
            print(
                f"    Zoom {zoom}: {tiles_count} tiles "
                + (f"({_format_seconds(time_to_save_tiles)})" if max_requests_per_second else "")
            )
            total_tiles_count += tiles_count

        print(f"Total tiles count: {total_tiles_count}")
        if max_requests_per_second:
            print(
                f"Minimal time to download tiles: {_format_seconds(total_time_to_save_tiles)} "
                f"(max RPS is {max_requests_per_second})"
            )
        begin_time = time.perf_counter()
        for zoom, (min_x, max_x, min_y, max_y) in zoom_to_x_y_ranges.items():
            await raster_map_api.download_tiles(
                zoom=zoom,
                min_x=min_x,
                max_x=max_x,
                min_y=min_y,
                max_y=max_y,
            )
        download_time = time.perf_counter() - begin_time
        print(
            f"{total_tiles_count} tiles downloaded in "
            f"{_format_seconds(download_time)}. "
            f"Average RPS: {total_tiles_count / download_time:.2f}"
        )


@cli.command(help="Download tiles from remote server to .sqlitedb file.")
@click.argument(
    "output_file",
    type=click.Path(dir_okay=False, path_type=Path),
)
@click.option(
    "-f",
    "--force",
    "replace_file",
    is_flag=True,
    default=False,
    help="Override the output file if it exists.",
)
@click.option(
    "-u",
    "--url-mask",
    "url_mask",
    required=True,
    help="Server url mask from where you want to download tiles. "
    "It should have `{x}`, `{y}` and `{z}` in it. "
    "For example, https://tile.openstreetmap.org/{z}/{x}/{y}.png.",
)
@click.option(
    "-l",
    "--upper-left",
    "upper_left_coordinates",
    required=True,
    nargs=2,
    type=float,
    help="Coordinates of the upper-left corner of the section to be extracted.",
)
@click.option(
    "-r",
    "--bottom-right",
    "bottom_right_coordinates",
    required=True,
    nargs=2,
    type=float,
    help="Coordinates of the bottom-right corner of the section to be extracted.",
)
@click.option(
    "--min-zoom",
    "min_zoom",
    type=int,
    default=0,
    help="Minimum zoom with which tiles will be downloaded. By default 0.",
)
@click.option(
    "--max-zoom",
    "max_zoom",
    type=int,
    default=18,
    help="Minimum zoom with which tiles will be downloaded. By default 18.",
)
@click.option(
    "--max-rpc",
    "--max-requests-per-second",
    "max_requests_per_second",
    type=int,
    default=0,
    help="Max requests per second limit. By default no limit.",
)
@click.option(
    "-t",
    "--timeout",
    "timeout",
    type=int,
    default=300,
    help="Request timeount in seconds. By default 300.",
)
@click.option(
    "--max-retry-count",
    "max_retry_count",
    type=int,
    default=10,
    help="Maximum number of retries to server if timeout is reached. By default 10.",
)
@click.option(
    "-c",
    "--chuck-size",
    "chunk_size",
    type=int,
    default=2048,
    help="Size of a chunk with tiles stored in RAM. "
    "After filling a chunk with tiles, they are saved to .sqlitedb output file. By default 2048",
)
def download_raster_map(
    output_file: Path,
    url_mask: str,
    replace_file: bool,
    upper_left_coordinates: tuple[float, float],
    bottom_right_coordinates: tuple[float, float],
    min_zoom: int,
    max_zoom: int,
    max_requests_per_second: int,
    timeout: int,
    max_retry_count: int,
    chunk_size: int,
) -> None:
    asyncio.run(
        _download_raster_map(
            output_file=output_file,
            url_mask=url_mask,
            replace_file=replace_file,
            upper_left_coordinates=upper_left_coordinates,
            bottom_right_coordinates=bottom_right_coordinates,
            min_zoom=min_zoom,
            max_zoom=max_zoom,
            max_requests_per_second=max_requests_per_second,
            timeout=timeout,
            max_retry_count=max_retry_count,
            chunk_size=chunk_size,
        )
    )
