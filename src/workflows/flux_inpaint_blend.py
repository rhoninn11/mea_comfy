import torch
import numpy as np

from comfy_script.runtime.real import *
load()
from comfy_script.runtime.real.nodes import *

from skimage import io

from src.utils_mea import img_pt_2_np

def comfy_script_test(schnell=True):
    with Workflow():
        src_img, mask = LoadImage('clipspace/clipspace-mask-8620452.png [input]')
        soft_mask = ImpactGaussianBlurMask(mask, 50, 75)
        pt_mask = soft_mask.clone().detach()
        pt_mask = torch.stack((pt_mask, pt_mask, pt_mask), dim=-1)


        model = UnetLoaderGGUF('flux1-dev-Q5_0.gguf')
        model = DifferentialDiffusion(model)
        _, clip, vae = CheckpointLoaderSimple('flux1-schnell-fp8.safetensors')


        empty_neg = CLIPTextEncode('', clip)
        first_desc = CLIPTextEncode("wornderful forest in a background", clip)
        second_desc = CLIPTextEncode("stoned cow is eating a grass", clip)
        third_desc = CLIPTextEncode("it's about to rain", clip)
        first_combination = ConditioningConcat(second_desc, first_desc)
        second_combination = ConditioningConcat(first_combination, third_desc)


        positive, negative, latent = InpaintModelConditioning(second_combination, empty_neg, vae, src_img, soft_mask)
        latent = KSamplerAdvanced(model, 'enable', 73676964823421, 20, 1, 'euler', 'simple', positive, negative, latent, 14, 20, 'disable')
        img_out = VAEDecode(latent, vae)

        pt_img = src_img*(1-pt_mask) + img_out*pt_mask
        pt_img = pt_img.detach()
        
        SaveImage(pt_img, 'ComfyUI')