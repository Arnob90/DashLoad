import extras
import threading
import hook
import time


class NetworkConnectionPoller:
    def __init__(self, timeout=3.0, poll_ms=50) -> None:
        self.poll_ms = poll_ms
        self.timeout = timeout
        self.available = extras.internet_present(timeout=self.timeout)
        self.connection_status_changed_hook = hook.Hook()
        self.poll_thread = threading.Thread(target=self.poll, daemon=True)
        self.poll_thread.start()

    def poll(self):
        while True:
            currently_available = extras.internet_present(timeout=self.timeout)
            if self.available != currently_available:
                self.available = currently_available
                self.connection_status_changed_hook()
            time.sleep(self.poll_ms / 1000)
