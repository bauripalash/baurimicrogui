from micropython import const


def color_565(r: int, g: int, b: int):
    return ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)


COLOR_BLACK = 0
COLOR_WHITE = const(0xFFFF)
COLOR_RED = const(0xF800)
COLOR_GREEN = const(0x07E0)
COLOR_BLUE = const(0x001F)


COLOR_YELLOW = const(0xFFE0)
COLOR_CYAN = const(0x07FF)
COLOR_MAGENTA = const(0xF81F)
COLOR_SILVER = const(0xBDF7)
COLOR_GRAY = const(0x8410)
