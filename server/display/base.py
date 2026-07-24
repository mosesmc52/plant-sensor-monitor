from abc import ABC, abstractmethod

from PIL import Image


class Display(ABC):
    """Abstract display interface."""

    @abstractmethod
    def initialize(self) -> None:
        """Initialize the display hardware."""
        raise NotImplementedError

    @abstractmethod
    def show(self, image: Image.Image) -> None:
        """Render a completed Pillow image."""
        raise NotImplementedError

    @abstractmethod
    def sleep(self) -> None:
        """Put the display into low-power mode."""
        raise NotImplementedError

    @abstractmethod
    def shutdown(self) -> None:
        """Release hardware resources."""
        raise NotImplementedError
