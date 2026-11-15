
import shutil
import subprocess
from pathlib import Path


SUPPORTED_MOTIONS = {
    "static",
    "slow_zoom_in",
    "slow_zoom_out",
    "slow_pan_left",
    "slow_pan_right"
}


def create_motion_segment(
    image_path,
    output_path,
    frames,
    resolution=(854, 480),
    fps=24,
    motion_type="static",
    intensity=0.03
):
    """Convert a still image into a video segment with configurable motion."""

    image_path = Path(image_path)
    output_path = Path(output_path)

    width, height = resolution

    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    if not shutil.which("ffmpeg"):
        raise RuntimeError("FFmpeg is not installed or not in PATH.")

    if frames < 1:
        raise ValueError("Frames must be greater than zero.")

    if fps < 1:
        raise ValueError("FPS must be greater than zero.")

    if width < 2 or height < 2 or width % 2 or height % 2:
        raise ValueError("Resolution must contain positive even dimensions.")

    if motion_type not in SUPPORTED_MOTIONS:
        raise ValueError(f"Unsupported motion type: {motion_type}")

    if not 0 <= intensity <= 0.15:
        raise ValueError("Motion intensity must be between 0 and 0.15.")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    temp_path = output_path.with_name(
        output_path.stem + ".tmp" + output_path.suffix
    )

    # Prepare the image for video rendering.
    base_filter = (
        f"scale={width}:{height}:force_original_aspect_ratio=increase,"
        f"crop={width}:{height},"
        "setsar=1,"
    )

    # Static images do not need zoompan.
    if motion_type == "static":
        video_filter = (
            base_filter
            + f"fps={fps},"
            + f"trim=end_frame={frames},"
            + "setpts=PTS-STARTPTS"
        )

    else:
        progress = f"on/{max(frames - 1, 1)}"
        amount = f"{intensity:.6f}"

        if motion_type == "slow_zoom_in":
            zoom = f"1+{amount}*{progress}"
            x = "iw/2-(iw/zoom/2)"
            y = "ih/2-(ih/zoom/2)"

        elif motion_type == "slow_zoom_out":
            zoom = f"1+{amount}*(1-{progress})"
            x = "iw/2-(iw/zoom/2)"
            y = "ih/2-(ih/zoom/2)"

        elif motion_type == "slow_pan_right":
            zoom = f"1+{amount}"
            x = f"(iw-iw/zoom)*{progress}"
            y = "ih/2-(ih/zoom/2)"

        elif motion_type == "slow_pan_left":
            zoom = f"1+{amount}"
            x = f"(iw-iw/zoom)*(1-{progress})"
            y = "ih/2-(ih/zoom/2)"

        video_filter = (
            base_filter
            + f"zoompan=z='{zoom}':"
            + f"x='{x}':"
            + f"y='{y}':"
            + f"d=1:s={width}x{height}:fps={fps},"
            + f"trim=end_frame={frames},"
            + "setpts=PTS-STARTPTS"
        )

    command = [
        "ffmpeg",
        "-y",
        "-loglevel", "error",
        "-loop", "1",
        "-framerate", str(fps),
        "-i", str(image_path),
        "-vf", video_filter,
        "-frames:v", str(frames),
        "-an",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "23",
        "-pix_fmt", "yuv420p",
        str(temp_path)
    ]

    try:
        subprocess.run(command, check=True)

        if not temp_path.exists() or temp_path.stat().st_size == 0:
            raise RuntimeError("FFmpeg did not produce a valid video segment.")

        temp_path.replace(output_path)

    finally:
        if temp_path.exists():
            temp_path.unlink()

    return output_path
