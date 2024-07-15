import io
import sqlite3
import warnings
from pathlib import Path

import click
from PIL import Image
from tqdm import tqdm

from .cli import cli
from .utils import _remove_file


@cli.command(help="Converts mbtiles format to sqlitedb format suitable for OsmAnd")
@click.argument(
    "mbtiles_path",
    metavar="INPUT_FILE",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
)
@click.argument(
    "sqlitedb_path", metavar="OUTPUT_FILE", type=click.Path(dir_okay=False, path_type=Path)
)
@click.option(
    "-f",
    "--force",
    "replace_file",
    is_flag=True,
    default=False,
    help="Override output file if it exists",
)
@click.option(
    "-j", "--jpeg-quality", type=int, help="Convert tiles to JPEG with specified quality"
)
def convert_mbtiles_to_sqlitedb(
    mbtiles_path: Path,
    sqlitedb_path: Path,
    replace_file: bool = False,
    jpeg_quality: int | None = None,
) -> None:
    _remove_file(
        sqlitedb_path, "Output file %s already exists. Add -f option for overwrite", replace_file
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
    image_file = Image.open(io.BytesIO(raw_bytes))
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning)
        image = image_file.convert("RGB")
    stream = io.BytesIO()
    image.save(stream, format="JPEG", subsampling=0, quality=quality)
    return stream.getvalue()


if __name__ == "__main__":
    convert_mbtiles_to_sqlitedb()
