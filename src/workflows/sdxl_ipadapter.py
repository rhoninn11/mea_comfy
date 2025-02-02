import torch
import numpy as np

from comfy_script.runtime.real import *
load()
from comfy_script.runtime.real.nodes import *

from skimage import io

from src.utils_mea import img_pt_2_np

MODELS = []

def load_models_once():
    global MODELS
    if len(MODELS):
        return tuple(MODELS)
    
    model, clip, vae = CheckpointLoaderSimple('photopediaXL_45.safetensors')
    model, clip = LoraLoader(model, clip, 'Hyper-SDXL-12steps-CFG-lora.safetensors', 0.9, 1)
    model, ipnet = IPAdapterUnifiedLoader(model, 'STANDARD (medium strength)', None)

    MODELS = [model, clip, vae, ipnet]
    print("+++ models loaded")
    return tuple(MODELS)

def sdxl_ipadapter(in_img: torch.Tensor, mask: torch.Tensor, prompt_text: str, img_power: float):
    with Workflow():
        seed = 3
        steps = 12
        blen_step = 8

        model, clip, vae, ipnet = load_models_once()

        ops_model = IPAdapter(model, ipnet, in_img, 0.5, 0, 0.7, 'standard', None)
        ops_model = RescaleCFG(ops_model, 0.7)
        positive = CLIPTextEncode('traditional slavic nomad man, he is very lucky today', clip)
        negative = CLIPTextEncode('text, watermark', clip)
        latent = EmptyLatentImage(1024, 1024, 1)
        latent = KSamplerAdvanced(ops_model, 'enable', seed, 12, 5, 'euler_ancestral', 'sgm_uniform', positive, negative, latent, 0, steps, 'disable')
        out_img = VAEDecode(latent, vae)

        return out_img.to(in_img.device)


def workflow(img: torch.Tensor, mask: torch.Tensor, prompt_text: str, img_power: float = 0.5) -> torch.Tensor:
    result = sdxl_ipadapter(img, mask, prompt_text, img_power)
    return result