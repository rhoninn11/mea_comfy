import torch

from comfy_script.runtime.real import *
load()
from comfy_script.runtime.real.nodes import *

from workflows.base import comfyWorkflow
from proto.comfy_pb2 import *

from src.utils_mea import *

class IpAdapter(comfyWorkflow):
    def __init__(self):
        self.img_ref = None
        self.reload_adapter = True
        self.cached_adapter = None

    def set_crop(self, ref_img: Image):
        self.img_ref = img_proto_2_pt(ref_img)
        self.reload_adapter = True

    def load_models(self):
        model, clip, vae = CheckpointLoaderSimple('photopediaXL_45.safetensors')
        model, clip = LoraLoader(model, clip, 'Hyper-SDXL-12steps-CFG-lora.safetensors', 0.9, 1)
        model, ipnet = IPAdapterUnifiedLoader(model, 'STANDARD (medium strength)', None)
        return [model, clip, vae, ipnet]
    
    def adapter_from_cache(self, model, ipnet):
        if self.reload_adapter == True:
            crop_img = PrepImageForClipVision(self.img_ref, 'LANCZOS', 'top', 0)
            self.cached_adapter = IPAdapter(model, ipnet, crop_img, 0.7, 0, 0.7, 'standard', None)
            self.reload_adapter = False
            
        return self.cached_adapter
        
    
    def sdxl_ipadapter(self, in_img: torch.Tensor, prompt_text: str):
        steps = 12
        seed = 3

        with Workflow():

            model, clip, vae, ipnet = self.models_from_cache()
            positive, negative = self.prompt_triplet(prompt_text, clip)
            latent = EmptyLatentImage(1024, 1024, 1)

            ipnet_armed = self.adapter_from_cache(model, ipnet)
            ipnet_armed = RescaleCFG(ipnet_armed, 0.7)
            
            latent = KSamplerAdvanced(ipnet_armed, 'enable', seed, steps, 5, 'euler_ancestral', 'sgm_uniform', positive, negative, latent, 0, steps, 'disable')
            out_img = VAEDecode(latent, vae)
            return out_img.to(in_img.device)


    def workflow(self, img: torch.Tensor, mask: torch.Tensor, prompt_text: str, img_power: float = 0.5) -> torch.Tensor:
        result = self.sdxl_ipadapter(img, prompt_text)
        return result
