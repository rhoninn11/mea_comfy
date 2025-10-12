from comfy_script.runtime.real import *
load()
from comfy_script.runtime.real.nodes import *

from workflows.base import ComfyWorkflow

import torch
import numpy as np
from skimage import io

from src.utils_mea import img_pt_2_np
from src.state import ServState
import mea_gen_d.comfy_pb2 as pb2


MODELS = []

class BasicWorkflow(ComfyWorkflow):
    def _init_(self):
        self.possible_variable = None
        self.MODEL_TYPE = "SDXL"

    def load_models(self) -> list[any]:
        model, clip, vae = CheckpointLoaderSimple('photopediaXL_45.safetensors')
        model, clip = LoraLoader(model, clip, 'Hyper-SDXL-12steps-CFG-lora.safetensors', 0.9, 1)
        return [model, clip, vae] 
    
    def sdxl_txt2img(self, prompt_text: str) -> torch.Tensor:
        seed = self.opts.seed
        print("+++ seed is: ", seed)
        steps = 12

        with Workflow():
            model, clip, vae = self.models_from_cache()
            first_step = 0
            positive_prompt, negative_prompt = self.chained_prompts(clip); 

            empty_latent = EmptyLatentImage(1024, 1024, 1)
            gen_latent = KSamplerAdvanced(model, 'enable', seed,12, 1,
                                            'euler_ancestral_cfg_pp', #sampler
                                            'normal', #scheduler
                                            positive_prompt, negative_prompt, empty_latent, 
                                            first_step, steps, 'disable')
            gen_img: torch.Tensor = VAEDecode(gen_latent, vae)
            gen_img = gen_img.to(torch.device("cpu"))

            # detach uwalniał na 
            return gen_img.cpu().detach()
        