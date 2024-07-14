from argparse import ArgumentParser
from pathlib import Path

import requests
from tqdm import tqdm

from .const import MAP_NAMES, TILES_URL
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


def setup_parser() -> ArgumentParser:
    parser = ArgumentParser(
        description="Download mbtiles files from https://tiles.nakarte.me/files"
    )
    parser.add_argument("maps_dir", type=Path, help="directory where maps will be downloaded")
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        dest="force",
        default=False,
        help="override output files if exists",
    )
    parser.add_argument(
        "--jpg",
        dest="jpeg_quality",
        action="store",
        help="convert tiles to JPEG with specified quality",
    )
    parser.add_argument("-m", "--maps", nargs="+", help="list of map names to download")
    return parser


def main():
    parser = setup_parser()
    args = parser.parse_args()

    available_maps_str = f"Available maps:\n    {'\n    '.join(MAP_NAMES)}"
    map_names_to_download = args.maps
    if not map_names_to_download:
        print(f"Use -m argument to specify maps which you want to download.\n{available_maps_str}")
        exit(1)
    if map_names_to_download == ["all"]:
        print("Downloading all available maps.")
        map_names_to_download = MAP_NAMES
    else:
        invalid_map_names = [i for i in map_names_to_download if i not in MAP_NAMES]
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
        download_file(url=url, file_path=args.maps_dir / f"{map_name}.mbtiles", force=args.force)


if __name__ == "__main__":
    main()
