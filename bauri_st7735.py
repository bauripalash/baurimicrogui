"""Simple and Minimal Micropython Driver for ST7735 Displays"""

import time
from machine import Pin, SPI
import framebuf
import micropython

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

class BauriDispDriver(framebuf.FrameBuffer):
    pass

class BauriST7735(framebuf.FrameBuffer):
    dc_pin: Pin
    reset_pin: Pin | None = None
    cs_pin: Pin | None = None
    spi: SPI
    height: int
    width: int
    rotation: int
    colormode: int
    colordata: bytearray
    color_buf: bytes
    

    def __init__(
        self,
        *,
        spi: SPI,
        p_dc: int | Pin,
        p_reset: int | Pin | None,
        p_cs: int | Pin | None,
        width: int = 128,
        height: int = 160,
        rotation: int = ROT_0,
        colormode: int = COL_RGB,
    ) -> None:
        self.spi = spi
        self.width = width
        self.height = height
        self.rotation = rotation
        self.colormode = colormode

        if isinstance(p_dc, Pin):
            self.dc_pin = p_dc
        elif isinstance(p_dc, int):
            self.dc_pin = Pin(p_dc, Pin.OUT)
        else:
            print("Invalid DC Pin Type")
            return

        if p_reset is not None:
            if isinstance(p_reset, Pin):
                self.reset_pin = p_reset
            elif isinstance(p_reset, int):
                self.reset_pin = Pin(p_reset, Pin.OUT)
            else:
                print("Invalid RESET Pin Type")
                return
        if p_cs is not None:
            if isinstance(p_cs, Pin):
                self.cs_pin = p_cs
            elif isinstance(p_cs, int):
                self.cs_pin = Pin(p_cs, Pin.OUT)
            else:
                print("Invalid CS Pin Type")

        # self.fb_mode = framebuf.GS8
        # buff = bytearray(height * width)
        # self.mv_buff = memoryview(buff)
        # super().__init__(buff, self.height, self.width, self.fb_mode)
        self.fb_mode = framebuf.RGB565
        self.raw_buf = bytearray(self.width * self.height * 2)
        #self.buf = framebuf.FrameBuffer(
        #    self.raw_buf, self.width, self.height, self.fb_mode
        #)
        super().__init__(self.raw_buf, self.width, self.height, self.fb_mode)

        self.colordata = bytearray(2)

        # self.init_display()

    def _dc(self, value: int) -> None:
        """Send `value` to DC/AO Pin"""
        self.dc_pin(value)

    def _cs(self, value: int) -> None:
        """Send `value` to CS Pin if present"""

        if self.cs_pin is not None:
            self.cs_pin(value)

    def _reset(self, value: int) -> None:
        """Send `value` to RESET Pin if present"""
        if self.reset_pin is not None:
            self.reset_pin(value)

    def _hardw_reset(self) -> None:
        """Hardware Reset"""
        self._dc(0)
        self._reset(1)
        time.sleep_us(500)
        self._reset(0)
        time.sleep_us(500)
        self._reset(1)
        time.sleep_us(500)

    def _cmd(self, cmd: int) -> None:
        """Write command to the device"""
        self._dc(0)
        self._cs(0)
        self.spi.write(bytearray([cmd]))
        self._cs(1)

    def _wdata(self, data: bytearray) -> None:
        """Write raw data to the device"""
        self._dc(1)
        self._cs(0)
        self.spi.write(data)
        self._cs(1)

    def _argcmd(self, cmd: int, data: bytearray) -> None:
        """Write command followed by `data` bytearray"""
        self._cmd(cmd)
        self._wdata(data)

    def disp_on(self) -> None:
        """Turn on display"""
        self._cmd(DISPON)

    def disp_off(self) -> None:
        """Turn off display"""
        self._cmd(DISPOFF)

    def disp_invert(self, iv: bool) -> None:
        """Toggle invert. True -> Invert."""
        if iv:
            self._cmd(INVON)
        else:
            self._cmd(INVOFF)

    def init_display(self) -> None:
        self._hardw_reset()  # Hardware Reset
        self._cmd(SWRESET)  # Software reset
        time.sleep_us(150)
        self._cmd(SLPOUT)  # Out of Sleep Mode
        time.sleep_us(255)

        # The data says I dont know
        # Adafruit Lib mentions it as
        # Rate = fosc/(1x2+40) * (LINE+2C+2D)
        # What that means, I will look into it ;)
        frame_rate_ctrl_data = bytearray([0x01, 0x2C, 0x2D])

        # Frame rate control for normal mode
        self._argcmd(FRMCTR_1, frame_rate_ctrl_data)
        # Frame rate control for idle mode
        self._argcmd(FRMCTR_2, frame_rate_ctrl_data)

        # Frame rate partial mode data
        frame_rate_ctrl_data = bytearray([0x01, 0x2C, 0x2D, 0x01, 0x2C, 0x2D])

        # Frame rate control for partial mode
        self._argcmd(FRMCTR_3, frame_rate_ctrl_data)

        # Display Inversion Control
        # Data -> No inversion
        self._argcmd(INVCTR, bytearray([0x07]))

        # Power Control
        # Data ->
        # 0x02 -> -4.6V
        # 0x84 -> AUTO mode
        self._argcmd(PWCTR_1, bytearray([0xA2, 0x02, 0x84]))

        # Power Control
        # Data ->VGH25=2.4C VGSEL=-10 VGH=3 * AVDD
        self._argcmd(PWCTR_2, bytearray([0xC5]))

        # Power Control
        # Data ->
        # 0x0A -> Opamp Current small
        # 0x00 -> Boost Frequency
        self._argcmd(PWCTR_3, bytearray([0x0A, 0x00]))

        # Power Control
        # Data ->
        # 0x8A -> Opamp Current small
        # 0x2A -> Boost Frequency
        self._argcmd(PWCTR_4, bytearray([0x8A, 0x2A]))

        # Power Control
        # Data ->
        # 0x8A -> Opamp Current small
        # 0xEE -> Boost Frequency
        self._argcmd(PWCTR_5, bytearray([0x8A, 0xEE]))

        # Power Control
        self._argcmd(VMCTR_1, bytearray([0x0E]))

        # Invert Off
        self._cmd(INVOFF)

        ## Offset RGB Stuff here
        self.offset = (2, 1)

        ## Rotation Stuff
        # self._argcmd(MADCTL, bytearray([self.rotation | DISP_RGB]))
        # self._argcmd(MADCTL, bytearray([0x05]))
        self._set_rotation()

        self._argcmd(COLMOD, bytearray([0x05]))

        # Gamma Control - Positive polarity
        self._argcmd(
            GMCTRP_1,
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
        self._argcmd(
            GMCTRN_1,
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

        self._cmd(NORON)
        time.sleep_us(10)
        self._cmd(DISPON)
        time.sleep_us(100)

        self._cs(1)

        self._set_rotation()

    def _set_rotation(self) -> None:
        if self.rotation == ROT_90 or self.rotation == ROT_270:
            _h = self.height
            _w = self.width
            self.width = _h
            self.height = _w
        self._argcmd(MADCTL, bytearray([self.rotation | self.colormode]))

    def _populate_colordata(self, color: int):
        self.colordata[0] = color >> 8
        self.colordata[1] = color

    def _push_color(self, color: int):
        # self.colordata[0] = color >> 8
        # self.colordata[1] = color
        self._populate_colordata(color)
        self._wdata(self.colordata)

    def _set_color(self, color: int):
        # colordata = bytearray()
        # colordata.append(color >> 8)
        # colordata.append(color)
        self._populate_colordata(color)
        self.color_buf = bytes(self.colordata) * 32
        #print(self.color_buf)

    def _draw(self, numPixels: int):
        self._dc(1)
        self._cs(0)

        for _ in range(numPixels // 32):
            self.spi.write(self.color_buf)
        rest = int(numPixels) % 32
        if rest > 0:
            b = bytes(self.colordata) * rest
            self.spi.write(b)
        self._cs(1)

    def raw_fill_rect(
        self, pos_x: int, pos_y: int, width: int, height: int, color: int
    ) -> None:
        x1 = clamp_cord(pos_x, 0, self.width)
        y1 = clamp_cord(pos_y, 0, self.height)
        x2 = clamp_cord(pos_x + width, 0, self.width)
        y2 = clamp_cord(pos_y + height, 0, self.height)

        self._set_win(x1, y1, abs(x2 - pos_x), abs(y2 - pos_y))
        self._set_color(color)
        self._draw((x2 - x1 + 1) * (y2 - y1 + 1))

    def _set_win(self, pos_x: int, pos_y: int, width: int, height: int) -> None:
        x = pos_x + self.offset[0]
        y = pos_y + self.offset[1]
        data = bytearray([self.offset[0], x, self.offset[0], x + width])
        self._argcmd(CASET, data)
        data = bytearray([self.offset[1], y, self.offset[1], y + height])
        self._argcmd(RASET, data)
        self._cmd(RAMWR)

    def _pixel(self, pos_x: int, pos_y: int, color: int) -> None:
        self._set_win(pos_x, pos_y, 1, 1)
        self._push_color(color)

    def _get_swapper_buf(self) -> bytearray:
        buf = bytearray(len(self.raw_buf))
        for i in range(0, len(self.raw_buf), 2):
            buf[i] = self.raw_buf[i + 1]
            buf[i + 1] = self.raw_buf[i]

        return buf

    def disp(self, flip_endianness: bool = False) -> None:
        self._set_win(0, 0, self.width - 1, self.height - 1)
        self._dc(1)
        self._cs(0)
        # I am not sure if this issue specific to my display unit. But without
        # flipping endinanness. colors are all messed up.
        # Don't pass any argument if you see colors correctly without flipping.
        if flip_endianness:
            self.spi.write(self._get_swapper_buf())
        else:
            self.spi.write(self.raw_buf)
        self._cs(1)


    


if __name__ == "__main__":
    #print("SPI init ->")
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
    tft.init_display()
    tft.disp_off()
    tft.disp_on()

    raw_draw_run = False
    # Raw Drawing
    if raw_draw_run:
        for i in range(50):
            tft._pixel(40 + i, 159, COLOR_WHITE)

        tft.fill_rect(0, 0, tft.width, tft.height, COLOR_BLACK)

        tft.fill_rect(20, 20, 20, 20, COLOR_GREEN)

        tft.fill_rect(50, 20, 20, 20, COLOR_GREEN)

        tft.fill_rect(20, 50, 50, 10, COLOR_WHITE)
    # End Raw Drawing
    else:
        tft.fill(COLOR_BLACK)
        #print("GREEN ->", hex(COLOR_GREEN))
        tft.fill_rect(20, 20, 20, 20, COLOR_GREEN)
        tft.fill_rect(50, 20, 20, 20, COLOR_GREEN)
        tft.fill_rect(20, 50, 50, 10, COLOR_WHITE)
        # tft.buf.line(0,0, tft.width, tft.height, COLOR_BLUE)
        # tft.buf.line(tft.width,0, 0, tft.height, COLOR_BLUE)
        tft.text("Hello World! this is very fun", 80, 20, COLOR_WHITE)
        tft.disp(True)
