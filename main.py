"""Simple and Minimal Micropython Driver for ST7735 Displays"""

from machine import Pin, SPI
from baurimicrogui.gui import BauriMicroGUI
from baurimicrogui.drivers.display.st7735 import *
from baurimicrogui.drivers.input.simple_joystick import SimpleJoyStick
from baurimicrogui.colors import *
from baurimicrogui.utils import *
from baurimicrogui.widgets.label import Label
from baurimicrogui.widgets.button import Button
import gc


class ProjectGreenZero:
    display_spi: SPI
    display_driver: BauriMicroST7735
    jstick: SimpleJoyStick
    ui: BauriMicroGUI

    def __init__(self) -> None:
        self.display_spi = SPI(
            1,
            baudrate=8000000,
            polarity=0,
            phase=0,
            sck=Pin(18),
            mosi=Pin(23),
            miso=None,
        )
        self.display_driver = BauriMicroST7735(
            spi=self.display_spi,
            p_dc=32,
            p_reset=None,
            p_cs=5,
            width=128,
            height=160,
            rotation=ROT_180,
        )
        gc.collect()
        self.jstick = SimpleJoyStick(13, 4, 21)
        self.ui = BauriMicroGUI(self.display_driver, 128, 160, ROT_180, COL_RGB)
        self.ui.bg(COLOR_BLACK)
        self.n = 0
        self.ui.loop_navigation = True

    def setup_jstick(self) -> None:
        self.jstick.right_press_fn = lambda: self.inp_next_cb()
        self.jstick.left_press_fn = lambda: self.inp_prev_cb()
        self.jstick.btn_press_fn = lambda: self.inp_sel_cb()

    def setup_gui(self) -> None:
        self.def_pad = Offset(left=8, right=8, top=8, bottom=8)

        self.head_lbl = Label(
            "Green Mango", 20, 0, COLOR_GREEN, COLOR_BLACK, padding=self.def_pad
        )
        self.p_btn = Button("[+]", 20, 20, COLOR_BLUE, COLOR_RED, padding=self.def_pad)

        self.m_btn = Button("[-]", 20, 60, COLOR_BLUE, COLOR_RED, padding=self.def_pad)

        self.p_btn.on_click = lambda: self.plus_btn_click()
        self.m_btn.on_click = lambda: self.minus_btn_click()

        self.ui.add_widget(self.head_lbl)
        self.ui.add_widget(self.p_btn)
        self.ui.add_widget(self.m_btn)

    def plus_btn_click(self) -> None:
        self.n += 1
        self.update_label()

    def minus_btn_click(self) -> None:
        self.n -= 1
        self.update_label()

    def update_label(self) -> None:
        self.head_lbl.set_text("clicked:{}".format(self.n))

    def inp_next_cb(self) -> None:
        self.ui.action_next()

    def inp_prev_cb(self) -> None:
        self.ui.action_prev()

    def inp_sel_cb(self) -> None:
        self.ui.action_click()

    def run(self) -> None:
        self.ui.flush()

        while True:
            self.jstick.listen()


def main():
    m = ProjectGreenZero()
    m.setup_gui()
    m.setup_jstick()
    m.run()


if __name__ == "__main__":
    main()
