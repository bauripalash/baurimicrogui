from machine import Pin, SPI


class BauriMicroDispDriver:
    def __init__(self) -> None:
        pass

    def setup(
        self,
        spi: SPI,
        pin_dc: int | Pin,
        pin_cs: int | Pin,
        pin_reset: int | Pin | None,
        width: int = 128,
        height: int = 160,
        rotation: int = 0x0,
        colormode: int = 0x0,
    ) -> bool:
        self.spi = spi
        self.width = width
        self.height = height
        self.rotation = rotation
        self.colormode = colormode

        if isinstance(pin_dc, Pin):
            self.dc_pin = pin_dc
        elif isinstance(pin_dc, int):
            self.dc_pin = Pin(pin_dc, Pin.OUT)
        else:
            print("Invalid DC Pin Type")
            return False

        if isinstance(pin_cs, Pin):
            self.cs_pin = pin_cs
        elif isinstance(pin_cs, int):
            self.cs_pin = Pin(pin_cs, Pin.OUT)
        else:
            print("Invalid CS Pin Type")
            return False

        if pin_reset is not None:
            if isinstance(pin_reset, Pin):
                self.reset_pin = pin_reset
            elif isinstance(pin_reset, int):
                self.reset_pin = Pin(pin_reset, Pin.OUT)
            else:
                print("Invalid RESET Pin Type")
                return False

        return True

    def dc(self, value: int) -> None:
        """Send `value` to DC/AO Pin"""
        self.dc_pin.value(value)

    def cs(self, value: int) -> None:
        """Send `value` to CS Pin"""
        self.cs_pin.value(value)

    def reset(self, value: int) -> None:
        """Send `value` to RESET Pin if present"""
        if self.reset_pin is not None:
            self.reset_pin.value(value)

    def hw_reset(self) -> None:
        """Hardware Reset"""
        pass

    def cmd(self, cmd: int) -> None:
        """Send command to the device"""
        pass

    def write_data(self, data: bytearray) -> None:
        """Send raw data to the device"""
        pass

    def argcmd(self, cmd: int, data: bytearray) -> None:
        """Send command followed by `data` bytearray"""
        pass

    def disp_on(self) -> None:
        """Turn on display"""
        pass

    def disp_off(self) -> None:
        """Turn off display"""
        pass

    def disp_invert(self, invert: bool) -> None:
        """Toggle invert. True -> Invert."""
        pass

    def boot_display(self) -> None:
        """Run Init Sequence for the display"""
        pass

    def set_region(
        self, pos_x: int, pos_y: int, width: int, height: int
    ) -> None:
        """Set Region for drawing"""
        pass

    def display(self, buffer: bytearray, flip_endianness: bool = False) -> None:
        """Display/Flush drawing data to the display"""
        pass
