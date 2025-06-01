from datetime import datetime
import os
import queue
import time
import requests

from config import Preset, Target
from logger import log_info
from presets import MANIFEST_PARSERS
from promise import Promise


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
        delay(10)


def delay(seconds: float):
    # log_info(f"Delaying for {seconds} seconds...")
    time.sleep(seconds)


def delay_until(timestamp: float):
    now = int(time.time())
    if timestamp <= now:
        return
    delay(timestamp - now)


def http_get(url):
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


def download_image(url: str, dest: str):
    path = dest
    if os.path.exists(dest):
        log_info(f"File {dest} already exists, skipping download.")
        return
    if os.path.isdir(dest):
        # If dest is a directory, construct the full path
        filename = os.path.basename(url)
        path = os.path.join(dest, filename)
        if os.path.exists(path):
            log_info(f"File {path} already exists, skipping download.")
            return
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    log_info(f"Downloading {url} to {path}...")
    response = http_get(url)

    with open(dest, "wb") as file:
        file.write(response.content)


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
        basename = os.path.basename(url)
        fmt = preset.export
        dest = fmt.format(
            basename=basename,
            target_name=target.name,
            timestamp=timestamp,
            utcdate=(
                datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")
                if timestamp
                else "unknown"
            ),
        )
        if dest.endswith("/") or dest.endswith("\\"):
            dest += basename
        if os.path.exists(dest):
            log_info(f"File {dest} already exists, skipping download.")
            continue
        log_info(f"Processing image: {image}, destination: {dest}")
        if not dest:
            log_info(f"Skipping image with empty destination: {image}")
            continue
        try:
            download_image(url, dest)
        except Exception as e:
            log_info(f"Failed to download image {url}: {e}")
    log_info(f"Polling for target {target.name} completed.")
