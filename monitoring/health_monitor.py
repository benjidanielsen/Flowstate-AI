import time
import threading
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
import os
import shutil
from importlib import import_module, util
from typing import Callable, Iterable, List, Optional, Tuple, Union


_PSUTIL = None
if util.find_spec("psutil") is not None:
    _PSUTIL = import_module("psutil")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class HealthMonitor:
    def __init__(
        self,
        check_interval: int = 60,
        alert_email: Optional[str] = None,
        recovery_callback: Optional[Callable[[], None]] = None,
        cpu_load_threshold: float = 0.85,
        memory_usage_threshold: float = 0.85,
        disk_usage_threshold: float = 0.9,
        disk_path: str = "/",
        custom_checks: Optional[Iterable[Callable[[], Union[bool, str, Tuple[bool, str], None]]]] = None,
    ) -> None:
        """Configure a new ``HealthMonitor`` instance.

        Args:
            check_interval: Seconds between health checks.
            alert_email: Email address to send alerts to.
            recovery_callback: Function to call for auto recovery attempts.
            cpu_load_threshold: Maximum acceptable normalized CPU load (5 min average).
            memory_usage_threshold: Maximum acceptable memory utilisation expressed as a
                fraction (e.g. ``0.85`` = 85%). This requires ``psutil``.
            disk_usage_threshold: Maximum acceptable disk usage expressed as a fraction.
            disk_path: Filesystem path whose disk usage should be monitored.
            custom_checks: Optional iterable of callables used for bespoke health
                checks. Each callable can return ``True``/``False`` or a tuple of the
                form ``(healthy: bool, message: str)``. Returning ``None`` is treated as
                success, while any other truthy value is recorded as a warning message.
        """
        self.check_interval = check_interval
        self.alert_email = alert_email
        self.recovery_callback = recovery_callback
        self.cpu_load_threshold = cpu_load_threshold
        self.memory_usage_threshold = memory_usage_threshold
        self.disk_usage_threshold = disk_usage_threshold
        self.disk_path = disk_path
        self.custom_checks = list(custom_checks or [])
        for check in self.custom_checks:
            if not callable(check):
                raise ValueError("All custom checks must be callable.")

        self._stop_event = threading.Event()
        self._last_health_report: List[str] = []

    def check_system_health(self) -> bool:
        """Run built-in and custom health checks.

        Returns ``True`` when the system is considered healthy, otherwise ``False``.
        ``self._last_health_report`` is populated with human-readable messages for any
        failing checks.
        """
        logging.info("Performing system health check...")
        issues = self._run_health_checks()
        self._last_health_report = issues

        if issues:
            for issue in issues:
                logging.warning(issue)
            return False

        return True

    def _run_health_checks(self) -> List[str]:
        issues: List[str] = []

        cpu_issue = self._check_cpu_load()
        if cpu_issue:
            issues.append(cpu_issue)

        memory_issue = self._check_memory_usage()
        if memory_issue:
            issues.append(memory_issue)

        disk_issue = self._check_disk_usage()
        if disk_issue:
            issues.append(disk_issue)

        issues.extend(self._run_custom_checks())

        return issues

    def _check_cpu_load(self) -> Optional[str]:
        if not hasattr(os, "getloadavg"):
            logging.debug("OS does not provide load averages; skipping CPU check.")
            return None

        try:
            _load1, load5, _load15 = os.getloadavg()
        except OSError as exc:  # pragma: no cover - platform specific
            logging.debug("Unable to read load average: %s", exc)
            return None

        cpu_count = os.cpu_count() or 1
        normalized_load = load5 / cpu_count

        if normalized_load > self.cpu_load_threshold:
            return (
                f"High CPU load detected: {normalized_load:.2f} (threshold "
                f"{self.cpu_load_threshold:.2f})"
            )

        return None

    def _check_memory_usage(self) -> Optional[str]:
        if _PSUTIL is None:
            logging.debug("psutil is not available; skipping memory usage check.")
            return None

        memory = _PSUTIL.virtual_memory()
        usage_ratio = memory.percent / 100.0

        if usage_ratio > self.memory_usage_threshold:
            return (
                "High memory usage detected: "
                f"{memory.percent:.1f}% (threshold {self.memory_usage_threshold * 100:.0f}%)"
            )

        return None

    def _check_disk_usage(self) -> Optional[str]:
        try:
            usage = shutil.disk_usage(self.disk_path)
        except FileNotFoundError:
            return f"Disk path '{self.disk_path}' could not be found for monitoring."

        if usage.total == 0:  # pragma: no cover - defensive
            return f"Disk path '{self.disk_path}' reports zero total capacity."

        used_ratio = usage.used / usage.total

        if used_ratio > self.disk_usage_threshold:
            return (
                f"Low disk space on '{self.disk_path}': {used_ratio * 100:.1f}% used "
                f"(threshold {self.disk_usage_threshold * 100:.0f}%)."
            )

        return None

    def _run_custom_checks(self) -> List[str]:
        issues: List[str] = []

        for check in self.custom_checks:
            check_name = getattr(check, "__name__", repr(check))
            try:
                result = check()
            except Exception as exc:  # pragma: no cover - custom user code
                issues.append(f"Custom check '{check_name}' raised an exception: {exc}")
                continue

            if isinstance(result, tuple):
                if not result:
                    issues.append(
                        f"Custom check '{check_name}' returned an empty result tuple."
                    )
                    continue
                healthy, *message_parts = result
                message = message_parts[0] if message_parts else ""
                if not healthy:
                    issues.append(
                        message or f"Custom check '{check_name}' reported an issue."
                    )
            elif isinstance(result, bool):
                if not result:
                    issues.append(f"Custom check '{check_name}' reported an issue.")
            elif result is not None:
                issues.append(f"Custom check '{check_name}' reported: {result}")

        return issues

    def get_last_health_report(self) -> List[str]:
        """Return the messages from the most recent health check."""
        return list(self._last_health_report)

    def auto_recover(self):
        logging.warning("Attempting auto-recovery...")
        if self.recovery_callback:
            try:
                self.recovery_callback()
                logging.info("Auto-recovery executed successfully.")
            except Exception as e:
                logging.error(f"Auto-recovery failed: {e}")
        else:
            logging.warning("No recovery callback provided.")

    def send_alert(self, subject, message):
        if not self.alert_email:
            logging.warning("Alert email not configured. Skipping alert.")
            return

        # Configure your SMTP server here
        smtp_server = 'smtp.example.com'
        smtp_port = 587
        smtp_user = 'alert@flowstate-ai.com'
        smtp_password = 'yourpassword'

        try:
            msg = MIMEMultipart()
            msg['From'] = smtp_user
            msg['To'] = self.alert_email
            msg['Subject'] = subject
            msg.attach(MIMEText(message, 'plain'))

            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
            server.quit()

            logging.info(f"Alert sent to {self.alert_email}")
        except Exception as e:
            logging.error(f"Failed to send alert email: {e}")

    def monitor_loop(self):
        logging.info("Starting health monitor loop...")
        while not self._stop_event.is_set():
            healthy = self.check_system_health()
            if not healthy:
                issue_summary = "; ".join(self._last_health_report) or "Unknown issue."
                logging.error("System health check failed: %s", issue_summary)
                self.auto_recover()
                detected_issues = self._last_health_report or ["Unknown issue"]
                alert_message = (
                    "System health check failed and auto-recovery was attempted.\n\n"
                    "Issues detected:\n- " + "\n- ".join(detected_issues)
                )
                self.send_alert(
                    subject='Flowstate-AI System Health Alert',
                    message=alert_message
                )
            else:
                logging.info("System is healthy.")
            time.sleep(self.check_interval)

    def start(self):
        self._stop_event.clear()
        self._thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self._thread.start()
        logging.info("Health monitor started.")

    def stop(self):
        self._stop_event.set()
        self._thread.join()
        logging.info("Health monitor stopped.")


# Example usage:
if __name__ == '__main__':
    def dummy_recovery():
        logging.info("Running dummy recovery steps...")

    def dummy_service_check():
        service_available = True
        return service_available, "Dummy service is unavailable."

    monitor = HealthMonitor(
        check_interval=30,
        alert_email='admin@flowstate-ai.com',
        recovery_callback=dummy_recovery,
        custom_checks=[dummy_service_check]
    )
    monitor.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        monitor.stop()
