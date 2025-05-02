from baurimicrogui.widgets import BauriMicroWidget
from baurimicrogui.widgets.label import Label
from baurimicrogui.canvas import BauriMicroCanvas
from baurimicrogui.utils import Offset
from baurimicrogui.colors import COLOR_WHITE

try:
    from typing import Callable, Optional
except ImportError:
    pass


class Button(BauriMicroWidget):
    canvas: BauriMicroCanvas | None = None
    first_draw: bool = True
    wtype = "button"
    label: Label
    has_on_click = True
    on_click_callback: Optional[Callable[[], None]]

    def __init__(
        self,
        text: str,
        pos_x: int,
        pos_y: int,
        color: int,
        bg_color: int,
        border_color: int | None = None,
        on_click_callback=None,
        padding: Offset | None = None,
        overflow: bool = False,
        max_width: int = -1,
        max_height: int = -1,
        transparent: bool = False,
        hover_thickness: int = 1,
        hover_color: int = COLOR_WHITE,
    ) -> None:

        self.pos_x = pos_x
        self.pos_y = pos_y
        if on_click_callback is not None:
            self.on_click_callback = on_click_callback
        else:
            self.on_click_callback = None

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
        self.is_interactive = True
        self.hover_thickness = hover_thickness
        self.hover_color = hover_color
        self.label._calc_size()
        self.sync_w_h()

    def __str__(self) -> str:
        return "Button[Text={}|Size={},{}]".format(
            self.label.text, self.label.rect_width, self.label.rect_height
        )

    def sync_w_h(self) -> None:
        self.width = self.label.width
        self.height = self.label.height

    def set_text(self, text: str) -> None:
        self.label.set_text(text)
        self.sync_w_h()

    def get_calc_size(self) -> tuple[int, int]:
        w, h = self.label.get_calc_size()
        self.sync_w_h()
        return w, h

    def on_click(self) -> None:
        if self.on_click_callback is not None:
            self.on_click_callback()

    def hover(self, enable: bool = True) -> None:
        return super().hover(enable)

    def draw_hover(self, canvas: BauriMicroCanvas) -> None:
        rect_width, rect_height = self.label.get_calc_size()
        canvas.draw_rect(
            self.label.pos_x,
            self.label.pos_y,
            rect_width,
            rect_height,
            thickness=self.hover_thickness,
            color=self.hover_color,
        )

        # TODO: Better Solution?

    def draw(self, canvas: BauriMicroCanvas) -> None:
        self.first_draw = False
        self.label.draw(canvas)

        if self.enable_hover:
            self.draw_hover(canvas)
