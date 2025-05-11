
import numpy as np
import mea_gen_d.comfy_pb2 as pb2

def img_proto_2_np(img_proto: pb2.Image) -> np.ndarray:
    img_np = np.frombuffer(img_proto.pixels, dtype=np.uint8)
    img_np = img_np.reshape(img_proto.info.height, img_proto.info.width, img_proto.info.img_type)
    return img_np


def img_np_2_proto(img_np: np.ndarray) -> pb2.Image:
    print(img_np.shape)
    width, height, ch = img_np.shape
    img_type = pb2.ImgType.RGB if ch == 3 else pb2.ImgType.MONO
    img_info = pb2.ImgInfo(width=width, height=height, img_type=img_type)
    byte_data = img_np.tobytes()
    img_proto = pb2.Image(info=img_info, pixels=byte_data)
    return img_proto
