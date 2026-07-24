from display.display import create_display
from display.renderer import render_plant_screen


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
