import threading
import time


class Promise:
    def __init__(self):
        self._condition = threading.Condition()
        self._result = None
        self._is_resolved = False
        self._callback = None

    def resolve(self, result):
        with self._condition:
            self._result = result
            self._is_resolved = True
            if self._callback:
                self._callback(result)
            self._condition.notify_all()

    def then(self, callback):
        with self._condition:
            if self._is_resolved:
                # If already resolved, call the callback immediately
                callback(self._result)
            else:
                # Otherwise, store the callback to be called later
                self._callback = callback

    def wait(self):
        with self._condition:
            while not self._is_resolved:
                self._condition.wait()
            return self._result


def delay(seconds: float):
    # log_info(f"Delaying for {seconds} seconds...")
    time.sleep(seconds)


def delay_until(timestamp: float):
    now = int(time.time())
    if timestamp <= now:
        return
    delay(timestamp - now)


def start_thread(target, *args, **kwargs):
    thread = threading.Thread(target=target, args=args, kwargs=kwargs)
    thread.daemon = True  # Set as daemon thread
    thread.start()
    return thread
