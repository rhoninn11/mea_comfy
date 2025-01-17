import os
import shutil

def ensure_path_exist(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

def proj_asset(asset_path):
    prompt_src = f"assets/{asset_path}"
    prompt_dst = f"fs/{asset_path}"
    
    ensure_path_exist(os.path.dirname(prompt_dst))
    if not os.path.exists(prompt_dst):
        if not os.path.exists(prompt_src):
            raise FileExistsError()
        shutil.copy(prompt_src, prompt_dst)

    return prompt_dst

import json

def file2json2obj(json_file):
    data = None
    with open(json_file, 'r', encoding='utf-8') as j_file:
        json_content = j_file.read()
        data = json.loads(json_content)
    return data
