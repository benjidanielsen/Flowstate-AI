import time
import threading
import requests

class PollingSystem:
    def __init__(self, poll_interval, endpoint, callback):
        """
        Initializes the polling system.

        :param poll_interval: Time in seconds between polls.
        :param endpoint: URL or API endpoint to poll.
        :param callback: Function to call with new data when updates detected.
        """
        self.poll_interval = poll_interval
        self.endpoint = endpoint
        self.callback = callback
        self._stop_event = threading.Event()
        self._thread = None
        self._last_data = None

    def _poll(self):
        while not self._stop_event.is_set():
            try:
                response = requests.get(self.endpoint)
                response.raise_for_status()
                data = response.json()

                if data != self._last_data:
                    self._last_data = data
                    self.callback(data)
            except Exception as e:
                print(f"Polling error: {e}")

            time.sleep(self.poll_interval)

    def start(self):
        if self._thread and self._thread.is_alive():
            print("Polling already running")
            return

        self._stop_event.clear()
        self._thread = threading.Thread(target=self._poll)
        self._thread.daemon = True
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join()


# Example callback function
if __name__ == "__main__":
    def print_update(data):
        print(f"Received update: {data}")

    # Example usage
    poller = PollingSystem(poll_interval=5, endpoint="https://api.example.com/updates", callback=print_update)
    poller.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        poller.stop()
        print("Polling stopped")
