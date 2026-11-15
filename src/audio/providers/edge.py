
import asyncio
from pathlib import Path

import edge_tts


async def _generate(text: str, output: Path, voice: str):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(str(output))


def generate(text: str, output: Path, voice: str):
    temporary_output = output.with_name(
        output.stem + ".tmp" + output.suffix
    )

    try:
        asyncio.run(_generate(text, temporary_output, voice))

        if not temporary_output.is_file() or temporary_output.stat().st_size == 0:
            raise RuntimeError("Edge TTS generated an empty audio file.")

        temporary_output.replace(output)

    except Exception:
        temporary_output.unlink(missing_ok=True)
        raise
