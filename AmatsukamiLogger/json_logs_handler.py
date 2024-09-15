import os
from AmatsukamiLogger.base_logger import BaseLogger
import orjson


class JsonLogsHandler(BaseLogger):
    def __init__(self,
                 service_name: str = "unnamed_service",
                 enable_datadog_support: bool = os.getenv('AL_ENABLE_DATADOG_LOGGING', "False") in {"True", "true"},
                 redirect_3rd_party_loggers: bool = True):
        """ Creates A logger config log handler, suitable for K8S ENVs.
            You Must Have a COMMIT_HASH environment variable set to the commit hash
        """
        self.short_hash = self._get_git_revision_short_hash()
        self.service_name = service_name
        self.enable_datadog_support = enable_datadog_support
        if self.enable_datadog_support:
            import ddtrace
            self.tracer = ddtrace.tracer
            self.dd_config = ddtrace.config
        super().__init__(redirect_3rd_party_loggers)

    def _get_git_revision_short_hash(self):
        return os.environ["COMMIT_HASH"]

    def log_format(self, record):
        record = self.lineup_external_log_record(record)
        log_record = self._get_base_log_fields(record)
        if exception := record["exception"]:
            log_record["exception_type"] = type(exception.value).__name__
            log_record["traceback"] = self._get_traceback()
        if extra := record["extra"]:
            log_record.update(extra)
        record["extra"]["serialized"] = orjson.dumps(log_record, default=str, option=orjson.OPT_APPEND_NEWLINE).decode(
            "utf-8")
        return "{extra[serialized]}"

    def add_datadog_tags(self, log_fields):
        span = self.tracer.current_span() if self.enable_datadog_support else None
        trace_id, span_id = (span.trace_id, span.span_id) if span else (None, None)
        log_fields.update({
            'dd.trace_id': str(trace_id or 0),
            'dd.span_id': str(span_id or 0),
            'dd.env': self.dd_config.env or "",
            'dd.service': self.dd_config.service or "",
            'dd.version': self.dd_config.version or ""
        })

    def _get_base_log_fields(self, record):
        level = record["level"].name
        if self.enable_datadog_support and record["level"].no == 25:  # Datadog do not support SUCCESS LEVEL (25 is SUCCESS)
            level = 'INFO'
        log_fields = {
            "line": record["line"],
            "module": record["module"],
            "timestamp": record["time"],
            "message": record["message"],
            "commit": self.short_hash,
            "service_name": self.service_name,
            "hostname": self.hostname,
            "level": level
        }
        if self.enable_datadog_support:
            self.add_datadog_tags(log_fields)
        return log_fields
