import os
import subprocess
import orjson
from AmatsukamiLogger.base_logger import BaseLogger


class LocalLogsHandler(BaseLogger):
    def __init__(self,
                 service_name: str = "unnamed_service",
                 local_logs_extra_types: [type] = None,
                 redirect_3rd_party_loggers: bool = True):
        """ Creates A config log handler, suitable for local ENVs.
        Parameters
        ----------
        service_name : str,
          field which will be in every log (default is "unnamed_service")
        local_logs_extra_types : [type],
          list of logs fields types which will be added to the first line in the log if possible
          (default is [int, float, bool]) plus str which does not have \n in them and their length do not pass 40 chars
        redirect_3rd_party_loggers : bool,
          flag used to redirect all loggers handlers that being used to loguru logger (default is True)
        """
        super().__init__(redirect_3rd_party_loggers)
        self.short_hash = self._get_git_revision_short_hash
        self.allowed_extra_fields_types = local_logs_extra_types or [int, float, bool]
        self._base_log_fields = ["|<level>{level}</level>",
                                 "| <level>{time:YYYY-MM-DD HH:mm:ss:SSS}</level>",
                                 f" |<level>{self.short_hash}</level>",
                                 f"| <level>{self._hostname}</level> ",
                                 f"| <level>{service_name}</level>",
                                 " | <level>{module}:{line}</level>"]

    def log_format(self, record):
        record = self.lineup_external_log_record(record)
        local_log_field = self._base_log_fields.copy()
        self._add_const_fields(local_log_field, record)
        self._handle_message_formating(local_log_field, record)
        self._add_pretty_print_extra_fields(local_log_field, record)
        return "".join(local_log_field)

    def _add_const_fields(self, local_log_field, record):
        simple_extra_fields_names = self._get_allowed_extra_fields(record)
        for field in simple_extra_fields_names:
            local_log_field.append(f" | <m>{field}:{record['extra'].pop(field)}</m>")

    def _get_allowed_extra_fields(self, record) -> set:
        simple_extra_fields = set()
        for field, value in record["extra"].items():
            if type(value) in self.allowed_extra_fields_types:
                simple_extra_fields.add(field)
        return {field for field, value in record["extra"].items() if self._is_allowed_local_extra_field(field, value)}

    def _is_allowed_local_extra_field(self, field, value) -> bool:
        if field[0] == '_':
            return False
        if type(value) in self.allowed_extra_fields_types:
            return True
        if type(value) == str and "\n" not in value and len(value) < 40:
            return True
        return False

    def _handle_message_formating(self, local_log_field, record):
        if exception := record["exception"]:
            record["extra"]["traceback"] = self._get_traceback()
            local_log_field[0] = "|<RED><normal><b>EXCEPTION</b></normal></RED>"
            local_log_field.append(
                f"\n|<RED><normal><b>{type(exception.value).__name__}</b></normal></RED>| <RED><normal><b><u>{exception.value}:</u></b></normal></RED> | " + "<level>{message}</level>")
            local_log_field.append("\n<red>{extra[traceback]}</red>\n")
        else:
            local_log_field.append("\n<level>{message}</level>\n")

    @staticmethod
    def _add_pretty_print_extra_fields(local_log_field, record):
        if extra := record["extra"]:
            if extra.get("traceback"):
                no_traceback_extra = extra.copy()
                del no_traceback_extra["traceback"]
                if no_traceback_extra:
                    record["extra"]["json_extra"] = orjson.dumps(no_traceback_extra, default=str,
                                                                 option=orjson.OPT_INDENT_2 |
                                                                        orjson.OPT_SORT_KEYS).decode('utf-8')
                    local_log_field.append("<level>{extra[json_extra]}</level>\n")
            else:
                record["extra"]["json_extra"] = orjson.dumps(extra, default=str,
                                                             option=orjson.OPT_INDENT_2 |
                                                                    orjson.OPT_SORT_KEYS).decode('utf-8')
                local_log_field.append("<level>{extra[json_extra]}</level>\n")


    @property
    def _get_git_revision_short_hash(self) -> str:
        if commit_hash := os.environ.get("COMMIT_HASH"):
            return commit_hash
        try:
            result = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
            if result.returncode:
                return "not_git_repo"
            else:
                return result.stdout.decode('ascii').strip()
        except Exception:
            return "not_git_repo"
