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
    CLIPTextEncode,
    CheckpointLoaderSimple,
    EmptyLatentImage,
    NODE_CLASS_MAPPINGS,
    LoadImage,
    SaveImage,
    LoraLoader,
    ConditioningConcat,
    VAEDecode,
    KSamplerAdvanced,
    KSampler,
)


from skimage import io

def comfy_ui_workflow(input_image: torch.Tensor, promtp_text: str = ""):
    import_custom_nodes()
    with torch.inference_mode():
        checkpointloadersimple = CheckpointLoaderSimple()
        checkpointloadersimple_41 = checkpointloadersimple.load_checkpoint(
            ckpt_name="Stable-Cascade\stable_cascade_stage_c.safetensors"
        )
        c_unet, c_clip, c_vae = checkpointloadersimple_41

        cliptextencode = CLIPTextEncode()
        cliptextencode_6 = cliptextencode.encode(text=promtp_text, clip=c_clip,)
        positive, = cliptextencode_6

        cliptextencode_7 = cliptextencode.encode(text="text, watermark", clip=c_clip,)
        negative, = cliptextencode_7

        checkpointloadersimple_42 = checkpointloadersimple.load_checkpoint(
            ckpt_name="Stable-Cascade\stable_cascade_stage_b.safetensors"
        )
        b_unet, b_clip, b_vae = checkpointloadersimple_42
        loadimage_48 = (input_image,)

        stablecascade_stagec_vaeencode = NODE_CLASS_MAPPINGS[
            "StableCascade_StageC_VAEEncode"
        ]()
        ksampler = KSampler()
        stablecascade_stageb_conditioning = NODE_CLASS_MAPPINGS[
            "StableCascade_StageB_Conditioning"
        ]()
        vaedecode = VAEDecode()
        saveimage = SaveImage()

        img_to_gen = 1
        for q in range(img_to_gen):
            stablecascade_stagec_vaeencode_49 = stablecascade_stagec_vaeencode.generate(
                compression=32,
                image=input_image,
                vae=c_vae,
            )

            stage_c_latent, stage_b_latent = stablecascade_stagec_vaeencode_49

            denoise = 1
            steps = int(20 *denoise)

            ksampler_3 = ksampler.sample(
                seed=q,
                steps=steps,
                cfg=4,
                sampler_name="euler",
                scheduler="simple",
                denoise=denoise,
                model=c_unet,
                positive=positive,
                negative=negative,
                latent_image=stage_c_latent,
            )
            stage_c_latent, = ksampler_3

            stablecascade_stageb_conditioning_36 = (
                stablecascade_stageb_conditioning.set_prior(
                    conditioning=get_value_at_index(cliptextencode_6, 0),
                    stage_c=stage_c_latent,
                )
            )

            ksampler_33 = ksampler.sample(
                seed=q+1,
                steps=10,
                cfg=1.1,
                sampler_name="euler",
                scheduler="simple",
                denoise=1,
                model=get_value_at_index(checkpointloadersimple_42, 0),
                positive=get_value_at_index(stablecascade_stageb_conditioning_36, 0),
                negative=get_value_at_index(cliptextencode_7, 0),
                latent_image=stage_b_latent,
            )

            vaedecode_8 = vaedecode.decode(
                samples=get_value_at_index(ksampler_33, 0),
                vae=get_value_at_index(checkpointloadersimple_42, 2),
            )

            result_image = get_value_at_index(vaedecode_8, 0)
            return result_image



def workflow(pt_iamge: torch.Tensor) -> torch.Tensor:
    prompt_text = "connected nodes of blooming flowers, hovering in as aureola around planet earth"
    # prompt_text = "a slavic forester in the forest"
    return comfy_ui_workflow(pt_iamge, prompt_text)