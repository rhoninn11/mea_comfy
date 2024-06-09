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


def comfy_ui_workflow():
    import_custom_nodes()
    with torch.inference_mode():
        checkpointloadersimple = CheckpointLoaderSimple()
        checkpointloadersimple_4 = checkpointloadersimple.load_checkpoint(
            ckpt_name="photopediaXL_45.safetensors"
        )

        emptylatentimage = EmptyLatentImage()
        emptylatentimage_5 = emptylatentimage.generate(
            width=1024, height=1024, batch_size=1
        )

        loraloader = LoraLoader()
        loraloader_22 = loraloader.load_lora(
            lora_name="sd_xl_offset_example-lora_1.0.safetensors",
            strength_model=1,
            strength_clip=1,
            model=get_value_at_index(checkpointloadersimple_4, 0),
            clip=get_value_at_index(checkpointloadersimple_4, 1),
        )

        loraloader_21 = loraloader.load_lora(
            lora_name="Hyper-SDXL-12steps-CFG-lora.safetensors",
            strength_model=1,
            strength_clip=1,
            model=get_value_at_index(loraloader_22, 0),
            clip=get_value_at_index(loraloader_22, 1),
        )

        cliptextencode = CLIPTextEncode()
        prompt_text = "a forester in the slavic style"

        cliptextencode_6 = cliptextencode.encode(
            text=prompt_text,
            clip=get_value_at_index(loraloader_21, 1),
        )

        cliptextencode_7 = cliptextencode.encode(
            text="text, watermark, look too perfect",
            clip=get_value_at_index(loraloader_21, 1),
        )

        brushnetloader = NODE_CLASS_MAPPINGS["BrushNetLoader"]()
        brushnetloader_10 = brushnetloader.brushnet_loading(
            brushnet="brushnet_random_mask.safetensors", dtype="float16"
        )

        loadimage = LoadImage()
        loadimage_14 = loadimage.load_image(
            image="clipspace/clipspace-mask-80537.png [input]"
        )

        mask = loadimage_14[1]
        print(f"mask shape: {mask.shape}")
        print(f"mask type: {mask.dtype}")
        print(f"mask min: {mask.min()}")
        print(f"mask max: {mask.max()}")
        print(f"mask mean: {mask.mean()}")

        brushnet = NODE_CLASS_MAPPINGS["BrushNet"]()
        ksampler = KSampler()
        vaedecode = VAEDecode()
        saveimage = SaveImage()

        for q in range(10):
            brushnet_12 = brushnet.model_update(
                scale=0.8,
                start_at=0,
                end_at=10000,
                model=get_value_at_index(loraloader_21, 0),
                vae=get_value_at_index(checkpointloadersimple_4, 2),
                image=get_value_at_index(loadimage_14, 0),
                mask=get_value_at_index(loadimage_14, 1),
                brushnet=get_value_at_index(brushnetloader_10, 0),
                positive=get_value_at_index(cliptextencode_6, 0),
                negative=get_value_at_index(cliptextencode_7, 0),
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
                vae=get_value_at_index(checkpointloadersimple_4, 2),
            )

            saveimage_9 = saveimage.save_images(
                filename_prefix="ComfyUI", images=get_value_at_index(vaedecode_8, 0)
            )


def workflow():
    comfy_ui_workflow()