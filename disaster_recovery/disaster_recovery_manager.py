import logging
import time
import threading

class DisasterRecoveryManager:
    def __init__(self, primary_service, backup_service, check_interval=10):
        """
        :param primary_service: An object with is_healthy() and failover() methods
        :param backup_service: An object with start() and is_healthy() methods
        :param check_interval: Time interval in seconds to check service health
        """
        self.primary_service = primary_service
        self.backup_service = backup_service
        self.check_interval = check_interval
        self.failover_triggered = False
        self._stop_event = threading.Event()
        self.monitor_thread = threading.Thread(target=self._monitor_services, daemon=True)
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def start(self):
        logging.info("Starting Disaster Recovery Manager...")
        self.backup_service.start()
        self.monitor_thread.start()

    def stop(self):
        logging.info("Stopping Disaster Recovery Manager...")
        self._stop_event.set()
        self.monitor_thread.join()

    def _monitor_services(self):
        while not self._stop_event.is_set():
            try:
                if not self.primary_service.is_healthy():
                    logging.warning("Primary service is down. Initiating failover.")
                    if not self.failover_triggered:
                        self.primary_service.failover(self.backup_service)
                        self.failover_triggered = True
                else:
                    if self.failover_triggered:
                        logging.info("Primary service recovered. Reverting failover.")
                        self.primary_service.revert_failover()
                        self.failover_triggered = False
            except Exception as e:
                logging.error(f"Error during health check or failover: {e}")
            time.sleep(self.check_interval)


# Example stub classes to demonstrate usage (replace with real implementations)
class Service:
    def __init__(self, name):
        self.name = name
        self._healthy = True
        self._active = False

    def is_healthy(self):
        # Implement actual health check logic here
        return self._healthy

    def failover(self, backup_service):
        logging.info(f"Failing over from {self.name} to {backup_service.name}")
        self._active = False
        backup_service._active = True

    def revert_failover(self):
        logging.info(f"Reverting failover to primary service {self.name}")
        self._active = True

    def start(self):
        logging.info(f"Starting service {self.name}")
        self._active = True


# Example usage:
# primary = Service('PrimaryService')
# backup = Service('BackupService')
# drm = DisasterRecoveryManager(primary, backup)
# drm.start()
# ... later drm.stop()
