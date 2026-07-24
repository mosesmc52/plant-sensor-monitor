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
            # Waveshare distributes multiple versions of this driver. The
            # current one calls the class EPD, while older/vendor variants
            # use a model-specific class name.
            display_class = None
            for name in ("EPD", "EPD_7in5_V2", "EPD_7IN5_V2"):
                candidate = getattr(epd7in5_V2, name, None)
                if isinstance(candidate, type):
                    display_class = candidate
                    break

            if display_class is None:
                # Fall back to capability-based discovery for local forks
                # whose class name differs from Waveshare's examples.
                for candidate in vars(epd7in5_V2).values():
                    if (
                        isinstance(candidate, type)
                        and hasattr(candidate, "init")
                        and hasattr(candidate, "display")
                        and hasattr(candidate, "getbuffer")
                    ):
                        display_class = candidate
                        break

            if display_class is None:
                available = ", ".join(
                    name
                    for name, candidate in vars(epd7in5_V2).items()
                    if isinstance(candidate, type) and not name.startswith("_")
                ) or "none"
                raise RuntimeError(
                    "The Waveshare 7.5in V2 driver does not expose a compatible "
                    f"display class ({available}); loaded {epd7in5_V2.__file__}."
                )
            self._display = display_class()
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
        if self._display is None:
            return

        try:
            self.sleep()
        except OSError as exc:
            # The vendor driver may already have closed the SPI descriptor.
            # The image has already been sent, so cleanup should remain safe.
            print(f"Display sleep skipped: {exc}")
        finally:
            self._display = None
