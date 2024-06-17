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
    return pt_image[:,:,:, 0]


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

class ComfyService(pb2_grpc.ComfyServicer):
    def __init__(self):
        self.for_now = "😇"
        self.img_pt = None
        self.mask_pt = None

    def SetImage(self, request: pb2.Image, context):
        print(f"+++ set image")
        print(f"+++ img size: {request.info.width}x{request.info.height}")
        img_np = np.frombuffer(request.pixels, dtype=np.uint8)
        img_np = img_np.reshape(request.info.height, request.info.width, 3)
        img_pt = img_np_2_pt(img_np, transpose=False, one_minus_one=False)
        self.img_pt = img_pt.unsqueeze(0)
        print(f"+++ img pt shape: {self.img_pt.shape}")
        return pb2.Empty()
    
    def SetMask(self, request: pb2.Image, context):
        print(f"+++ set mask")
        print(f"+++ mask size: {request.info.width}x{request.info.height}")
        mask_np = np.frombuffer(request.pixels, dtype=np.uint8)
        mask_np = mask_np.reshape(request.info.height, request.info.width, 1)
        mask_pt = img_np_2_pt(mask_np, transpose=False, one_minus_one=False)
        self.mask_pt = mask_pt.unsqueeze(0)
        print(f"+++ mask pt shape: {self.mask_pt.shape}")
        return pb2.Empty()
    
    def Inpaint(self, request, context):
        print(f"+++ inpaint")

        img_pt = wokflow_inpaint(self.img_pt, self.mask_pt)

        _, width, height, _ = img_pt.shape
        img_info = pb2.ImgInfo(width=width, height=height, img_type=pb2.ImgType.RGB)
        byte_data = img_pt_2_np(img_pt, transpose=False, one_minus_one=False).tobytes()
        img = pb2.Image(info=img_info, pixels=byte_data)
        return img

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

    _, width, height, _ = img_pt.shape
    img_info = pb2.ImgInfo(width=width, height=height, img_type=pb2.ImgType.RGB)
    byte_data = img_pt_2_np(img_pt, transpose=False, one_minus_one=False).tobytes()
    img_proto = pb2.Image(info=img_info, pixels=byte_data)

    mask_file = 'assets/mask.png'
    mask_pt = load_image(mask_file)
    mask_pt = single_channel(mask_pt)

    _, width, height = mask_pt.shape
    mask_info = pb2.ImgInfo(width=width, height=height, img_type=pb2.ImgType.MONO)
    byte_data = img_pt_2_np(mask_pt, transpose=False, one_minus_one=False).tobytes()
    mask_proto = pb2.Image(info=mask_info, pixels=byte_data)


    channel = grpc.insecure_channel("localhost:50051")
    stub = pb2_grpc.ComfyStub(channel)

    stub.SetImage(img_proto)
    stub.SetMask(mask_proto)
    inpaint_out = stub.Inpaint(pb2.Empty())
    img_np = np.frombuffer(inpaint_out.pixels, dtype=np.uint8)
    img_np = img_np.reshape(1, inpaint_out.info.height, inpaint_out.info.width, 3)
    io.imsave('fs/out_client.png', img_np)


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



