import os

from display.preview import PreviewDisplay
from display.renderer import render_plant_screen
from display.waveshare import WaveshareDisplay


def create_display():
    backend = os.getenv(
        "DISPLAY_BACKEND",
        "preview",
    )

    if backend == "waveshare":
        return WaveshareDisplay()

    if backend != "preview":
        raise ValueError(
            f"Unsupported DISPLAY_BACKEND={backend!r}; "
            "use 'preview' or 'waveshare'."
        )

    return PreviewDisplay()


def main() -> None:
    image = render_plant_screen(
        plant_name="Basil",
        message="I am healthy!",
        moisture_percent=62,
        temperature_f=72.5,
        humidity_percent=51,
    )

    display = create_display()
    display.initialize()
    try:
        display.show(image)
    finally:
        display.shutdown()


if __name__ == "__main__":
    main()
