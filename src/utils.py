import os

def ensure_path_exist(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
