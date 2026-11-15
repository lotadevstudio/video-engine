
import os
from pathlib import Path


def generate(
    text: str,
    output: Path,
    voice: str,
    model: str = "eleven_multilingual_v2"
):
    from elevenlabs.client import ElevenLabs

    api_key = os.getenv("ELEVENLABS_API_KEY")

    if not api_key:
        raise ValueError("ELEVENLABS_API_KEY is not configured.")

    temporary_output = output.with_name(
        output.stem + ".tmp" + output.suffix
    )

    try:
        client = ElevenLabs(api_key=api_key)

        audio = client.text_to_speech.convert(
            text=text,
            voice_id=voice,
            model_id=model,
            output_format="mp3_44100_128"
        )

        with temporary_output.open("wb") as file:
            for chunk in audio:
                file.write(chunk)

        if not temporary_output.is_file() or temporary_output.stat().st_size == 0:
            raise RuntimeError("ElevenLabs generated an empty audio file.")

        temporary_output.replace(output)

    except Exception:
        temporary_output.unlink(missing_ok=True)
        raise
