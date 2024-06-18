from src.utils import img_np_2_pt, img_pt_2_np
import skimage.io as io

import os, torch
from workflows.workflow_cascade_img2img import workflow as workflow_cascade
from workflows.workflow_sdxl_inpaint import workflow as wokflow_inpaint


def load_image(file):
    img_np = io.imread(file)
    img_pt = img_np_2_pt(img_np, transpose=False, one_minus_one=False)
    img_pt = img_pt.unsqueeze(0)
    return img_pt

def single_channel(pt_image):
    return pt_image[:,:,:, 0:1]


def inpaint_demo():
    img_file = 'assets/img.png'
    img_pt = load_image(img_file)

    mask_file = 'assets/mask.png'
    mask_pt = load_image(mask_file)
    mask_pt = single_channel(mask_pt)

    img_pt = wokflow_inpaint(img_pt, mask_pt)
    
    img_pt = img_pt.squeeze(0)
    img_np = img_pt_2_np(img_pt, transpose=False, one_minus_one=False)
    os.makedirs('fs', exist_ok=True)
    io.imsave('fs/out.png', img_np)

import proto.comfy_pb2 as pb2
import proto.comfy_pb2_grpc as pb2_grpc

def img_proto_2_pt(img_proto: pb2.Image) -> torch.Tensor:
    img_np = np.frombuffer(img_proto.pixels, dtype=np.uint8)
    img_np = img_np.reshape(img_proto.info.height, img_proto.info.width, img_proto.info.img_type)
    img_pt = img_np_2_pt(img_np, transpose=False, one_minus_one=False)
    return img_pt.unsqueeze(0)

def img_pt_2_proto(img_pt: torch.Tensor) -> pb2.Image:
    _, width, height, ch = img_pt.shape
    img_type = pb2.ImgType.RGB if ch == 3 else pb2.ImgType.MONO
    img_info = pb2.ImgInfo(width=width, height=height, img_type=img_type)
    byte_data = img_pt_2_np(img_pt, transpose=False, one_minus_one=False).tobytes()
    img_pt = pb2.Image(info=img_info, pixels=byte_data)
    return img_pt



class ComfyService(pb2_grpc.ComfyServicer):
    def __init__(self):
        self.for_now = "😇"
        self.img_pt = None
        self.mask_pt = None

    def SetImage(self, request: pb2.Image, context):
        print(f"+++ set image")
        self.img_pt = img_proto_2_pt(request)
        return pb2.Empty()
    
    def SetMask(self, request: pb2.Image, context):
        print(f"+++ set mask")
        self.mask_pt = img_proto_2_pt(request)
        return pb2.Empty()
    
    def Inpaint(self, request, context) -> pb2.Image:
        print(f"+++ inpaint")
        img_pt = wokflow_inpaint(self.img_pt, self.mask_pt)
        return img_pt_2_proto(img_pt)
    

def _load_credential_from_file(filepath):
    real_path = os.path.abspath(filepath)
    with open(real_path, "rb") as f:
        return f.read()


SERVER_CERTIFICATE = _load_credential_from_file("assets/credentials/localhost.crt")
SERVER_CERTIFICATE_KEY = _load_credential_from_file("assets/credentials/localhost.key")
ROOT_CERTIFICATE = _load_credential_from_file("assets/credentials/root.crt")

import time
import grpc
import concurrent.futures as futures
import numpy as np

def start_server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    service = ComfyService()
    pb2_grpc.add_ComfyServicer_to_server(service, server)

    server.add_insecure_port("localhost:50051")
    server.start()
    print("+++ Server started")
    server.wait_for_termination()

def start_client():
    print("+++ Client starting...")
    img_file = 'assets/img.png'
    img_pt = load_image(img_file)
    img_proto = img_pt_2_proto(img_pt)

    mask_file = 'assets/mask.png'
    mask_pt = load_image(mask_file)
    mask_pt = single_channel(mask_pt)
    mask_proto = img_pt_2_proto(mask_pt)

    channel = grpc.insecure_channel("localhost:50051")
    stub = pb2_grpc.ComfyStub(channel)

    tick = time.perf_counter()
    stub.SetImage(img_proto)
    stub.SetMask(mask_proto)
    inpaint_proto = stub.Inpaint(pb2.Empty())
    tock = time.perf_counter()
    print(f"+++ Inpainting took {(tock - tick)} s")
    io.imsave('fs/out_client_1.png', img_pt_2_np(img_proto_2_pt(inpaint_proto), transpose=False, one_minus_one=False))


import argparse



def main():
    parser = argparse.ArgumentParser(description="comfy ui workflow run")
    parser.add_argument("-demo", action="store_true", help="run demo script for comfy ui inpaint")
    parser.add_argument("-server", action="store_true", help="start grpc for comfy ui inpaint")
    parser.add_argument("-client", action="store_true", help="start grpc client for comfy ui inpaint")

    args = parser.parse_args()
    if args.demo:
        inpaint_demo()
    if args.server:
        start_server()
    if args.client:
        start_client()
    else:
        parser.print_help()



