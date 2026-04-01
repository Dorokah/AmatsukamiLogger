import json
import logging
import sys
import warnings
from unittest.mock import patch

import pytest
from loguru import logger


@pytest.fixture(autouse=True)
def reset_logger():
    """Remove all loguru handlers before each test."""
    logger.remove()
    yield
    logger.remove()


# ---------------------------------------------------------------------------
# initialize()
# ---------------------------------------------------------------------------

class TestInitialize:
    def test_local_mode_logs_to_stderr(self, capsys):
        from AmatsukamiLogger import initialize
        initialize(enable_json_logging=False, service_name="svc", log_level="DEBUG")
        logger.info("hello local")
        captured = capsys.readouterr()
        assert "hello local" in captured.err

    def test_json_mode_emits_valid_json(self, capsys):
        from AmatsukamiLogger import initialize
        initialize(enable_json_logging=True, service_name="svc", log_level="DEBUG")
        logger.info("hello json")
        captured = capsys.readouterr()
        parsed = json.loads(captured.err.strip())
        assert parsed["message"] == "hello json"
        assert parsed["service_name"] == "svc"
        assert parsed["level"] == "INFO"

    def test_json_mode_includes_standard_fields(self, capsys):
        from AmatsukamiLogger import initialize
        initialize(enable_json_logging=True, service_name="svc")
        logger.warning("check fields")
        parsed = json.loads(capsys.readouterr().err.strip())
        for field in ("message", "level", "module", "line", "timestamp", "hostname", "commit", "service_name"):
            assert field in parsed, f"missing field: {field}"

    def test_no_stdout_when_log_to_stdout_false(self, capsys):
        from AmatsukamiLogger import initialize
        initialize(enable_json_logging=False, log_to_stdout=False)
        logger.info("should not appear")
        assert capsys.readouterr().err == ""

    def test_suppress_standard_logging(self):
        from AmatsukamiLogger import initialize
        initialize(
            enable_json_logging=False,
            suppress_standard_logging={"noisy_lib": logging.ERROR},
        )
        assert logging.getLogger("noisy_lib").level == logging.ERROR

    def test_no_auto_init_on_import(self):
        """Importing the package must not auto-initialize the logger."""
        mods_to_remove = [k for k in sys.modules if k.startswith("AmatsukamiLogger")]
        for mod in mods_to_remove:
            del sys.modules[mod]
        import AmatsukamiLogger
        assert not hasattr(AmatsukamiLogger, "logger_default_init_called")


# ---------------------------------------------------------------------------
# JsonLogsHandler
# ---------------------------------------------------------------------------

