import os
import subprocess
from AmatsukamiLogger.base_logger import BaseLogger
import orjson


class JsonLogsHandler(BaseLogger):
    def __init__(self,
                 service_name: str = "unnamed_service",
                 redirect_3rd_party_loggers: bool = True) -> None:
        """ Creates A logger config log handler, suitable for K8S ENVs. """
        self._short_hash = self._get_git_revision_short_hash()
        self._service_name = service_name
        super().__init__(redirect_3rd_party_loggers)

    def _get_git_revision_short_hash(self) -> str:
        if commit_hash := os.environ.get("COMMIT_HASH"):
            return commit_hash
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--short', 'HEAD'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            if result.returncode:
                return "not_git_repo"
            return result.stdout.decode('ascii').strip()
        except Exception:
            return "not_git_repo"

    def log_format(self, record) -> str:
        record = self.lineup_external_log_record(record)
        log_record = self._get_base_log_fields(record)
        if exception := record["exception"]:
            log_record["exception_type"] = type(exception.value).__name__
            log_record["traceback"] = self._get_traceback()
        if extra := record["extra"]:
            log_record.update(extra)
        record["extra"]["serialized"] = orjson.dumps(
            log_record, default=str, option=orjson.OPT_APPEND_NEWLINE
        ).decode("utf-8")
        return "{extra[serialized]}"

    def _get_base_log_fields(self, record) -> dict:
        return {
            "line": record["line"],
            "module": record["module"],
            "timestamp": record["time"],
            "message": record["message"],
            "commit": self._short_hash,
            "service_name": self._service_name,
            "hostname": self._hostname,
            "level": record["level"].name,
        }
