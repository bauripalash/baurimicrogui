"""Simple and Minimal Micropython Driver for ST7735 Displays"""

import time
from machine import Pin, SPI
import framebuf
import micropython


# Rotation -> 0, 90, 180, 270 (Clockwise)
ROT_0 = 0x00
ROT_90 = 0x60
ROT_180 = 0xC0
ROT_270 = 0xA0

COL_BGR = 0x08
COL_RGB = 0x00


def DispColor(r: int, g: int, b: int):
    return ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)


COLOR_BLACK = 0
COLOR_WHITE = DispColor(255, 255, 255)
COLOR_RED = DispColor(255, 0, 0)
COLOR_GREEN = DispColor(0, 255, 0)
COLOR_BLUE = DispColor(0, 0, 255)


def clamp_cord(pos: int, smallest: int, biggest: int) -> int:
    """Clamp a giver number within `smallest` and `biggest` and return it"""

    if pos < smallest:
        return smallest
    elif pos > biggest:
        return biggest
    else:
        return pos


class BauriDispDriver:
    def __init__(self) -> None:
        pass

    def setup(
        self,
        spi: SPI,
        pin_dc: int | Pin,
        pin_cs: int | Pin,
        pin_reset: int | Pin | None,
        width: int = 128,
        height: int = 160,
        rotation: int = ROT_0,
        colormode: int = COL_RGB,
    ) -> bool:
        self.spi = spi
        self.width = width
        self.height = height
        self.rotation = rotation
        self.colormode = colormode

        if isinstance(pin_dc, Pin):
            self.dc_pin = pin_dc
        elif isinstance(pin_dc, int):
            self.dc_pin = Pin(pin_dc, Pin.OUT)
        else:
            print("Invalid DC Pin Type")
            return False

        if isinstance(pin_cs, Pin):
            self.cs_pin = pin_cs
        elif isinstance(pin_cs, int):
            self.cs_pin = Pin(pin_cs, Pin.OUT)
        else:
            print("Invalid CS Pin Type")
            return False

        if pin_reset is not None:
            if isinstance(pin_reset, Pin):
                self.reset_pin = pin_reset
            elif isinstance(pin_reset, int):
                self.reset_pin = Pin(pin_reset, Pin.OUT)
            else:
                print("Invalid RESET Pin Type")
                return False

        return True

    def dc(self, value: int) -> None:
        """Send `value` to DC/AO Pin"""
        self.dc_pin.value(value)

    def cs(self, value: int) -> None:
        """Send `value` to CS Pin"""
        self.cs_pin.value(value)

    def reset(self, value: int) -> None:
        """Send `value` to RESET Pin if present"""
        if self.reset_pin is not None:
            self.reset_pin.value(value)

    def hw_reset(self) -> None:
        """Hardware Reset"""
        pass

    def cmd(self, cmd: int) -> None:
        """Send command to the device"""
        pass

    def write_data(self, data: bytearray) -> None:
        """Send raw data to the device"""
        pass

    def argcmd(self, cmd: int, data: bytearray) -> None:
        """Send command followed by `data` bytearray"""
        pass

    def disp_on(self) -> None:
        """Turn on display"""
        pass

    def disp_off(self) -> None:
        """Turn off display"""
        pass

    def disp_invert(self, invert: bool) -> None:
        """Toggle invert. True -> Invert."""
        pass

    def boot_display(self) -> None:
        """Run Init Sequence for the display"""
        pass

    def set_region(
        self, pos_x: int, pos_y: int, width: int, height: int
    ) -> None:
        """Set Region for drawing"""
        pass

    def display(self, buffer: bytearray, flip_endianness: bool = False) -> None:
        """Display/Flush drawing data to the display"""
        pass


