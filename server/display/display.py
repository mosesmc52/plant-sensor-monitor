"""Display backend compatibility module."""

import os

from .base import Display
from .preview import PreviewDisplay
from .waveshare import WaveshareDisplay

__all__ = ["Display", "PreviewDisplay", "WaveshareDisplay", "create_display"]


def create_display() -> Display:
    backend = os.getenv("DISPLAY_BACKEND", "preview")

    if backend == "waveshare":
        return WaveshareDisplay()

    if backend == "preview":
        return PreviewDisplay()

    raise ValueError(
        f"Unsupported DISPLAY_BACKEND={backend!r}; use 'preview' or 'waveshare'."
    )
