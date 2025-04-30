import time
import machine
import micropython
from baurimicrogui.drivers.input import BauriMicroInputDriver

try:
    from typing import Optional, Callable
except ImportError:
    pass


class SimpleJoyStick(BauriMicroInputDriver):
    x_center_pos: int = 0
    y_center_pos: int = 0
    x_value: float = 0.0
    y_value: float = 0.0
    xa: machine.ADC
    ya: machine.ADC

    threashold: float = 0.2

    btn_pin: machine.Pin
    has_btn: bool = False

    MaxVal = micropython.const(65535)
    sample_delay: int = 5

    left_press_fn: Optional[Callable[[], None]] = None
    left_release_fn: Optional[Callable[[], None]] = None
    right_press_fn: Optional[Callable[[], None]] = None
    right_release_fn: Optional[Callable[[], None]] = None
    up_press_fn: Optional[Callable[[], None]] = None
    up_release_fn: Optional[Callable[[], None]] = None
    down_press_fn: Optional[Callable[[], None]] = None
    down_release_fn: Optional[Callable[[], None]] = None
    btn_press_fn: Optional[Callable[[], None]] = None

    S_IDLE = micropython.const(0)
    S_LEFT = micropython.const(1)
    S_RIGHT = micropython.const(2)
    S_UP = micropython.const(3)
    S_DOWN = micropython.const(4)
    current_state: int = S_IDLE
    prev_state: int = S_IDLE

    def __init__(
        self,
        x_adc,
        y_adc,
        btn_pin=None,
        delay: int = 5,
        threashold: float = 0.2,
    ) -> None:
        if isinstance(x_adc, int):
            self.xa = machine.ADC(machine.Pin(x_adc, machine.Pin.IN))
        else:
            self.xa = machine.ADC(x_adc)

        if isinstance(y_adc, int):
            self.ya = machine.ADC(machine.Pin(y_adc, machine.Pin.IN))
        else:
            self.ya = machine.ADC(y_adc)

        if btn_pin is not None:
            self.has_btn = True
            if isinstance(btn_pin, int):
                self.btn_pin = machine.Pin(
                    btn_pin,
                    machine.Pin.IN,
                    machine.Pin.PULL_UP,
                )
            else:
                self.btn_pin = btn_pin

        self.xa.width(machine.ADC.WIDTH_12BIT)
        self.ya.width(machine.ADC.WIDTH_12BIT)

        self.xa.atten(machine.ADC.ATTN_11DB)
        self.ya.atten(machine.ADC.ATTN_11DB)
        self.threashold = threashold

        self.calibrate()

    def calibrate(self) -> None:
        print("[+] joystick calibration started")

        total_x = 0
        total_y = 0

        for _ in range(10):
            total_x += self.xa.read_u16()
            total_y += self.ya.read_u16()

            time.sleep_ms(2)

        self.x_center_pos = total_x // 10
        self.y_center_pos = total_y // 10

        print("[+] joystick calibration finished")

    def _read(self):
        dx: float = 0.0
        dy: float = 0.0
        for _ in range(3):
            dx += self.xa.read_u16()
            dy += self.ya.read_u16()

        dx /= 3.0
        dx -= self.x_center_pos
        dy /= 3.0
        dy -= self.y_center_pos

        if dx >= 0:
            self.x_value = dx / (self.MaxVal - self.x_center_pos)
        else:
            self.x_value = dx / self.x_center_pos

        if dy >= 0:
            self.y_value = dy / (self.MaxVal - self.y_center_pos)
        else:
            self.y_value = dy / self.y_center_pos

        self.y_value = round(self.y_value, 1)
        self.x_value = round(self.x_value, 1)

    def get_state(self) -> int:
        t = self.threashold

        self._read()
        if self.x_value >= t:
            return self.S_RIGHT
        if self.x_value <= -t:
            return self.S_LEFT
        if self.y_value >= t:
            return self.S_UP
        if self.y_value <= -t:
            return self.S_DOWN

        return self.S_IDLE

    def _call_fn(self, state: int, released: bool = False) -> None:
        if state == self.S_LEFT:
            if released:
                if self.left_release_fn is not None:
                    self.left_release_fn()
            else:
                if self.left_press_fn is not None:
                    self.left_press_fn()
        elif state == self.S_RIGHT:
            if released:
                if self.right_release_fn is not None:
                    self.right_release_fn()
            else:
                if self.right_press_fn is not None:
                    self.right_press_fn()
        elif state == self.S_UP:
            if released:
                if self.up_release_fn is not None:
                    self.up_release_fn()
            else:
                if self.up_press_fn is not None:
                    self.up_press_fn()
        elif state == self.S_DOWN:
            if released:
                if self.down_release_fn is not None:
                    self.down_release_fn()
            else:
                if self.down_press_fn is not None:
                    self.down_press_fn()

    def state_to_str(self, state=None) -> str:
        s = self.current_state
        if state is not None:
            s = state

        if s == self.S_LEFT:
            return "LEFT"
        if s == self.S_RIGHT:
            return "RIGHT"
        if s == self.S_UP:
            return "UP"
        if s == self.S_DOWN:
            return "DOWN"

        return "IDLE"

    def _handle(self):
        if self.has_btn:
            btn_val = not self.btn_pin.value()
            if btn_val:
                if self.btn_press_fn is not None:
                    self.btn_press_fn()

        self.current_state = self.get_state()

        if self.current_state != self.prev_state:
            if self.prev_state != self.S_IDLE:
                # print("RELEASED -> ", self.state_to_str(self.prev_state))
                self._call_fn(self.prev_state, True)
            if self.current_state != self.S_IDLE:
                # print("PRESSED -> ", self.state_to_str())
                self._call_fn(self.current_state, False)
        self.prev_state = self.current_state

    def handle(self):
        while True:
            self._handle()

    def debug_loop(self):
        while True:
            self._read()
            print("X -> ", self.x_value)
            print("Y -> ", self.y_value)
            time.sleep_ms(5)

    def listen(self) -> None:
        self.handle()
