from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from math import ceil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

DISPLAY_WIDTH = 800
DISPLAY_HEIGHT = 480

FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CHARACTER_DIRECTORY = PROJECT_ROOT / "server" / "assets" / "characters"


@dataclass(frozen=True)
class PlantPanelData:
    plant_name: str
    state: str
    health_percent: int


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


@lru_cache(maxsize=None)
def _load_character(state: str) -> Image.Image:
    """Load a state image from <project-root>/assets/characters/."""
    filename = f"{state}.png"
    path = CHARACTER_DIRECTORY / filename

    if not path.exists():
        fallback = CHARACTER_DIRECTORY / "offline.png"
        if fallback.exists():
            path = fallback
        else:
            return _placeholder_character(state)

    return Image.open(path).convert("1")


def _placeholder_character(state: str) -> Image.Image:
    """Create a simple fallback graphic when an asset is missing."""
    image = Image.new("1", (240, 240), 255)
    draw = ImageDraw.Draw(image)
    font = _load_font(FONT_BOLD, 18)

    draw.ellipse((45, 55, 195, 205), outline=0, width=5)
    draw.ellipse((85, 110, 100, 125), fill=0)
    draw.ellipse((140, 110, 155, 125), fill=0)
    draw.arc((95, 120, 145, 165), 0, 180, fill=0, width=4)
    draw.text((20, 210), state.replace("_", " "), font=font, fill=0)
    return image


def _panel_grid(plant_count: int) -> tuple[int, int]:
    if plant_count <= 1:
        return 1, 1
    if plant_count == 2:
        return 2, 1
    if plant_count <= 4:
        return 2, 2

    columns = min(4, ceil(plant_count ** 0.5))
    rows = ceil(plant_count / columns)
    return columns, rows


def _draw_health_bar(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    width: int,
    height: int,
    health_percent: int,
    font: ImageFont.ImageFont,
) -> None:
    health = max(0, min(100, health_percent))
    fill_width = int((width - 4) * health / 100)

    draw.rounded_rectangle(
        (x, y, x + width, y + height),
        radius=max(3, height // 2),
        outline=0,
        width=2,
    )

    if fill_width > 0:
        draw.rounded_rectangle(
            (x + 2, y + 2, x + 2 + fill_width, y + height - 2),
            radius=max(2, (height - 4) // 2),
            fill=0,
        )

    label = f"{health}%"
    label_box = draw.textbbox((0, 0), label, font=font)
    label_width = label_box[2] - label_box[0]
    draw.text(
        (x + width - label_width, y - 24),
        label,
        font=font,
        fill=0,
    )


def _draw_panel(
    canvas: Image.Image,
    plant: PlantPanelData,
    x: int,
    y: int,
    width: int,
    height: int,
) -> None:
    draw = ImageDraw.Draw(canvas)
    compact = width < 300 or height < 220

    title_font = _load_font(FONT_BOLD, 22 if compact else 30)
    state_font = _load_font(FONT_REGULAR, 15 if compact else 20)
    health_font = _load_font(FONT_BOLD, 14 if compact else 18)

    padding = 12
    draw.rounded_rectangle(
        (x, y, x + width, y + height),
        radius=12,
        outline=0,
        width=3,
    )

    title = plant.plant_name[:24]
    draw.text((x + padding, y + padding), title, font=title_font, fill=0)

    state_label = plant.state.replace("_", " ").title()
    state_box = draw.textbbox((0, 0), state_label, font=state_font)
    state_width = state_box[2] - state_box[0]
    draw.text(
        (x + width - state_width - padding, y + padding + 4),
        state_label,
        font=state_font,
        fill=0,
    )

    character = _load_character(plant.state).copy()

    health_area_height = 48 if compact else 60
    image_top = y + 50
    image_bottom = y + height - health_area_height - 12
    image_height = max(40, image_bottom - image_top)
    image_width = max(40, width - padding * 2)

    # Keep the complete character inside the panel. The source assets are
    # portrait-oriented and must be scaled to the available panel area.
    character.thumbnail(
        (image_width, image_height),
        resample=Image.Resampling.LANCZOS,
    )
    character_x = x + (width - character.width) // 2
    character_y = image_top + (image_height - character.height) // 2
    canvas.paste(character, (character_x, character_y))

    bar_x = x + padding
    bar_width = width - padding * 2
    bar_height = 16 if compact else 20
    bar_y = y + height - bar_height - 14

    _draw_health_bar(
        draw=draw,
        x=bar_x,
        y=bar_y,
        width=bar_width,
        height=bar_height,
        health_percent=plant.health_percent,
        font=health_font,
    )


def render_plant_dashboard(
    plants: list[PlantPanelData],
    max_plants: int = 4,
) -> Image.Image:
    """Render up to max_plants into an 800x480 e-ink dashboard."""
    image = Image.new("1", (DISPLAY_WIDTH, DISPLAY_HEIGHT), 255)

    visible_plants = plants[: max(1, max_plants)]
    if not visible_plants:
        draw = ImageDraw.Draw(image)
        font = _load_font(FONT_BOLD, 36)
        draw.text((210, 210), "No plants configured", font=font, fill=0)
        return image

    columns, rows = _panel_grid(len(visible_plants))
    margin = 10
    gap = 8

    panel_width = (
        DISPLAY_WIDTH - margin * 2 - gap * (columns - 1)
    ) // columns
    panel_height = (
        DISPLAY_HEIGHT - margin * 2 - gap * (rows - 1)
    ) // rows

    for index, plant in enumerate(visible_plants):
        row = index // columns
        column = index % columns
        x = margin + column * (panel_width + gap)
        y = margin + row * (panel_height + gap)
        _draw_panel(image, plant, x, y, panel_width, panel_height)

    return image


def render_blank_display() -> Image.Image:
    """Render an all-white image used to reset the e-ink display."""
    return Image.new("1", (DISPLAY_WIDTH, DISPLAY_HEIGHT), 255)
