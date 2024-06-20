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
    unet, clip, vae = basic_checkpoint

    loraloader = LoraLoader()
    model_with_offset = loraloader.load_lora(
        lora_name="sd_xl_offset_example-lora_1.0.safetensors",
        strength_model=1,
        strength_clip=1,
        model=unet,
        clip=clip,
    )
    unet, clip = model_with_offset

    model_but_faster = loraloader.load_lora(
        lora_name="Hyper-SDXL-12steps-CFG-lora.safetensors",
        strength_model=1,
        strength_clip=1,
        model=unet,
        clip=clip,
    )
    unet, clip = model_but_faster

    brushnetloader = NODE_CLASS_MAPPINGS["BrushNetLoader"]()
    brushnet_model, = brushnetloader.brushnet_loading(
        brushnet="brushnet_random_mask.safetensors", dtype="float16"
    )
    models_loaded_flag = True

def comfy_ui_workflow(in_img: torch.Tensor, in_mask: torch.Tensor, in_prmpt: str):
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

        
        brushnet = NODE_CLASS_MAPPINGS["BrushNet"]()
        ksampler = KSampler()
        vaedecode = VAEDecode()

        brushnet_12 = brushnet.model_update(
            scale=0.8,
            start_at=0,
            end_at=10000,
            model=unet,
            vae=vae,
            image=in_img,
            mask=in_mask,
            brushnet=brushnet_model,
            positive=get_value_at_index(positive, 0),
            negative=get_value_at_index(negative, 0),
        )

        ksampler_3 = ksampler.sample(
            seed=0,
            steps=12,
            cfg=5,
            sampler_name="euler_ancestral",
            scheduler="normal",
            denoise=1,
            model=get_value_at_index(brushnet_12, 0),
            positive=get_value_at_index(brushnet_12, 1),
            negative=get_value_at_index(brushnet_12, 2),
            latent_image=get_value_at_index(brushnet_12, 3),
        )

        vaedecode_8 = vaedecode.decode(
            samples=get_value_at_index(ksampler_3, 0),
            vae=vae,
        )

        result_img=get_value_at_index(vaedecode_8, 0)
        return result_img


from skimage import io

def workflow(img: torch.Tensor, mask: torch.Tensor):
    prompt_text = "the planet earth"
    result = comfy_ui_workflow( img, mask, prompt_text)
    return result