import sqlite3
from pathlib import Path

import click

from .cli import cli
from .utils import _remove_file


@cli.command(
    help="Merges multiple .sqlitedb map files into a single file.\n\n"
    "If multiple files contain tiles with the same coordinates, "
    "the tile from the first file in the argument list will be used."
)
@click.argument(
    "input_map_paths",
    metavar="INPUT_FILES",
    nargs=-1,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
)
@click.argument("output_file", type=click.Path(dir_okay=False, path_type=Path))
@click.option(
    "-f",
    "--force",
    is_flag=True,
    default=False,
    help="Override the output file if it exists.",
)
def merge_sqlitedb_maps(
    input_map_paths: list[Path], output_file: Path, force: bool = False
) -> None:
    _remove_file(output_file, "Output file %s already exists. Add -f option for overwrite", force)

    destination = sqlite3.connect(output_file)
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


if __name__ == "__main__":
    merge_sqlitedb_maps()
