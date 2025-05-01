from baurimicrogui.canvas import BauriMicroCanvas


class BauriMicroWidget:
    pos_x: int = 0
    pos_y: int = 0
    width: int = 0
    height: int = 0
    first_draw: bool = True
    wtype: str = ""
    is_interactive: bool = False
    enable_hover: bool = False

    has_on_click: bool = False
    has_on_up: bool = False
    hash_on_down: bool = False

    def __init__(self) -> None:
        pass

    def __str__(self) -> str:
        return "Widget[Text=|Size=]"

    def get_calc_size(self) -> tuple[int, int]:
        """Return calculated Width and Height.
        Very Costly, without first drawing"""
        return 0, 0

    def hover(self, enable: bool = True) -> None:
        """On Hover"""
        pass

    def on_click(self) -> None:
        """On click"""
        pass

    def on_up(self) -> None:
        """On Upwards"""
        pass

    def on_down(self) -> None:
        """On Downwards"""
        pass

    def draw_hover(self, canvas: BauriMicroCanvas) -> None:
        """Draw hovered state"""
        pass

    def draw(self, canvas: BauriMicroCanvas) -> None:
        """Draw the button onto the Canvas"""
        pass
