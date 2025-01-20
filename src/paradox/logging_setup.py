import inspect
import logging
import os
import sys
from loguru import logger

#
os.environ.setdefault('KIVY_LOG_MODE', 'PYTHON')
os.environ.setdefault('LOGURU_AUTOINIT', '0')


class ToLoguru(logging.Handler):
    """
    This Handler redirects all stdlib logging to loguru.

    Usage:

    >> import logging
    >> logging.basicConfig(handlers=[ToLoguru()], level=0, force=True)

    """

    def emit(self, record: logging.LogRecord) -> None:
        import loguru

        # Get corresponding Loguru level if it exists.
        level: str | int
        try:
            level = loguru.logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        loguru.logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


# Redirect all stdlib logging to loguru
logging.basicConfig(handlers=[ToLoguru()], level=0, force=True)


# Loguru settings
logger.configure(handlers=[
    dict(
        sink = sys.stderr,
        # format="[{time}] {message}",
        level = "DEBUG",
        colorize = True,
        backtrace = True,
        diagnose = True,
        filter = {
            "": os.environ.get("LOGLEVEL", "INFO"),  # Default.
            "kivy.lang.parser": "ERROR",
            "kivy": os.environ.get("LOGLEVEL", "WARNING"),
            # "paradox.client": "DEBUG",
        }
    ),
    # dict(sink="file.log", enqueue=True, serialize=True),
])


logger.info('Logging configured')

