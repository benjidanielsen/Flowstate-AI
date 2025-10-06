import logging
import traceback
import sys
import threading
import datetime

class ErrorTracker:
    """
    ErrorTracker sets up comprehensive error tracking and reporting.
    It captures uncaught exceptions globally, logs them with detailed traceback,
    timestamps, and thread info. It also provides a manual logging interface.
    """

    def __init__(self, log_file_path="flowstate_ai_error.log"):
        self.logger = logging.getLogger("FlowstateAIErrorTracker")
        self.logger.setLevel(logging.ERROR)

        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | Thread-%(thread)d | %(message)s'
        )

        file_handler = logging.FileHandler(log_file_path)
        file_handler.setLevel(logging.ERROR)
        file_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)

        # Hook into the global exception handler
        sys.excepthook = self.handle_exception

        # For threading exceptions (Python 3.8+)
        if hasattr(threading, 'excepthook'):
            threading.excepthook = self.thread_exception_hook

    def handle_exception(self, exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            # Call default excepthook for KeyboardInterrupt
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        error_message = ''.join(
            traceback.format_exception(exc_type, exc_value, exc_traceback)
        )
        self.logger.error(f"Uncaught exception:\n{error_message}")

    def thread_exception_hook(self, args):
        # args is a threading.ExceptHookArgs object
        if issubclass(args.exc_type, KeyboardInterrupt):
            return

        error_message = ''.join(
            traceback.format_exception(args.exc_type, args.exc_value, args.exc_traceback)
        )
        self.logger.error(f"Uncaught thread exception (Thread-{args.thread.ident}):\n{error_message}")

    def log_error(self, error: Exception, context: str = None):
        """
        Manually log an error with optional context information.
        """
        error_message = ''.join(traceback.format_exception_only(type(error), error)).strip()
        context_message = f" Context: {context}" if context else ""
        self.logger.error(f"Manual error log: {error_message}{context_message}")


# Singleton instance for easy import and use
error_tracker = ErrorTracker()