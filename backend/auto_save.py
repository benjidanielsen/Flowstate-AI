import os
import json
import threading
import time
from datetime import datetime

class AutoSaveManager:
    def __init__(self, save_dir='auto_saves', interval=5):
        """
        :param save_dir: Directory where auto-save files will be stored
        :param interval: Auto-save interval in seconds
        """
        self.save_dir = save_dir
        self.interval = interval
        self.data = None
        self.version = 0
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
        self._thread = None

        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)

    def start(self, get_data_callback):
        """
        Start the auto-save thread
        :param get_data_callback: function that returns the current data state to save
        """
        self.get_data_callback = get_data_callback
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self):
        while not self._stop_event.is_set():
            time.sleep(self.interval)
            self.save_version()

    def save_version(self):
        """
        Save a new version of the data
        """
        with self._lock:
            self.data = self.get_data_callback()
            if self.data is None:
                return

            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            self.version += 1
            filename = f'version_{self.version}_{timestamp}.json'
            filepath = os.path.join(self.save_dir, filename)

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)

    def list_versions(self):
        """
        List all saved versions sorted by version number descending
        :return: list of filenames
        """
        files = os.listdir(self.save_dir)
        versions = [f for f in files if f.startswith('version_') and f.endswith('.json')]
        versions.sort(reverse=True)  # Newest first
        return versions

    def load_version(self, filename):
        """
        Load a specific version file
        :param filename: name of the version file
        :return: data loaded from file
        """
        filepath = os.path.join(self.save_dir, filename)
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Version file {filename} not found")

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data

    def rollback(self, filename):
        """
        Rollback to a specific version
        :param filename: version file to rollback to
        :return: data loaded after rollback
        """
        data = self.load_version(filename)
        with self._lock:
            self.data = data
            # Save a new version after rollback to keep history
            self.save_version()
        return data

    def stop(self):
        """Stop the auto-save thread"""
        self._stop_event.set()
        if self._thread:
            self._thread.join()
