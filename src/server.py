import os

import proto.comfy_pb2 as pb2
import proto.comfy_pb2_grpc as pb2_grpc
from utils_mea import img_proto_2_pt, img_pt_2_proto, img_proto_2_np

from workflows.flux_inpaint_blend import workflow as workflow_inpaint
from workflows.flux_img2img import workflow as workflow_img2img


class ComfyService(pb2_grpc.ComfyServicer):
    def __init__(self):
        self.for_now = "😇"
        self.img_pt = None
        self.mask_pt = None
        self.options: pb2.Options = pb2.Options(prompt="flowers on sufrace of the earth")

    def SetImage(self, request: pb2.Image, context):
        print(f"+++ set image")
        self.img_pt = img_proto_2_pt(request)
        return pb2.Empty()
    
    def SetMask(self, request: pb2.Image, context):
        print(f"+++ set mask")
        self.mask_pt = img_proto_2_pt(request)
        return pb2.Empty()
    
    def SetOptions(self, request: pb2.Options, context):
        self.options = request
        return pb2.Empty()
    
    def Inpaint(self, request, context) -> pb2.Image:
        print(f"+++ inpaint")
        prompt = self.options.prompt
        img_pt = workflow_inpaint(self.img_pt, self.mask_pt, prompt)
        return img_pt_2_proto(img_pt)

    def Img2Img(self, request, context) -> pb2.Image:
        print("+++ img2img")
        prompt = self.options.prompt
        img_power = self.options.img_power
        img_pt = workflow_img2img(self.img_pt, self.mask_pt, prompt, img_power)
        return img_pt_2_proto(img_pt)
    

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

    server.add_secure_port(f"localhost:{port}", ssl_options)
    # server.add_insecure_port(f"localhost:{port}")

    server.start()
    print("+++ Server started")
    server.wait_for_termination()
