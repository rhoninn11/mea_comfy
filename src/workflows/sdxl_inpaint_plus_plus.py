import torch
import numpy as np

from comfy_script.runtime.real import *
load()
from comfy_script.runtime.real.nodes import *

from skimage import io

from src.utils_mea import img_pt_2_np
from workflows.base import comfyWorkflow

MODELS = []

class InpaintWorkflow(comfyWorkflow):
    def _init_(self):
        self.possible_variable = None

    def load_models(self) -> list[any]:
        model, clip, vae = CheckpointLoaderSimple('photopediaXL_45.safetensors')
        model, clip = LoraLoader(model, clip, 'Hyper-SDXL-12steps-CFG-lora.safetensors', 0.9, 1)
        dd_model = DifferentialDiffusion(model)
        # rename from original "random_mask_brushnet_ckpt_sdxl_v0"
        bnet = BrushNetLoader('random_mask_brushnet.safetensors', 'float16')
        return [model, clip, vae, bnet, dd_model] 
    
    def sdxVl_inpaint(self, img: torch.Tensor, mask: torch.Tensor, prompt_text: str, img_power: float) -> torch.Tensor:
        seed = 3
        steps = 12
        blen_step = 8

        with Workflow():
            src_img = img
            src_mask = mask[:,:,:,0]
            # soft_mask = ImpactGaussianBlurMask(src_mask, 25, 100)
            soft_mask = MaskBlur(src_mask, 25, 'auto')
            pt_mask = soft_mask.clone().detach()
            pt_mask = torch.stack((pt_mask, pt_mask, pt_mask), dim=-1)

            model, clip, vae, bnet, model_dd = self.models_from_cache()

            pos_text = CLIPTextEncode(prompt_text, clip)
            neg_text = CLIPTextEncode('text, watermark', clip)

            bn_mode, bn_pos, bn_neg, bn_latent = BrushNet(model, vae, src_img, soft_mask, bnet, pos_text, neg_text, 0.8, 0, 10000)

            first_step = int(img_power*steps)
            bn_inpaint = KSamplerAdvanced(bn_mode, 'enable', seed, 12, 1, 'euler_ancestral_cfg_pp', 'normal', bn_pos, bn_neg, bn_latent, first_step, steps, 'disable')
            bn_img = VAEDecode(bn_inpaint, vae)
            bn_img = bn_img.to(pt_mask.device)

            bn_img_blend = bn_img*pt_mask + src_img*(1 - pt_mask)
            bn_img_blend = bn_img_blend.detach()
            
            
            dd_pos, dd_neg, dd_latent = InpaintModelConditioning(pos_text, neg_text, vae, bn_img_blend, soft_mask)
            dd_inpaint = KSamplerAdvanced(model_dd, 'enable', seed, 12, 1, 'euler_ancestral_cfg_pp', 'normal', dd_pos, dd_neg, dd_latent, blen_step, steps, 'disable')
            dd_img = VAEDecode(dd_inpaint, vae)
            dd_img = dd_img.to(src_img.device)

            dd_img_blend = src_img*(1-pt_mask) + dd_img*pt_mask
            dd_img_blend = dd_img_blend.cpu().detach()

            return dd_img_blend
        
    
    def workflow(self, img: torch.Tensor, mask: torch.Tensor, prompt_text: str, img_power: float = 0.5) -> torch.Tensor:
        result = self.sdxVl_inpaint(img, mask, prompt_text, img_power)
        return result.to(torch.device("cpu"))
