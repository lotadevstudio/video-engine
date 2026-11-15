
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.audio.generator import generate_audio


class AudioGeneratorTests(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.output = Path(self.temp_dir.name) / "narration.mp3"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_existing_audio_is_skipped(self):
        self.output.write_bytes(b"existing audio")

        with patch("src.audio.generator.edge.generate") as mock_edge:
            result = generate_audio(
                "Test narration",
                str(self.output),
                provider="edge"
            )

        self.assertEqual(result, self.output)
        mock_edge.assert_not_called()

    def test_overwrite_forces_regeneration(self):
        self.output.write_bytes(b"old audio")

        def fake_generate(text, output, voice):
            output.write_bytes(b"new audio")

        with patch(
            "src.audio.generator.edge.generate",
            side_effect=fake_generate
        ):
            generate_audio(
                "New narration",
                str(self.output),
                provider="edge",
                overwrite=True
            )

        self.assertEqual(self.output.read_bytes(), b"new audio")

    def test_failed_generation_preserves_existing_audio(self):
        self.output.write_bytes(b"original audio")

        with patch(
            "src.audio.generator.edge.generate",
            side_effect=RuntimeError("Simulated failure")
        ):
            with self.assertRaises(RuntimeError):
                generate_audio(
                    "Replacement narration",
                    str(self.output),
                    provider="edge",
                    overwrite=True
                )

        self.assertEqual(self.output.read_bytes(), b"original audio")

    def test_failed_generation_does_not_create_final_file(self):
        with patch(
            "src.audio.generator.edge.generate",
            side_effect=RuntimeError("Simulated failure")
        ):
            with self.assertRaises(RuntimeError):
                generate_audio(
                    "Test narration",
                    str(self.output),
                    provider="edge"
                )

        self.assertFalse(self.output.exists())

    def test_elevenlabs_dispatch(self):
        with patch("src.audio.generator.elevenlabs.generate") as mock_elevenlabs:
            mock_elevenlabs.return_value = None

            generate_audio(
                "Production narration",
                str(self.output),
                provider="elevenlabs",
                voice="test_voice_id"
            )

            mock_elevenlabs.assert_called_once()

    def test_unsupported_provider(self):
        with self.assertRaises(ValueError):
            generate_audio(
                "Test narration",
                str(self.output),
                provider="unknown"
            )


if __name__ == "__main__":
    unittest.main()
