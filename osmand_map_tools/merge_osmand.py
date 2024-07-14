#!/usr/bin/env python3
import sqlite3
from argparse import ArgumentParser
from pathlib import Path

from .utils import _remove_file


def setup_parser() -> ArgumentParser:
    parser = ArgumentParser(description="Merge multiple OsmAnd (.sqlitedb) files into single")
    parser.add_argument(
        "input",
        nargs="+",
        type=Path,
        help="input files. If multiple files contain tile with the same coordinates, "
        "tile from first (from argument list) file will be used",
    )
    parser.add_argument("output", type=str, help="output file directory")
    parser.add_argument(
        "-f",
        "--force",
        dest="force",
        action="store_true",
        default=False,
        help="override output files if exists",
    )
    return parser


def merge_osmand_maps(input_map_paths: list[Path], output_file_path: Path, force: bool) -> None:
    _remove_file(
        output_file_path, "Output file %s  already exists. Add -f option for overwrite", force
    )

    destination = sqlite3.connect(output_file_path)
    destination_cursor = destination.cursor()

    destination_cursor.execute(
        "CREATE TABLE tiles (x INT, y INT, z INT, s INT, image BLOB, PRIMARY KEY (x, y, z, s))"
    )
    destination_cursor.execute("CREATE TABLE info (maxzoom INT, minzoom INT)")

    for source_path in input_map_paths:
        with sqlite3.connect(source_path) as source:
            source_cursor = source.cursor()
            for row in source_cursor.execute("SELECT x, y, z image FROM tiles"):
                x, y, z, image = row
                destination_cursor.execute(
                    "SELECT COUNT(*) FROM tiles WHERE x = ? AND y = ? AND z = ?", (x, y, z)
                )
                if destination_cursor.fetchone()[0] == 0:
                    destination_cursor.execute(
                        "INSERT INTO tiles (x, y, z, s, image) VALUES (?, ?, ?, ?, ?)",
                        (x, y, z, 0, sqlite3.Binary(image)),
                    )

    destination_cursor.execute(
        "INSERT INTO info (maxzoom, minzoom) SELECT MAX(z), MIN(z) FROM tiles"
    )
    destination.commit()
    destination.close()


def main():
    parser = setup_parser()
    args = parser.parse_args()
    merge_osmand_maps(input_map_paths=args.input, output_file_path=args.output, force=args.force)


if __name__ == "__main__":
    main()
