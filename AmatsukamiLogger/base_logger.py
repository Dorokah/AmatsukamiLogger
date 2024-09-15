import abc
import socket
import traceback


class BaseLogger:
    def __init__(self, redirect_3rd_party_loggers: bool = True):
        self._hostname = socket.gethostname()
        self._redirect_3rd_party_loggers = redirect_3rd_party_loggers

    @abc.abstractmethod
    def log_format(self, record):
        pass

    @abc.abstractmethod
    def _get_git_revision_short_hash(self):
        pass

    def lineup_external_log_record(self, record):
        if self._redirect_3rd_party_loggers and 'logger_name' in record['extra']:
            record['module'] = record['extra'].pop('module')
            record['line'] = record['extra'].pop('line')
        return record

    @staticmethod
    def _get_traceback():
        return traceback.format_exc()
