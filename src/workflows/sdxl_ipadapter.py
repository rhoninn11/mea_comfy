import torch

from comfy_script.runtime.real import *
load()
from comfy_script.runtime.real.nodes import *

from workflows.base import comfyWorkflow
from proto.comfy_pb2 import Crop

class IpAdapter(comfyWorkflow):

    def set_crop(self, c: Crop):
        self.crop = c    

    def load_models(self):
        model, clip, vae = CheckpointLoaderSimple('photopediaXL_45.safetensors')
        model, clip = LoraLoader(model, clip, 'Hyper-SDXL-12steps-CFG-lora.safetensors', 0.9, 1)
        model, ipnet = IPAdapterUnifiedLoader(model, 'STANDARD (medium strength)', None)
        return [model, clip, vae, ipnet]
    
    def sdxl_ipadapter(self, in_img: torch.Tensor, mask: torch.Tensor, prompt_text: str, img_power: float):
        with Workflow():
            seed = 3
            steps = 12

            model, clip, vae, ipnet = self.models_from_cache()

            c = self.crop
            crop_img = ImageCrop(in_img, c.w, c.h, c.x, c.y)
            crop_img = PrepImageForClipVision(crop_img, 'LANCZOS', 'top', 0)

            print("+++ before ipa")
            ops_model = IPAdapter(model, ipnet, crop_img, 0.7, 0, 0.7, 'standard', None)
            print("+++ before rescale")
            ops_model = RescaleCFG(ops_model, 0.7)
            print("+++ after rescale")
            
            positive, negative = self.tripple_prompt(prompt_text, clip)
            
            latent = EmptyLatentImage(1024, 1024, 1)
            latent = KSamplerAdvanced(ops_model, 'enable', seed, 12, 5, 'euler_ancestral', 'sgm_uniform', positive, negative, latent, 0, steps, 'disable')
            out_img = VAEDecode(latent, vae)

            return out_img.to(in_img.device)


    def workflow(self, img: torch.Tensor, mask: torch.Tensor, prompt_text: str, img_power: float = 0.5) -> torch.Tensor:
        result = self.sdxl_ipadapter(img, mask, prompt_text, img_power)
        return result
