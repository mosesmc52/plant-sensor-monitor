from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

DISPLAY_WIDTH = 800
DISPLAY_HEIGHT = 480

FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def _load_font(path: str, size: int) -> ImageFont.ImageFont:
    """Load a readable font on Linux, macOS, and minimal containers."""
    candidates = (
        Path(path),
        Path("/System/Library/Fonts/Helvetica.ttc"),
        Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
    )

    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)

    return ImageFont.load_default()


def render_plant_screen(
    plant_name: str,
    message: str,
    moisture_percent: int,
    temperature_f: float,
    humidity_percent: float,
) -> Image.Image:
    image = Image.new(
        mode="1",
        size=(DISPLAY_WIDTH, DISPLAY_HEIGHT),
        color=255,
    )

    draw = ImageDraw.Draw(image)

    title_font = _load_font(FONT_BOLD, 54)
    message_font = _load_font(FONT_BOLD, 36)
    value_font = _load_font(FONT_REGULAR, 30)

    draw.rectangle(
        (8, 8, DISPLAY_WIDTH - 8, DISPLAY_HEIGHT - 8),
        outline=0,
        width=4,
    )

    draw.text(
        (40, 35),
        plant_name,
        font=title_font,
        fill=0,
    )

    draw.text(
        (40, 125),
        message,
        font=message_font,
        fill=0,
    )

    draw.text(
        (40, 230),
        f"Soil moisture: {moisture_percent}%",
        font=value_font,
        fill=0,
    )

    draw.text(
        (40, 290),
        f"Temperature: {temperature_f:.1f} F",
        font=value_font,
        fill=0,
    )

    draw.text(
        (40, 350),
        f"Humidity: {humidity_percent:.0f}%",
        font=value_font,
        fill=0,
    )

    return image
