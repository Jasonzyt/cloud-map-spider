import os

from config import Export
from logger import log_error, log_info


def do_export(data: bytes, exports: list[Export], url: str, variables: dict[str, str]):
    if not exports:
        log_error("No exports defined.")
        return
    for export in exports:
        exporter = EXPORTERS.get(export.type)
        if not exporter:
            log_error(f"Unknown export type: {export.type}")
            continue
        try:
            exporter(data, export, url, variables)
        except Exception as e:
            log_error(f"Error during export {export.name}: {e}")


# Exporters


def export_file(data: bytes, export: Export, url: str, variables: dict[str, str]):
    dest = export.path
    if not dest:
        log_error(f"No destination path specified for export {export.name}.")
        return
    try:
        dest = dest.format(**variables)
        if dest.endswith("/") or dest.endswith("\\"):
            dest += os.path.basename(url)

        if os.path.exists(dest):
            log_info(f"File {dest} already exists, skipping export.")
            return
        if not os.path.exists(os.path.dirname(dest)):
            os.makedirs(os.path.dirname(dest))
    except Exception as e:
        log_error(f"Error formatting destination path: {e}")
        return
    with open(dest, "wb") as file:
        file.write(data)
    log_info(f"Exported {url} to {dest}")


EXPORTERS = {
    "file": export_file,
}
