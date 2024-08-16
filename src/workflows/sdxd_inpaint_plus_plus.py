import torch
import numpy as np

from comfy_script.runtime.real import *
load()
from comfy_script.runtime.real.nodes import *

from skimage import io

from src.utils_mea import img_pt_2_np

def comfy_script_test():
    with Workflow():
        seed = 451409010129606

        src_img, mask = LoadImage('clipspace/clipspace-mask-6972334.png [input]')
        soft_mask = ImpactGaussianBlurMask(mask, 50, 75)
        pt_mask = soft_mask.clone().detach()
        pt_mask = torch.stack((pt_mask, pt_mask, pt_mask), dim=-1)


        model, clip, vae = CheckpointLoaderSimple('photopediaXL_45.safetensors')
        model, clip2 = LoraLoader(model, clip, 'Hyper-SDXL-12steps-CFG-lora.safetensors', 0.9, 1)
        model_dd = DifferentialDiffusion(model)
        brushnet = BrushNetLoader('brushnet_random_mask.safetensors', 'float16')
        pos_text = CLIPTextEncode('text for inpainting', clip2)
        neg_text = CLIPTextEncode('text, watermark', clip2)
        unet_plus_brushnet, positive, negative, brushnet_latent = BrushNet(model, vae, src_img, mask, brushnet, pos_text, neg_text, 0.8, 0, 10000)

        brush_net_pass_latent = KSamplerAdvanced(unet_plus_brushnet, 'enable', seed, 12, 1, 'euler_ancestral_cfg_pp', 'normal', positive, negative, brushnet_latent, 0, 12, 'disable')
        brush_net_pass_img = VAEDecode(brush_net_pass_latent, vae)
        
        first_img_blend = src_img*(1-pt_mask) + brush_net_pass_img*pt_mask
        first_img_blend = first_img_blend.detach()

        positive2, negative2, blend_phase_latent = InpaintModelConditioning(pos_text, neg_text, vae, first_img_blend, soft_mask)
        print("blend_phase_latent latent", blend_phase_latent["samples"].shape)
        final_latent = KSamplerAdvanced(model_dd, 'enable', seed, 12, 1, 'euler_ancestral_cfg_pp', 'normal', positive2, negative2, blend_phase_latent, 8, 12, 'disable')
        print("final_latent latent", final_latent["samples"].shape)
        img_out = VAEDecode(final_latent, vae)

        pt_img = src_img*(1-pt_mask) + img_out*pt_mask
        pt_img = pt_img.detach()

        np_src_img = img_pt_2_np(src_img*(1-pt_mask), False, False)
        np_out_img = img_pt_2_np(img_out*pt_mask, False, False)
        np_out_img_just = img_pt_2_np(img_out, False, False)
        np_blend = img_pt_2_np(pt_img, False, False)

        io.imsave("fs/tmp/np_src_img.png", np_src_img)
        io.imsave("fs/tmp/np_out_img.png", np_out_img)
        io.imsave("fs/tmp/np_blend.png", np_blend)
        io.imsave("fs/tmp/esafsdf.png", np_out_img_just)