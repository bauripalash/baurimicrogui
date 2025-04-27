"""Simple and Minimal Micropython Driver for ST7735 Displays"""

import time
from machine import Pin, SPI
from baurimicrogui.gui import BauriMicroGUI
from baurimicrogui.drivers.display.st7735 import *
from baurimicrogui.colors import *
from baurimicrogui.utils import *
from baurimicrogui.widgets.button import Button
from baurimicrogui.widgets.label import Label


vl: int = 0


def main():
    global vl
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
    tft = BauriMicroST7735(
        spi=s,
        p_dc=32,
        p_reset=None,
        p_cs=5,
        width=128,
        height=160,
        rotation=ROT_180,
    )

    ui = BauriMicroGUI(tft, 128, 160, ROT_180, COL_RGB)
    ui.bg(COLOR_BLACK)
    pad = Offset(left=8, right=8, top=8, bottom=8)

    lbl = Label("clicked:", 20, 0, COLOR_GREEN, COLOR_BLACK, padding=pad)

    btn_plus = Button(
        "[+]",
        20,
        20,
        COLOR_GREEN,
        COLOR_RED,
        padding=pad,
    )

    btn_size = btn_plus.get_calc_size()

    l = "clicked:"
    btn_minus = Button(
        "[-]",
        20 + btn_size[0] + 10,
        20,
        COLOR_GREEN,
        COLOR_BLUE,
        padding=pad,
    )

    def minus_click():
        global vl
        print("minus clicked")
        vl -= 1
        lbl.set_text(l + str(vl))

    def plus_click():
        global vl
        print("plus clicked")
        vl += 1
        lbl.set_text(l + str(vl))

    btn_plus.on_click = plus_click

    btn_minus.on_click = minus_click

    print("Plus Size -> ", btn_size)

    ui.add_widget(lbl)

    ui.add_widget(btn_plus)
    ui.add_widget(btn_minus)

    ui.flush(True)

    for i in range(5):
        for _ in range(len(ui.widgets)):
            print("Simulating Next click")
            ui.action_next()
            # print("Simulating Select click")
            ui.action_click()
            time.sleep_ms(100)

        ui.windex = -1


if __name__ == "__main__":
    main()
