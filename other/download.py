import requests
from tqdm import tqdm

import os

def ensure_path_exist(path):
    if os.path.exists(path):
        os.makedirs(path, exist_ok=True)

def download_file(save_path, url):
    block_kb = 64
    block_size = block_kb * 1024
    
    ensure_path_exist(save_path)
    filename = url.split("/")[-1]
    dst_file = os.path.join(save_path, filename)
    if os.path.exists(dst_file):
        print(f"+++ model already downloaded:D ({filename})")
        return
    
    resp = requests.get(url, stream=True)
    total_size = resp.headers.get("content-length", 0)
    print(f"+++ downloading model ({filename}) size of {total_size}B")

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

flux_dev = "https://huggingface.co/Comfy-Org/flux1-dev/resolve/main/flux1-dev-fp8.safetensors"
flux_schenll = "https://huggingface.co/Comfy-Org/flux1-schnell/resolve/main/flux1-schnell-fp8.safetensors"
flux_dev_nf4 = "https://huggingface.co/lllyasviel/flux1-dev-bnb-nf4/resolve/main/flux1-dev-bnb-nf4-v2.safetensors"
flux_dev_gguf_5b = "https://huggingface.co/city96/FLUX.1-dev-gguf/resolve/main/flux1-dev-Q5_0.gguf"
flux_dev_gguf_4b = "https://huggingface.co/city96/FLUX.1-dev-gguf/resolve/main/flux1-dev-Q4_0.gguf"



comfy_path = os.getenv('COMFY')
if comfy_path is None:
    print("!!! path to ComfyUI must be set in env variable 'COMFY'")
    exit()

loras_path = os.path.join(comfy_path, "models/loras/")
inpaint_path = os.path.join(comfy_path, "models/inpaint/")
unet_path = os.path.join(comfy_path, "models/unet/")
checkpoints_path = os.path.join(comfy_path, "models/checkpoints")


download_file(unet_path, flux_dev_gguf_4b)