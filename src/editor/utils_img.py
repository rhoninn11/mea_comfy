
from PyQt5.QtGui import QImage
import numpy as np

IMG_FORMAT = QImage.Format_RGBA8888
CH_NUM = 4

def qt_to_np_img(qt_img: QImage) -> np.ndarray:
    width = qt_img.width()
    height = qt_img.height()
    buffer = qt_img.constBits().asarray(height * width * CH_NUM)
    return np.frombuffer(buffer, dtype=np.uint8).reshape((height, width, CH_NUM))

def np_to_qt_img(np_img: np.ndarray) -> QImage:
    height, width, _ = np_img.shape
    qt_img = QImage(np_img.data, width, height, IMG_FORMAT)
    qt_img.detach()
    return qt_img