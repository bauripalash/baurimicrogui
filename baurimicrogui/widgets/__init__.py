from baurimicrogui.canvas import BauriMicroCanvas


class BauriMicroWidget:
    pos_x: int = 0
    pos_y: int = 0
    width: int = 0
    height: int = 0
    first_draw: bool = True
    wtype: str = ""
    is_interactive: bool = False

    def __init__(self) -> None:
        pass

    def get_calc_size(self) -> tuple[int, int]:
        """Return calculated Width and Height.
        Very Costly, without first drawing"""
        return 0, 0

    def hover(self, canvas: BauriMicroCanvas) -> None:
        """On Hover"""
        pass

    def draw(self, canvas: BauriMicroCanvas) -> None:
        """Draw the button onto the Canvas"""
        pass
