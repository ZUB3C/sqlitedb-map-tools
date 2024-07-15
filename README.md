# SQLiteDB Map Tools

Converts mbtiles format to sqlitedb format suitable for OsmAnd and RMaps.
Also possible convert tiles to jpeg to reduce the file size (`--jpeg-quality` option).

## Installing

**Python 3.10 or above is required**

```sh
pipx install git+https://github.com/ZUB3C/osmand-map-tools.git
```

## Convert mbtiles to sqlitedb

```text
Usage: mbtiles2sqlitedb [OPTIONS] INPUT_FILE OUTPUT_FILE

  Converts mbtiles format to sqlitedb format suitable for OsmAnd

Options:
  -f, --force                 Override output file if it exists
  -j, --jpeg-quality INTEGER  Convert tiles to JPEG with specified quality
  --help                      Show this message and exit.
```

### Examples

Simple:

```sh
mbtiles2sqlitedb input.mbtiles output.sqlitedb
```

Converting tiles to jpeg with compression:

```sh
mbtiles2sqlitedb -j 75 input.mbtiles output.sqlitedb
```

---

## Cut sqlitedb map

```text
Usage: sqlitedb-cut [OPTIONS] INPUT_FILE OUTPUT_FILE

  Cut rectangular piece of map from sqlitedb file into separate map

Options:
  -l, --upper-left FLOAT...    Coordinates of the upper left corner of the
                               piece of mapthat needs to be cut into a
                               separate map.  [required]
  -r, --bottom-right FLOAT...  Coordinates of the bottom right corner of the
                               piece of mapthat needs to be cut into a
                               separate map.  [required]
  -f, --force                  Override output file if it exists
  --help                       Show this message and exit.
```

### Example

```sh
sqlitedb-cut map.sqlitedb map-fragment.sqlitedb --upper-left 44.00961 42.23831 --bottom-right 43.15811 43.01285
```

---

## Merge sqlitedb maps

```text
Usage: sqlitedb-merge [OPTIONS] INPUT_FILES OUTPUT_FILE

  Merge multiple OsmAnd (.sqlitedb) files into a single file.

  If multiple files contain tile with the same coordinates, tile from first
  (from argument list) file will be used.

Options:
  -f, --force  Override output file if it exist
  --help       Show this message and exit.
```

### Example

```sh
sqlitedb-merge map1.sqlitedb map2.sqlitedb merged-map.sqlitedb
```

## Download [nakarte.me](https://nakarte.me) maps

```text
Usage: nakarteme-dl [OPTIONS] [MAPS]...

  Download .mbtiles map files from https://tiles.nakarte.me/files.

  Pass 'all' as map name to download all available maps.

Options:
  -o, --output DIRECTORY  Directory where maps will be downloaded
  -f, --force             Override output file if it exist
  --help                  Show this message and exit.
```

### Example

```sh
nakarteme-dl -o mbtiles topo500 topo1000
```

Available maps:
- ArbaletMO
- adraces
- eurasia25km
- ggc250
- ggc500
- ggc1000
- ggc2000
- montenegro250m
- new_gsh_050k
- new_gsh_100k
- osport
- purikov
- topo001m
- topo250
- topo500
- topo1000
- wikimedia_commons_images
