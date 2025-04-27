from machine import Pin, SPI
import esp
import esp32

from baurimicrogui.colors import *
from baurimicrogui.gui import BauriMicroGUI
from baurimicrogui.drivers.display.st7735 import *

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
    ui.canvas.draw_text("Booted!", 20, 20, COLOR_GREEN)
    ui.canvas.draw_text(
        "Temp: " + str(esp32.raw_temperature()) + "*F", 20, 20 + 9, COLOR_GREEN
    )
    ui.canvas.show(True)