class BauriST7735(BauriDispDriver):
    dc_pin: Pin
    reset_pin: Pin | None = None
    spi: SPI
    height: int
    width: int
    rotation: int
    colormode: int

    cs_pin: Pin | None = None

    SWRESET = 0x01
    SLPOUT = 0x11

    FRMCTR_1 = 0xB1
    FRMCTR_2 = 0xB1
    FRMCTR_3 = 0xB3

    INVCTR = 0xB4

    PWCTR_1 = 0xC0
    PWCTR_2 = 0xC1
    PWCTR_3 = 0xC2
    PWCTR_4 = 0xC3
    PWCTR_5 = 0xC4

    VMCTR_1 = 0xC5
    INVOFF = 0x20
    INVON = 0x21

    MADCTL = 0x36
    COLMOD = 0x3A

    CASET = 0x2A
    RASET = 0x2B

    GMCTRP_1 = 0xE0
    GMCTRN_1 = 0xE1

    NORON = 0x13
    DISPOFF = 0x28
    DISPON = 0x29

    RAMWR = 0x2C

    def __init__(
        self,
        *,
        spi: SPI,
        p_dc: int | Pin,
        p_reset: int | Pin | None,
        p_cs: int | Pin,
        width: int = 128,
        height: int = 160,
        rotation: int = ROT_0,
        colormode: int = COL_RGB,
    ) -> None:
        super().__init__()
        isok = self.setup(
            spi, p_dc, p_cs, p_reset, width, height, rotation, colormode
        )
        if not isok:
            print("Failed to Setup Display")

    def dc(self, value: int) -> None:
        self.dc_pin(value)

    def cs(self, value: int) -> None:

        if self.cs_pin is not None:
            self.cs_pin(value)

    def reset(self, value: int) -> None:
        if self.reset_pin is not None:
            self.reset_pin(value)

    def hw_reset(self) -> None:
        self.dc(0)
        self.reset(1)
        time.sleep_us(500)
        self.reset(0)
        time.sleep_us(500)
        self.reset(1)
        time.sleep_us(500)

    def cmd(self, cmd: int) -> None:
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([cmd]))
        self.cs(1)

    def write_data(self, data: bytearray) -> None:
        self.dc(1)
        self.cs(0)
        self.spi.write(data)
        self.cs(1)

    def argcmd(self, cmd: int, data: bytearray) -> None:
        self.cmd(cmd)
        self.write_data(data)

    def disp_on(self) -> None:
        self.cmd(self.DISPON)

    def disp_off(self) -> None:
        self.cmd(self.DISPOFF)

    def disp_invert(self, invert: bool) -> None:
        if invert:
            self.cmd(self.INVON)
        else:
            self.cmd(self.INVOFF)

    def boot_display(self) -> None:
        self.hw_reset()  # Hardware Reset
        self.cmd(self.SWRESET)  # Software reset
        time.sleep_us(150)
        self.cmd(self.SLPOUT)  # Out of Sleep Mode
        time.sleep_us(255)

        # The data says I dont know
        # Adafruit Lib mentions it as
        # Rate = fosc/(1x2+40) * (LINE+2C+2D)
        # What that means, I will look into it ;)
        frame_rate_ctrl_data = bytearray([0x01, 0x2C, 0x2D])

        # Frame rate control for normal mode
        self.argcmd(self.FRMCTR_1, frame_rate_ctrl_data)
        # Frame rate control for idle mode
        self.argcmd(self.FRMCTR_2, frame_rate_ctrl_data)

        # Frame rate partial mode data
        frame_rate_ctrl_data = bytearray([0x01, 0x2C, 0x2D, 0x01, 0x2C, 0x2D])

        # Frame rate control for partial mode
        self.argcmd(self.FRMCTR_3, frame_rate_ctrl_data)

        # Display Inversion Control
        # Data -> No inversion
        self.argcmd(self.INVCTR, bytearray([0x07]))

        # Power Control
        # Data ->
        # 0x02 -> -4.6V
        # 0x84 -> AUTO mode
        self.argcmd(self.PWCTR_1, bytearray([0xA2, 0x02, 0x84]))

        # Power Control
        # Data ->VGH25=2.4C VGSEL=-10 VGH=3 * AVDD
        self.argcmd(self.PWCTR_2, bytearray([0xC5]))

        # Power Control
        # Data ->
        # 0x0A -> Opamp Current small
        # 0x00 -> Boost Frequency
        self.argcmd(self.PWCTR_3, bytearray([0x0A, 0x00]))

        # Power Control
        # Data ->
        # 0x8A -> Opamp Current small
        # 0x2A -> Boost Frequency
        self.argcmd(self.PWCTR_4, bytearray([0x8A, 0x2A]))

        # Power Control
        # Data ->
        # 0x8A -> Opamp Current small
        # 0xEE -> Boost Frequency
        self.argcmd(self.PWCTR_5, bytearray([0x8A, 0xEE]))

        # Power Control
        self.argcmd(self.VMCTR_1, bytearray([0x0E]))

        # Invert Off
        self.cmd(self.INVOFF)

        ## Offset RGB Stuff here
        self.offset = (2, 1)

        ## Rotation Stuff
        # self.argcmd(MADCTL, bytearray([self.rotation | DISP_RGB]))
        # self.argcmd(MADCTL, bytearray([0x05]))
        self._set_rotation()

        self.argcmd(self.COLMOD, bytearray([0x05]))

        # Gamma Control - Positive polarity
        self.argcmd(
            self.GMCTRP_1,
            bytearray(
                [
                    0x02,
                    0x1C,
                    0x07,
                    0x12,
                    0x37,
                    0x32,
                    0x29,
                    0x2D,
                    0x29,
                    0x25,
                    0x2B,
                    0x39,
                    0x00,
                    0x01,
                    0x03,
                    0x10,
                ]
            ),
        )

        # Gamma Control - Negative polarity
        self.argcmd(
            self.GMCTRN_1,
            bytearray(
                [
                    0x03,
                    0x1D,
                    0x07,
                    0x06,
                    0x2E,
                    0x2C,
                    0x29,
                    0x2D,
                    0x2E,
                    0x2E,
                    0x37,
                    0x3F,
                    0x00,
                    0x00,
                    0x02,
                    0x10,
                ]
            ),
        )

        self.cmd(self.NORON)
        time.sleep_us(10)
        self.cmd(self.DISPON)
        time.sleep_us(100)

        self.cs(1)

        self._set_rotation()

    def _set_rotation(self) -> None:
        if self.rotation == ROT_90 or self.rotation == ROT_270:
            _h = self.height
            _w = self.width
            self.width = _h
            self.height = _w
        self.argcmd(self.MADCTL, bytearray([self.rotation | self.colormode]))

    def set_region(
        self, pos_x: int, pos_y: int, width: int, height: int
    ) -> None:
        x = pos_x + self.offset[0]
        y = pos_y + self.offset[1]
        data = bytearray([self.offset[0], x, self.offset[0], x + width])
        self.argcmd(self.CASET, data)
        data = bytearray([self.offset[1], y, self.offset[1], y + height])
        self.argcmd(self.RASET, data)
        self.cmd(self.RAMWR)

    def _get_swapped_buf(self, buffer: bytearray) -> bytearray:
        buf = bytearray(len(buffer))
        for i in range(0, len(buffer), 2):
            buf[i] = buffer[i + 1]
            buf[i + 1] = buffer[i]

        return buf

    def display(self, buffer: bytearray, flip_endianness: bool = False) -> None:
        self.set_region(0, 0, self.width - 1, self.height - 1)
        self.dc(1)
        self.cs(0)
        # I am not sure if this issue specific to my display unit. But without
        # flipping endinanness. colors are all messed up.
        # Don't pass any argument if you see colors correctly without flipping.
        if flip_endianness:
            self.spi.write(self._get_swapped_buf(buffer))
        else:
            self.spi.write(buffer)
        self.cs(1)


