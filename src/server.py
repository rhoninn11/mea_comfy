import os

import torch
from mea_gen_d.comfy_pb2 import *
import mea_gen_d.comfy_pb2 as pb2
import mea_gen_d.comfy_pb2_grpc as pb2_grpc
from utils_proto import img_np_2_proto, img_proto_2_np
from utils_mea import img_np_2_pt, img_pt_2_np

from workflows.flux_inpaint_blend import workflow as workflow_inpaint_f
from workflows.flux_img2img import workflow as workflow_img2img
from workflows.flux_txt2img import workflow as workflow_tmg2img

from workflows.base import ComfyWorkflow
from workflows.sdxl_ipadapter import IpAdapter
from workflows.sdxl_inpaint_plus_plus import InpaintWorkflow
from workflows.sdxl_txt2img import BasicWorkflow


def img_proto_2_pt(img_proto: pb2.Image) -> torch.Tensor:
    img_np = img_proto_2_np(img_proto)
    img_pt = img_np_2_pt(img_np, transpose=False, one_minus_one=False)
    return img_pt.unsqueeze(0)

def img_pt_2_proto(img_pt: torch.Tensor) -> pb2.Image:
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
        self.options: Options = Options(
            seed=0,
            img_power=1,
            model_flag=pb2.SDXL
        )
        self.ipnet = IpAdapter()
        self.inpaint = InpaintWorkflow()
        self.sdxl_txt = BasicWorkflow()
        self.reload: bool = True
        self.img_ref = None
        self.imgs: dict[str, torch.Tensor | None] = {}
        self.gen_state: state.ServState = state.ServState()



    def SetPrompt(self, request: pb2.SlotedPrompt, context):
        self.gen_state.prompts[request.slot] = request.prompt
        print("+++ Prompt was set")
        return Empty()
        


    def SetImage(self, request: SlotedImage, context):
        print(f"+++ set image")
        pt_img = img_proto_2_pt(request.image)
        at_slot = pb2.Slot.keys()[request.slot]
        # self.gen_state.imgs[at_slot] = pt_img
        return Empty()

    def SetMask(self, request: Image, context):
        print(f"+++ set mask")
        # hmmm i think it can fail, but for now i do not need to set mask i think
        # np_img = img_proto_2_np(request)
        # self.mask_pt = img_np_2_pt(np_img)

        self.mask_pt = img_proto_2_pt(request)
        
        print(f"+++ mash shape {self.mask_pt.shape}")
        return Empty()
    
    def SetOptions(self, request: Options, context):
        self.options = request
        print("+++ options was set")
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

        at_slot = pb2.Slot.keys()[pb2.Slot.Slot_A]
        img_pt = self.gen_state.imgs[at_slot]
        if _inpt in [SDXL, BOTH]:
            img_pt = self.inpaint.workflow(img_pt, self.mask_pt, prompt, _imgp)
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
        slot = self.options.prompt_chain[0]
        img_power = self.options.img_power
        img_pt = workflow_img2img(self.img_pt, self.mask_pt, prompt, img_power)
        return img_pt_2_proto(img_pt)
    
    def Txt2Img(self, request, context):
        slot = self.options.prompt_chain[0]
        prompt = self.gen_state.prompts[slot]
        self.sdxl_txt.opts = self.options
        self.sdxl_txt.state = self.gen_state
        img_pt = self.sdxl_txt.sdxl_txt2img(prompt)
        # img_pt = workflow_tmg2img(prompt)
        return img_pt_2_proto(img_pt)
    
    def Reboot(self, request, context) -> pb2.Empty:
        print("+++ reboot hit, but how to close it properly")
        return pb2.Empty()
    
    

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
    # server.add_secure_port(serv_address, ssl_options)
    server.add_insecure_port(serv_address)

    server.start()
    print("+++ Server started")
    server.wait_for_termination()
