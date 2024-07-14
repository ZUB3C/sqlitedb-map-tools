#!/usr/bin/env python3
import io
import sqlite3
from argparse import ArgumentParser
from pathlib import Path

from PIL import Image
from tqdm import tqdm

from .utils import _remove_file


def convert_mbtiles_to_sqlitedb(
    mbtiles_path: Path,
    sqlitedb_path: Path,
    replace_file: bool = False,
    jpeg_quality: int | None = None,
) -> None:
    _remove_file(
        sqlitedb_path, "Output file %s  already exists. Add -f option for overwrite", replace_file
    )

    source = sqlite3.connect(mbtiles_path)
    destination = sqlite3.connect(sqlitedb_path)

    source_cursor = source.cursor()
    destination_cursor = destination.cursor()

    destination_cursor.execute(
        "CREATE TABLE tiles (x INT, y INT, z INT, s INT, image BLOB, PRIMARY KEY (x, y, z, s))"
    )
    destination_cursor.execute("CREATE TABLE info (maxzoom INT, minzoom INT)")

    input_data = source_cursor.execute(
        "SELECT zoom_level, tile_column, tile_row, tile_data FROM tiles"
    )

    for row in tqdm(iterable=input_data, desc=mbtiles_path.stem):
        image = row[3]
        if jpeg_quality is not None:
            image = to_jpg(image, int(jpeg_quality))
        zoom, x_tile, y_tile = map(int, row[:3])
        y = (1 << zoom) - 1 - y_tile  # 2 ** zoom - 1 - y_tile
        z = 17 - zoom
        destination_cursor.execute(
            "INSERT INTO tiles (x, y, z, s, image) VALUES (?, ?, ?, ?, ?)",
            (x_tile, y, z, 0, sqlite3.Binary(image)),
        )

    destination_cursor.execute(
        "INSERT INTO info (maxzoom, minzoom) SELECT MAX(z), MIN(z) FROM tiles"
    )

    destination.commit()
    source.close()
    destination.close()


def to_jpg(raw_bytes: bytes, quality: int) -> bytes:
    image = Image.open(io.BytesIO(raw_bytes))
    image = image.convert("RGB")
    stream = io.BytesIO()
    image.save(stream, format="JPEG", subsampling=0, quality=quality)
    return stream.getvalue()


def _setup_parser() -> ArgumentParser:
    parser = ArgumentParser(
        description="Converts mbtiles format to sqlitedb format suitable for OsmAnd"
    )
    parser.add_argument("input", type=Path, help="input file path")
    parser.add_argument("output", type=Path, help="output file path")
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        dest="force",
        default=False,
        help="override output file if exists",
    )
    parser.add_argument(
        "--jpg",
        dest="jpeg_quality",
        action="store",
        type=int,
        help="convert tiles to JPEG with specified quality",
    )
    return parser


def main():
    parser = _setup_parser()

    args = parser.parse_args()

    convert_mbtiles_to_sqlitedb(
        mbtiles_path=args.input,
        sqlitedb_path=args.output,
        replace_file=args.force,
        jpeg_quality=args.jpeg_quality,
    )


if __name__ == "__main__":
    main()
