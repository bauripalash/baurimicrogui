from baurimicrogui.canvas import BauriMicroCanvas
from baurimicrogui.colors import *
from baurimicrogui.utils import clamp_cord
from baurimicrogui.widgets import BauriMicroWidget
from baurimicrogui.drivers.display import BauriMicroDispDriver
from baurimicrogui.widgets.button import Button

import gc


class BauriMicroGUI:
    canvas: BauriMicroCanvas
    screen_width: int
    screen_height: int
    widgets: list[BauriMicroWidget]
    flip_endianness: bool = False
    flush_color: int = COLOR_BLACK
    num_widgets: int = 0
    loop_navigation: bool = False

    def __init__(
        self,
        driver: BauriMicroDispDriver,
        width: int,
        height: int,
        rotation: int = 0x0,
        colormode: int = 0x0,
    ) -> None:
        self.screen_width = width
        self.screen_height = height
        self.canvas = BauriMicroCanvas(
            driver, width, height, rotation, colormode
        )
        gc.enable()
        gc.collect()

        self.widgets = []
        self.windex = -1

    def cur_widget(self) -> BauriMicroWidget:
        return self.widgets[self.windex]

    def navigate_widgets(self, forward: bool = True) -> None:
        if self.num_widgets == 0:
            return
        direction = 1 if forward else -1
        n = self.windex + direction

        if self.loop_navigation:
            n %= self.num_widgets
            while not n == self.num_widgets:
                if self.widgets[n].is_interactive:
                    self.windex = n
                    break
                n = (n + direction) % self.num_widgets

        else:
            while 0 <= n < self.num_widgets:
                if self.widgets[n].is_interactive:
                    self.windex = n
                    break
                n += direction

    def action_next(self) -> None:
        self.set_hover(self.cur_widget(), False)
        self.navigate_widgets(True)
        self.set_hover(self.cur_widget(), True)
        self.flush()

    def set_hover(self, widget: BauriMicroWidget, enable: bool) -> None:
        if isinstance(widget, Button):
            widget.hover(enable)

    def action_prev(self) -> None:
        self.set_hover(self.cur_widget(), False)
        self.navigate_widgets(False)
        self.set_hover(self.cur_widget(), True)
        self.flush()

    def action_up(self) -> None:
        pass

    def action_down(self) -> None:
        pass

    def action_click(self) -> None:
        cwidget = self.cur_widget()
        if isinstance(cwidget, Button):
            if cwidget.on_click is not None:
                cwidget.on_click()

        self.flush()

    def bg(self, color: int) -> None:
        self.canvas.fill_display(color)

    def add_widget(self, widget) -> None:
        self.num_widgets += 1
        self.widgets.append(widget)

    def flush(self) -> None:

        self.canvas.fill_display(self.flush_color)

        for widget in self.widgets:
            widget.draw(self.canvas)

        self.canvas.show()
