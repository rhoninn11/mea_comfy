import os
import time
import numpy as np

import grpc
import proto.comfy_pb2 as pb2
import proto.comfy_pb2 as comfy
import proto.comfy_pb2_grpc as pb2_grpc

from skimage import io

from utils_proto import *
from utils import proj_asset, file2json2obj, ensure_path_exist, Timeline

def clone(mesg: str):
    print(mesg)
    exit(1)


# channer leduction fns 
def uno_channel(img: np.ndarray) -> np.ndarray:
    return img[:,:, 0:1]

def trio_channel(img: np.ndarray) -> np.ndarray:
    return img[:,:, 0:3]
# ------------------------

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


# for safe rpc connection over tcp
def _load_credential_from_file(filepath):
    real_path = os.path.abspath(filepath)
    with open(real_path, "rb") as f:
        return f.read()


SERVER_CERTIFICATE = _load_credential_from_file("assets/credentials/localhost.crt")
SERVER_CERTIFICATE_KEY = _load_credential_from_file("assets/credentials/localhost.key")
ROOT_CERTIFICATE = _load_credential_from_file("assets/credentials/root.crt")
# -------------------------------------------------------------------------------------



RPC_STUB: pb2_grpc.ComfyStub = None
def assert_stub_exist():
    if RPC_STUB != None:
        return
    
    clone("!!! stub not initialized")


# comfy grpc examples
def sequence_gen(opt: pb2.Options):
    save_dir = "fs/seq"
    ensure_path_exist(save_dir)

    for i, _power in enumerate(np.linspace(0,0.25,5).tolist()):
        opt.img_power = _power
        RPC_STUB.SetOptions(opt)
        _result = RPC_STUB.Inpaint(pb2.Empty())
        io.imsave(f'{save_dir}/out_img_{i:02}.png', img_proto_2_np(_result))

def sequence_adapter_run(opt: pb2.Options, proto_img: pb2.Image):
    save_dir = "fs/seq_ada"   
    ensure_path_exist(save_dir)
    print("+++ Elo", proto_img.info)
    np_ref_img = img_proto_2_np(proto_img)
    print("input", np_ref_img.shape)
    img_size = np_ref_img.shape[0]
    win_size = int(img_size/4)
    shift = 200

    x_offs = [256]
    y_offs = [0, 128, 256, 512, 768]

    for x_off in x_offs:
        for y_off in y_offs:
            # print(x_off, y_off, type(x_off), type(win_size), type(img_size))
            min_img = np_ref_img[y_off:y_off + win_size, x_off:x_off + win_size, :]
            RPC_STUB.SetCrop(img_np_2_proto(min_img))
            result = RPC_STUB.Ipnet(pb2.Empty())
            np_result = img_proto_2_np(result).copy()

            min_img = min_img[::2, ::2, :]
            print("img size",min_img.shape)
            print("dst shape", np_result.shape)
            np_result[0:128,0:128,:] = min_img[:,:,:]
            file = f'{save_dir}/img_{x_off}_{y_off}.png'
            print(file)
            io.imsave(file, np_result)
            # exit(1)
 

def single_adapter_run(opt: pb2.Options, ):
    save_dir = "fs"
    opt.img_power = 0.0
    opt.inpt_flag = pb2.SDXL
    RPC_STUB.SetOptions(opt)
    _result = RPC_STUB.Ipnet(pb2.Empty())
    print("first step")
    io.imsave(f'{save_dir}/out_img_sgl.png', img_proto_2_np(_result))   

# using two models workflow for inpaint
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
# -----------------------------------------------------------------------

# dump image as proto fule
def serdes_pipe(img_proto: pb2.Image, write=False) -> pb2.Image:
    bin_data = img_proto.SerializeToString()
    if write:
        with open("fs/serdesdump", "wb") as bin_file:
            bin_file.write(bin_data)

    return pb2.Image.FromString(bin_data)

def start_client():
    rpc_client()

def rpc_client():
    global RPC_STUB
    port = 50051

    # spawn assets in fs

    print("+++ Client starting...")
    config = file2json2obj(proj_asset("client_config.json"))
    server_address = config["server_addres"]
    endpoint = f"{server_address}:{port}"

    credentials = grpc.ssl_channel_credentials(ROOT_CERTIFICATE)
    channel_options = [('grpc.ssl_target_name_override', 'localhost')] # tmp workaround
    
    channel = grpc.secure_channel(endpoint, credentials, options=channel_options)
    RPC_STUB= pb2_grpc.ComfyStub(channel)

    img_np = trio_channel(load_image('img.png'))
    mask_np = uno_channel(load_image('mask.png'))

    prompt = load_prompt()
    print("test prompt: ",prompt)

    opts = pb2.Options(
        prompts=[prompt],
        img_power=1,
        inpt_flag=pb2.FLUX,
        seed=2)


    print(img_np.shape)
    img_proto = img_np_2_proto(img_np)
    set_image_data = comfy.SetImageData(slot=comfy.Slot.Slot_A, image=img_proto)
    img_proto = serdes_pipe(img_proto, True)

    mask_proto = img_np_2_proto(mask_np)
    
    assert_stub_exist()
    with Timeline() as time_messure:
        RPC_STUB.SetImage(set_image_data)
        RPC_STUB.SetMask(mask_proto)
        RPC_STUB.SetOptions(opts)
        
        # test playground
        # sequence_gen(_opt)
        # single_gen(_opt)
        # single_adapter_run(_opt)
        sequence_adapter_run(opts, img_proto)
        print("do nothing")
    