class BauriSimpleUI:
    driver: BauriDispDriver
    width: int
    height: int
    fb_mode: int
    raw_buf: bytearray
    buf: framebuf.FrameBuffer
    rotation: int
    colormode: int

    def __init__(
        self,
        driver: BauriDispDriver,
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

        self.driver.boot_display()

    def pixel(self, pos_x: int, pos_y: int) -> None:
        pass

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

        if fill:
            fill_col = color
            if fill_color is not None:
                fill_col = fill_color
            self.buf.fill_rect(pos_x, pos_y, width, height, fill_col)

        if thickness > 1:
            for i in range(thickness):
                self.buf.rect(
                    pos_x + i, pos_y + i, width - i * 2, height - i * 2, color
                )
        elif thickness < 1:
            return
        else:
            self.buf.rect(pos_x, pos_y, width, height, color)

    def draw_circle(
        self,
        pos_x: int,
        pos_y: int,
        r: int,
        color: int,
        thickness: int = 1,
        fill: bool = False,
        fill_color: int | None = None,
    ) -> None:

        if thickness > 1:
            for i in range(thickness):
                self.buf.ellipse(pos_x, pos_y, r - i, r - i, color, False)
        elif thickness < 1:
            return
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
    ) -> None:
        pass

    def draw_text(
        self,
        text: str,
        pos_x: int,
        pos_y: int,
        wrap: bool = False,
        wrap_width: int | None = None,
    ) -> None:
        pass

    def show(self) -> None:
        self.driver.display(self.raw_buf, True)


if __name__ == "__main__":
    # print("SPI init ->")
    s = SPI(
        1,
        baudrate=8000000,
        polarity=0,
        phase=0,
        sck=Pin(18),
        mosi=Pin(23),
        miso=None,
    )
    tft = BauriST7735(
        spi=s,
        p_dc=32,
        p_reset=None,
        p_cs=5,
        width=128,
        height=160,
        rotation=ROT_180,
    )

    ui = BauriSimpleUI(tft, 128, 160, ROT_180, COL_RGB)
    ui.buf.fill(COLOR_BLACK)
    # ui.buf.fill_rect(20, 20, 20, 20, COLOR_GREEN)
    # ui.draw_rect(20, 20, 100, 100, COLOR_GREEN, thickness=10, fill=True, fill_color=COLOR_BLUE)
    ui.draw_circle(
        ui.width // 2,
        ui.height // 2,
        50,
        COLOR_GREEN,
        thickness=10,
        fill=True,
        fill_color=COLOR_BLUE,
    )

    # ui.buf.fill_rect(50, 20, 20, 20, COLOR_GREEN)
    # ui.buf.fill_rect(20, 50, 50, 10, COLOR_WHITE)
    # ui.buf.text("Hello World! this is very fun", 80, 20, COLOR_WHITE)
    ui.show()
