import os

import torch
from proto.comfy_pb2 import *
import proto.comfy_pb2 as comfy
import proto.comfy_pb2_grpc as pb2_grpc
from utils_proto import img_np_2_proto, img_proto_2_np
from utils_mea import img_np_2_pt, img_pt_2_np

from workflows.flux_inpaint_blend import workflow as workflow_inpaint_f
from workflows.flux_img2img import workflow as workflow_img2img
from workflows.flux_txt2img import workflow as workflow_tmg2img

from workflows.sdxl_ipadapter import IpAdapter
from workflows.sdxl_inpaint_plus_plus import workflow as workflow_inpaint_xl


def img_proto_2_pt(img_proto: comfy.Image) -> torch.Tensor:
    img_np = img_proto_2_np(img_proto)
    img_pt = img_np_2_pt(img_np, transpose=False, one_minus_one=False)
    return img_pt.unsqueeze(0)

def img_pt_2_proto(img_pt: torch.Tensor) -> comfy.Image:
    if len(img_pt.shape) > 3:
        img_pt = img_pt[0]

    img_np = img_pt_2_np(img_pt, transpose=False, one_minus_one=False)
    img_proto = img_np_2_proto(img_np)
    return img_proto

import state

# i would like to base this service around limited set of options
# just 4 slots for image, mask, and prompts, used for all operations in comfy
# for more exotice workflows meaby i shoud develop other format of passing data :D

class ComfyService(pb2_grpc.ComfyServicer):
    def __init__(self):
        self.img_pt = None
        self.mask_pt = None
        self.options: Options = Options(prompts=["flowers on sufrace of the earth"])
        self.ipnet = IpAdapter()
        self.reload: bool = True
        self.img_ref = None
        self.imgs: dict[str, torch.Tensor | None] = {}
        self.gen_state: state.GeneraotorState = state.GeneraotorState()

    def SetImage(self, request: SetImageData, context):
        print(f"+++ set image")
        pt_img = img_proto_2_pt(request.image)
        at_slot = comfy.Slot.keys()[request.slot]
        self.gen_state.imgs[at_slot] = pt_img
        return Empty()
    
    def SetMask(self, request: Image, context):
        print(f"+++ set mask")
        # hmmm i think it can fail, but for now i do not need to set mask i think
        np_img = img_proto_2_np(request)
        self.mask_pt = img_np_2_pt(np_img)
        return Empty()
    
    def SetOptions(self, request: Options, context):
        self.options = request
        for key, prompt in zip(comfy.Slot.keys(), self.options.prompts):
            self.gen_state.prompts[key] = prompt
        return Empty()
    
    def SetCrop(self, request: Image, context):
        self.ipnet.img_ref = img_proto_2_pt(request)
        self.ipnet.refresh_crop()
        return Empty()
    
    def Inpaint(self, request, context) -> Image:
        opt = self.options
        prompt = opt.prompts[0]
        _inpt = opt.inpt_flag
        _imgp = opt.img_power
        img_pt = self.gen_state.imgs[comfy.Slot.Slot_A]
        if _inpt in [SDXL, BOTH]:
            img_pt = workflow_inpaint_xl(img_pt, self.mask_pt, prompt, _imgp)
            img_pt = img_pt.to(self.img_pt.device)
        if _inpt in [FLUX, BOTH]:
            img_pt = workflow_inpaint_f(img_pt, self.mask_pt, prompt, _imgp)
        return img_pt_2_proto(img_pt)

    def Ipnet(self, request, context) -> Image:
        print("+++ ip adapter")
        prompt = self.options.prompts[0]
        img_power = self.options.img_power
        img_pt = self.ipnet.workflow(self.img_pt, self.mask_pt, prompt, img_power)
        return img_pt_2_proto(img_pt)
        

    def Img2Img(self, request, context) -> Image:
        print("+++ img2img")
        prompt = self.options.prompts[0]
        img_power = self.options.img_power
        img_pt = workflow_img2img(self.img_pt, self.mask_pt, prompt, img_power)
        return img_pt_2_proto(img_pt)
    
    def Txt2Img(self, request, context):
        prompt = self.options.prompts[0]
        img_pt = workflow_tmg2img(prompt)
        return img_pt_2_proto(img_pt)
    
    def Reboot(self, request, context) -> comfy.Empty:
        return comfy.Empty()
    
    

def _load_credential_from_file(filepath):
    real_path = os.path.abspath(filepath)
    with open(real_path, "rb") as f:
        return f.read()


SERVER_CERTIFICATE = _load_credential_from_file("assets/credentials/localhost.crt")
SERVER_CERTIFICATE_KEY = _load_credential_from_file("assets/credentials/localhost.key")
ROOT_CERTIFICATE = _load_credential_from_file("assets/credentials/root.crt")

import grpc
import concurrent.futures as futures

def start_server():

    port = 50051

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    service = ComfyService()
    pb2_grpc.add_ComfyServicer_to_server(service, server)

    auth_clinet_too = False
    ssl_options = grpc.ssl_server_credentials(((SERVER_CERTIFICATE_KEY, SERVER_CERTIFICATE),), ROOT_CERTIFICATE, auth_clinet_too)

    serv_address = f"0.0.0.0:{port}"
    server.add_secure_port(serv_address, ssl_options)
    # server.add_insecure_port(serv_address)

    server.start()
    print("+++ Server started")
    server.wait_for_termination()
