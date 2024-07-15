GGC_MAP_SCALES = [250, 500, 1000, 2000]
TOPO_MAP_SCALES = [250, 500, 1000]
MAP_NAMES = [
    "ArbaletMO",
    "adraces",
    "eurasia25km",
    *[f"ggc{scale}" for scale in GGC_MAP_SCALES],
    "montenegro250m",
    "new_gsh_050k",
    "new_gsh_100k",
    "osport",
    "purikov",
    "topo001m",
    *[f"topo{scale}" for scale in TOPO_MAP_SCALES],
    "wikimedia_commons_images",
]
TILES_URL = "https://tiles.nakarte.me/files"
