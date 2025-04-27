from baurimicrogui.widgets import BauriMicroWidget
from baurimicrogui.widgets.label import Label
from baurimicrogui.canvas import BauriMicroCanvas
from baurimicrogui.utils import *
from baurimicrogui.colors import *


class Button(BauriMicroWidget):
    canvas: BauriMicroCanvas | None = None
    first_draw: bool = True
    is_interactive = True
    wtype = "button"
    label: Label

    def __init__(
        self,
        text: str,
        pos_x: int,
        pos_y: int,
        color: int,
        bg_color: int,
        border_color: int | None = None,
        on_click=None,
        padding: Offset | None = None,
        overflow: bool = False,
        max_width: int = -1,
        max_height: int = -1,
        transparent: bool = False,
    ) -> None:

        if on_click is not None:
            self.on_click = on_click
        else:
            self.on_click = None

        self.label = Label(
            text,
            pos_x,
            pos_y,
            color,
            bg_color,
            border_color,
            padding,
            overflow,
            max_width,
            max_height,
            transparent,
        )
        self.label._calc_size()

    def set_text(self, text: str) -> None:
        self.label.set_text(text)

    def hover(self, canvas: BauriMicroCanvas) -> None:
        rect_width, rect_height = self.label.get_calc_size()
        canvas.draw_rect(
            self.label.pos_x,
            self.label.pos_y,
            rect_width,
            rect_height,
            thickness=2,
            color=COLOR_WHITE,
        )

        # TODO: Better Solution?
        canvas.show(True)

    def get_calc_size(self) -> tuple[int, int]:
        return self.label.get_calc_size()

    def draw(self, canvas: BauriMicroCanvas) -> None:
        self.first_draw = False
        self.label.draw(canvas)
