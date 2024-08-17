import torch
import numpy as np

from comfy_script.runtime.real import *
load()
from comfy_script.runtime.real.nodes import *

from skimage import io

from src.utils_mea import img_pt_2_np

def comfy_flux_img2img(text_prompt: str, schnell=True) -> torch.Tensor:
    
    assert False, "!!! comfy_flux_img2img not implemented"
    return torch.Tensor((1,1,1,1))

def workflow(img: torch.Tensor, mask: torch.Tensor, prompt_text) -> torch.Tensor:
    result = comfy_flux_img2img(prompt_text)
    return result