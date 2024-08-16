import torch
import numpy as np

from comfy_script.runtime.real import *
load()
from comfy_script.runtime.real.nodes import *

from skimage import io

from src.utils_mea import img_pt_2_np

def comfy_script_test():
    with Workflow():
        seed = 1

        model, clip, vae = CheckpointLoaderSimple('flux1-schnell-fp8.safetensors')
        model = DifferentialDiffusion(model)

        first_desc = CLIPTextEncode("wornderful forest in a background", clip)
        second_desc = CLIPTextEncode("stoned cow is eating a grass", clip)
        third_desc = CLIPTextEncode("it's about to rain", clip)
        first_combination = ConditioningConcat(second_desc, first_desc)
        second_combination = ConditioningConcat(first_combination, third_desc)

        clip_text_encode_negative_prompt_conditioning = CLIPTextEncode('', clip)
        latent = EmptySD3LatentImage(1024, 1024, 1)
        latent = KSampler(model, seed, 4, 1, 'euler', 'simple', second_combination, clip_text_encode_negative_prompt_conditioning, latent, 1)
        img_out = VAEDecode(latent, vae)

        np_out_img = img_pt_2_np(img_out, False, False)
        io.imsave("fs/tmp/flux_result.png", np_out_img)