

import os
import sys

def setUpComfy():
    value = os.getenv('COMFY')
    if value is not None:
        sys.path.append(value)
    else:
        print("COMFY not set in this system, at this moment is the only way")
        exit()


my_args = sys.argv.copy()
sys.argv = sys.argv[:1]
# to not interference with comfy

# setUpComfy()
sys.path.append("src")
sys.path.append("src/mea_gen_d")

sys.argv = my_args
import argparse
# from src.main import main
# main()

# from src.workflows.sdxd_inpaint_plus_plus import comfy_script_test
# from src.workflows.flux_schnell_txt2img import comfy_script_test
# comfy_script_test()

def main():
    parser = argparse.ArgumentParser(description="comfy ui workflow run")
    parser.add_argument("-demo", action="store_true", help="run demo script for comfy ui inpaint")
    parser.add_argument("-server", action="store_true", help="start grpc for comfy ui inpaint")
    parser.add_argument("-client", action="store_true", help="start grpc client for comfy ui inpaint")
    parser.add_argument("-editor", action="store_true", help="start simple Qt inpaint editor")
    parser.add_argument("-llm", action="store_true", help="start ollama tinkering script")
    parser.add_argument("-wss", action="store_true", help="start websocket server")
    parser.add_argument("-wsc", action="store_true", help="start websocket client")

    args = parser.parse_args()
    if args.demo:
        from src.demo import inpaint_demo as demo
        demo()
    elif args.server:
        from src.server import start_server as serve
        serve()
    elif args.client:
        from src.client import start_client as client
        client()
    elif args.llm:
        from llm import main as app
        app()
    elif args.editor:
        from src.editor.app import main as editor
        editor()
    elif args.wss:
        import src.ws.server
    elif args.wsc:
        import src.ws.client
    else:
        parser.print_help()

main()