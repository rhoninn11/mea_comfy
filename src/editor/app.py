import sys
import PyQt5
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QSlider
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen, QColor, QKeyEvent, QCursor, QBrush
from PyQt5.QtCore import Qt, QPoint, QSize, QBuffer, QTimer, QRect
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
            ["save mask", self.save_image],
            ["reset mask", self.canvas.reset_mask],
            ["reset image", self.canvas.reset_image],
            ["zoom in", self.canvas.zoom_in],
            ["zoom out", self.canvas.zoom_out],
        ]

        for name, fn in self.btns_fns:
            btn = QPushButton(name)
            btn.clicked.connect(fn)
            controls_layout.addWidget(btn)
            self.btns.append(btn)

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
            self.canvas.save_mask(file_name)

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
        self.parent: ImageMaskEditor = parent
        self.u_image = QImage(self.size(), QImage.Format_RGBA8888)
        self.u_image.fill(Qt.white)
        self.u_img_crop = QImage(self.size(), QImage.Format_RGBA8888)
        self.u_img_crop.fill(Qt.white)

        self.u_mask = QImage(self.size(), QImage.Format_RGBA8888)
        self.u_mask.fill(Qt.black)
        self.u_crop_mask = QImage(self.size(), QImage.Format_RGBA8888)
        self.u_crop_mask.fill(Qt.black)

        self.last_point = QPoint()
        
        self.drawing = False
        self.drag_start = None
        self.scale = 1
        self.offset = QPoint(0, 0)

        self.ops_timer = None
        self.timer_active = False

        self.brush_picking_active = False
        self.brush_size = 5

        self.crop_origin_active = False
        self.crop_at = QPoint(0,0)

        self.crop_size_active = False
        self.crop_size = QPoint(0, 0)

        self.crop_render_pnt = QPoint(0, 0)

        self.initil_image_load()

        self.key_fns: tuple[tuple] = (
            (Qt.Key_Q, (self.brush_size_picking_start, self.brush_size_picking_end)),
            (Qt.Key_W, (self.origin_picking_start, self.origin_picking_start)),
            (Qt.Key_E, (self.crop_delta_picking_start, self.crop_delta_picking_end)),
            (Qt.Key_Escape, (self.parent.close, self.parent.close))

        ) 
    
# brush size
    def brush_size_picking_start(self):
        self.timer_setup(self.brush_size_picking)
        self.picker = DeltaPicker()
        self.initial_point = QPoint(self.brush_size, 0)
        self.brush_picking_active = True

    def brush_size_picking_end(self):
        self.timer_cleanup()
        self.brush_picking_active = False
        self.update()
    
    def brush_size_picking(self):
        delta_point = self.initial_point + self.picker.delta()
        self.parent.brush_slider.setValue(delta_point.x())
        self.update()
# crop
    def crop_delta_picking_start(self):
        self.timer_setup(self.crop_delta_picking)
        self.crop_size_active = True
        self.picker = DeltaPicker()
        self.initial_point = self.crop_size
        self.update()

    def crop_delta_picking_end(self):
        self.crop_size_active = False
        self.timer_cleanup()
        self.update()

    def crop_delta_picking(self):
        delta_point = self.initial_point + self.picker.delta()
        self.crop_size = delta_point
        self.update()

# crop origin
    def origin_picking_start(self):
        self.timer_setup(self.crop_origin_picking)
        self.crop_origin_active = True
        self.picker = DeltaPicker()
        self.origin_last = self.crop_at
        self.update()

    def origin_picking_end(self):
        self.crop_origin_active = False
        self.timer_cleanup()
        self.update()

    def crop_origin_picking(self):
        delta_point = self.origin_last + self.picker.delta()
        self.crop_at = delta_point
        self.update()

