from baurimicrogui.drivers.display import BauriMicroDispDriver
from baurimicrogui.utils import *
import framebuf


class BauriMicroCanvas:
    driver: BauriMicroDispDriver
    width: int
    height: int
    fb_mode: int
    raw_buf: bytearray
    buf: framebuf.FrameBuffer
    rotation: int
    colormode: int
    char_width: int
    char_height: int

    EL_TOP_RIGHT = const(0x1)
    EL_TOP_LEFT = const(0x2)
    EL_BOTTOM_RIGHT = const(0x8)
    EL_BOTTOM_LEFT = const(0x4)
    EL_FULL = const(0xF)

    def __init__(
        self,
        driver: BauriMicroDispDriver,
        width: int,
        height: int,
        rotation: int,
        colormode: int,
    ) -> None:
        self.driver = driver
        self.width = width
        self.height = height
        self.rotation = rotation
        self.colormode = colormode

        self.raw_buf = bytearray(self.width * self.height * 2)
        self.fb_mode = framebuf.RGB565
        self.buf = framebuf.FrameBuffer(
            self.raw_buf, self.width, self.height, self.fb_mode
        )
        self.mv = memoryview(self.raw_buf)

        self.char_width = 8
        self.char_height = 8

        self.driver.boot_display()

    def color(self, r: int, g: int, b: int) -> int:
        return ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)

    def fill_display(self, color: int) -> None:
        self.buf.fill(color)

    def pixel(self, pos_x: int, pos_y: int, color: int) -> None:
        self.buf.pixel(pos_x, pos_y, color)

    def get_pixel(self, pos_x: int, pos_y: int) -> int:
        return self.buf.pixel(pos_x, pos_y)

    def draw_rect(
        self,
        pos_x: int,
        pos_y: int,
        width: int,
        height: int,
        color: int,
        thickness: int = 1,
        fill: bool = False,
        fill_color: int | None = None,
        clamp: bool = False,
    ) -> None:
        x = pos_x
        y = pos_y
        w = width
        h = height

        if clamp:
            x = clamp_cord(x, 0, self.width)
            y = clamp_cord(y, 0, self.height)

            if width + x > self.width:
                w = self.width - x

            if height + y > self.height:
                h = self.height - y

        if fill:
            fill_col = color
            if fill_color is not None:
                fill_col = fill_color
            self.buf.fill_rect(x, y, w, h, fill_col)

        if thickness > 1:
            for i in range(thickness):
                self.buf.rect(x + i, y + i, w - i * 2, h - i * 2, color)
        elif thickness < 1:
            return
        else:
            self.buf.rect(x, y, w, h, color)

    def draw_circle(
        self,
        pos_x: int,
        pos_y: int,
        r: int,
        color: int,
        thickness: int = 1,
        fill: bool = False,
        fill_color: int | None = None,
        clamp: bool = False,
    ) -> None:

        if clamp:
            pos_x = clamp_cord(pos_x, 0, self.width)
            pos_y = clamp_cord(pos_y, 0, self.height)

        if thickness > 1:
            for i in range(thickness):
                self.buf.ellipse(pos_x, pos_y, r - i, r - i, color, False)
        elif thickness < 1:
            pass
        else:
            self.buf.ellipse(pos_x, pos_y, r, r, color, False)

        if fill:
            fill_col = color
            if fill_color is not None:
                fill_col = fill_color
            self.buf.ellipse(
                pos_x, pos_y, r - thickness, r - thickness, fill_col, True
            )

    def draw_ellipse(
        self,
        pos_x: int,
        pos_y: int,
        r_x: int,
        r_y: int,
        color: int,
        thickness: int = 1,
        fill: bool = False,
        fill_color: int | None = None,
        quad: int = EL_FULL,
    ) -> None:
        if thickness > 1:
            for i in range(thickness):
                self.buf.ellipse(
                    pos_x, pos_y, r_x - i, r_y - i, color, False, quad
                )
        elif thickness < 1:
            pass
        else:
            self.buf.ellipse(pos_x, pos_y, r_x, r_y, color, False, quad)

        if fill:
            fill_col = color
            if fill_color is not None:
                fill_col = fill_color
            self.buf.ellipse(
                pos_x,
                pos_y,
                r_x - thickness,
                r_y - thickness,
                fill_col,
                True,
                quad,
            )

    def draw_text(
        self,
        text: str,
        pos_x: int,
        pos_y: int,
        color: int,
        wrap: bool = False,
        wrap_width: int | None = None,
        wrap_chars: int | None = None,
        char_width: int = 8,
        char_height: int = 8,
    ) -> None:
        if wrap:
            max_chars = abs(self.width - pos_x) // char_width

            if wrap_width is not None:
                max_chars = (wrap_width - pos_x) // char_width

            if wrap_chars is not None:
                max_chars = wrap_chars

            new_y_pos = pos_y
            for i in range(0, len(text), max_chars):
                self.buf.text(text[i : i + max_chars], pos_x, new_y_pos, color)
                new_y_pos += char_height

        else:
            self.buf.text(text, pos_x, pos_y, color)

    def show(self) -> None:
        self.driver.display(self.mv)
