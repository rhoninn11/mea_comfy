import torch
import numpy as np

from comfy_script.runtime.real import *
load()
from comfy_script.runtime.real.nodes import *

from skimage import io

from src.utils_mea import img_pt_2_np

MODELS = []

def load_models_once(base_name):
    global MODELS
    if len(MODELS):
        return tuple(MODELS)
    
    model, clip, vae = CheckpointLoaderSimple(base_name)
    model = DifferentialDiffusion(model)

    MODELS = [model, clip, vae]
    print("+++ models loaded")
    return tuple(MODELS)


def comfy_flux_inpaint(img: torch.Tensor, mask: torch.Tensor, prompt_text: str, schnell=True) -> torch.Tensor:
    with Workflow():
        seed = 3
        img_power = 0.5
        steps = 20

        flux_dev = 'flux1-dev-fp8.safetensors'
        flux_schenll = 'flux1-schnell-fp8.safetensors'

        model_name = flux_dev

        src_img = img
        src_mask = mask[:,:,:,0]
        soft_mask = ImpactGaussianBlurMask(src_mask, 25, 75)
        pt_mask = soft_mask.clone().detach()
        pt_mask = torch.stack((pt_mask, pt_mask, pt_mask), dim=-1)

        dd_model, clip, vae = load_models_once(model_name)

        empty_neg = CLIPTextEncode('', clip)
        first_desc = CLIPTextEncode(prompt_text, clip)

        # 
        second_desc = CLIPTextEncode("stoned cow is eating a grass", clip)
        third_desc = CLIPTextEncode("it's about to rain", clip)
        first_combination = ConditioningConcat(second_desc, first_desc)
        second_combination = ConditioningConcat(first_combination, third_desc)
        # 

        dd_pos, dd_neg, dd_latent = InpaintModelConditioning(first_desc, empty_neg, vae, src_img, soft_mask)

        first_step = int(img_power*steps)
        dd_latent = KSamplerAdvanced(dd_model, 'enable', seed, 20, 1, 'euler', 'simple', dd_pos, dd_neg, dd_latent, first_step, 20, 'disable')
        dd_img = VAEDecode(dd_latent, vae)
        dd_img = dd_img.to(pt_mask.device)

        dd_img_blend = src_img*(1-pt_mask) + dd_img*pt_mask
        dd_img_blend = dd_img_blend.detach()

        return dd_img_blend

def workflow(img: torch.Tensor, mask: torch.Tensor, prompt_text: str) -> torch.Tensor:
    result = comfy_flux_inpaint(img, mask, prompt_text)
    return result