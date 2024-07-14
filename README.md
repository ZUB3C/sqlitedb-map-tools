# mbtiles2osmand

Converts mbtiles format to sqlitedb format suitable for OsmAnd and RMaps.
Also possible convert tiles to jpeg to reduce the file size (`--jpg` option).

## Installing

```sh
git clone https://github.com/ZUB3C/osmand-map-tools.git
cd osmand-map-tools
poetry install
poetry shell
```


## Usage

`python mbtiles2osmand.py [-h] [-f] [--jpg JPEG_QUALITY] input output`

```
input               input file
output              output file

optional arguments:
  -h, --help          show this help message and exit
  -f, --force          override output file if exists
  --jpg JPEG_QUALITY  convert tiles to JPEG with specified quality
```

## Examples

Simple:
`python mbtiles2osmand.py input.mbtiles output.sqlitedb`

Converting tiles to jpeg with compression:
`python mbtiles2osmand.py --jpg 75 input.mbtiles output.sqlitedb`

---

# cut_osmand_map

`python cut_osmand_map map.sqlitedb map-fragment.sqlitedb`



# merge_osmand

`python merge_osmand.py [-h] [-f] input [input ...] output`
```
Unite multiple osmand files into single

positional arguments:
  input       input files. If multiple files contain tile with the same coordinates tile from first (from argument list) file will be used
  output      output file

optional arguments:
  -h, --help  show this help message and exit
  -f, -force  override output file if exists
```
