import sys
import PyQt5
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QSlider
from PyQt5.QtWidgets import QStackedLayout, QStackedWidget
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen, QColor, QKeyEvent, QBrush
from PyQt5.QtCore import Qt, QPoint, QSize, QBuffer
from PIL import Image
import numpy as np
import io

from typing import Callable

from editor.org_vol_1 import edit_action, rt_edit_organizer
from editor.org_vol_1 import update_timer
from editor.utils_img import IMG_FORMAT, np_to_qt_img, qt_to_np_img
from src.utils import proj_asset

class q_test_stack(QStackedWidget):

    def swipe(self):
        idx = self.currentIndex()
        max_idx = self.count() - 1
        idx += 1
        if idx > max_idx:
            idx = 0
    
        self.setCurrentIndex(idx)

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

        second_on_stack = QWidget()
        test_btn = QPushButton(second_on_stack)

        # Canvas
        self.stack = q_test_stack()
        main_layout.addWidget(self.stack)

        self.canvas = Canvas(self, self.stack.swipe)
        self.stack.addWidget(self.canvas)
        self.stack.addWidget(second_on_stack)
        

        # Control buttons
        controls_layout = QHBoxLayout()

        self.btns: list[QPushButton] = []
        self.btns_fns: list[tuple] = [
            ["load image", self.load_image],
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


        main_layout.addLayout(controls_layout)

    def load_image(self):
        file_name = proj_asset("img_in.png")
        self.canvas.load_image(file_name)

    def save_image(self):
        file_name = proj_asset("mask.png")
        self.canvas.save_mask(file_name)

    def keyPressEvent(self, event: QKeyEvent):
        if event.isAutoRepeat():
            return
        self.canvas.keyPressEvent(event)
        event.accept()

    def keyReleaseEvent(self, event: QKeyEvent):
        if event.isAutoRepeat():
            return
        self.canvas.keyReleaseEvent(event)
        event.accept()

class PropertySpawner():
    def __init__(self, editor: rt_edit_organizer):
        self.editor_ref = editor

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def add_edit_action(self, 
                          init_fn: Callable[..., QPoint], 
                          edit_fn: Callable[[QPoint], None]) -> edit_action:
        args = [self.editor_ref, self.editor_ref.widget_ref]
        prop = edit_action(*args)
        prop.bind_signals(init_fn, edit_fn)

        self.editor_ref.edit_starts.append(prop.edit_start)
        self.editor_ref.edit_ends.append(prop.edit_end)
        return prop


class Canvas(QWidget):
    def __init__(self, parent, fn):
        super().__init__(parent)

        self.resize(QSize(1024, 1024))
        self.parent: ImageMaskEditor = parent
        self.u_image = QImage(self.size(), IMG_FORMAT)
        self.u_image.fill(Qt.white)
        self.u_img_crop = QImage(self.size(), IMG_FORMAT)
        self.u_img_crop.fill(Qt.white)
        self.u_img_scaled = QImage(self.size(), IMG_FORMAT)
        self.u_img_scaled.fill(Qt.white)

        self.u_img_out = QImage(self.size(), IMG_FORMAT)
        self.u_img_out.fill(Qt.black)

        self.u_mask = QImage(self.size(), IMG_FORMAT)
        self.u_mask.fill(Qt.transparent)
        self.u_crop_mask = QImage(self.size(), IMG_FORMAT)
        self.u_crop_mask.fill(Qt.transparent)

        self.last_point = QPoint()
        self.fn_ref = fn
        
        self.drawing = False
        self.drag_start = None
        self.scale = 0.5
        self.offset = QPoint(0, 0)

        self.scales = [2, 1.5, 1, 0.75, 0.5, 0.33, 0.25]
        self.scale_proxy = 100
        self.img_scale = self.select_img_scale()
        

        self.ops_timer = update_timer(self)

        self.crop_render_pnt = QPoint(0, 0)

        self.initial_img_load()

        self.brush_size = 5
        self.crop_at = QPoint(0,0)
        self.crop_size = QPoint(0, 0)
        self.editor_init()

        self.key_fns: list[tuple] = [
            (Qt.Key_A, (self.crop_ops, lambda: None)),
            (Qt.Key_Escape, (self.parent.close, self.parent.close)),
            (Qt.Key_Plus, (self.fn_ref, lambda: None)),
        ]
        
        edit_keys = [Qt.Key_Q, Qt.Key_W, Qt.Key_E, Qt.Key_R, Qt.Key_T]
        for key, fns in zip(edit_keys, zip(self.editor.edit_starts, self.editor.edit_ends)):
            self.key_fns.append((key, fns))
        
        
    def brush_size_init(self) -> QPoint:
        return QPoint(self.brush_size, 0)
    def brush_size_edit(self, value: QPoint):
        self.brush_size = value.x()

    def crop_at_init(self) -> QPoint:
        return self.crop_at
    def crop_at_edit(self, value: QPoint):
        self.crop_at = value

    def crop_size_init(self) -> QPoint:
        return self.crop_size
    def crop_size_edit(self, value: QPoint):
        self.crop_size = value

    def scale_proxy_init(self) -> QPoint:
        return QPoint(self.scale_proxy, 0)
    def scale_proxy_edit(self, value: QPoint):
        self.scale_proxy = value.x()
        self.img_scale = self.select_img_scale()

    def select_img_scale(self):
        for scale in self.scales:
            if self.scale_proxy >= scale * 100:
                return scale
            
        return self.scales[-1]

    def editor_init(self):
        self.editor = rt_edit_organizer(self)
        with PropertySpawner(self.editor) as fab:
            self.brush_size_prop = fab.add_edit_action(self.brush_size_init, self.brush_size_edit)
            self.crop_at_prop = fab.add_edit_action(self.crop_at_init, self.crop_at_edit)
            self.crop_size_prop = fab.add_edit_action(self.crop_size_init, self.crop_size_edit)
            self.scale_proxy_prop = fab.add_edit_action(self.scale_proxy_init, self.scale_proxy_edit)


    def initial_img_load(self):
        t = self.ops_timer
        file_name = proj_asset("img.png")
        one_shot_fn = lambda : self.load_image(file_name)
        loaded_shot = lambda : t.one_time_detonation(one_shot_fn)
        t.timer_setup(loaded_shot, step_ms=200)

    def load_image(self, file_name):
        print("+++ load image")
        self.u_image.load(file_name)
        size = self.u_image.size()

        crop_rect = (int(0), int(0), size.width(), size.height())
        self.crop_render_pnt = QPoint(0, 0)
        self.u_img_crop = self.u_image.copy(*crop_rect)

        self.u_mask = QImage(self.u_image.size(), IMG_FORMAT)
        self.reset_mask()
        self.update()

    def save_mask(self, file_name):
        buffer = QBuffer()
        buffer.open(QBuffer.ReadWrite)

        final_mask = self.render_final_mask()
        final_mask.save(buffer, "PNG")
        pil_img = Image.open(io.BytesIO(buffer.data()))
        pil_img.save(file_name)

    def save_image(self, file_name):
        buffer = QBuffer()
        buffer.open(QBuffer.ReadWrite)

        final_img = self.render_final_image()
        final_img.save(buffer, "PNG")
        pil_img = Image.open(io.BytesIO(buffer.data()))
        pil_img.save(file_name)

    def outline_pens(self, smaller_size, bigger_size):
        pen_attr = (Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        out_pen = QPen(Qt.black, bigger_size, *pen_attr)
        in_pen = QPen(Qt.white, smaller_size, *pen_attr)
        return out_pen, in_pen
    
    def draw_w_outline(self, pens, painter: QPainter, fn):
        for pen in pens:
            painter.setPen(pen)
            fn()


    def draw_brush_size(self, painter: QPainter):
        position = QPoint(100, 100)
        pens = self.outline_pens(self.brush_size, self.brush_size+10)
        draw_fn = lambda: painter.drawPoint(position)
        self.draw_w_outline(pens, painter, draw_fn)

    def draw_crop_origin(self, painter: QPainter):
        pens = self.outline_pens(10, 15)
        draw_fn = lambda: painter.drawPoint(self.crop_at)
        self.draw_w_outline(pens, painter, draw_fn)

    def draw_crop_frame(self, painter: QPainter):
        pos = (self.crop_at.x(), self.crop_at.y())
        size = (self.crop_size.x(), self.crop_size.y())
        
        pens = self.outline_pens(5, 10)
        draw_fn = lambda: painter.drawRect(*pos, *size)
        self.draw_w_outline(pens, painter, draw_fn)

    def render_final_mask(self):
        in_brush = QBrush(Qt.black, Qt.SolidPattern)

        self.u_crop_mask.fill(Qt.white)
        painter = QPainter(self.u_crop_mask)

        blend_frame = 25
        x = self.crop_render_pnt.x() + blend_frame
        y = self.crop_render_pnt.y() + blend_frame

        img = self.u_img_scaled
        w = img.size().width() - 2*blend_frame
        h = img.size().height() - 2*blend_frame

        painter.setBrush(in_brush)
        painter.drawRect(x, y, w, h)

        np_mask_buffer_a = qt_to_np_img(self.u_mask).astype(np.int16)
        np_mask_buffer_b = qt_to_np_img(self.u_crop_mask).astype(np.int16)

        final_mask = np.clip(np_mask_buffer_a + np_mask_buffer_b, 0, 255).astype(np.uint8)
        return np_to_qt_img(final_mask)
    
    def render_final_image(self):
        self.u_img_out.fill(Qt.black)
        painter = QPainter(self.u_img_out)

        img = self.u_img_scaled
        pos = (self.crop_render_pnt.x(), self.crop_render_pnt.y())

        painter.drawImage(*pos, img)
        return self.u_img_out

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.scale(self.scale, self.scale)
        painter.translate(self.offset)

        x = self.crop_render_pnt.x()
        y = self.crop_render_pnt.y()
        pos = (x, y)

        self.img_scale_ops()
        painter.drawImage( x,y, self.u_img_scaled)

        if self.brush_size_prop.active:
            self.draw_brush_size(painter)

        if self.crop_at_prop.active:
            self.draw_crop_origin(painter)

        if self.crop_size_prop.active:
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
        self.u_mask.fill(Qt.transparent)
        self.update()

    def reset_image(self):
        self.u_image.fill(Qt.white)
        self.reset_mask()
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
        pressed_key = event.key() 
        for key, fns in self.key_fns:
            if pressed_key == key:
                fns[0]()

    def keyReleaseEvent(self, event):
        released_key = event.key() 
        for key, fns in self.key_fns:
            if released_key == key:
                fns[1]()

    def img_scale_ops(self):
        orig_size = self.u_image.size()
        scale = self.select_img_scale()
        new_size = (int(orig_size.width()*scale), int(orig_size.height()*scale))
        self.u_img_scaled = self.u_image.scaled(*new_size)

    def crop_ops(self):
        self.crop_render_pnt = self.crop_at
        pnt = self.crop_at
        sz = self.crop_size
        crop_rect = (pnt.x(), pnt.y(), sz.x(), sz.y())
        self.u_img_crop = self.u_image.copy(*crop_rect)
        self.save_mask("fs/mask.png")
        self.save_image("fs/img.png")
        self.update()

def main():
    app = QApplication(sys.argv)
    ex = ImageMaskEditor()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
   main()