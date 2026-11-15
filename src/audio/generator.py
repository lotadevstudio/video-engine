
from pathlib import Path

from .providers import edge, elevenlabs


def generate_audio(
    text: str,
    output_path: str,
    provider: str = "edge",
    voice: str = None,
    model: str = "eleven_multilingual_v2",
    overwrite: bool = False
) -> Path:
    """Generate narration using the selected TTS provider."""

    if not text.strip():
        raise ValueError("Narration text cannot be empty.")

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    # Skip generation if a valid output already exists.
    if output.is_file() and output.stat().st_size > 0 and not overwrite:
        print(f"Audio already exists. Skipping: {output}")
        return output

    print(f"Generating audio using {provider}: {output}")

    if provider == "edge":
        voice = voice or "en-US-AriaNeural"
        edge.generate(text, output, voice)

    elif provider == "elevenlabs":
        if not voice:
            raise ValueError("An ElevenLabs voice ID is required.")

        elevenlabs.generate(text, output, voice, model)

    else:
        raise ValueError(f"Unsupported audio provider: {provider}")

    # Confirm that generation actually produced a file.
    if not output.is_file() or output.stat().st_size == 0:
        raise RuntimeError(f"Audio generation failed: {output}")

    print(f"Audio generated successfully: {output}")

    return output
