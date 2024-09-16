import os
import grpc

from skimage import io
from utils_mea import img_np_2_pt
import shutil

def load_image(file):
    img_np = io.imread(file)
    img_pt = img_np_2_pt(img_np, transpose=False, one_minus_one=False)
    img_pt = img_pt.unsqueeze(0)
    return img_pt

def single_channel(pt_image):
    return pt_image[:,:,:, 0:1]

def load_prompt():
    import json

    prompt_src = "assets\prompt.json"
    prompt_dst = "fs/prompt.json"
    if not os.path.exists(prompt_dst):
        if not os.path.exists(prompt_src):
            return "very simple tree"
        shutil.copy(prompt_src, prompt_dst)

    f = open(prompt_dst, "r")
    prompt = json.load(f)["prompt"]
    return prompt



import proto.comfy_pb2 as pb2
import proto.comfy_pb2_grpc as pb2_grpc
from utils_mea import img_proto_2_pt, img_pt_2_proto, img_proto_2_np

def _load_credential_from_file(filepath):
    real_path = os.path.abspath(filepath)
    with open(real_path, "rb") as f:
        return f.read()


SERVER_CERTIFICATE = _load_credential_from_file("assets/credentials/localhost.crt")
SERVER_CERTIFICATE_KEY = _load_credential_from_file("assets/credentials/localhost.key")
ROOT_CERTIFICATE = _load_credential_from_file("assets/credentials/root.crt")

import time


def start_client():
    port = 50051

    # spawn assets in fs

    print("+++ Client starting...")
    img_file = 'assets/img.png'
    img_pt = load_image(img_file)
    img_proto = img_pt_2_proto(img_pt)

    mask_file = 'assets/mask.png'
    mask_pt = load_image(mask_file)
    mask_pt = single_channel(mask_pt)
    mask_proto = img_pt_2_proto(mask_pt)

    ssl_options = grpc.ssl_channel_credentials(ROOT_CERTIFICATE)
    channel = grpc.secure_channel(f"localhost:{port}", ssl_options)
    # channel = grpc.insecure_channel(f"localhost:{port}")

    stub = pb2_grpc.ComfyStub(channel)

    

    prompt = load_prompt()
    print(prompt)
    img_power = 0.2
    gen_opt = pb2.Options(prompt=prompt, img_power=img_power)

    tick = time.perf_counter()
    # stub.SetImage(img_proto)
    # stub.SetMask(mask_proto)
    stub.SetOptions(gen_opt)
    # result_proto = stub.Inpaint(pb2.Empty())
    # result_proto = stub.Img2Img(pb2.Empty())
    result_proto = stub.Txt2Img(pb2.Empty())
    tock = time.perf_counter()

    inpaint_np = img_proto_2_np(result_proto)
    print(f"+++ Inpainting took {(tock - tick)} s")
    io.imsave('fs/out_client_1.png', inpaint_np)

