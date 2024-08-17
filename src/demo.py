import os

import skimage.io as io

from utils_mea import img_np_2_pt, img_pt_2_np

from workflows.flux_inpaint_blend import workflow as workflow_inpaint
from workflows.flux_img2img import workflow as workflow_img2img

def load_image(file):
    img_np = io.imread(file)
    img_pt = img_np_2_pt(img_np, transpose=False, one_minus_one=False)
    img_pt = img_pt.unsqueeze(0)
    return img_pt

def single_channel(pt_image):
    return pt_image[:,:,:, 0:1]


def inpaint_demo():
    img_file = 'assets/img.png'
    img_pt = load_image(img_file)

    mask_file = 'assets/mask.png'
    mask_pt = load_image(mask_file)
    mask_pt = single_channel(mask_pt)

    img_pt = workflow_inpaint(img_pt, mask_pt)
    
    img_pt = img_pt.squeeze(0)
    img_np = img_pt_2_np(img_pt, transpose=False, one_minus_one=False)
    os.makedirs('fs', exist_ok=True)
    io.imsave('fs/out.png', img_np)
