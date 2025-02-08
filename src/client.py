import os
import time
import numpy as np

import grpc
import proto.comfy_pb2 as pb2
import proto.comfy_pb2_grpc as pb2_grpc

from skimage import io

from utils_mea import *
from utils import proj_asset, file2json2obj, ensure_path_exist

def uno_channel(img: np.ndarray) -> np.ndarray:
    return img[:,:, 0:1]

def trio_channel(img: np.ndarray) -> np.ndarray:
    return img[:,:, 0:3]

def load_prompt():
    import json
    prompt_file = proj_asset("prompt.json")
    f = open(prompt_file, "r")
    prompt = json.load(f)["prompt"]
    return prompt

def load_image(name) -> np.ndarray:
    img_file = proj_asset(name)
    print("+++ reading img from file: ",img_file)
    return io.imread(img_file)

def save_img(name: str):
    name.split()


def _load_credential_from_file(filepath):
    real_path = os.path.abspath(filepath)
    with open(real_path, "rb") as f:
        return f.read()


SERVER_CERTIFICATE = _load_credential_from_file("assets/credentials/localhost.crt")
SERVER_CERTIFICATE_KEY = _load_credential_from_file("assets/credentials/localhost.key")
ROOT_CERTIFICATE = _load_credential_from_file("assets/credentials/root.crt")


def sequence_gen(opt: pb2.Options, stub: pb2_grpc.ComfyStub):
    save_dir = "fs/seq"
    ensure_path_exist(save_dir)

    for i, _power in enumerate(np.linspace(0,0.25,5).tolist()):
        opt.img_power = _power
        stub.SetOptions(opt)
        _result = stub.Inpaint(pb2.Empty())
        io.imsave(f'{save_dir}/out_img_{i:02}.png', img_proto_2_np(_result))

def sequence_adapter_run(opt: pb2.Options, stub: pb2_grpc.ComfyStub, proto_img: pb2.Image):
    save_dir = "fs/seq_ada"   
    ensure_path_exist(save_dir)
    print("+++ Elo", proto_img.info)
    np_ref_img = img_proto_2_np(proto_img)
    img_size = np_ref_img.shape[0]
    win_size = int(img_size/2)
    shift = 200

    x_offs = [256]
    y_offs = [0, 128, 256, 512]

    for x_off in x_offs:
        for y_off in y_offs:
            # print(x_off, y_off, type(x_off), type(win_size), type(img_size))
            min_img = np_ref_img[y_off:y_off + win_size, x_off:x_off + win_size, :]

            stub.SetCrop(img_np_2_proto(min_img))
            result = stub.Ipnet(pb2.Empty())
            np_result = img_proto_2_np(result).copy()

            min_img = min_img[::4, ::4, :]
            np_result[0:128,0:128,:] = min_img[:,:,:]
            io.imsave(f'{save_dir}/img_{x_off}_{y_off}.png', np_result)
 

def single_adapter_run(opt: pb2.Options, stub: pb2_grpc.ComfyStub):
    save_dir = "fs"
    opt.img_power = 0.0
    opt.inpt_flag = pb2.SDXL
    stub.SetOptions(opt)
    _result = stub.Ipnet(pb2.Empty())
    print("first step")
    io.imsave(f'{save_dir}/out_img_sgl.png', img_proto_2_np(_result))   

def single_gen(opt: pb2.Options, stub: pb2_grpc.ComfyStub):
    save_dir = "fs"

    opt.img_power = 0.0
    opt.inpt_flag = pb2.SDXL
    stub.SetOptions(opt)
    _result = stub.Inpaint(pb2.Empty())
    print("first step")

    opt.img_power = 0.35
    opt.inpt_flag = pb2.FLUX
    stub.SetOptions(opt)
    stub.SetImage(_result)
    _result = stub.Inpaint(pb2.Empty())
    print("second step")
    io.imsave(f'{save_dir}/out_img_sgl.png', img_proto_2_np(_result))

class Timeline():
    t_bucket: float
    text: str
    def __init__(self, text):
        self.text = text

    def __enter__(self):
        self.t_bucket = time.perf_counter()
    
    def __exit__(self, t, v, trace):
        elapsed = time.perf_counter() - self.t_bucket
        print(f"+++ {self.text} took: {elapsed/1000} s")
        return False

def serdes_pipe(img_proto: pb2.Image, write=False) -> pb2.Image:
    bin_data = img_proto.SerializeToString()
    if write:
        with open("fs/serdesdump", "wb") as bin_file:
            bin_file.write(bin_data)

    return pb2.Image.FromString(bin_data)

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

    img_np = trio_channel(load_image('img.png'))
    mask_np = uno_channel(load_image('mask.png'))

    prompt = load_prompt()
    print("test prompt: ",prompt)

    opts = pb2.Options(
        prompts=[prompt],
        img_power=1,
        inpt_flag=pb2.FLUX)

    img_proto = img_np_2_proto(img_np)
    img_proto = serdes_pipe(img_proto, True)

    mask_proto = img_np_2_proto(mask_np)

    with Timeline("simple run") as time_messure:
        stub.SetImage(img_proto)
        stub.SetMask(mask_proto)
        stub.SetOptions(opts)
        
        # sequence_gen(_opt, stub)
        # single_gen(_opt, stub)
        # single_adapter_run(_opt, stub)
        sequence_adapter_run(opts, stub, img_proto)
    

