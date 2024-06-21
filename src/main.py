from utils_mea import img_np_2_pt, img_pt_2_np
import skimage.io as io

import os, torch
from workflows.workflow_cascade_img2img import workflow as workflow_cascade
from workflows.workflow_sdxl_inpaint import workflow as workflow_inpaint
from workflows.workflow_sdxl_img2img import workflow as workflow_img2img


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

    img_pt = workflow_inpaint(img_pt, mask_pt)
    
    img_pt = img_pt.squeeze(0)
    img_np = img_pt_2_np(img_pt, transpose=False, one_minus_one=False)
    os.makedirs('fs', exist_ok=True)
    io.imsave('fs/out.png', img_np)

import proto.comfy_pb2 as pb2
import proto.comfy_pb2_grpc as pb2_grpc
from utils_mea import img_proto_2_pt, img_pt_2_proto, img_proto_2_np



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
        img_pt = workflow_inpaint(self.img_pt, self.mask_pt)
        return img_pt_2_proto(img_pt)
    
    def Img2Img(self, request, context) -> pb2.Image:
        img_pt = workflow_img2img(self.img_pt)
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
    inpaint_np = img_proto_2_np(inpaint_proto)
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
        inpaint_demo()
    if args.server:
        start_server()
    if args.client:
        start_client()
    else:
        parser.print_help()



