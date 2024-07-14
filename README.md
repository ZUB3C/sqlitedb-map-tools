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

```sh
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

```sh
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
cut-osmand-map map.sqlitedb map-fragment.sqlitedb
```

---

# merge-osmand

```sh
merge-osmand [-h] [-f] input [input ...] output
```

```sh
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
