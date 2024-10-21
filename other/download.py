import requests
from tqdm import tqdm

import os

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
    
    download_file(model["url"], model_file)


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

model_file = "assets/comfy/models.json"
spawn_file = "assets/comfy/to_spawn.json"
yes = os.path.exists(model_file) and os.path.exists(spawn_file)
if not yes:
    print(f"File not found {model_file} or {spawn_file}.")
    print("try to run from root directory")
    exit()

comfy_path = os.getenv('COMFY')
if comfy_path is None:
    print("!!! path to ComfyUI must be set in env variable 'COMFY'")
    exit()

import json

f = open(model_file, "r")
models_list = json.load(f)["models"]
f.close()
f = open(spawn_file, "r")
to_spawn_list = json.load(f)["to_spawn"]
f.close()

for model in models_list:
    if model["name"] in to_spawn_list:
        download_model(model, os.path.join(comfy_path, "models"))

print("+++ all requested models spawned")
