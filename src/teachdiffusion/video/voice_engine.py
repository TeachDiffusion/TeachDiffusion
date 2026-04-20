"""Voice Engine — text-to-speech with teacher pacing and intonation.

Generates audio narration for each teaching step, with pacing
that matches the pedagogical intent (slow for new concepts,
normal for review, pauses for student thinking).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from teachdiffusion.pedagogy.schema import PacingType, TeachingStep


@dataclass
class AudioClip:
    """Generated audio for a teaching step."""

    step_number: int
    audio_path: str
    text: str
    duration_seconds: float
    is_stub: bool = False


class VoiceEngine:
    """Text-to-speech engine for teaching narration.

    Supports Kokoro TTS (open source) and falls back to stub mode.

    Usage:
        engine = VoiceEngine()
        audio = engine.synthesize(teaching_step)
    """

    # Pacing maps to speech rate multipliers
    PACING_RATES = {
        PacingType.SLOW: 0.8,
        PacingType.NORMAL: 1.0,
        PacingType.FAST: 1.2,
        PacingType.PAUSE: 0.7,
    }

    def __init__(
        self,
        output_dir: str = "./outputs/audio",
        voice: str = "af_heart",  # Kokoro voice ID
    ) -> None:
        self._output_dir = Path(output_dir)
        self._output_dir.mkdir(parents=True, exist_ok=True)
        self._voice = voice
        self._tts_available = self._check_tts()

    def _check_tts(self) -> bool:
        """Check if Kokoro TTS is available."""
        try:
            import kokoro  # noqa: F401
            return True
        except ImportError:
            return False

    def synthesize(self, step: TeachingStep) -> AudioClip:
        """Generate audio for a teaching step.

        Args:
            step: The TeachingStep to narrate.

        Returns:
            AudioClip with path to the generated audio.
        """
        if self._tts_available:
            try:
                return self._synthesize_kokoro(step)
            except Exception:
                pass

        return self._synthesize_stub(step)

    def synthesize_text(self, text: str, filename: str = "output") -> AudioClip:
        """Synthesize arbitrary text (convenience method)."""
        step = TeachingStep(
            step_number=0,
            step_type="build_intuition",
            content=text,
        )
        return self.synthesize(step)

    def _synthesize_kokoro(self, step: TeachingStep) -> AudioClip:
        """Synthesize using Kokoro TTS."""
        import kokoro
        import soundfile as sf

        rate = self.PACING_RATES.get(step.pacing, 1.0)
        output_path = self._output_dir / f"step_{step.step_number:03d}.wav"

        pipeline = kokoro.KPipeline(lang_code="a")
        audio_data = None
        sample_rate = 24000

        for _, _, audio_chunk in pipeline(step.content, voice=self._voice, speed=rate):
            if audio_data is None:
                audio_data = audio_chunk
            else:
                import numpy as np
                audio_data = np.concatenate([audio_data, audio_chunk])

        if audio_data is not None:
            sf.write(str(output_path), audio_data, sample_rate)
            duration = len(audio_data) / sample_rate
        else:
            duration = step.duration_seconds

        return AudioClip(
            step_number=step.step_number,
            audio_path=str(output_path),
            text=step.content,
            duration_seconds=duration,
        )

    def _synthesize_stub(self, step: TeachingStep) -> AudioClip:
        """Create a stub when TTS is not available."""
        output_path = self._output_dir / f"step_{step.step_number:03d}_stub.txt"

        rate = self.PACING_RATES.get(step.pacing, 1.0)
        # Estimate duration: ~150 words per minute at normal speed
        word_count = len(step.content.split())
        estimated_duration = (word_count / 150) * 60 / rate

        with open(output_path, "w") as f:
            f.write(f"Audio Stub — Step {step.step_number}\n")
            f.write(f"Text: {step.content}\n")
            f.write(f"Pacing: {step.pacing.value} (rate: {rate}x)\n")
            f.write(f"Estimated duration: {estimated_duration:.1f}s\n")
            f.write(f"\nInstall Kokoro for TTS: pip install kokoro soundfile\n")

        return AudioClip(
            step_number=step.step_number,
            audio_path=str(output_path),
            text=step.content,
            duration_seconds=estimated_duration,
            is_stub=True,
        )

    def batch_synthesize(self, steps: list[TeachingStep]) -> list[AudioClip]:
        """Synthesize audio for multiple steps."""
        return [self.synthesize(step) for step in steps]
