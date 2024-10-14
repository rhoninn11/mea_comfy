import os
import grpc

from skimage import io
from utils_mea import img_np_2_pt

from utils import proj_asset, file2json2obj, ensure_path_exist

def uno_channel(pt_img):
    return pt_img[:,:,:, 0:1]

def trio_channel(pt_img):
    return pt_img[:,:,:, 0:3]

def load_prompt():
    import json
    prompt_file = proj_asset("prompt.json")
    f = open(prompt_file, "r")
    prompt = json.load(f)["prompt"]
    return prompt

def load_image(name):
    img_file = proj_asset(name)
    print(img_file)
    img_np = io.imread(img_file)
    img_pt = img_np_2_pt(img_np, transpose=False, one_minus_one=False)
    img_pt = img_pt.unsqueeze(0)
    return img_pt

def save_img(name: str):
    name.split()


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
import numpy as np

def sequence_gen(opt: pb2.Options, stub: pb2_grpc.ComfyStub):
    save_dir = "fs/seq"
    ensure_path_exist(save_dir)
    for i, _power in enumerate(np.linspace(0,0.25,5).tolist()):
        opt.img_power = _power
        stub.SetOptions(opt)
        _result = stub.Inpaint(pb2.Empty())
        io.imsave(f'{save_dir}/out_img_{i:02}.png', img_proto_2_np(_result))

def single_gen(opt: pb2.Options, stub: pb2_grpc.ComfyStub):
    save_dir = "fs"
    stub.SetOptions(opt)
    _result = stub.Inpaint(pb2.Empty())
    io.imsave(f'{save_dir}/out_img_sgl.png', img_proto_2_np(_result))

def start_client():
    port = 50051

    # spawn assets in fs

    print("+++ Client starting...")
    config = file2json2obj(proj_asset("client_config.json"))
    server_address = config["server_addres"]
    endpoint = f"{server_address}:{port}"

    credentials = grpc.ssl_channel_credentials(ROOT_CERTIFICATE)
    channel_options = [('grpc.ssl_target_name_override', 'localhost')] # tmp workaround
    
    channel = grpc.secure_channel(endpoint, credentials, options=channel_options)
    stub = pb2_grpc.ComfyStub(channel)

    img_pt = load_image('img.png')
    img_pt = trio_channel(img_pt)
    mask_pt = load_image('mask.png')
    mask_pt = uno_channel(mask_pt)

    prompt = load_prompt()
    print(prompt)

    _opt = pb2.Options(
        prompts=[prompt],
        img_power=1,
        inpt_flag=pb2.FLUX)
    _img = img_pt_2_proto(img_pt)
    _mask = img_pt_2_proto(mask_pt)
    
    tick = time.perf_counter()
    stub.SetImage(_img)
    stub.SetMask(_mask)
    
    sequence_gen(_opt, stub)
    single_gen(_opt, stub)

    tock = time.perf_counter()

    print(f"+++ Inpainting + io took {(tock - tick)} s")
    

