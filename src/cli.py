import click

from .klb import klb
from .utils import SingletonLogger


@click.command()
@click.option("--debug", default=True, help="Enable debug mode")
def kook_live_bot(debug: bool) -> None:
    """
    Run the kook live bot.

    Args:
        debug: If True, run the bot in debug mode.
    """
    logger = SingletonLogger(debug).get_logger()
    klb()


if __name__ == "__main__":
    kook_live_bot()
