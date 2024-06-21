import os
import random
import sys
from typing import Sequence, Mapping, Any, Union
import torch

def get_value_at_index(obj: Union[Sequence, Mapping], index: int) -> Any:
    """Returns the value at the given index of a sequence or mapping.

    If the object is a sequence (like list or string), returns the value at the given index.
    If the object is a mapping (like a dictionary), returns the value at the index-th key.

    Some return a dictionary, in these cases, we look for the "results" key

    Args:
        obj (Union[Sequence, Mapping]): The object to retrieve the value from.
        index (int): The index of the value to retrieve.

    Returns:
        Any: The value at the given index.

    Raises:
        IndexError: If the index is out of bounds for the object and the object is not a mapping.
    """
    try:
        return obj[index]
    except KeyError:
        return obj["result"][index]


def import_custom_nodes() -> None:
    """Find all custom nodes in the custom_nodes folder and add those node objects to NODE_CLASS_MAPPINGS

    This function sets up a new asyncio event loop, initializes the PromptServer,
    creates a PromptQueue, and initializes the custom nodes.
    """
    import asyncio
    import execution
    from nodes import init_custom_nodes
    import server

    # Creating a new event loop and setting it as the default loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Creating an instance of PromptServer with the loop
    server_instance = server.PromptServer(loop)
    execution.PromptQueue(server_instance)

    # Initializing custom nodes
    init_custom_nodes()

from nodes import (
    CheckpointLoaderSimple,
    NODE_CLASS_MAPPINGS,
    SaveImage,
    EmptyLatentImage,
    LoraLoader,
    LoadImage,
    VAEDecode,
    VAEEncode,
    KSampler,
    CLIPTextEncode,
)

UNET = 0
CLIP = 1
VAE = 2


custom_imported_flag = False
def comfy_plugins():
    global custom_imported_flag
    if custom_imported_flag:
        return

    print(f"+++ first model run")
    import_custom_nodes()
    custom_imported_flag = True


models_loaded_flag = False
unet, clip, vae, brushnet_model = None, None, None, None
def load_models():

    global models_loaded_flag
    if models_loaded_flag:
        return
    
    print(f"+++ load models")
    global unet, clip, vae, brushnet_model
    checkpointloadersimple = CheckpointLoaderSimple()
    basic_checkpoint = checkpointloadersimple.load_checkpoint(
        ckpt_name="sd_xl_base_1.0_0.9vae.safetensors"
    )
    _ , clip, vae = basic_checkpoint

    tensorrtloader = NODE_CLASS_MAPPINGS["TensorRTLoader"]()
    rt_model = tensorrtloader.load_unet(
        unet_name="xl_8step_img2img_$stat-b-1-h-1024-w-1024_00001_.engine",
        model_type="sdxl_base",
    )

    unet, = rt_model

    models_loaded_flag = True

import math

def comfy_ui_workflow(in_img: torch.Tensor, in_prmpt: str):
    comfy_plugins()
    global unet, clip, vae, brushnet_model
    with torch.inference_mode():
        load_models()
        cliptextencode = CLIPTextEncode()
        prompt_text = in_prmpt

        positive = cliptextencode.encode(
            text=prompt_text,
            clip=clip,
        )

        negative = cliptextencode.encode(
            text="text, watermark, look too perfect",
            clip=clip,
        )

        ksampler = KSampler()
        vaedecode = VAEDecode()
        vaeencode = VAEEncode()

        vaeencode_19 = vaeencode.encode(
            pixels=in_img,
            vae=vae,
        )

        latent, = vaeencode_19

        denoise = 0.2
        max_steps = 8
        steps = int(math.ceil(denoise*max_steps))

        ksampler_3 = ksampler.sample(
            seed=0,
            steps=steps,
            cfg=7,
            sampler_name="euler",
            scheduler="kerras",
            denoise=denoise,
            model=unet,
            positive=get_value_at_index(positive, 0),
            negative=get_value_at_index(negative, 0),
            latent_image=latent,
        )

        vaedecode_8 = vaedecode.decode(
            samples=get_value_at_index(ksampler_3, 0),
            vae=vae,
        )

        result_img=get_value_at_index(vaedecode_8, 0)
        return result_img
    


def workflow(img: torch.Tensor):
    prompt_text = "slavic shaman chanting spells"
    result = comfy_ui_workflow( img, prompt_text)
    return result