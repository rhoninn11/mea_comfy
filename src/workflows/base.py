from comfy_script.runtime.real import *
load()
from comfy_script.runtime.real.nodes import *

import torch

from src.state import ServState
import src.mea_gen_d.comfy_pb2 as pb2

class ComfyWorkflow():
    MODELS = ()

    def _torch_info():
        print("+++ some torch info")
        

    def __init__(self):
        self.MODEL_TYPE = "NONE"
        self.opts: pb2.Options
        self.state: ServState

    def models_from_cache(self):
        if len(self.MODELS):
            return tuple(self.MODELS)

        self.MODELS = self.load_models()        

        print("+++ models loaded")
        return tuple(self.MODELS)
    

    def load_models():
        pass
    

    def chained_prompts(self, clip):
        chain = self.opts.prompt_chain
        slot_list: list[pb2.Slot] = []
        for link in chain:
            slot_list.append(link)

        pos_enc = None
        neg_enc = CLIPTextEncode('text, watermark', clip)

        slot_list.reverse()
        for slot in slot_list:
            text = self.state.prompts[slot]
            prompt_enc = CLIPTextEncode(text, clip)
            if pos_enc == None:
                pos_enc = prompt_enc
                continue

            pos_enc = ConditioningConcat(prompt_enc, pos_enc)
        assert(pos_enc != None)
        return pos_enc, neg_enc
