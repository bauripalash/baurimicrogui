import gc
import micropython
import time
from machine import Pin, SPI
from baurimicrogui.drivers.display import BauriMicroDispDriver

ROT_0 = 0x00
ROT_90 = 0x60
ROT_180 = 0xC0
ROT_270 = 0xA0

COL_BGR = 0x08
COL_RGB = 0x00


@micropython.native
def swap_end(row_buf: memoryview, buf: memoryview, size: int) -> None:
    for i in range(0, size, 2):
        row_buf[i] = buf[i + 1]
        row_buf[i + 1] = buf[i]


class BauriMicroST7735(BauriMicroDispDriver):
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

        gc.collect()

        self.rowbuf = bytearray(width * 2)
        self.rowbuf_mv = memoryview(self.rowbuf)

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

    def display(self, buffer: memoryview) -> None:
        self.set_region(0, 0, self.width - 1, self.height - 1)
        self.dc(1)
        self.cs(0)
        row_bts = self.width * 2
        # I am not sure if this issue specific to my display unit. But without
        # flipping endinanness. colors are all messed up.
        # Don't pass any argument if you see colors correctly without flipping.
        # s = machine.SoftSPI()

        # self.spi.write(buffer)
        for row in range(self.height):
            r_start = row * row_bts
            swap_end(
                self.rowbuf_mv, buffer[r_start : r_start + row_bts], row_bts
            )
            self.spi.write(self.rowbuf_mv)

        self.cs(1)

        # self.dc(0)
        # self.cs(0)
        # self.spi.write(bytearray([self.RAMWR]))
        # self.dc(1)
        # self.spi.write(buffer)
        # for i in range(0, len(buffer), 2):
        #    self.spi.write(bytearray([buffer[i+1],buffer[i]]))
        # self.cs(1)
