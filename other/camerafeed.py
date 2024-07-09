import cv2, time, math
import numpy as np

capture_device = cv2.VideoCapture(0)

SD_W, SD_H = 1024, 1024

def crop_frame(frame):
    h, w, ch = frame.shape

    left, right = 0, w
    delta = w - SD_W
    if delta > 0:
        shift = math.ceil(delta/2)
        left = shift - 1
        right = left + SD_W

    bottom, top = 0, h
    delta = h - SD_H
    if delta > 0:
        shift = math.ceil(delta/2)
        bottom = shift - 1
        top = bottom + SD_H

    crop = frame[bottom:top, left:right, :]
    # print(F"+++ frame shape: {frame.shape}, crop shape: {crop.shape}")

    return crop

import sys
sys.path.append("src")
sys.path.append("src/proto")

import grpc
import proto.comfy_pb2 as pb2
import proto.comfy_pb2_grpc as pb2_grpc
from utils_mea import img_proto_2_np, img_np_2_proto

import asyncio

run_cond: bool = True
stub: pb2_grpc.ComfyStub
recent_frame: np.ndarray = None
recent_result: np.ndarray = None
info = []

def start_client():
    global stub, info
    info.append("+++ connection to client...")
    channel = grpc.aio.insecure_channel("localhost:50051")
    stub = pb2_grpc.ComfyStub(channel)
    info.append("+++ connected")



async def img2img(img_np: np.ndarray) -> np.ndarray:
    global stub
    img_proto = img_np_2_proto(img_np)
    await stub.SetImage(img_proto)
    img2img_proto = await stub.Img2Img(pb2.Empty())
    img2img_np = img_proto_2_np(img2img_proto)
    return img2img_np


async def comfy_loop():
    global run_cond, recent_frame, recent_result

    start_client()
    while run_cond:
        if recent_frame is None:
            asyncio.sleep(0.01)
            continue

        recent_result = await img2img(recent_frame)

def asyncio_timeline(loop):
    global info
    asyncio.set_event_loop(loop)
    print("+++ asyncio loop started")
    loop.run_forever()


def capture_and_show():
    frame: np.ndarray
    global capture_device, info
    global run_cond, recent_frame, recent_result

    then = time.perf_counter()
    while run_cond:
        ret, frame = capture_device.read()
        if ret:
            now = time.perf_counter()
            frame_time = now - then
            then = now

            recent_frame = crop_frame(frame)
            display_result = recent_frame
            if recent_result is not None:
                display_result = np.concatenate((recent_frame, recent_result), axis=1)
            
            cv2.imshow("webcam", display_result)

            if cv2.waitKey(1):
                if len(info):
                    print(info[0])
                    info.pop(0)



import threading
loop = asyncio.new_event_loop()
thread = threading.Thread(target=asyncio_timeline, args=(loop, ), daemon=True).start()
asyncio.run_coroutine_threadsafe(comfy_loop(), loop)



capture_and_show()


