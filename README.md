# mbtiles2osmand

Converts mbtiles format to sqlitedb format suitable for OsmAnd and RMaps.
Also possible convert tiles to jpeg to reduce the file size (`--jpg` option).

## Installing

```sh
pipx install git+https://github.com/ZUB3C/osmand-map-tools.git
```

## Usage

```
mbtiles2osmand [-h] [-f] [--jpg JPEG_QUALITY] input output
```

```text
input               input file
output              output file

optional arguments:
  -h, --help          show this help message and exit
  -f, --force          override output file if exists
  --jpg JPEG_QUALITY  convert tiles to JPEG with specified quality
```

### Examples

Simple:

```sh
mbtiles2osmand input.mbtiles output.sqlitedb
```

Converting tiles to jpeg with compression:

```sh
mbtiles2osmand --jpg 75 input.mbtiles output.sqlitedb
```

---

# cut-osmand-map

```sh
cut-osmand-map [-h] [-f] [-l UPPER_LEFT UPPER_LEFT] [-r BOTTOM_RIGHT BOTTOM_RIGHT] input output
```

```text
Cut rectangular piece of map from sqlitedb file into separate map

positional arguments:
  input                 input file directory
  output                output file directory

options:
  -h, --help            show this help message and exit
  -f, --force           override output files if exists
  -l UPPER_LEFT UPPER_LEFT, --upper-left UPPER_LEFT UPPER_LEFT
                        Coordinates of the upper left corner of the piece of mapthat needs to be cut into a separate map.
  -r BOTTOM_RIGHT BOTTOM_RIGHT, --bottom-right BOTTOM_RIGHT BOTTOM_RIGHT
                        Coordinates of the bottom right corner of the piece of mapthat needs to be cut into a separate map.
```

### Example

```sh
cut-osmand-map map.sqlitedb map-fragment.sqlitedb --upper-left 44.00961 42.23831 --bottom-right 43.15811 43.01285
```

---

# merge-osmand

```sh
merge-osmand [-h] [-f] input [input ...] output
```

```text
Unite multiple osmand files into single

positional arguments:
  input       input files. If multiple files contain tile with the same coordinates tile from first (from argument list) file will be used
  output      output file

optional arguments:
  -h, --help  show this help message and exit
  -f, -force  override output file if exists
```

### Example

```sh
merge-osmand map1.sqlitedb map2.sqlitedb merged-map.sqlitedb
```

# download-nakarte-me-maps

```sh
download-nakarte-me-maps [-h] [-f] [--jpg JPEG_QUALITY] [-m MAPS [MAPS ...]] maps_dir
```

```text
Download mbtiles files from https://tiles.nakarte.me/files

positional arguments:
  maps_dir              directory where maps will be downloaded

options:
  -h, --help            show this help message and exit
  -f, --force           override output files if exists
  --jpg JPEG_QUALITY    convert tiles to JPEG with specified quality
  -m MAPS [MAPS ...], --maps MAPS [MAPS ...]
                        list of map names to download
```

### Example

```sh
download-nakarte-me-maps mbtiles -m topo500 topo1000
```

Available maps:

    ArbaletMO
    adraces
    eurasia25km
    ggc250
    ggc500
    ggc1000
    ggc2000
    montenegro250m
    new_gsh_050k
    new_gsh_100k
    osport
    purikov
    topo001m
    topo250
    topo500
    topo1000
    wikimedia_commons_images
