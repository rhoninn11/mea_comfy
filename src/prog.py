from src.utils import img_np_2_pt, img_pt_2_np
import skimage.io as io

import os
from workflows.workflow_cascade_img2img import workflow
# from workflows.workflow_sdxl_inpaint import workflow

def prog():
    file = 'assets/img.png'
    img_np = io.imread(file)
    img_pt = img_np_2_pt(img_np, transpose=False, one_minus_one=False)
    img_pt = img_pt.unsqueeze(0)

    img_pt = workflow(img_pt)
    
    img_pt = img_pt.squeeze(0)
    img_np = img_pt_2_np(img_pt, transpose=False, one_minus_one=False)
    os.makedirs('fs', exist_ok=True)
    io.imsave('fs/out.png', img_np)


    # workflow()
