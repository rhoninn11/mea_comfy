

# get env variables
import os, sys, json


# open json repo file
import json
import git

file = open('repolist.json', "r")
repolist = json.load(file)

def setUpComfy():
    value = os.getenv('COMFY')
    if value is not None:
        sys.path.append(value)
    else:
        print("COMFY not set in this system, at this moment is the only way")
        exit()
        # if not os.path.exists(repolist['comfy']["dir"]):
        #     git.Repo.clone_from(repolist['comfy']["url"], repolist['comfy']["dir"])
        #     # install comfy ui
        # sys.path.append(repolist['comfy']["dir"])

my_args = sys.argv.copy()
sys.argv = sys.argv[:1]
# to not interference with comfy

setUpComfy()
sys.path.append("src")
sys.path.append("src/proto")

sys.argv = my_args
from src.main import main
main()

# from src.workflows.sdxd_inpaint_plus_plus import comfy_script_test
# from src.workflows.flux_schnell_txt2img import comfy_script_test
# comfy_script_test()
