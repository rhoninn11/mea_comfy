import requests
from tqdm import tqdm

import os


def download_file(url, save_path):
    filename = url.split("/")[-1]
    resp = requests.get(url, stream=True)
    total_size = resp.headers.get("content-length", 0)
    block_kb = 64
    block_size = block_kb * 1024
    print(total_size)
    progres_bar = tqdm(total=int(total_size), unit="B")
    file = open(os.path.join(save_path, filename), "wb")
    for chunk in resp.iter_content(block_size):
        progres_bar.update(len(chunk))
        file.write(chunk)
    file.close()


hyper_2_steps = "https://huggingface.co/ByteDance/Hyper-SD/resolve/main/Hyper-SDXL-2steps-lora.safetensors"
hyper_8_steps = "https://huggingface.co/ByteDance/Hyper-SD/resolve/main/Hyper-SDXL-8steps-CFG-lora.safetensors"
hyper_12_steps = "https://huggingface.co/ByteDance/Hyper-SD/resolve/main/Hyper-SDXL-12steps-CFG-lora.safetensors"
brushnet = "https://huggingface.co/Kijai/BrushNet-fp16/resolve/main/brushnet_random_mask_fp16.safetensors"

comfy_path = "C:/Users/artla/Desktop/dev/comfy_ui/"
loras = "models/loras/"
inpaint = "models/inpaint/"

hyper_8_steps_path = os.path.join(comfy_path, loras)
hyper_12_steps_path = os.path.join(comfy_path, loras)
brushnet_path = os.path.join(comfy_path, inpaint)

# download_file(hyper_8_steps, hyper_8_steps_path)
# download_file(hyper_12_steps, hyper_12_steps_path)
if os.path.exists(comfy_path):
    print("elo")
    os.makedirs(brushnet_path, exist_ok=True)
download_file(brushnet, brushnet_path)