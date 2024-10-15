from typing import Callable
from PyQt5.QtCore import QPoint, QTimer
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QWidget


class delta_picker():
    def __init__(self):
        self.ref_point = QCursor.pos()

    def delta(self):
        c_now = QCursor.pos()
        delta_x = c_now.x() - self.ref_point.x()
        delta_y = c_now.y() - self.ref_point.y()
        return QPoint(delta_x, delta_y)


class update_timer():
    def __init__(self, widget: QWidget):
        self.ops_timer = None
        self.in_edit = False
        self.widget_ref = widget

    def timer_setup(self, update_fn, step_ms=20):
        if self.in_edit:
            return

        self.ops_timer = QTimer(self.widget_ref)
        self.ops_timer.timeout.connect(update_fn)
        self.ops_timer.start(step_ms)
        self.in_edit = True

    def timer_cleanup(self):
        if not self.in_edit:
            return

        self.ops_timer.stop()
        self.ops_timer.deleteLater()
        self.ops_timer = None
        self.in_edit = False

    def one_time_detonation(self, update_fn):
        update_fn()
        self.timer_cleanup()


class rt_edit_organizer():
    def __init__(self, widget: QWidget):

        self.widget_ref = widget
        self.edit_interval = update_timer(self.widget_ref)
        self.edit_mode_exit()

        self.edit_starts = []
        self.edit_ends = []


    def edit_mode_enter(self):
        self.edit_mode = True

    def edit_mode_exit(self):
        self.edit_mode = False


class edit_action():
    def __init__(self, editor: rt_edit_organizer, to_update: QWidget):
        self.editor_ref = editor
        self.initial_point = QPoint(0,0)
        self.active = False
        self.to_update = to_update

        self.bind_signals(lambda: QPoint(0,0), lambda point: print(point))

    def bind_signals(self, init_fn: Callable[[], QPoint], edit_fn: Callable[[QPoint], None]):
        self.init_sample = init_fn
        self.edit_sample = edit_fn

    def edit_start(self):
        e = self.editor_ref
        if e.edit_mode:
            return

        e.edit_mode_enter()
        e.edit_interval.timer_setup(self.edit_update)
        self.picker = delta_picker()
        self.initial_point = self.init_sample()
        self.active = True

        self.to_update.update()

    def edit_end(self):
        e = self.editor_ref
        if not e.edit_mode:
            return

        e.edit_mode_exit()
        e.edit_interval.timer_cleanup()
        self.active = False

        self.to_update.update()

    def edit_update(self):
        delta_point = self.initial_point + self.picker.delta()
        self.edit_sample(delta_point)
        self.to_update.update()