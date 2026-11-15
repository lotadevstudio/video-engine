
import subprocess
from pathlib import Path


def get_audio_duration(audio_path):
    """Return the duration of an audio file in seconds."""

    audio_path = Path(audio_path)

    if not audio_path.exists():
        raise FileNotFoundError(
            f"Narration file not found: {audio_path}"
        )

    result = subprocess.run(
        [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(audio_path)
        ],
        capture_output=True,
        text=True,
        check=True
    )

    try:
        duration = float(result.stdout.strip())
    except ValueError:
        raise ValueError(
            f"Could not read audio duration: {audio_path}"
        )

    if duration <= 0:
        raise ValueError("Audio duration must be greater than zero.")

    return duration
