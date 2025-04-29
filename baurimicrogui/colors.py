from micropython import const

def color_565(r: int, g: int, b: int):
    return ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)


COLOR_BLACK = 0
COLOR_WHITE = const(0xffff)
COLOR_RED = const(0xf800)
COLOR_GREEN = const(0x07e0)
COLOR_BLUE = const(0x001f)


COLOR_YELLOW = const(0xffe0)
COLOR_CYAN = const(0x07ff)
COLOR_MAGENTA = const(0xf81f)
COLOR_SILVER = const(0xbdf7)
COLOR_GRAY = const(0x8410)
