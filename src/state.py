import torch
import mea_gen_d.comfy_pb2 as pb2

class ServState():
    def __init__(self):
        self.imgs: dict[pb2.Slot, torch.Tensor | None] = {}
        self.masks: dict[pb2.Slot, torch.Tensor | None] = {}
        self.prompts: dict[pb2.Slot, str] = {}
        slot_keys = pb2.Slot.keys()

        for key in slot_keys:
            val = pb2.Slot.Value(key)
            self.imgs[val] = None
            self.masks[val] = None
            self.prompts[val] = ""
        