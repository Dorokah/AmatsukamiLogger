import logging
import os
import sys
import warnings
from typing import Literal
from loguru import logger
from AmatsukamiLogger.local_logs_handler import LocalLogsHandler
from AmatsukamiLogger.loguru_forwarder import showwarning, LoguruForwarder
from AmatsukamiLogger.json_logs_handler import JsonLogsHandler


def take_over_loggers() -> None:
    logging.basicConfig(handlers=[LoguruForwarder()], level=0, force=True)


def initialize(enable_json_logging: bool = os.getenv('AL_ENABLE_JSON_LOGGING', "False") in {"True", "true"},
               service_name: str = "unnamed_service",
               log_level: Literal[
                   "TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "EXCEPTION", "CRITICAL"] = "INFO",
               local_logs_extra_types: list[type] | None = None,
               log_to_stdout: bool = True,
               log_file_name: str | None = None,
               loguru_stdout_extras: dict | None = None,
               loguru_log_file_extras: dict | None = None,
               redirect_3rd_party_loggers: bool = True,
               redirect_warnings: bool = True,
               suppress_standard_logging: dict | None = None,
               enable_colors: bool = True) -> None:
    """ Creates A logger config log handler and set loguru to use that handler.
    Parameters
    ----------
    enable_json_logging : bool
      when enabled logs will be sent in json format.
    service_name : str,
      field which will be in every log (default is "unnamed_service")
    log_level : str,
      TRACE < DEBUG < INFO < SUCCESS < WARNING < ERROR, EXCEPTION < CRITICAL (default is INFO)
    local_logs_extra_types : list[type] | None,
      list of logs fields types which will be added to the first line in the log if possible
      (default is [int, float, bool]) plus str which does not have \n in them and their length do not pass 40 chars
    log_to_stdout : bool,
      flag used to enable logging to stdout (default is True)
    log_file_name : str | None,
      flag used to enable logging to a file; the value will be the log file name (default is None)
    loguru_stdout_extras : dict | None,
      dict for extra args passed to logger.add() for stdout.
      https://loguru.readthedocs.io/en/stable/api/logger.html#loguru._logger.Logger.add
    loguru_log_file_extras : dict | None,
      dict for extra args passed to logger.add() for file logging.
      https://loguru.readthedocs.io/en/stable/api/logger.html#loguru._logger.Logger.add
    redirect_3rd_party_loggers : bool,
      flag used to redirect all stdlib logging handlers to loguru (default is True)
    redirect_warnings : bool,
      flag used to redirect all warnings.warn() to logger.warning() (default is True)
    suppress_standard_logging : dict{logger_name[str]: log_level[int]} | None,
      dict of loggers by name to set to the desired log level (default is None)
    enable_colors : bool,
      flag used to enable colored logs by level; only relevant when logging to console (default is True)
    """
    logger.remove()

    if enable_json_logging:
        logs_handler = JsonLogsHandler(service_name, redirect_3rd_party_loggers)
    else:
        logs_handler = LocalLogsHandler(service_name, local_logs_extra_types, redirect_3rd_party_loggers)

    if log_to_stdout:
        logger.add(sys.stderr, colorize=enable_colors, serialize=False, format=logs_handler.log_format,
                   level=log_level,
                   **(loguru_stdout_extras or {}))

    if log_file_name:
        logger.add(log_file_name, serialize=False, format=logs_handler.log_format, level=log_level,
                   **(loguru_log_file_extras or {}))

    if redirect_3rd_party_loggers:
        take_over_loggers()

    if redirect_warnings:
        warnings.showwarning = showwarning

    if suppress_standard_logging:
        for name, level in suppress_standard_logging.items():
            logging.getLogger(name).setLevel(level)
