import datetime
import logging
import sys

log = logging.getLogger('netmode-noc')


class Style:
    RED = '\033[31m'
    YELLOW = '\033[33m'
    WHITE = '\033[97m'
    GREEN = '\033[32m'
    BLUE = '\033[34m'
    ESCAPE = '\033[0m'
    UNDERLINE = '\033[4m'
    BOLD = '\033[1m'


LOG_COLORS = {
    'DEBUG': Style.BLUE,
    'INFO': Style.WHITE,
    'WARNING': Style.YELLOW,
    'ERROR': Style.RED,
    'CRITICAL': Style.RED,
}


class ColoredFormatter(logging.Formatter):

    def __init__(self, msg):
        logging.Formatter.__init__(self, fmt=msg)

    def format(self, record):
        levelname = record.levelname
        if levelname in LOG_COLORS:
            levelname_color = LOG_COLORS[levelname] + levelname + Style.ESCAPE
            record.levelname = levelname_color
        return logging.Formatter.format(self, record)


def init_logging(name='noc-netmode', logfile='logs/main.log'):

    class LogFilter(logging.Filter):

        def __init__(self, level):
            self.level = level

        def filter(self, record):
            return record.levelno < self.level

    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)

    colored_formatter = ColoredFormatter(
        '[%(asctime)s] [%(module)s.%(funcName)s] [%(levelname)s] %(message)s')

    logger_stderr = logging.StreamHandler(sys.stderr)
    logger_stderr.setFormatter(colored_formatter)
    logger_stderr.setLevel(logging.DEBUG)

    log.addHandler(logger_stderr)

    return log