class TestJsonLogsHandler:
    def test_commit_hash_from_env(self, monkeypatch):
        monkeypatch.setenv("COMMIT_HASH", "abc1234")
        from AmatsukamiLogger.json_logs_handler import JsonLogsHandler
        handler = JsonLogsHandler()
        assert handler._short_hash == "abc1234"

    def test_commit_hash_git_fallback(self, monkeypatch):
        monkeypatch.delenv("COMMIT_HASH", raising=False)
        with patch("AmatsukamiLogger.json_logs_handler.subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = b"deadbee\n"
            from AmatsukamiLogger.json_logs_handler import JsonLogsHandler
            handler = JsonLogsHandler()
        assert handler._short_hash == "deadbee"

    def test_commit_hash_no_git(self, monkeypatch):
        monkeypatch.delenv("COMMIT_HASH", raising=False)
        with patch("AmatsukamiLogger.json_logs_handler.subprocess.run") as mock_run:
            mock_run.return_value.returncode = 128
            from AmatsukamiLogger.json_logs_handler import JsonLogsHandler
            handler = JsonLogsHandler()
        assert handler._short_hash == "not_git_repo"

    def test_commit_hash_subprocess_exception(self, monkeypatch):
        monkeypatch.delenv("COMMIT_HASH", raising=False)
        with patch("AmatsukamiLogger.json_logs_handler.subprocess.run", side_effect=OSError):
            from AmatsukamiLogger.json_logs_handler import JsonLogsHandler
            handler = JsonLogsHandler()
        assert handler._short_hash == "not_git_repo"

    def test_extra_fields_included_in_json(self, capsys):
        from AmatsukamiLogger import initialize
        initialize(enable_json_logging=True, service_name="svc")
        logger.info("with extra", user_id=42)
        parsed = json.loads(capsys.readouterr().err.strip())
        assert parsed["user_id"] == 42

    def test_exception_fields_in_json(self, capsys):
        from AmatsukamiLogger import initialize
        initialize(enable_json_logging=True, service_name="svc")
        try:
            raise ValueError("boom")
        except ValueError:
            logger.exception("caught it")
        parsed = json.loads(capsys.readouterr().err.strip())
        assert parsed["exception_type"] == "ValueError"
        assert "traceback" in parsed


# ---------------------------------------------------------------------------
# LocalLogsHandler
# ---------------------------------------------------------------------------

class TestLocalLogsHandler:
    def test_extra_types_default(self):
        from AmatsukamiLogger.local_logs_handler import LocalLogsHandler
        handler = LocalLogsHandler()
        assert int in handler.allowed_extra_fields_types
        assert float in handler.allowed_extra_fields_types
        assert bool in handler.allowed_extra_fields_types

    def test_extra_types_custom(self):
        from AmatsukamiLogger.local_logs_handler import LocalLogsHandler
        handler = LocalLogsHandler(local_logs_extra_types=[str, int])
        assert str in handler.allowed_extra_fields_types
        assert int in handler.allowed_extra_fields_types

    def test_is_allowed_extra_field_underscore_prefix(self):
        from AmatsukamiLogger.local_logs_handler import LocalLogsHandler
        handler = LocalLogsHandler()
        assert not handler._is_allowed_local_extra_field("_private", "value")

    def test_is_allowed_extra_field_short_string(self):
        from AmatsukamiLogger.local_logs_handler import LocalLogsHandler
        handler = LocalLogsHandler()
        assert handler._is_allowed_local_extra_field("key", "short value")

    def test_is_allowed_extra_field_long_string(self):
        from AmatsukamiLogger.local_logs_handler import LocalLogsHandler
        handler = LocalLogsHandler()
        assert not handler._is_allowed_local_extra_field("key", "x" * 41)

    def test_is_allowed_extra_field_multiline_string(self):
        from AmatsukamiLogger.local_logs_handler import LocalLogsHandler
        handler = LocalLogsHandler()
        assert not handler._is_allowed_local_extra_field("key", "line1\nline2")

    def test_commit_hash_from_env(self, monkeypatch):
        monkeypatch.setenv("COMMIT_HASH", "localtest")
        from AmatsukamiLogger.local_logs_handler import LocalLogsHandler
        handler = LocalLogsHandler()
        assert handler.short_hash == "localtest"


# ---------------------------------------------------------------------------
# LoguruForwarder / warnings redirect
# ---------------------------------------------------------------------------

class TestIntegrations:
    def test_third_party_logger_redirect(self, capsys):
        from AmatsukamiLogger import initialize
        initialize(enable_json_logging=False, redirect_3rd_party_loggers=True, log_level="DEBUG")
        logging.getLogger("some_lib").info("third party msg")
        assert "third party msg" in capsys.readouterr().err

    def test_warnings_redirect(self, capsys):
        from AmatsukamiLogger import initialize
        initialize(enable_json_logging=False, redirect_warnings=True, log_level="WARNING")
        with warnings.catch_warnings():
            warnings.simplefilter("always")
            warnings.warn("test warning message")
        assert "test warning message" in capsys.readouterr().err

    def test_context_injection_json(self, capsys):
        from AmatsukamiLogger import initialize
        initialize(enable_json_logging=True, service_name="ctx_svc")
        with logger.contextualize(request_id="req-xyz"):
            logger.info("ctx log")
        parsed = json.loads(capsys.readouterr().err.strip())
        assert parsed["request_id"] == "req-xyz"
