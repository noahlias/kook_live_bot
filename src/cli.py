import click

from .klb import klb
from .utils import SingletonLogger


@click.command()
@click.option("--debug", default=False, help="Enable debug mode")
def kook_live_bot(debug: bool) -> None:
    """
    Run the kook live bot.

    Args:
        debug: If True, run the bot in debug mode.
    """
    klb(debug=debug)


if __name__ == "__main__":
    kook_live_bot()
