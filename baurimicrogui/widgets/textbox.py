import gc
from baurimicrogui import utils
from baurimicrogui.colors import COLOR_GREEN, COLOR_RED, COLOR_WHITE
from baurimicrogui.widgets import BauriMicroWidget
from baurimicrogui.canvas import BauriMicroCanvas
from baurimicrogui.utils import Offset, get_text_size

DEFAULT_HEIGHT = 50
DEFAULT_WIDTH = 60
DEFAULT_SCROLL_BG = COLOR_GREEN
DEFAULT_SCROLL_COLOR = COLOR_RED
DEFAULT_SCROLLBAR_WIDTH = 6


class Textbox(BauriMicroWidget):
    lines: list[str]
    num_lines: int
    height: int
    width: int
    canvas: BauriMicroCanvas | None

    color: int  # Text Color
    bg: int | None  # Background Color. None for Transparent
    border_color: int

    first_draw: bool
    wtype: str
    is_interactive: bool

    def setup(
        self,
        pos_x: int,
        pos_y: int,
        color: int,
        bg: int | None,
        border: int | None = None,
        padding: Offset | None = None,
        width: int | None = None,
        height: int | None = None,
        scroll: bool = False,
        scroll_bg: int | None = None,
        scroll_color: int | None = None,
        scroll_width: int = DEFAULT_SCROLLBAR_WIDTH,
        hover_color: int = COLOR_WHITE,
        char_height: int = 8,
        char_width: int = 8,
    ) -> bool:
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.color = color
        self.bg = bg
        self.padding = padding
        self.scroll = scroll

        if border is not None:
            self.border_color = border
        else:
            if bg is not None:
                self.border_color = bg
            else:
                self.border_color = self.color

        self.lines = []
        self.num_lines = 0
        self.canvas = None
        self.first_draw = True
        self.wtype = "textbox"
        self.is_interactive = True

        self.width = width if width is not None else DEFAULT_WIDTH
        self.height = height if height is not None else DEFAULT_HEIGHT

        self.hover_color = hover_color

        self.text_pos_x = self.pos_x
        self.text_width = self.width
        self.text_pos_y = self.pos_y
        self.text_height = self.height

        if padding is not None:
            self.text_pos_x += padding.left
            self.text_width -= padding.left + padding.right
            self.text_pos_y += padding.top
            self.text_height -= padding.top + padding.right

        if scroll:
            self.scroll_bg = (
                scroll_bg if scroll_bg is not None else DEFAULT_SCROLL_BG
            )
            self.scroll_color = (
                scroll_color
                if scroll_color is not None
                else DEFAULT_SCROLL_COLOR
            )
            self.scroll_width = scroll_width
            self.text_width -= scroll_width

        self.char_width = char_width
        self.line_height = char_height  # change later
        self.visible_lines = self.text_height // self.line_height
        self.scroll_offset = 0
        self.has_on_up = True
        self.hash_on_down = True

        gc.collect()

        return True

    def generate_wrapped_lines(self) -> None:
        self.max_chars = (self.text_width - self.text_pos_x) // self.char_width
        self.lines = utils.wrap_list_by_maxchar(self.lines, self.max_chars)

    def clear_lines(self) -> None:
        self.lines = []

    def print(self, str: str, nonewline: bool = False) -> None:
        if nonewline and self.num_lines > 0:
            self.lines[self.num_lines - 1] += str
        else:
            self.lines.append(str)
            self.num_lines += 1

        self.generate_wrapped_lines()

    def hover(self, enable: bool = True) -> None:
        return super().hover(enable)

    def draw_hover(self, canvas: BauriMicroCanvas) -> None:
        canvas.draw_rect(
            self.pos_x,
            self.pos_y,
            self.width,
            self.height,
            color=self.hover_color,
            fill=False,
        )

    def scroll_down(self) -> None:
        if self.scroll_offset + self.visible_lines < len(self.lines):
            self.scroll_offset += 1

    def scroll_up(self) -> None:
        if self.scroll_offset > 0:
            self.scroll_offset -= 1

    def on_up(self) -> None:
        self.scroll_up()

    def on_down(self) -> None:
        self.scroll_down()

    def draw_lines(self, canvas: BauriMicroCanvas) -> None:
        total_lines = len(self.lines)
        for i in range(self.visible_lines):
            lid = self.scroll_offset + i
            if lid < total_lines:
                line = self.lines[lid]
                canvas.draw_text(
                    line,
                    self.text_pos_x,
                    self.text_pos_y + i * self.line_height,
                    self.color,
                )
            else:
                break

    def draw_scrollbar(self, canvas: BauriMicroCanvas) -> None:
        sbar_width = self.scroll_width
        sbar_x = self.pos_x + self.width - sbar_width
        sbar_y = self.pos_y
        sbar_height = self.height

        canvas.draw_rect(
            sbar_x, sbar_y, sbar_width, sbar_height, self.scroll_bg, fill=True
        )

        total_lines = len(self.lines)
        if total_lines > self.visible_lines:
            ctrl_height = int(sbar_height * self.visible_lines / total_lines)
            if ctrl_height < 5:
                ctrl_height = 5

            max_scroll = total_lines - self.visible_lines
            scroll_ratio = self.scroll_offset / max_scroll
            ctrl_y = sbar_y + int(scroll_ratio * (sbar_height - ctrl_height))
            canvas.draw_rect(
                sbar_x,
                ctrl_y,
                sbar_width,
                ctrl_height,
                self.scroll_color,
                fill=True,
            )

    def draw(self, canvas: BauriMicroCanvas) -> None:
        self.canvas = canvas
        self.first_draw = False

        canvas.draw_rect(
            self.pos_x,
            self.pos_y,
            self.width,
            self.height,
            color=self.color,
            fill=self.bg is not None,
            fill_color=self.bg,
        )

        self.draw_lines(canvas)

        if self.scroll:
            self.draw_scrollbar(canvas)

        canvas.draw_rect(
            self.pos_x,
            self.pos_y,
            self.width,
            self.height,
            self.border_color,
            fill=False,
        )

        if self.enable_hover:
            self.draw_hover(canvas)
