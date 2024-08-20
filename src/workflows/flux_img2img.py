import torch
import math
import numpy as np

from comfy_script.runtime.real import *
load()
from comfy_script.runtime.real.nodes import *

from skimage import io

from src.utils_mea import img_pt_2_np

def comfy_flux_img2img(text_prompt: str, img_power: float, src_img: torch.Tensor, schnell=True) -> torch.Tensor:
    with Workflow():
        seed = 0
        power = max(min(1.0, img_power), 0.0)

        model = UnetLoaderGGUF('flux1-dev-Q5_0.gguf')
        _, clip, vae = CheckpointLoaderSimple('flux1-schnell-fp8.safetensors')

        src_latent = VAEEncode(src_img, vae)

        empty_neg = CLIPTextEncode('', clip)
        first_desc = CLIPTextEncode(text_prompt, clip)
        second_desc = CLIPTextEncode("stoned cow is eating a grass", clip)
        third_desc = CLIPTextEncode("it's about to rain", clip)
        first_combination = ConditioningConcat(second_desc, first_desc)
        second_combination = ConditioningConcat(first_combination, third_desc)

        total_steps = 20
        init_step = int(round(total_steps * power))
        latent = KSamplerAdvanced(model, 'enable', seed, total_steps, 1, 'euler', 'simple', first_desc, empty_neg, src_latent, init_step, total_steps, 'disable')
        img_out = VAEDecode(latent, vae)

        # SaveImage(pt_img, 'ComfyUI')
        return img_out


def workflow(img: torch.Tensor, mask: torch.Tensor, prompt_text, img_power) -> torch.Tensor:
    result = comfy_flux_img2img(prompt_text, img_power, img, img_power)
    return result