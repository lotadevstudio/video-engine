
import json
import shutil
import subprocess
from pathlib import Path

from .audio import get_audio_duration
from .images import get_scene_images
from .motion import create_motion_segment


def render_scene(
    scene_config_path,
    resolution,
    fps,
    overwrite=False
):
    """Render a complete scene using its saved configuration."""

    # Step 1: Validate the scene configuration path.
    scene_config_path = Path(scene_config_path).resolve()

    if not scene_config_path.is_file():
        raise FileNotFoundError(
            f"Scene configuration not found: {scene_config_path}"
        )

    scene_dir = scene_config_path.parent

    if not shutil.which("ffmpeg"):
        raise RuntimeError(
            "FFmpeg is not installed or not in PATH."
        )

    # Step 2: Validate rendering settings.
    if (
        not isinstance(resolution, (list, tuple))
        or len(resolution) != 2
    ):
        raise ValueError(
            "Resolution must contain exactly two dimensions."
        )

    width, height = resolution

    if (
        not isinstance(width, int)
        or isinstance(width, bool)
        or not isinstance(height, int)
        or isinstance(height, bool)
        or width < 2
        or height < 2
        or width % 2
        or height % 2
    ):
        raise ValueError(
            "Resolution must contain positive even integer dimensions."
        )

    if (
        not isinstance(fps, (int, float))
        or isinstance(fps, bool)
        or fps <= 0
    ):
        raise ValueError("FPS must be a positive number.")

    # Step 3: Load scene instructions.
    with scene_config_path.open("r", encoding="utf-8") as file:
        scene_data = json.load(file)

    if not isinstance(scene_data, dict):
        raise ValueError("Scene configuration must be a JSON object.")

    scene_defaults = scene_data.get("defaults", {})

    if not isinstance(scene_defaults, dict):
        raise ValueError("Scene defaults must be a JSON object.")

    default_motion = scene_defaults.get(
        "motion",
        {"type": "static", "intensity": 0.03}
    )

    if not isinstance(default_motion, dict):
        raise ValueError("Default motion must be a JSON object.")

    # Step 4: Index shot configurations by ID.
    scene_shots = scene_data.get("shots", [])

    if not isinstance(scene_shots, list) or not scene_shots:
        raise ValueError("Scene must contain at least one shot.")

    shots = {}

    for shot in scene_shots:
        if not isinstance(shot, dict):
            raise ValueError("Every shot configuration must be an object.")

        shot_id = shot.get("id")

        if (
            not isinstance(shot_id, int)
            or isinstance(shot_id, bool)
            or shot_id < 1
        ):
            raise ValueError(
                f"Invalid shot ID: {shot_id}"
            )

        if shot_id in shots:
            raise ValueError(f"Duplicate shot ID: {shot_id}")

        shot_motion = shot.get("motion", {})

        if not isinstance(shot_motion, dict):
            raise ValueError(
                f"Motion configuration for shot {shot_id} must be an object."
            )

        shots[shot_id] = shot

    # Step 5: Resolve scene assets and output paths.
    project_dir = scene_dir.parent.parent

    audio_path = scene_dir / "narration.mp3"
    videos_dir = scene_dir / "assets" / "videos"

    output_dir = project_dir / "renders"
    output_path = output_dir / f"{scene_dir.name}.mp4"

    if not audio_path.is_file():
        raise FileNotFoundError(
            f"Scene narration not found: {audio_path}"
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    videos_dir.mkdir(parents=True, exist_ok=True)

    # Skip an existing render unless overwrite is enabled.
    if output_path.exists() and not overwrite:
        print(f"Render already exists: {output_path}")
        return output_path

    # Step 6: Read narration duration and discover images.
    duration = get_audio_duration(audio_path)

    images = get_scene_images(scene_dir)

    if len(images) != len(shots):
        raise ValueError(
            f"Shot mismatch: configuration contains {len(shots)} shots, "
            f"but {len(images)} images were found."
        )

    # Match each image to its shot configuration.
    image_shots = []

    for image_path in images:
        try:
            shot_number = int(
                image_path.stem.split("_")[-1]
            )
        except ValueError:
            raise ValueError(
                f"Invalid shot image filename: {image_path.name}"
            )

        if shot_number not in shots:
            raise ValueError(
                f"No shot configuration found for image: {image_path.name}"
            )

        image_shots.append((image_path, shots[shot_number]))

    # Step 7: Calculate total frames and distribute them across shots.
    total_frames = round(duration * fps)

    if total_frames < len(image_shots):
        raise ValueError(
            "Not enough video frames to allocate at least one "
            "frame to every shot."
        )

    base_frames = total_frames // len(image_shots)
    remaining_frames = total_frames % len(image_shots)

    print("\n" + "=" * 55)
    print(f"RENDERING: {scene_dir.name}")
    print("=" * 55)

    print(f"Scene: {scene_data.get('title', scene_dir.name)}")
    print(f"Narration duration: {duration:.3f} seconds")
    print(f"Number of shots: {len(image_shots)}")
    print(f"Resolution: {width}x{height}")
    print(f"Total frames: {total_frames}")
    print(f"Frame rate: {fps} FPS")

    # Step 8: Generate video segments.
    segments = []

    for index, (image_path, shot) in enumerate(image_shots):
        frames = base_frames

        if index < remaining_frames:
            frames += 1

        segment_path = videos_dir / f"{image_path.stem}.mp4"

        # Merge scene-level and shot-level motion settings.
        motion = {
            **default_motion,
            **shot.get("motion", {})
        }

        motion_type = motion.get("type", "static")
        intensity = motion.get("intensity", 0.03)

        print(
            f"\nGenerating shot {index + 1}/{len(image_shots)} "
            f"({frames} frames)..."
        )

        print(f"Motion: {motion_type}")

        create_motion_segment(
            image_path=image_path,
            output_path=segment_path,
            frames=frames,
            resolution=(width, height),
            fps=fps,
            motion_type=motion_type,
            intensity=intensity
        )

        segments.append(segment_path)

    # Step 9: Create an ordered FFmpeg concat list.
    concat_file = videos_dir / "concat.txt"

    with concat_file.open("w", encoding="utf-8") as file:
        for segment in segments:
            file.write(f"file '{segment.name}'\n")

    # Temporary output prevents incomplete renders being
    # mistaken for successfully completed videos.
    temp_output = output_path.with_name(
        output_path.stem + ".tmp" + output_path.suffix
    )

    # Step 10: Join segments and add narration.
    command = [
        "ffmpeg",
        "-y",
        "-loglevel", "error",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_file.name,
        "-i", str(audio_path),
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "128k",
        "-shortest",
        "-movflags", "+faststart",
        str(temp_output)
    ]

    try:
        print("\nJoining video segments and adding narration...")

        subprocess.run(
            command,
            check=True,
            cwd=str(videos_dir)
        )

        if not temp_output.exists() or temp_output.stat().st_size == 0:
            raise RuntimeError(
                "FFmpeg did not produce a valid scene video."
            )

        temp_output.replace(output_path)

    finally:
        if concat_file.exists():
            concat_file.unlink()

        if temp_output.exists():
            temp_output.unlink()

    print("\n" + "=" * 55)
    print("SCENE RENDERED SUCCESSFULLY!")
    print("=" * 55)
    print(f"Output: {output_path}")

    return output_path
