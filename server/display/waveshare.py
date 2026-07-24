from PIL import Image

from .base import Display


class WaveshareDisplay(Display):
    def __init__(self) -> None:
        self._display = None

    def _get_display(self):
        # Lazy import prevents macOS from importing Linux-only
        # gpiozero and spidev dependencies.
        try:
            from vendor.waveshare_epd import epd7in5_V2
        except (ImportError, OSError, RuntimeError) as exc:
            raise RuntimeError(
                "The Waveshare display backend requires "
                "Raspberry Pi OS, gpiozero, and spidev."
            ) from exc

        if self._display is None:
            self._display = epd7in5_V2.EPD()
        return self._display

    def initialize(self) -> None:
        self._get_display().init()

    def show(self, image: Image.Image) -> None:
        display = self._get_display()

        expected_size = (
            display.width,
            display.height,
        )

        if image.size != expected_size:
            raise ValueError(
                f"Expected image size {expected_size}, " f"received {image.size}."
            )

        monochrome_image = image.convert("1")

        print("Sending image to display...")
        display.display(display.getbuffer(monochrome_image))

        print("Display updated.")

    def sleep(self) -> None:
        if self._display is not None:
            # Sleep preserves the final e-ink image.
            self._display.sleep()

    def shutdown(self) -> None:
        self.sleep()
        self._display = None
