import datetime
import logging
import sys

log = logging.getLogger('netmode-noc')

class Style:
	RED 	= '\033[31m'
	YELLOW 	= '\033[33m'
	WHITE 	= '\033[97m'
	GREEN 	= '\033[32m'
	BLUE	= '\033[34m'
	ESCAPE 	= '\033[0m'


LOG_COLORS = {
    'WARNING': Style.YELLOW,
    'INFO': Style.WHITE,
    'DEBUG': Style.BLUE,
    'CRITICAL': Style.YELLOW,
    'ERROR': Style.RED
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


def init_logging(name='noc-netmode', logfile='main.log'):
    
    class LogFilter(logging.Filter):
        def __init__(self, level):
            self.level = level

        def filter(self, record):
            return record.levelno < self.level

    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)

    colored_formatter = ColoredFormatter('[%(asctime)s] [%(module)-10s] [%(levelname)-20s] %(message)s')
    log_filter = LogFilter(logging.WARNING)

    file_logger = logging.FileHandler(logfile)
    file_logger.setFormatter(logging.Formatter(fmt='[%(asctime)s] [%(levelname)s] %(message)s'))
    file_logger.setLevel(logging.DEBUG)

    logger_stdout = logging.StreamHandler(sys.stdout)
    logger_stdout.setFormatter(colored_formatter)
    logger_stdout.addFilter(log_filter)
    logger_stdout.setLevel(logging.INFO)

    logger_stderr = logging.StreamHandler(sys.stderr)
    logger_stderr.setFormatter(colored_formatter)
    logger_stderr.setLevel(logging.WARNING)


    logging.getLogger().addHandler(logger_stdout)
    logging.getLogger().addHandler(logger_stderr)
    logging.getLogger().addHandler(file_logger)

    return log
