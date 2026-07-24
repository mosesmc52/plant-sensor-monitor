"""Display backend compatibility module."""

from .base import Display
from .preview import PreviewDisplay
from .waveshare import WaveshareDisplay

__all__ = ["Display", "PreviewDisplay", "WaveshareDisplay"]
