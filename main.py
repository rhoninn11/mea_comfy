

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
        # if not os.path.exists(repolist['comfy']["dir"]):
        #     git.Repo.clone_from(repolist['comfy']["url"], repolist['comfy']["dir"])
        #     # install comfy ui
        # sys.path.append(repolist['comfy']["dir"])

setUpComfy()
sys.path.append("src")

from prog import prog
prog()
