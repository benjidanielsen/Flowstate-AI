import logging
import sys
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_DIR = REPO_ROOT / "ai-gods"
if str(MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(MODULE_DIR))

import error_handling  # type: ignore  # noqa: E402


class ErrorHandlingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.logger = logging.getLogger("test_logger")
        self.logger.handlers.clear()
        self.log_records = []

        class ListHandler(logging.Handler):
            def emit(inner_self, record: logging.LogRecord) -> None:
                self.log_records.append(record)

        self.logger.addHandler(ListHandler())
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False

    def test_log_exception_returns_payload_and_logs(self) -> None:
        error = ValueError("boom")
        payload = error_handling.log_exception(
            self.logger,
            error,
            context={"component": "unit"},
            message="failure",
            level=logging.ERROR,
        )

        self.assertEqual(payload["event"], "exception")
        self.assertEqual(payload["error_type"], "ValueError")
        self.assertEqual(payload["message"], "failure")
        self.assertEqual(payload["component"], "unit")
        self.assertEqual(self.log_records[-1].levelno, logging.ERROR)

    def test_retry_succeeds_after_transient_error(self) -> None:
        attempt_container = {"count": 0}

        def flaky_operation() -> str:
            attempt_container["count"] += 1
            if attempt_container["count"] < 2:
                raise RuntimeError("try again")
            return "ok"

        with mock.patch.object(error_handling.time, "sleep", autospec=True) as sleep_mock:
            result = error_handling.retry(
                flaky_operation,
                retries=3,
                initial_delay=0.01,
                logger=self.logger,
                context={"operation": "flaky"},
            )

        self.assertEqual(result, "ok")
        self.assertEqual(attempt_container["count"], 2)
        sleep_mock.assert_called_once()

    def test_retry_raises_after_max_attempts(self) -> None:
        def always_fail() -> None:
            raise ValueError("nope")

        with mock.patch.object(error_handling.time, "sleep", autospec=True):
            with self.assertRaises(ValueError):
                error_handling.retry(
                    always_fail,
                    retries=1,
                    initial_delay=0.01,
                    logger=self.logger,
                    context={"operation": "always_fail"},
                )

        error_logs = [record for record in self.log_records if record.levelno >= logging.ERROR]
        self.assertTrue(error_logs, "Expected error log when retries exhausted")

    def test_guard_suppresses_exceptions_and_returns_none(self) -> None:
        calls = {"count": 0}

        @error_handling.guard(self.logger, context={"unit": "guard"})
        def guarded() -> str:
            calls["count"] += 1
            raise KeyError("fail")

        result = guarded()
        self.assertIsNone(result)
        self.assertEqual(calls["count"], 1)
        error_logs = [record for record in self.log_records if record.levelno >= logging.ERROR]
        self.assertTrue(error_logs)


if __name__ == "__main__":
    unittest.main()
