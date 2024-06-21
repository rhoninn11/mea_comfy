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

def ospth(path: str) -> str:
    if os.name == "nt":
        path = path.replace("/", "\\")
    return path


offset = "https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_offset_example-lora_1.0.safetensors"
hyper_2_steps = "https://huggingface.co/ByteDance/Hyper-SD/resolve/main/Hyper-SDXL-2steps-lora.safetensors"
hyper_8_steps = "https://huggingface.co/ByteDance/Hyper-SD/resolve/main/Hyper-SDXL-8steps-CFG-lora.safetensors"
hyper_12_steps = "https://huggingface.co/ByteDance/Hyper-SD/resolve/main/Hyper-SDXL-12steps-CFG-lora.safetensors"
# brushnet = "https://huggingface.co/Kijai/BrushNet-fp16/resolve/main/brushnet_random_mask_fp16.safetensors" #fuck this is for 1.5 
brushnet = "https://huggingface.co/grzelakadam/brushnet_xl_models/resolve/main/random_mask_brushnet_ckpt_sdxl_v0.safetensors" 

comfy_path = os.getenv('COMFY')
if comfy_path is None:
    print("!!! path to ComfyUI must be set in env variable 'COMFY'")
    exit()

loras = "models/loras/"
inpaint = "models/inpaint/"

loras_path = os.path.join(comfy_path, loras)
inpaint_path = os.path.join(comfy_path, inpaint)

# download_file(hyper_2_steps, ospth(loras_path))
# download_file(hyper_8_steps, ospth(loras_path))
# download_file(hyper_12_steps, ospth(loras_path))
if os.path.exists(comfy_path):
    print("elo")
    os.makedirs(inpaint_path, exist_ok=True)
download_file(brushnet, inpaint_path)
# download_file(offset, ospth(loras_path))