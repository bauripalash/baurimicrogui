def wrap_list_by_maxchar(lines: list[str], max_chars: int) -> list[str]:
    wl: list[str] = []

    for line in lines:
        for i in range(0, len(line), max_chars):
            wl.append(line[i : i + max_chars])
    return wl


def get_text_size(
    text: str,
    pos_x: int = 0,
    wrap: bool = False,
    screen_width: int = 0,
    wrap_width: int | None = None,
    wrap_chars: int | None = None,
    char_width: int = 8,
    char_height: int = 8,
) -> tuple[int, int]:
    text_len = len(text)
    px = pos_x
    # py = pos_y

    if wrap:
        max_chars = abs(screen_width - px) // char_width

        if wrap_width is not None:
            max_chars = (wrap_width - px) // char_width
        if wrap_chars is not None:
            max_chars = wrap_chars

        chunks = []

        for i in range(0, text_len, max_chars):
            chunks.append(text[i : i + max_chars])

        total_height = len(chunks) * char_height
        total_width = len(max(chunks, key=len) * char_width)

        return (total_width, total_height)

    return (text_len * char_width, char_height)


def clamp_cord(pos: int, smallest: int, biggest: int) -> int:
    """Clamp a giver number within `smallest` and `biggest` and return it.
    If `pos` is smaller than `smallest` return `smallest`.
    If `pos` is greater than `biggest` return `biggest`.
    """

    if pos < smallest:
        return smallest
    elif pos > biggest:
        return biggest
    else:
        return pos


def flip_endian(n: int) -> int:
    """Flip Endianness"""
    return ((n & 0xFF) << 8) | ((n >> 8) & 0xFF)


class Offset:
    def __init__(
        self, left: int = 0, right: int = 0, top: int = 0, bottom: int = 0
    ) -> None:
        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom


def one_offset() -> Offset:
    return Offset(1, 1, 1, 1)
