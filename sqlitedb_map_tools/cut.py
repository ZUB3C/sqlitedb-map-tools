import math
import sqlite3
import time
from pathlib import Path

import click

from .cli import cli
from .utils import _remove_file


def tile_position_to_coordinates(x_tile: int, y_tile: int, zoom: int) -> tuple[float, float]:
    n = 1 << zoom  # 2 ** zoom
    longitude_degrees = x_tile / n * 360.0 - 180.0
    print(f"{longitude_degrees=}")
    latitude_radians = math.atan(math.sinh(math.pi * (1 - 2 * y_tile / n)))
    latitude_degrees = math.degrees(latitude_radians)
    return latitude_degrees, longitude_degrees


def coordinates_to_tile_position(
    latitude_radians: float, longitude_degrees: float, zoom: int
) -> tuple[float, float]:
    latitude_radians = math.radians(latitude_radians)
    n = 1 << zoom  # 2 ** zoom
    x_tile = int((longitude_degrees + 180.0) / 360.0 * n)
    y_tile = int((1.0 - math.asinh(math.tan(latitude_radians)) / math.pi) / 2.0 * n)
    return x_tile, y_tile


@cli.command(
    help="Extracts a rectangular section of a map from a .sqlitedb file into a separate map."
)
@click.argument(
    "input_file",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
)
@click.argument("output_file", type=click.Path(dir_okay=False, path_type=Path))
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
    "-f",
    "--force",
    is_flag=True,
    default=False,
    help="Override the output file if it exists.",
)
def cut_sqlitedb_map(
    input_file: Path,
    output_file: Path,
    upper_left_coordinates: tuple[float, float],
    bottom_right_coordinates: tuple[float, float],
    force: bool,
) -> None:
    latitude1, longitude1 = upper_left_coordinates
    latitude2, longitude2 = bottom_right_coordinates
    if not (latitude1 > latitude2 and longitude1 < longitude2):
        print("Enter the coordinates of the upper left and bottom right corners correctly")
        exit(1)
    _remove_file(output_file, "Output file %s already exists. Add -f option for overwrite", force)

    source = sqlite3.connect(input_file)
    destination = sqlite3.connect(output_file)

    source_cursor = source.cursor()
    destination_cursor = destination.cursor()

    destination_cursor.execute(
        "CREATE TABLE tiles (x INT, y INT, z INT, s INT, image BLOB, PRIMARY KEY (x, y, z, s))"
    )
    destination_cursor.execute("CREATE TABLE info (maxzoom INT, minzoom INT)")

    min_zoom, max_zoom = source_cursor.execute("SELECT minzoom, maxzoom FROM info").fetchone()
    total_tiles_count = 0
    start_time = time.perf_counter()
    for zoom in range(min_zoom, max_zoom + 1):
        min_x_tile, max_y_tile = coordinates_to_tile_position(latitude1, longitude1, zoom)
        max_x_tile, min_y_tile = coordinates_to_tile_position(latitude2, longitude2, zoom)
        min_x_tile, max_x_tile = sorted((min_x_tile, max_x_tile))
        min_y_tile, max_y_tile = sorted((min_y_tile, max_y_tile))

        input_data = source_cursor.execute(
            "SELECT x, y, z, image "
            "FROM tiles "
            "WHERE z = ? AND ? <= x AND x <= ? AND ? <= y AND y <= ?",
            (17 - zoom, min_x_tile, max_x_tile, min_y_tile, max_y_tile),
        )
        tiles_count = 0
        for row in input_data:
            x_tile, y_tile, zoom, image = row
            destination_cursor.execute(
                "INSERT INTO tiles (x, y, z, s, image) VALUES (?, ?, ?, ?, ?)",
                (x_tile, y_tile, zoom, 0, sqlite3.Binary(image)),
            )
            tiles_count += 1
        total_tiles_count += tiles_count
        current_time = time.perf_counter()
        print(f"Zoom {zoom}: {tiles_count} tiles ({current_time - start_time:.3f} s)")
        start_time = current_time
    destination_cursor.execute(
        "INSERT INTO info (maxzoom, minzoom) VALUES(?, ?)", (max_zoom, min_zoom)
    )
    destination.commit()
    print(f"Total tiles count: {total_tiles_count}")


if __name__ == "__main__":
    cut_sqlitedb_map()
