import io
import math
import warnings
from collections.abc import AsyncIterable, AsyncIterator
from pathlib import Path
from typing import TypeVar

from PIL.Image import Image as ImageType


def _remove_file(file_path: Path, message: str, force: bool = False) -> None:
    if file_path.is_file():
        if force:
            Path.unlink(file_path)
        else:
            print(message % str(file_path))
            exit(1)


def tile_position_to_coordinates(x_tile: int, y_tile: int, zoom: int) -> tuple[float, float]:
    n = 1 << zoom  # 2 ** zoom
    longitude_degrees = x_tile / n * 360.0 - 180.0
    print(f"{longitude_degrees=}")
    latitude_radians = math.atan(math.sinh(math.pi * (1 - 2 * y_tile / n)))
    latitude_degrees = math.degrees(latitude_radians)
    return latitude_degrees, longitude_degrees


def coordinates_to_tile_position(
    latitude_radians: float, longitude_degrees: float, zoom: int
) -> tuple[int, int]:
    latitude_radians = math.radians(latitude_radians)
    n = 1 << zoom  # 2 ** zoom
    x_tile = int((longitude_degrees + 180.0) / 360.0 * n)
    y_tile = int((1.0 - math.asinh(math.tan(latitude_radians)) / math.pi) / 2.0 * n)
    return x_tile, y_tile


T = TypeVar("T")  # Type variable for the items in the async iterable


async def async_enumerate(
    aiterable: AsyncIterable[T], start: int = 0
) -> AsyncIterator[tuple[int, T]]:
    """Async generator that behaves like enumerate."""
    i: int = start
    async for item in aiterable:
        yield i, item
        i += 1


def to_jpg(image: ImageType, quality: int = 100) -> bytes:
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning)
        image = image.convert("RGB")
    stream = io.BytesIO()
    image.save(stream, format="JPEG", subsampling=0, quality=quality)
    return stream.getvalue()
