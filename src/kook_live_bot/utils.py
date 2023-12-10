import datetime
import sys

from loguru import logger


class SingletonLogger:
    _instance = None

    def __new__(cls, debug=False):
        if cls._instance is None:
            cls._instance = super(SingletonLogger, cls).__new__(cls)
            cls._instance._set_logger(debug)
        return cls._instance

    def _set_logger(self, debug):
        logger.remove()
        format_string = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"

        level = "DEBUG" if debug else "INFO"

        # stdout handler
        logger.add(sys.stdout, format=format_string, colorize=True, level=level)

        # file handler
        logger.add(
            "kook_live_bot.log",
            format=format_string,
            colorize=True,
            level=level,
            rotation="1 week",
            retention="10 days",
        )

    def get_logger(self):
        return logger


def calc_time_total(t: float) -> str:
    """
    Convert a time duration from seconds to a human-readable string.

    Args:
        t: The time duration in seconds.

    Returns:
        A string representing the time duration in a human-readable format.
    """
    t = int(t * 1000)
    if t < 5000:
        return f"{t} milliseconds"

    timedelta = datetime.timedelta(seconds=t // 1000)
    day = timedelta.days
    hour, mint, sec = tuple(int(n) for n in str(timedelta).split(",")[-1].split(":"))

    total = ""
    if day:
        total += f"{day} days "
    if hour:
        total += f"{hour} hours "
    if mint:
        total += f"{mint} minutes "
    if sec and not day and not hour:
        total += f"{sec} seconds "
    return total
