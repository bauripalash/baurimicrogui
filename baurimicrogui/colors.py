def color_565(r: int, g: int, b: int):
    return ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)


COLOR_BLACK = 0
COLOR_WHITE = color_565(255, 255, 255)
COLOR_RED = color_565(255, 0, 0)
COLOR_GREEN = color_565(0, 255, 0)
COLOR_BLUE = color_565(0, 0, 255)
