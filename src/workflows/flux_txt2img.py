import torch
import numpy as np

from comfy_script.runtime.real import *
load()
from comfy_script.runtime.real.nodes import *

from skimage import io

from src.utils_mea import img_pt_2_np

def comfy_flux_txt2img(prompt: str, seed_: int, schnell=True):
    with Workflow():
        seed = seed_
        steps_dev = 20
        steps_schnell = 4
        flux_dev = 'flux1-dev-fp8.safetensors'
        flux_schenll = 'flux1-schnell-fp8.safetensors'

        steps = steps_dev
        model_name = flux_dev

        if schnell:
            steps = steps_schnell
            model_name = flux_schenll

        model, clip, vae = CheckpointLoaderSimple(model_name)
        model = DifferentialDiffusion(model)

        empty_neg = CLIPTextEncode('', clip)
        first_desc = CLIPTextEncode(prompt, clip)
        
        # 
        second_desc = CLIPTextEncode("stoned cow is eating a grass", clip)
        third_desc = CLIPTextEncode("it's about to rain", clip)
        first_combination = ConditioningConcat(second_desc, first_desc)
        second_combination = ConditioningConcat(first_combination, third_desc)
        # 

        cond_pos = first_desc

        latent = EmptySD3LatentImage(1024, 1024, 1)
        latent = KSamplerAdvanced(model, 'enable', seed, steps, 1, 'euler', 'simple', cond_pos, empty_neg, latent, 0, steps, 'disable')
        img_out = VAEDecode(latent, vae)

        pt_img = img_out.detach()
        return pt_img

def workflow(prompt_text: str, seed: int = 0) -> torch.Tensor:
    result = comfy_flux_txt2img(prompt_text, seed)
    return result