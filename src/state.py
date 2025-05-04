import torch
import proto.comfy_pb2 as comfy

class GeneraotorState():
    def __init__(self):
        self.imgs: dict[str, torch.Tensor | None] = {}
        self.masks: dict[str, torch.Tensor | None] = {}
        self.prompts: dict[str, str] = {}
        slot_keys = comfy.Slot.keys()

        for key in slot_keys:
            self.imgs[key] = None
            self.masks[key] = None
            self.prompts[key] = ""
        