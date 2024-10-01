import os
import torch
from skimage import io

MAIN_DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

def np_mmm_info(np_array):
    max_val = np_array.max()
    min_val = np_array.min()
    mean_val = np_array.mean()
    return f"np | mean - {mean_val}, min - {min_val}, max - {max_val}"

def pt_mmm_info(pt_tensor):
    max_val = pt_tensor.max()
    min_val = pt_tensor.min()
    mean_val = pt_tensor.mean()
    return f"pt | mean - {mean_val}, min - {min_val}, max - {max_val}"

def img_np_2_pt(img_np, one_minus_one=True, transpose=True):
    global MAIN_DEVICE
    if transpose:
        img_np = img_np.transpose((2, 0, 1))

    img_np = (img_np / 255.0)
    if one_minus_one:
        img_np = img_np * 2 - 1
    img_pt = torch.from_numpy(img_np).float().to(MAIN_DEVICE)
    
    return img_pt

def img_pt_2_np(img_pt, one_minus_one=True, transpose=True):
    img_np = img_pt.cpu().detach().numpy()
    # to uint 8
    if one_minus_one:
        img_np = img_np.clip(-1, 1)*0.5 + 0.5
    else:
        img_np = img_np.clip(0, 1)

    img_np = img_np * 255.0
    img_np = img_np.astype("uint8")
    if transpose:
        img_np = img_np.transpose((1, 2, 0))
    

    return img_np

import numpy as np
import proto.comfy_pb2 as pb2

def img_proto_2_np(img_proto: pb2.Image) -> np.ndarray:
    img_np = np.frombuffer(img_proto.pixels, dtype=np.uint8)
    img_np = img_np.reshape(img_proto.info.height, img_proto.info.width, img_proto.info.img_type)
    return img_np

def img_proto_2_pt(img_proto: pb2.Image) -> torch.Tensor:
    img_np = img_proto_2_np(img_proto)
    img_pt = img_np_2_pt(img_np, transpose=False, one_minus_one=False)
    return img_pt.unsqueeze(0)

def img_np_2_proto(img_np: np.ndarray) -> pb2.Image:
    print(img_np.shape)
    width, height, ch = img_np.shape
    img_type = pb2.ImgType.RGB if ch == 3 else pb2.ImgType.MONO
    img_info = pb2.ImgInfo(width=width, height=height, img_type=img_type)
    byte_data = img_np.tobytes()
    img_proto = pb2.Image(info=img_info, pixels=byte_data)
    return img_proto

def img_pt_2_proto(img_pt: torch.Tensor) -> pb2.Image:
    if len(img_pt.shape) > 3:
        img_pt = img_pt[0]

    img_np = img_pt_2_np(img_pt, transpose=False, one_minus_one=False)
    img_proto = img_np_2_proto(img_np)
    return img_proto