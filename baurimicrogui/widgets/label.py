from baurimicrogui.widgets import BauriMicroWidget
from baurimicrogui.canvas import BauriMicroCanvas
from baurimicrogui.utils import *
from baurimicrogui.colors import *


class Label(BauriMicroWidget):
    text: str = ""
    canvas: BauriMicroCanvas | None = None
    rect_width: int = 0
    rect_height: int = 0
    text_width: int = 0
    text_height: int = 0
    need_size_refresh: bool = True
    first_draw: bool = True
    wtype = "label"
    is_interactive = False

    def __init__(
        self,
        text: str,
        pos_x: int,
        pos_y: int,
        color: int,
        bg_color: int,
        border_color: int | None = None,
        padding: Offset | None = None,
        overflow: bool = False,
        max_width: int = -1,
        max_height: int = -1,
        transparent: bool = False,
    ) -> None:
        self.text = text
        self.pos_x = pos_x
        self.pos_y = pos_y

        self.color = color
        self.bg = bg_color
        self.transparent = transparent

        self.overflow = overflow

        if max_width < 0:
            self.max_width = None
        else:
            self.max_width = max_width

        if max_height < 0:
            self.max_height = None
        else:
            self.max_height = max_height

        self.padding = padding

        if border_color is not None:
            self.border_color = border_color
        else:
            self.border_color = self.bg

    def __str__(self) -> str:
        return "Label[Text={}|Size={},{}]".format(self.text, self.rect_width,self.rect_height)

    def set_text(self, text: str) -> None:
        self.text = text
        self.need_size_refresh = True

    def _calc_size(self, char_width: int = 8, char_height: int = 8) -> None:
        """update (rect_width, rect_height, text_width, text_height)"""
        prelim_text_w = len(self.text) * char_width

        if self.padding:
            prelim_text_w += self.padding.left + self.padding.right

        rect_width = min(
            prelim_text_w,
            self.max_width if self.max_width is not None else prelim_text_w + 1,
        )

        text_width = rect_width

        if self.padding:
            text_width -= self.padding.left + self.padding.right

        text_size = get_text_size(
            self.text, wrap=True, wrap_chars=text_width // char_width
        )
        text_width = text_size[0]
        text_height = text_size[1]

        if self.padding:
            text_height += self.padding.top + self.padding.bottom

        rect_height = min(
            text_height,
            self.max_height if self.max_height is not None else text_height + 1,
        )

        self.rect_width = rect_width
        self.rect_height = rect_height
        self.text_width = text_width
        self.text_height = text_height

        self.need_size_refresh = False

    def get_calc_size(self) -> tuple[int, int]:
        if self.need_size_refresh:
            self._calc_size()

        return (self.rect_width, self.rect_height)

    def draw(self, canvas: BauriMicroCanvas) -> None:
        self._calc_size()
        self.first_draw = False

        canvas.draw_rect(
            self.pos_x,
            self.pos_y,
            self.rect_width,
            self.rect_height,
            color=self.border_color,
            fill=not self.transparent,
            fill_color=self.bg,
        )

        text_px = self.pos_x
        text_py = self.pos_y

        if self.padding:
            text_px += self.padding.left
            text_py += self.padding.top

        canvas.draw_text(
            self.text,
            text_px,
            text_py,
            self.color,
            wrap=True,
            wrap_chars=self.text_width // canvas.char_width,
        )
