
import torch

from comfy_script.runtime.real import *
load()
from comfy_script.runtime.real.nodes import *


class comfyWorkflow():
    MODELS = ()

    def __init__(self):
        pass

    def models_from_cache(self):
        if len(self.MODELS):
            return tuple(self.MODELS)

        self.MODELS = self.load_models()        

        print("+++ models loaded")
        return tuple(self.MODELS)
    

    def load_models():
        pass
    

    def prompt_triplet(self, text_prompt: str, clip):
        first_desc = CLIPTextEncode(text_prompt, clip)
        second_desc = CLIPTextEncode("Placeholder: sad woman singing while raining", clip)
        third_desc = CLIPTextEncode("Placeholder: nostalgic photo of apple fruit", clip)

        default_neg = CLIPTextEncode('text, watermark', clip)

        # concat flow... later
        first_combination = ConditioningConcat(second_desc, first_desc)
        second_combination = ConditioningConcat(first_combination, third_desc)
        return first_desc, default_neg
