import os


MODEL_FILE = "assets/comfy/models.json"
PCKG_FILE = "assets/comfy/model_pckg.json"
PACK_NAME = "xl_pack"

yes = os.path.exists(MODEL_FILE) and os.path.exists(PCKG_FILE)
if not yes:
    print(f"File not found {MODEL_FILE} or {PCKG_FILE}.")
    print("try to run from root directory")
    exit()

COMFY_PATH = os.getenv('COMFY')
if COMFY_PATH is None:
    print("!!! path to ComfyUI must be set in env variable 'COMFY'")
    exit()


import requests
from tqdm import tqdm


def ensure_path_exist(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

def download_model(model, to):
    model_dir = os.path.join(to, model["dst"])
    ensure_path_exist(model_dir)
    model_file = os.path.join(model_dir, model["file"])
    if os.path.exists(model_file):
        print(f"+++ model already downloaded at {model_file}")
        return
    
    download_file(model["link"], model_file)


def download_file(url, dst_file):
    block_kb = 64
    block_size = block_kb * 1024
    
    resp = requests.get(url, stream=True)
    total_size = resp.headers.get("content-length", 0)
    print(f"+++ downloading file size of {total_size}B")

    progres_bar = tqdm(total=int(total_size), unit="B")
    file = open(dst_file, "wb")
    for chunk in resp.iter_content(block_size):
        progres_bar.update(len(chunk))
        file.write(chunk)
    file.close()

import json

def main():
    f = open(MODEL_FILE, "r")
    models_list = json.load(f)["models"]
    f.close()

    f = open(PCKG_FILE, "r")
    packs = json.load(f)
    f.close()
    
    to_spawn_list = packs[PACK_NAME]

    for model in models_list:
        print(model)
        if model["name"] in to_spawn_list:
            download_model(model, os.path.join(COMFY_PATH, "models"))

    print("+++ all requested models spawned")

main()
