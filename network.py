from datetime import datetime
import os
import queue
import requests

from config import Preset, Target
import exporter
from logger import log_info
from preset import MANIFEST_PARSERS
from async_utils import Promise, delay


q = queue.Queue()


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
    manifest = None
    try:
        manifest = get_manifest(target)
    except Exception as e:
        log_info(f"Failed to get manifest for target {target.name}: {e}")
        return
    for image in manifest:
        timestamp = image.get("timestamp")
        url = image.get("url")
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
        except Exception as e:
            log_info(f"Failed to get image {url}: {e}")
        if data is None:
            log_info(f"Skipping export for {url} due to previous error.")
            continue
        log_info(f"Exporting {url} with variables {variables}...")
        try:
            exporter.do_export(data, preset.exports, url, variables)
        except Exception as e:
            log_info(f"Error during export for {url}: {e}")
            continue

    log_info(f"Polling for target {target.name} completed.")
