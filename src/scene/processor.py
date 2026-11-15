
import json
from pathlib import Path
from typing import Union

from src.audio.generator import generate_audio
from src.visuals.generator import generate_image


def process_scene(
    project_dir: Union[str, Path],
    scene: dict,
    provider: str = "edge",
    voice: str = None,
    reference_paths: dict = None,
    visual_source: str = "ai",
    visual_provider: str = "cloudflare",
    width: int = 1024,
    height: int = 576,
    overwrite_audio: bool = False,
    overwrite_images: bool = False
) -> Path:
    """Initialize a scene and generate its narration and visual shots."""

    number = scene.get("number")
    title = scene.get("title")
    narration = scene.get("narration")
    shots = scene.get("shots", [])

    if not isinstance(number, int) or isinstance(number, bool) or number < 1:
        raise ValueError("Scene number must be a positive integer.")

    if not isinstance(title, str) or not title.strip():
        raise ValueError("Scene title cannot be empty.")

    if not isinstance(narration, str) or not narration.strip():
        raise ValueError("Scene narration cannot be empty.")

    if not isinstance(shots, list):
        raise ValueError(f"Scene {number}: shots must be a list.")

    project_dir = Path(project_dir)
    reference_paths = reference_paths or {}

    scene_dir = project_dir / "scenes" / f"scene_{number:03d}"

    # Create scene directories
    directories = [
        "assets/images",
        "assets/videos"
    ]

    scene_dir.mkdir(parents=True, exist_ok=True)

    for directory in directories:
        (scene_dir / directory).mkdir(parents=True, exist_ok=True)

    # Save scene configuration
    scene_config = scene_dir / "scene.json"

    with scene_config.open("w", encoding="utf-8") as file:
        json.dump(scene, file, indent=4, ensure_ascii=False)

    # Generate narration
    narration_path = scene_dir / "narration.mp3"

    generate_audio(
        text=narration,
        output_path=str(narration_path),
        provider=provider,
        voice=voice,
        overwrite=overwrite_audio
    )

    # Generate visual shots
    print("\n" + "=" * 55)
    print(f"GENERATING SHOTS: SCENE {number:03d}")
    print("=" * 55)

    for index, shot in enumerate(shots, start=1):
        shot_id = shot.get("id")
        description = shot.get("description")
        reference_ids = shot.get("references", [])

        if not isinstance(shot_id, int) or isinstance(shot_id, bool) or shot_id < 1:
            raise ValueError(
                f"Scene {number}: shot ID must be a positive integer."
            )

        if not isinstance(description, str) or not description.strip():
            raise ValueError(
                f"Scene {number}, shot {shot_id}: description is required."
            )

        if not isinstance(reference_ids, list):
            raise ValueError(
                f"Scene {number}, shot {shot_id}: references must be a list."
            )

        # Resolve reference IDs to actual image paths
        resolved_references = []

        for reference_id in reference_ids:
            if reference_id not in reference_paths:
                raise ValueError(
                    f"Unknown reference '{reference_id}' "
                    f"in scene {number}, shot {shot_id}."
                )

            resolved_references.append(reference_paths[reference_id])

        image_path = (
            scene_dir / "assets" / "images" / f"shot_{shot_id:03d}.png"
        )

        print(f"\nShot {index}/{len(shots)}: {shot_id}")

        generate_image(
            prompt=description,
            output_path=image_path,
            source=visual_source,
            provider=visual_provider,
            reference_images=resolved_references,
            width=width,
            height=height,
            overwrite=overwrite_images
        )

    print(f"\nScene {number:03d} processed successfully!")
    print(f"Title: {title}")
    print(f"Location: {scene_dir}")

    return scene_dir
