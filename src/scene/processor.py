
import json
from pathlib import Path
from typing import Union

from src.audio.generator import generate_audio


def process_scene(
    project_dir: Union[str, Path],
    scene: dict,
    provider: str = "edge",
    voice: str = None,
    overwrite_audio: bool = False
) -> Path:
    """Initialize a scene and generate its narration."""

    number = scene.get("number")
    title = scene.get("title")
    narration = scene.get("narration")

    if not isinstance(number, int) or isinstance(number, bool) or number < 1:
        raise ValueError("Scene number must be a positive integer.")

    if not isinstance(title, str) or not title.strip():
        raise ValueError("Scene title cannot be empty.")

    if not isinstance(narration, str) or not narration.strip():
        raise ValueError("Scene narration cannot be empty.")

    project_dir = Path(project_dir)

    scene_dir = project_dir / "scenes" / f"scene_{number:03d}"

    # Create scene directories.
    directories = [
        "assets/images",
        "assets/videos"
    ]

    scene_dir.mkdir(parents=True, exist_ok=True)

    for directory in directories:
        (scene_dir / directory).mkdir(parents=True, exist_ok=True)

    # Save scene configuration.
    scene_config = scene_dir / "scene.json"

    with scene_config.open("w", encoding="utf-8") as file:
        json.dump(scene, file, indent=4, ensure_ascii=False)

    # Generate narration.
    narration_path = scene_dir / "narration.mp3"

    generate_audio(
        text=narration,
        output_path=str(narration_path),
        provider=provider,
        voice=voice,
        overwrite=overwrite_audio
    )

    print(f"\nScene {number:03d} processed successfully!")
    print(f"Title: {title}")
    print(f"Location: {scene_dir}")

    return scene_dir
