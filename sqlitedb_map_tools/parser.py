from html.parser import HTMLParser

import requests

from .const import TILES_URL


class NakarteMeHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.data: list[str] = []
        self.current_tag: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.current_tag = tag

    def handle_endtag(self, tag: str) -> None:
        self.current_tag = None

    def handle_data(self, data: str) -> None:
        if self.current_tag == "a":
            self.data.append(data)


def get_available_map_names() -> list[str]:
    parser = NakarteMeHTMLParser()
    html = requests.get(TILES_URL, timeout=60).text
    parser.feed(html)
    maps = parser.data
    if "../" in maps:
        maps.remove("../")
    maps = [map_name.replace(".mbtiles", "", 1) for map_name in maps]
    return sorted(maps)
