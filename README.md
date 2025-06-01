# cloud-map-spider

## Feature

- Auto fetch and download cloud maps from NSMC and etc...
- Can be easily extended to other meteorological service sites

## Usage

```shell
git clone https://github.com/Jasonzyt/cloud-map-spider.git
cd cloud-map-spider
pip install -r requirements.txt
python3 main.py
```

## Implement

1. `poll`: polling threads will be created for all targets
2. `get_manifest`: get manifest from `target.url`
3. `parse_parset`: parse manifest content to image url list
4. `get_image`: get image data; if failed, mark `{url}` with `failed`
5. `save_temp`: save image to temp directory, marking `{url}` with `downloaded`
6. `do_exports`: do exports as the user definition
   1. If `exporter` returns `False`, mark `{url}.{export}` with `failed`; Otherwise, mark `{url}.{export}` with `success`
   2. If ALL exporters are marked with `success`, mark `{url}` with `success`
7. `clean`: if `{url}` is marked with `success`, delete the image from temp directory

## Legal Statement

This project is intended **solely for meteorological research purposes**.  
It is **not affiliated** with NSMC or any other organization.  
The contributors are **not responsible for any misuse or abuse** of this software.  
Please use this tool **legally and responsibly**.
