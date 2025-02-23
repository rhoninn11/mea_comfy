import os
import pyarrow.parquet as pq
import random
import numpy as np
from enum import Enum
from tqdm import tqdm
import requests

class Steps(Enum):
    init = 0
    decimation = 1
    download = 2
    render_ready = 3

root="./fs/tride"
file="smithsonian.parquet"
# https://huggingface.co/datasets/allenai/objaverse-xl/tree/main/smithsonian

datafile = os.path.join(root, file)
schema = pq.read_schema(datafile)
tf = pq.read_table(datafile).to_pandas()

print(schema)
file_id = 'fileIdentifier'
type_id = 'fileType'
tf_all = tf[[file_id, 'sha256', type_id]]

tf_glb = tf_all[tf_all[type_id] == "glb"]
tf_len = len(tf_glb)

sample_num = 100
ids_all = np.arange(0, tf_len, 1, dtype=np.int32)
sampled_ids = np.sort(random.sample(ids_all.tolist(), sample_num))
tf_few = tf_glb.iloc[sampled_ids] 

b = tf_few.iloc[0]
model_dir = "models"
model_path = os.path.join(root, model_dir)
os.makedirs(model_path)
for i, row in tqdm(enumerate(tf_few.iloc)):
    model_src = row[file_id]
    model_dst = os.path.join(model_path, f"model_{i:03d}.{row[type_id]}")
    with open(model_dst, "wb") as model_fd:
        r = requests.get(row[file_id])
        model_fd.write(r.content)
