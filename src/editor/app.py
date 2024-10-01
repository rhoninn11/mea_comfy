import sys
import PyQt5
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QSlider
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen, QColor, QKeyEvent, QCursor
from PyQt5.QtCore import Qt, QPoint, QSize, QBuffer, QTimer
from PIL import Image
import numpy as np
import io

class ImageMaskEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Image Mask Editor')
        self.setGeometry(100, 100, 800, 800)

        # Main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Canvas
        self.canvas = Canvas(self)
        main_layout.addWidget(self.canvas)

        # Control buttons
        controls_layout = QHBoxLayout()

        self.btns: list[QPushButton] = []
        self.btns_fns: list[tuple] = [
            ["load image", self.load_image],
            ["save", self.save_image],
        ]

        for name, fn in self.btns_fns:
            btn = QPushButton(name)
            btn.clicked.connect(fn)
            controls_layout.addWidget(btn)

        # self.load_btn = QPushButton('Load Image')
        # self.load_btn.clicked.connect(self.load_image)
        # controls_layout.addWidget(self.load_btn)

        # self.save_btn = QPushButton('Save')
        # self.save_btn.clicked.connect(self.save_image)
        # controls_layout.addWidget(self.save_btn)

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
        self.brush_slider.setMinimum(4)
        self.brush_slider.setMaximum(256)
        self.brush_slider.setValue(16)
        self.brush_slider.valueChanged.connect(self.canvas.set_brush_size)
        self.brush_slider.hide()

        main_layout.addWidget(self.brush_slider)
        main_layout.addLayout(controls_layout)

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

    def mouseMoveEvent(self, event):
        print("mouse moved xD")

class DeltaPicker():
    def __init__(self):
        self.ref_point = QCursor.pos()

    def delta(self):
        c_now = QCursor.pos()
        delta_x = c_now.x() - self.ref_point.x()
        delta_y = c_now.y() - self.ref_point.y()
        return QPoint(delta_x, delta_y)



