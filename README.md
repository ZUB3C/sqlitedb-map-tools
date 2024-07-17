# 🗺 SQLiteDB Map Tools

[![License](https://img.shields.io/github/license/ZUB3C/sqlitedb-map-tools?style=flat-square)](https://github.com/ZUB3C/sqlitedb-map-tools/blob/master/LICENSE)
![Python Versions](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-blue?style=flat-square)
![Status](https://img.shields.io/badge/status-stable-bright_green?style=flat-square)
[![MyPy](https://img.shields.io/badge/mypy-checked-blue?style=flat-square)](https://github.com/python/mypy)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json&style=flat-square)](https://github.com/astral-sh/ruff)

A set of CLI tools for working with .mbtiles map files, including a map downloader.

- `mbtiles2sqlitedb`: Converts .mbtiles format to .sqlitedb format, compatible with [OsmAnd](https://osmand.net/) and [Locus](https://www.locusmap.app/).
- `sqlitedb-cut`: Extracts a rectangular section of a map from a .sqlitedb file into a separate map file.
- `sqlitedb-merge`: Merges multiple .sqlitedb map files into a single file.
- `nakarteme-dl`: Downloads .mbtiles map files from [nakarte.me](https://tiles.nakarte.me/files).

Additionally, you can compress tiles using JPEG to reduce file size (see examples).

## 📦 Installing

**Python 3.10 or above is required.**

### Using [`pipx`](https://github.com/pypa/pipx) (recommended)

```sh
pipx install git+https://github.com/ZUB3C/sqlitedb-map-tools.git
```

### Using `pip`

```sh
pip install git+https://github.com/ZUB3C/sqlitedb-map-tools.git
```

---

## 🌿 Convert .mbtiles to .sqlitedb

```sh
mbtiles2sqlitedb [OPTIONS] INPUT_FILE OUTPUT_FILE
```

Converts .mbtiles format to .sqlitedb format suitable for OsmAnd and Locus.

```text
-f, --force                 Override the output file if it exists.
-j, --jpeg-quality INTEGER  Convert tiles to JPEG with the specified
                            quality.
```

### Examples

Simple:

```sh
mbtiles2sqlitedb input.mbtiles output.sqlitedb
```

Convert tiles to JPEG with compression level set to 80:

```sh
mbtiles2sqlitedb -j 80 input.mbtiles output.sqlitedb
```

## ✂️ Cut .sqlitedb map

```sh
sqlitedb-cut [OPTIONS] INPUT_FILE OUTPUT_FILE
```

Extracts a rectangular section of a map from a .sqlitedb file into a separate map.

```text
-l, --upper-left FLOAT...    Coordinates of the upper-left corner of the
                             section to be extracted.  [required]
-r, --bottom-right FLOAT...  Coordinates of the bottom-right corner of the
                             section to be extracted.  [required]
-f, --force                  Override the output file if it exists.
```

### Example

This command extracts a rectangular section from `map.sqlitedb` and saves it as
`map-fragment.sqlitedb`, using the specified coordinates for the upper-left and
bottom-right corners:

```sh
sqlitedb-cut map.sqlitedb map-fragment.sqlitedb --upper-left 44.00961 42.23831 --bottom-right 43.15811 43.01285
```

## 🧩 Merge .sqlitedb maps

```sh
sqlitedb-merge [OPTIONS] INPUT_FILES OUTPUT_FILE
```

Merges multiple .sqlitedb map files into a single file.

If multiple files contain tiles with the same coordinates, the tile from the
first file in the argument list will be used.

```text
-f, --force  Override the output file if it exists.
--help       Show this message and exit.
```

### Example

```sh
sqlitedb-merge map1.sqlitedb map2.sqlitedb merged-map.sqlitedb
```

## ⬇️ Download `nakarte.me` maps

```sh
nakarteme-dl [OPTIONS] MAPS...
```

Downloads .mbtiles map files from [tiles.nakarte.me](https://tiles.nakarte.me/files).

Use `all` as the map name to download all available maps.

```text
-o, --output DIRECTORY  Directory where maps will be downloaded.
-f, --force             Override the output file if it exists.
```

### Example

```sh
nakarteme-dl -o mbtiles topo500 topo1000
```

## ⬇️ Download raster map

```sh
raster-map-dl [OPTIONS] OUTPUT_FILE
```

Download tiles from remote server to .sqlitedb file.

```text
-f, --force                     Override the output file if it exists.
-u, --url-mask TEXT             Server url mask from where you want to
                                download tiles. It should have `{x}`, `{y}`
                                and `{z}` in it. For example, https://tile.o
                                penstreetmap.org/{z}/{x}/{y}.png.
                                [required]
-l, --upper-left FLOAT...       Coordinates of the upper-left corner of the
                                section to be extracted.  [required]
-r, --bottom-right FLOAT...     Coordinates of the bottom-right corner of
                                the section to be extracted.  [required]
--min-zoom INTEGER              Minimum zoom with which tiles will be
                                downloaded. By default 0.
--max-zoom INTEGER              Minimum zoom with which tiles will be
                                downloaded. By default 18.
--max-rpc, --max-requests-per-second INTEGER
                                Max requests per second limit. By default no
                                limit.
-t, --timeout INTEGER           Request timeount in seconds. By default 300.
--max-retry-count INTEGER       Maximum number of retries to server if
                                timeout is reached. By default 10.
-c, --chuck-size INTEGER        Size of a chunk with tiles stored in RAM.
                                After filling a chunk with tiles, they are
                                saved to .sqlitedb output file. By default
                                2048
```

### Example

```sh
raster-map-dl opentopomap-elbrus-region.sqlitedb -u "https://c.tile.opentopomap.org/{z}/{x}/{y}.png" --min-zoom 10 --max-zoom 16 --upper-left 44.00961 42.23831 --bottom-right 43.15811 43.01285
```

## 📜 License

This project is licensed under the GPLv3+ license - see the
[license file](https://github.com/ZUB3C/sqlitedb-map-tools/blob/master/LICENSE) for details.
