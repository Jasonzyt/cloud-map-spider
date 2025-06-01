from datetime import datetime
import os
import queue
import requests

from config import Preset, Target
import exporter
from log import Log, UrlLog
from logger import log_error, log_info
from preset import MANIFEST_PARSERS
from async_utils import Promise, delay


q = queue.Queue()
log = Log.load()


def process_queue():
    while True:
        (url, promise) = q.get()
        if url is None:
            break
        response = requests.get(url)
        log_info(f"GET {url} {response.status_code} {response.reason}")
        if promise is not None:
            promise.resolve(response)
        delay(5)


def http_get(url) -> requests.Response:
    log_info(f"Adding {url} to queue for processing...")
    promise = Promise()
    q.put((url, promise))
    return promise.wait()


def get_manifest(target: Target):
    response = http_get(target.manifest)
    manifest = MANIFEST_PARSERS[target.preset](
        response.text
    )  # Call the preset parser function
    return manifest


def get_image(url: str) -> bytes:
    response = http_get(url)
    response.raise_for_status()  # Raise an error for bad responses
    return response.content


def poll(target: Target, preset: Preset):
    log_info(f"Polling {target}...")
    if not os.path.exists("./temp"):
        os.makedirs("./temp")
        log_info("Temporary directory created at ./temp.")
    manifest = None
    try:
        manifest = get_manifest(target)
    except Exception as e:
        log_error(f"Failed to get manifest for target {target.name}: {e}")
        return
    for image in manifest:
        timestamp = image.get("timestamp")
        url = image.get("url")
        url_log = log.search(url)
        if url_log is not None and (url_log.success or url_log.downloaded):
            log_info(f"Skipping {url} as it has already been processed or downloaded.")
            continue
        elif url_log is None:
            url_log = UrlLog(url, timestamp)
            log.add(url_log)
            log.save()
        variables = {
            "target_name": target.name,
            "timestamp": timestamp,
            "utcdate": (
                datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")
                if timestamp
                else "unknown"
            ),
            "utchour": (
                datetime.fromtimestamp(timestamp).strftime("%H")
                if timestamp
                else "unknown"
            ),
            "utcminute": (
                datetime.fromtimestamp(timestamp).strftime("%M")
                if timestamp
                else "unknown"
            ),
            "basename": os.path.basename(url),
            "extname": os.path.splitext(url)[1],
        }
        data = None
        try:
            data = get_image(url)
            tempfile = f"./temp/{variables['basename']}"
            with open(tempfile, "wb") as f:
                log_info(f"Saving image to temporary file {tempfile}...")
                f.write(data)
            url_log.tempfile = tempfile
            log.update(url_log)
            log.save()
        except Exception as e:
            log_error(f"Failed to get image {url}: {e}")
        if data is None:
            log_info(f"Skipping export for {url} due to previous error.")
            continue
        log_info(f"Exporting {url} with variables {variables}...")
        try:
            url_log.exports = exporter.do_exports(data, preset.exports, url, variables)
            if url_log.success:
                log_info(f"All exports are done successfully, removing temp file...")
                os.remove(url_log.tempfile)
                url_log.tempfile = None
            log.update(url_log)
            log.save()
        except Exception as e:
            log_error(f"Error during export for {url}: {e}")
            continue

    log_info(f"Polling for target {target.name} completed.")
