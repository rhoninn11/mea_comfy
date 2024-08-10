import os

def ensure_path_exist(path):
    if os.path.exists(path):
        os.makedirs(path, exist_ok=True)
