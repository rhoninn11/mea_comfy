import os
import time
import grpc


from skimage import io
from utils_mea import img_np_2_pt


def load_image(file):
    img_np = io.imread(file)
    img_pt = img_np_2_pt(img_np, transpose=False, one_minus_one=False)
    img_pt = img_pt.unsqueeze(0)
    return img_pt

def single_channel(pt_image):
    return pt_image[:,:,:, 0:1]



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
    print("+++ Client starting...")
    img_file = 'assets/img.png'
    img_pt = load_image(img_file)
    img_proto = img_pt_2_proto(img_pt)

    mask_file = 'assets/mask.png'
    mask_pt = load_image(mask_file)
    mask_pt = single_channel(mask_pt)
    mask_proto = img_pt_2_proto(mask_pt)

    ssl_options = grpc.ssl_channel_credentials(ROOT_CERTIFICATE)
    channel = grpc.secure_channel("localhost:50051", ssl_options)

    stub = pb2_grpc.ComfyStub(channel)
    prompt = "earth hit by meteorite"
    img_power = 0.2
    gen_opt = pb2.Options(prompt=prompt, img_power=img_power)

    tick = time.perf_counter()
    stub.SetImage(img_proto)
    stub.SetMask(mask_proto)
    stub.SetOptions(gen_opt)
    # result_proto = stub.Inpaint(pb2.Empty())
    result_proto = stub.Img2Img(pb2.Empty())
    inpaint_np = img_proto_2_np(result_proto)
    tock = time.perf_counter()
    print(f"+++ Inpainting took {(tock - tick)} s")
    io.imsave('fs/out_client_1.png', inpaint_np)


import argparse




def main():
    parser = argparse.ArgumentParser(description="comfy ui workflow run")
    parser.add_argument("-demo", action="store_true", help="run demo script for comfy ui inpaint")
    parser.add_argument("-server", action="store_true", help="start grpc for comfy ui inpaint")
    parser.add_argument("-client", action="store_true", help="start grpc client for comfy ui inpaint")

    args = parser.parse_args()
    if args.demo:
        from src.demo import inpaint_demo as demo
        demo()
    if args.server:
        from src.server import start_server as serve
        serve()
    if args.client:
        start_client()
    else:
        parser.print_help()



