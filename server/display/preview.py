from pathlib import Path

from PIL import Image

from .base import Display


class PreviewDisplay(Display):
    def __init__(
        self,
        output_path: Path = Path("output/display.png"),
    ) -> None:
        self.output_path = output_path

    def initialize(self) -> None:
        """Preview output has no hardware to initialize."""

    def sleep(self) -> None:
        """Preview output has no sleep state."""

    def shutdown(self) -> None:
        """Preview output has no resources to release."""

    def show(self, image: Image.Image) -> None:
        self.output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        image.save(self.output_path)

        print(f"Display preview saved to " f"{self.output_path.resolve()}")