class Canvas(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.resize(QSize(1024, 1024))
        self.parent = parent
        self.u_image = QImage(self.size(), QImage.Format_ARGB32)
        self.u_image.fill(Qt.white)

        self.u_mask = QImage(self.size(), QImage.Format_ARGB32)
        self.u_mask.fill(Qt.black)

        self.last_point = QPoint()
        
        self.drawing = False
        self.drag_start = None
        self.scale = 0.75
        self.offset = QPoint(0, 0)

        self.ops_timer = None
        self.timer_active = False

        self.brush_picking_active = False
        self.brush_size = 5

        self.origin_picking_active = False
        self.origin = QPoint(0,0)

        self.crop_delta_picking_active = False
        self.crop_delta = QPoint(0, 0)

        self.initil_image_load()

    def initil_image_load(self):
        file_name = "fs/out_img.png"
        one_shot_fn = lambda : self.load_image(file_name)
        loaded_shot = lambda : self.one_time_detonation(one_shot_fn)
        print("+++ timer was set")
        self.timer_setup(loaded_shot, step_ms=200)


    def load_image(self, file_name):
        print("+++ load image")
        self.u_image.load(file_name)
        self.u_mask = QImage(self.u_image.size(), QImage.Format_ARGB32)
        self.u_mask.fill(Qt.black)
        self.update()

    def save_image(self, file_name):
        buffer = QBuffer()
        buffer.open(QBuffer.ReadWrite)
        self.u_mask.save(buffer, "PNG")
        combined = Image.open(io.BytesIO(buffer.data()))
        combined.save(file_name)

    def brush_picking_visualization(self, painter):
        point_a = QPoint(100,100)
        point_b = QPoint(101,100)
        painter.setPen(QPen(Qt.GlobalColor.black, self.brush_size+10, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.drawLine(point_a, point_b)
        painter.setPen(QPen(Qt.GlobalColor.white, self.brush_size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.drawLine(point_a, point_b)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.scale(self.scale, self.scale)
        painter.translate(self.offset)

        ss = self.size()
        new_w = int(ss.width() * self.scale)
        new_h = int(ss.height() * self.scale)
        u_image_scaled = self.u_image.scaled(new_w, new_h)
        
        
        painter.drawImage(0, 0, self.u_image)

        if self.brush_picking_active:
            self.brush_picking_visualization(painter)

        if self.crop_delta_picking_active:
            print("halo")
            corner_a = QPoint(self.origin.x(), self.origin.y())
            corner_b = QPoint(self.origin.x(), self.origin.y() + self.crop_delta.y())
            corner_c = QPoint(self.origin.x() + self.crop_delta.x(), self.origin.y() + self.crop_delta.y())
            corner_d = QPoint(self.origin.x() + self.crop_delta.x(), self.origin.y())
            painter.setPen(QPen(Qt.GlobalColor.black, 6, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawLine(corner_a, corner_b)
            painter.drawLine(corner_b, corner_c)
            painter.drawLine(corner_c, corner_d)
            painter.drawLine(corner_d, corner_a)
            painter.setPen(QPen(Qt.GlobalColor.white, 4, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawLine(corner_a, corner_b)
            painter.drawLine(corner_b, corner_c)
            painter.drawLine(corner_c, corner_d)
            painter.drawLine(corner_d, corner_a)

        opacity = 0.5
        painter.setOpacity(opacity)
        painter.drawImage(0, 0, self.u_mask)




    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.last_point = event.pos() / self.scale - self.offset
        elif event.button() == Qt.RightButton:
            self.drag_start = event.pos()

    def on_drawing(self, event):
        painter = QPainter(self.u_mask)
        painter.setPen(QPen(Qt.white, self.brush_size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        current_point = event.pos() / self.scale - self.offset
        painter.drawLine(self.last_point, current_point)
        self.last_point = current_point

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            if self.drawing:
                self.on_drawing(event)
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
        self.u_image.fill(Qt.white)
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

    def one_time_detonation(self, update_fn):
        update_fn()
        self.timer_cleanup()

    def timer_setup(self, update_fn, step_ms=20):
        if self.timer_active:
            return
        
        self.ops_timer = QTimer(self)
        self.ops_timer.timeout.connect(update_fn)
        self.ops_timer.start(step_ms)
        self.timer_active = True

    def timer_cleanup(self):
        if not self.timer_active:
            return 
        
        self.ops_timer.stop()
        self.ops_timer.deleteLater()
        self.ops_timer = None
        self.timer_active = False

# brush size
    def brush_size_picking_start(self):
        self.parent.brush_slider.show()
        self.timer_setup(self.brush_size_picking)
        self.picker = DeltaPicker()
        self.initial_size = self.brush_size
        self.brush_picking_active = True
    def brush_size_picking_end(self):
        self.parent.brush_slider.hide()
        self.timer_cleanup()
        self.brush_picking_active = False
    
    def brush_size_picking(self):
        new_size = self.initial_size + self.picker.delta().x()
        self.parent.brush_slider.setValue(new_size)
        self.update()
# crop
    def crop_delta_picking_start(self):
        self.timer_setup(self.crop_delta_picking)
        self.crop_delta_picking_active = True
        self.picker = DeltaPicker()
        self.update()
    def crop_delta_picking_end(self):
        self.crop_delta_picking_active = False
        self.timer_cleanup()

    def crop_delta_picking(self):
        self.crop_delta = self.picker.delta()
        self.update()

# crop origin
    def origin_picking_start(self):
        self.timer_setup(self.crop_origin_picking)
        self.origin_picking_active = True
        self.picker = DeltaPicker()
        self.origin_last = self.origin
        self.update()
    def origin_picking_end(self):
        self.origin_picking_active = False
        self.timer_cleanup()

    def crop_origin_picking(self):
        pass

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_B:
            self.brush_size_picking_start()
        elif event.key() == Qt.Key_C:
            self.crop_delta_picking_start()
        elif event.key() == Qt.Key.Key_Escape:
            self.parent.close()

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_B:
            self.brush_size_picking_end()
        elif event.key() == Qt.Key_C:
            self.crop_delta_picking_end()

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