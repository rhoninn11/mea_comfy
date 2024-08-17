import torch
import numpy as np

from comfy_script.runtime.real import *
load()
from comfy_script.runtime.real.nodes import *

from skimage import io

from src.utils_mea import img_pt_2_np

def comfy_script_test(schnell=True):
    with Workflow():
        seed = 1
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
        first_desc = CLIPTextEncode("wornderful forest in a background", clip)
        second_desc = CLIPTextEncode("stoned cow is eating a grass", clip)
        third_desc = CLIPTextEncode("it's about to rain", clip)
        first_combination = ConditioningConcat(second_desc, first_desc)
        second_combination = ConditioningConcat(first_combination, third_desc)

        latent = EmptySD3LatentImage(1024, 1024, 1)
        latent = KSampler(model, seed, 4, 1, 'euler', 'simple', second_combination, empty_neg, latent, 1)
        latent = KSamplerAdvanced(model, 'enable', 73676964823421, steps, 1, 'euler', 'simple', second_combination, empty_neg, latent, 0, steps, 'disable')
        img_out = VAEDecode(latent, vae)

        np_out_img = img_pt_2_np(img_out, False, False)
        io.imsave("fs/tmp/flux_result.png", np_out_img)