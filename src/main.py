# import os
# import time
# import grpc


# from skimage import io
# from utils_mea import img_np_2_pt

# import time
# import argparse


# def main():
#     parser = argparse.ArgumentParser(description="comfy ui workflow run")
#     parser.add_argument("-demo", action="store_true", help="run demo script for comfy ui inpaint")
#     parser.add_argument("-server", action="store_true", help="start grpc for comfy ui inpaint")
#     parser.add_argument("-client", action="store_true", help="start grpc client for comfy ui inpaint")
#     parser.add_argument("-editor", action="store_true", help="start simple Qt inpaint editor")
#     parser.add_argument("-llm", action="store_true", help="start ollama tinkering script")
#     parser.add_argument("-wss", action="store_true", help="start websocket server")
#     parser.add_argument("-wsc", action="store_true", help="start websocket client")

#     args = parser.parse_args()
#     if args.demo:
#         from src.demo import inpaint_demo as demo
#         demo()
#     elif args.server:
#         from src.server import start_server as serve
#         serve()
#     elif args.client:
#         from src.client import start_client as client
#         client()
#     elif args.llm:
#         from llm import main as app
#         app()
#     elif args.editor:
#         from src.editor.app import main as editor
#         editor()
#     elif args.wss:
#         import src.ws.server
#     else:
#         parser.print_help()



