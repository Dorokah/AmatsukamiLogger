import logging
import sys
import warnings
from pathlib import Path
from AmatsukamiLogger import logger


class LoguruForwarder(logging.Handler):
    # noinspection PyUnresolvedReferences,PyProtectedMember
    def emit(self, record):
        # Get corresponding Loguru level if it exists.
        message = f"[{record.name}] {record.getMessage()}"
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, message)


def showwarning(message, category, filename, lineno, file=None, line=None):
    path = Path(filename)
    extracted_external_logs_fields = {
        'module': path.stem,
        'line': lineno,
        'logger_name': f"warnings.warn"
    }
    new_message = warnings.formatwarning(message, category, filename, lineno, line)
    logger.warning(new_message, **extracted_external_logs_fields)
