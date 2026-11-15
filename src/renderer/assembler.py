
import shutil
import subprocess
from pathlib import Path


def assemble_video(
    project_dir,
    scenes,
    output_filename="final_video.mp4",
    overwrite=False
):
    """Combine rendered scene videos into one complete video."""

    project_dir = Path(project_dir).resolve()
    renders_dir = project_dir / "renders"

    if not renders_dir.is_dir():
        raise FileNotFoundError(
            f"Renders directory not found: {renders_dir}"
        )

    if not shutil.which("ffmpeg"):
        raise RuntimeError(
            "FFmpeg is not installed or not in PATH."
        )

    if not isinstance(scenes, list) or not scenes:
        raise ValueError("Project must contain at least one scene.")

    if (
        not isinstance(output_filename, str)
        or not output_filename.strip()
        or Path(output_filename).name != output_filename
        or not output_filename.endswith(".mp4")
    ):
        raise ValueError("Output filename must be a valid MP4 filename.")

    # Step 1: Resolve scene videos in project.json order.
    scene_videos = []
    seen_numbers = set()

    for scene in scenes:
        if not isinstance(scene, dict):
            raise ValueError("Every scene must be a JSON object.")

        number = scene.get("number")

        if (
            not isinstance(number, int)
            or isinstance(number, bool)
            or number < 1
        ):
            raise ValueError(
                f"Invalid scene number: {number}"
            )

        if number in seen_numbers:
            raise ValueError(
                f"Duplicate scene number: {number}"
            )

        seen_numbers.add(number)

        scene_video = renders_dir / f"scene_{number:03d}.mp4"

        if not scene_video.is_file():
            raise FileNotFoundError(
                f"Rendered scene video not found: {scene_video}"
            )

        scene_videos.append(scene_video)

    # Step 2: Prepare the final output path.
    output_path = renders_dir / output_filename

    if output_path.exists() and not overwrite:
        print(f"\nFinal video already exists: {output_path}")
        return output_path

    # Step 3: Create the FFmpeg concat list.
    concat_file = renders_dir / "assembly_concat.txt"

    with concat_file.open("w", encoding="utf-8") as file:
        for scene_video in scene_videos:
            file.write(f"file '{scene_video.name}'\n")

    temp_output = output_path.with_name(
        output_path.stem + ".tmp" + output_path.suffix
    )

    # Step 4: Assemble the scenes.
    command = [
        "ffmpeg",
        "-y",
        "-loglevel", "error",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_file.name,
        "-c", "copy",
        "-movflags", "+faststart",
        str(temp_output)
    ]

    try:
        print("\n" + "=" * 55)
        print("ASSEMBLING FINAL VIDEO")
        print("=" * 55)

        print(f"Number of scenes: {len(scene_videos)}")

        for index, scene_video in enumerate(scene_videos, start=1):
            print(f"Scene {index}: {scene_video.name}")

        print("\nJoining scenes...")

        subprocess.run(
            command,
            check=True,
            cwd=str(renders_dir)
        )

        if (
            not temp_output.exists()
            or temp_output.stat().st_size == 0
        ):
            raise RuntimeError(
                "FFmpeg did not produce a valid final video."
            )

        temp_output.replace(output_path)

    finally:
        if concat_file.exists():
            concat_file.unlink()

        if temp_output.exists():
            temp_output.unlink()

    print("\n" + "=" * 55)
    print("FINAL VIDEO ASSEMBLED SUCCESSFULLY!")
    print("=" * 55)
    print(f"Output: {output_path}")

    return output_path
