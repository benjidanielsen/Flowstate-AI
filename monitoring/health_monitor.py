import time
import threading
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class HealthMonitor:
    def __init__(self, check_interval=60, alert_email=None, recovery_callback=None):
        """
        :param check_interval: Seconds between health checks
        :param alert_email: Email address to send alerts to
        :param recovery_callback: Function to call for auto recovery
        """
        self.check_interval = check_interval
        self.alert_email = alert_email
        self.recovery_callback = recovery_callback
        self._stop_event = threading.Event()

    def check_system_health(self):
        """
        Implement actual system health checks here.
        Returns True if system is healthy, False otherwise.
        """
        # Placeholder checks:
        # Could be CPU usage, memory usage, service status, etc.
        # For demonstration, we simulate healthy system always.
        logging.info("Performing system health check...")
        # TODO: Add real health checks
        return True

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
                logging.error("System health check failed.")
                self.auto_recover()
                self.send_alert(
                    subject='Flowstate-AI System Health Alert',
                    message='System health check failed and auto-recovery attempted.'
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

    monitor = HealthMonitor(
        check_interval=30,
        alert_email='admin@flowstate-ai.com',
        recovery_callback=dummy_recovery
    )
    monitor.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        monitor.stop()
