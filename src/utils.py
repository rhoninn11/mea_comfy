import os
import shutil

import json

def ensure_path_exist(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

def proj_asset(asset_path: str) -> str:
    prompt_src = f"assets/{asset_path}"
    prompt_dst = f"fs/{asset_path}"
    
    ensure_path_exist(os.path.dirname(prompt_dst))
    if not os.path.exists(prompt_dst):
        if not os.path.exists(prompt_src):
            raise FileExistsError()
        shutil.copy(prompt_src, prompt_dst)

    return prompt_dst


class Proj:
    prefix: str = ""

    def __init__(self, dir: str):
        self.prefix = dir

    def asset(self, asset_path: str) -> str:
        return proj_asset(f"{self.prefix}/{asset_path}")




def file2json2obj(json_file):
    data = None
    with open(json_file, 'r', encoding='utf-8') as j_file:
        json_content = j_file.read()
        data = json.loads(json_content)
    return data

import time
class Timeline():
    then: float
    start: float
    now: float

    def __init__(self):
        pass

    def __enter__(self):
        self.start = time.perf_counter()
        self.then = self.start

    def __exit__(self, t, v, trace):
        self.total_elapse()
    
    def total_elapse(self):
        self.now = time.perf_counter()
        return (self.now - self.start)/1000
