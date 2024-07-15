import click
from click_help_colors import HelpColorsGroup


@click.group(
    cls=HelpColorsGroup,
    help_headers_color="bright_green",
    help_options_color="bright_yellow",
)
def cli() -> None:
    pass
