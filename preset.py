from datetime import datetime
import xml.etree.ElementTree as ET

"""
parse_manifest_[preset]
Parameters:
- raw (str): The raw input string to be parsed.
Returns:
- list[dict]: A list of dictionaries containing parsed data.
"""


def parse_manifest_nsmc(raw: str) -> list[dict]:
    root = ET.fromstring(raw)

    images = []
    for image in root.findall("image"):
        time = image.get("time")
        url = image.get("url")
        if time:
            time_obj = datetime.strptime(time, "%Y-%m-%d %H:%M (%Z)")
            timestamp = int(time_obj.timestamp())
        else:
            timestamp = None
        if url.startswith("//"):
            url = "https:" + url
        images.append({"timestamp": timestamp, "url": url})
    return images


MANIFEST_PARSERS = {
    "nsmc.org.cn": parse_manifest_nsmc,
}
