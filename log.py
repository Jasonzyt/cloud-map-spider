import pickle
import time

from logger import log_info

LOG_FILE = "./spider_log.dat"
KEEP_TIME = 60 * 60 * 24 * 3  # 7 days in seconds


class UrlLog:
    def __init__(
        self,
        url: str,
        timestamp: str,
        tempfile: str = None,
        exports: dict[str, bool] = {},
    ):
        self.url = url
        self.timestamp = timestamp
        self.tempfile = tempfile
        self.exports = exports

    @property
    def success(self) -> bool:
        success = True
        for export in self.exports.values():
            if not export:
                success = False
                break
        return success

    @property
    def downloaded(self) -> bool:
        return self.tempfile is not None

    def __repr__(self):
        return f"UrlLog(url={self.url}, timestamp={self.timestamp}, tempfile={self.tempfile}, exports={self.exports})"


class Log:
    def __init__(self, logs: list[UrlLog] = []):
        self.logs = logs

    def add(self, url_log: UrlLog):
        log_info(f"Adding log: {url_log}")
        self.logs.append(url_log)

    def update(self, new_log: UrlLog) -> bool:
        log_info(f"Updating log: {new_log}")
        for i, log in enumerate(self.logs):
            if log.url == new_log.url:
                self.logs[i] = new_log
                return True
        return False

    def search(self, url: str) -> UrlLog | None:
        for log in self.logs:
            if log.url == url:
                return log
        return None

    def clean(self):
        current_time = time.time()
        self.logs = [
            log
            for log in self.logs
            if current_time - log.timestamp < KEEP_TIME or not log.success
        ]

    @staticmethod
    def load() -> "Log":
        try:
            with open(LOG_FILE, "rb") as file:
                log = pickle.load(file)
                log.clean()
                return log
        except FileNotFoundError:
            return Log()

    def save(self):
        self.clean()
        with open(LOG_FILE, "wb") as file:
            pickle.dump(self, file)