# 

    def initil_image_load(self):
        file_name = "fs/out_img.png"
        one_shot_fn = lambda : self.load_image(file_name)
        loaded_shot = lambda : self.one_time_detonation(one_shot_fn)
        self.timer_setup(loaded_shot, step_ms=200)

    def load_image(self, file_name):
        print("+++ load image")
        self.u_image.load(file_name)
        size = self.u_image.size()

        crop_rect = (int(0), int(0), size.width(), size.height())
        self.crop_render_pnt = QPoint(0, 0)
        self.u_img_crop = self.u_image.copy(*crop_rect)

        self.u_mask = QImage(self.u_image.size(), QImage.Format_RGBA8888)
        self.u_mask.fill(Qt.black)
        self.update()

    def save_mask(self, file_name):
        buffer = QBuffer()
        buffer.open(QBuffer.ReadWrite)

        final_mask = self.render_final_mask()
        final_mask.save(buffer, "PNG")
        combined = Image.open(io.BytesIO(buffer.data()))
        combined.save(file_name)

    def draw_brush_size(self, painter: QPainter):
        pen_attr = (Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        out_pen = QPen(Qt.black, self.brush_size+10, *pen_attr)
        in_pen = QPen(Qt.white, self.brush_size, *pen_attr)

        position = QPoint(100, 100)

        painter.setPen(out_pen)
        painter.drawPoint(position)
        painter.setPen(in_pen)
        painter.drawPoint(position)

    def draw_crop_origin(self, painter: QPainter):
        pen_attr = (Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        out_pen = QPen(Qt.black, 15, *pen_attr)
        in_pen = QPen(Qt.white, 10, *pen_attr)

        painter.setPen(out_pen)
        painter.drawPoint(self.crop_at)
        painter.setPen(in_pen)
        painter.drawPoint(self.crop_at)

    def draw_crop_frame(self, painter: QPainter):
        pen_attr = (Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        out_pen = QPen(Qt.black, 10, *pen_attr)
        in_pen = QPen(Qt.white, 5, *pen_attr)

        pos = (self.crop_at.x(), self.crop_at.y())
        size = (self.crop_size.x(), self.crop_size.y())

        painter.setPen(out_pen)
        painter.drawRect(*pos, *size)

        painter.setPen(in_pen)
        painter.drawRect(*pos, *size)

    def render_final_mask(self):

        in_brush = QBrush(Qt.black, Qt.SolidPattern)

        self.u_crop_mask.fill(Qt.white)
        painter = QPainter(self.u_crop_mask)
        pos = (self.crop_render_pnt.x(), self.crop_render_pnt.y())
        size = (self.crop_size.x(), self.crop_size.y())

        painter.setBrush(in_brush)
        painter.drawRect(*pos, *size)

        np_mask_buffer_a = self.qt_to_np_img(self.u_mask).astype(np.int16)
        np_mask_buffer_b = self.qt_to_np_img(self.u_crop_mask).astype(np.int16)

        final_mask = np.clip(np_mask_buffer_a + np_mask_buffer_b, 0, 255).astype(np.uint8)
        return self.np_to_qt_img(final_mask)

    def qt_to_np_img(self, qt_img: QImage) -> np.ndarray:
        width = qt_img.width()
        height = qt_img.height()
        buffer = qt_img.constBits().asarray(height * width * 4)
        return np.frombuffer(buffer, dtype=np.uint8).reshape((height, width, 4))
    
    def np_to_qt_img(self, np_img: np.ndarray) -> QImage:
        height, width, _ = np_img.shape
        qt_img = QImage(np_img.data, width, height, QImage.Format_RGBA8888)
        qt_img.detach()
        return qt_img

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.scale(self.scale, self.scale)
        painter.translate(self.offset)

        pos = (self.crop_render_pnt.x(), self.crop_render_pnt.y())
        print(pos)
        painter.drawImage(*pos, self.u_img_crop)

        if self.brush_picking_active:
            self.draw_brush_size(painter)

        if self.crop_origin_active:
            self.draw_crop_origin(painter)

        if self.crop_size_active:
            self.draw_crop_frame(painter)


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

    def keyPressEvent(self, event):
        
        if event.key() == Qt.Key_Q:
            self.brush_size_picking_start()
        elif event.key() == Qt.Key_W:
            self.origin_picking_start()
        elif event.key() == Qt.Key_E:
            self.crop_delta_picking_start()
        elif event.key() == Qt.Key_R:
            self.crop_ops()
        elif event.key() == Qt.Key.Key_Escape:
            self.parent.close()

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Q:
            self.brush_size_picking_end()
        elif event.key() == Qt.Key_W:
            self.origin_picking_end()
        elif event.key() == Qt.Key_E:
            self.crop_delta_picking_end()

    def crop_ops(self):
        self.crop_render_pnt = self.crop_at
        pnt = self.crop_at
        sz = self.crop_size
        crop_rect = (pnt.x(), pnt.y(), sz.x(), sz.y())
        self.u_img_crop = self.u_image.copy(*crop_rect)
        self.update()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ImageMaskEditor()
    ex.show()
    sys.exit(app.exec_())