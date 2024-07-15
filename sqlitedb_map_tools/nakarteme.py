from pathlib import Path

import click
import requests
from tqdm import tqdm

from .cli import cli
from .const import TILES_URL
from .parser import get_available_map_names
from .utils import _remove_file


def download_file(url: str, file_path: Path, force: bool) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)
    _remove_file(file_path, "File %s already exists, skipping download", force)

    response = requests.get(url, stream=True, timeout=60)
    total_file_size = int(response.headers.get("content-length", 0))

    with (
        open(file_path, "wb") as file,
        tqdm(
            desc=file_path.stem,
            total=total_file_size,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
        ) as bar,
    ):
        for data in response.iter_content(chunk_size=1024):
            size = file.write(data)
            bar.update(size)


@cli.command(
    help="Download .mbtiles map files from https://tiles.nakarte.me/files.\n\n"
    "Pass 'all' as map name to download all available maps."
)
@click.argument("maps", nargs=-1)
@click.option(
    "-o",
    "--output",
    "output_dir",
    default=".",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Directory where maps will be downloaded",
)
@click.option(
    "-f", "--force", is_flag=True, default=False, help="Override output file if it exist"
)
def download_nakarteme_maps(
    maps: list[str], output_dir: Path = Path(), force: bool = False
) -> None:
    map_names = get_available_map_names()
    available_maps_str = "".join(("Available maps:\n    ", "\n    ".join(map_names)))
    map_names_to_download = maps
    if not map_names_to_download:
        print(f"Specify maps which you want to download as arguments.\n{available_maps_str}")
        exit(1)
    if map_names_to_download == ["all"]:
        print("Downloading all available maps.")
        map_names_to_download = map_names
    else:
        invalid_map_names = [i for i in map_names_to_download if i not in map_names]
        if invalid_map_names:
            print(f"Invalid map names: {', '.join(invalid_map_names)}.\n{available_maps_str}")
            exit(1)

    map_urls = [f"{TILES_URL}/{map_file_name}.mbtiles" for map_file_name in map_names_to_download]

    map_file_sizes: dict[str, int] = {}
    print("Map sizes:")
    for url, map_name in zip(map_urls, map_names_to_download, strict=True):
        response = requests.head(url, timeout=60)
        file_size = int(response.headers.get("content-length", 0))
        map_file_sizes[map_name] = file_size
        print(f"    {map_name}: {file_size / (1024 ** 3):.2f} GB")

    print(f"Total size to download: {sum(map_file_sizes.values()) / (1024 ** 3):.2f} GB")

    for url, map_name in zip(map_urls, map_names_to_download, strict=True):
        download_file(url=url, file_path=output_dir / f"{map_name}.mbtiles", force=force)


if __name__ == "__main__":
    download_nakarteme_maps()
