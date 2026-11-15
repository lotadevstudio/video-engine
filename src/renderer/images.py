
from pathlib import Path
import re


def get_scene_images(scene_dir):
    """Return scene shot images in numeric order."""

    images_dir = Path(scene_dir) / "assets" / "images"

    if not images_dir.exists():
        raise FileNotFoundError(
            f"Scene images directory not found: {images_dir}"
        )

    images = []

    for image_path in images_dir.glob("shot_*.png"):
        match = re.fullmatch(r"shot_(\d+)\.png", image_path.name)

        if match:
            shot_number = int(match.group(1))
            images.append((shot_number, image_path))

    images.sort(key=lambda item: item[0])

    if not images:
        raise FileNotFoundError(
            f"No shot images found in: {images_dir}"
        )

    return [image_path for _, image_path in images]
