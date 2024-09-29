import sys
import PyQt5
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QSlider
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen, QColor, QKeyEvent
from PyQt5.QtCore import Qt, QPoint, QSize, QBuffer
from PIL import Image
import numpy as np
import io

class ImageMaskEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Image Mask Editor')
        self.setGeometry(100, 100, 1200, 1200)

        # Main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Canvas
        self.canvas = Canvas(self)
        main_layout.addWidget(self.canvas)

        # Control buttons
        controls_layout = QHBoxLayout()
        main_layout.addLayout(controls_layout)

        self.load_btn = QPushButton('Load Image')
        self.load_btn.clicked.connect(self.load_image)
        controls_layout.addWidget(self.load_btn)

        self.save_btn = QPushButton('Save')
        self.save_btn.clicked.connect(self.save_image)
        controls_layout.addWidget(self.save_btn)

        self.reset_mask_btn = QPushButton('Reset Mask')
        self.reset_mask_btn.clicked.connect(self.canvas.reset_mask)
        controls_layout.addWidget(self.reset_mask_btn)

        self.reset_image_btn = QPushButton('Reset Image')
        self.reset_image_btn.clicked.connect(self.canvas.reset_image)
        controls_layout.addWidget(self.reset_image_btn)

        self.zoom_in_btn = QPushButton('Zoom In')
        self.zoom_in_btn.clicked.connect(self.canvas.zoom_in)
        controls_layout.addWidget(self.zoom_in_btn)

        self.zoom_out_btn = QPushButton('Zoom Out')
        self.zoom_out_btn.clicked.connect(self.canvas.zoom_out)
        controls_layout.addWidget(self.zoom_out_btn)

        # Brush size slider
        self.brush_slider = QSlider(Qt.Horizontal)
        self.brush_slider.setMinimum(1)
        self.brush_slider.setMaximum(50)
        self.brush_slider.setValue(5)
        self.brush_slider.valueChanged.connect(self.canvas.set_brush_size)
        main_layout.addWidget(self.brush_slider)

    def load_image(self):
        file_name = "fs/out_img.png"
        if file_name:
            self.canvas.load_image(file_name)

    def save_image(self):
        file_name = "fs/out_mask.png"
        if file_name:
            self.canvas.save_image(file_name)

    def keyPressEvent(self, event: QKeyEvent):
        if event.isAutoRepeat():
            return
        self.canvas.keyPressEvent(event)
        event.accept()

    def keyReleaseEvent(self, event):
        if event.isAutoRepeat():
            return
        self.canvas.keyReleaseEvent(event)
        event.accept()

class Canvas(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.resize(QSize(1024, 1024))
        self.parent = parent
        self.image = QImage(self.size(), QImage.Format_ARGB32)
        self.image.fill(Qt.white)

        self.u_mask = QImage(self.size(), QImage.Format_ARGB32)
        self.u_mask.fill(Qt.black)

        self.last_point = QPoint()
        self.brush_size = 5
        self.drawing = False
        self.drag_start = None
        self.scale = 1.0
        self.offset = QPoint(0, 0)


    def load_image(self, file_name):
        self.image.load(file_name)
        self.u_mask = QImage(self.image.size(), QImage.Format_ARGB32)
        self.u_mask.fill(Qt.black)
        self.update()

    def save_image(self, file_name):
        buffer = QBuffer()
        buffer.open(QBuffer.ReadWrite)
        self.u_mask.save(buffer, "PNG")
        combined = Image.open(io.BytesIO(buffer.data()))
        combined.save(file_name)


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.scale(self.scale, self.scale)
        painter.translate(self.offset)
        painter.drawImage(0, 0, self.image)
        painter.setOpacity(0.5)
        painter.drawImage(0, 0, self.u_mask)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.last_point = event.pos() / self.scale - self.offset
        elif event.button() == Qt.RightButton:
            self.drag_start = event.pos()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton and self.drawing:
            painter = QPainter(self.u_mask)
            painter.setPen(QPen(Qt.white, self.brush_size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            current_point = event.pos() / self.scale - self.offset
            painter.drawLine(self.last_point, current_point)
            self.last_point = current_point
            self.update()
        elif event.buttons() & Qt.RightButton:
            self.offset += (event.pos() - self.drag_start) / self.scale
            self.drag_start = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = False
        elif event.button() == Qt.RightButton:
            self.drag_start = None

    def set_brush_size(self, size):
        self.brush_size = size

    def reset_mask(self):
        self.u_mask.fill(Qt.black)
        self.update()

    def reset_image(self):
        self.image.fill(Qt.white)
        self.u_mask.fill(Qt.black)
        self.scale = 1.0
        self.offset = QPoint(0, 0)
        self.update()

    def zoom_in(self):
        self.scale *= 2
        self.update()

    def zoom_out(self):
        self.scale /= 2
        self.update()

    def keyPressEvent(self, event):
        print("press")
        if event.key() == Qt.Key_B:
            self.parent.brush_slider.show()
            print("+++ show slider")
        elif event.key() == Qt.Key_C:
            self.start_crop()

    def keyReleaseEvent(self, event):
        print("release")
        if event.key() == Qt.Key_B:
            self.parent.brush_slider.hide()
            print("+++ hide slider")
        elif event.key() == Qt.Key_C:
            self.end_crop()

    def start_crop(self):
        print("+++ crop start")
        self.cropping = True
        self.crop_start = None
        self.crop_end = None

    def end_crop(self):
        print("+++ crop end")
        if self.crop_start and self.crop_end:
            x1, y1 = self.crop_start.x(), self.crop_start.y()
            x2, y2 = self.crop_end.x(), self.crop_end.y()
            x1, x2 = min(x1, x2), max(x1, x2)
            y1, y2 = min(y1, y2), max(y1, y2)
            cropped_image = self.image.copy(x1, y1, x2-x1, y2-y1)
            cropped_mask = self.u_mask.copy(x1, y1, x2-x1, y2-y1)
            self.image = cropped_image
            self.u_mask = cropped_mask
            self.update()
        self.cropping = False
        self.crop_start = None
        self.crop_end = None

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ImageMaskEditor()
    ex.show()
    sys.exit(app.exec_())