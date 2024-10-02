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
    dd_model = DifferentialDiffusion(model)
    bnet = BrushNetLoader('random_mask_brushnet_ckpt_sdxl_v0.safetensors', 'float16')

    MODELS = [model, clip, vae, bnet, dd_model]
    print("+++ models loaded")
    return tuple(MODELS)


def sdxl_inpaint_plus(img: torch.Tensor, mask: torch.Tensor, prompt_text: str):
    with Workflow():
        seed = 0

        src_img = img
        src_mask = mask[:,:,:,0]
        print("zaladowany obraz ", src_img.shape)
        print("zaladowana maska ", src_mask.shape)

        soft_mask = ImpactGaussianBlurMask(src_mask, 50, 100)
        pt_mask = soft_mask.clone().detach()
        pt_mask = torch.stack((pt_mask, pt_mask, pt_mask), dim=-1)


        model, clip, vae, bnet, model_dd = load_models_once()

        pos_text = CLIPTextEncode(prompt_text, clip)
        neg_text = CLIPTextEncode('text, watermark', clip)

        bn_mode, bn_pos, bn_neg, bn_latent = BrushNet(model, vae, src_img, soft_mask, bnet, pos_text, neg_text, 0.8, 0, 10000)

        bn_inpaint = KSamplerAdvanced(bn_mode, 'enable', seed, 12, 1, 'euler_ancestral_cfg_pp', 'normal', bn_pos, bn_neg, bn_latent, 0, 12, 'disable')
        bn_img = VAEDecode(bn_inpaint, vae)
        bn_img = bn_img.to(pt_mask.device)

        bn_img_blend = bn_img*pt_mask + src_img*(1 - pt_mask)
        bn_img_blend = bn_img_blend.detach()

        dd_pos, dd_neg, dd_latent = InpaintModelConditioning(pos_text, neg_text, vae, bn_img_blend, soft_mask)
        dd_inpaint = KSamplerAdvanced(model_dd, 'enable', seed, 12, 1, 'euler_ancestral_cfg_pp', 'normal', dd_pos, dd_neg, dd_latent, 8, 12, 'disable')
        dd_img = VAEDecode(dd_inpaint, vae)
        dd_img = dd_img.to(src_img.device)

        dd_img_blend = src_img*(1-pt_mask) + dd_img*pt_mask
        dd_img_blend = dd_img_blend.cpu().detach()

        return dd_img_blend

        np_src_img = img_pt_2_np(src_img*(1-pt_mask), False, False)
        np_out_img = img_pt_2_np(dd_img*pt_mask, False, False)
        np_out_img_just = img_pt_2_np(dd_img, False, False)
        np_blend = img_pt_2_np(dd_img_blend, False, False)

        io.imsave("fs/tmp/np_src_img.png", np_src_img)
        io.imsave("fs/tmp/np_out_img.png", np_out_img)
        io.imsave("fs/tmp/np_blend.png", np_blend)
        io.imsave("fs/tmp/esafsdf.png", np_out_img_just)

def workflow(img: torch.Tensor, mask: torch.Tensor, prompt_text: str) -> torch.Tensor:
    print("obraz ", img.shape)
    print("maska ", mask.shape)
    result = sdxl_inpaint_plus(img, mask, prompt_text)
    return result