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
        

    def get_current_widget(
        self, fwd: bool = False, back: bool = False
    ) -> BauriMicroWidget:
        if fwd:
            self.windex += 1
            self.windex = clamp_cord(self.windex, 0, self.num_widgets - 1)

        if back:
            self.windex -= 1
            self.windex = clamp_cord(self.windex, 0, self.num_widgets - 1)

        print("cwidget -> ", self.widgets[self.windex])
        return self.widgets[self.windex]

    def get_interactive_widget(
        self, fwd: bool = False, back: bool = False
    ) -> BauriMicroWidget | None:
        pass

    def action_next(self) -> None:
        cwidget = self.get_current_widget(fwd=True)
        if isinstance(cwidget, Button):
            cwidget.hover(self.canvas)

        self.flush()

    def action_prev(self) -> None:
        cwidget = self.get_current_widget(back=True)
        if isinstance(cwidget, Button):
            cwidget.hover(self.canvas)

        self.flush()

    def action_up(self) -> None:
        pass

    def action_down(self) -> None:
        pass

    def action_click(self) -> None:
        cwidget = self.get_current_widget(False)
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
