"""Video Generator — generates teacher video clips from TeachingSteps.

Orchestrates the Wan 2.2 model to produce video clips for each
step in a TeachingScript, using the pedagogy-conditioned prompts.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from teachdiffusion.pedagogy.schema import TeachingScript, TeachingStep
from teachdiffusion.video.wan_lora import GenerationConfig, WanLoRAModel


@dataclass
class GeneratedClip:
    """A generated video clip for a single teaching step."""

    step_number: int
    video_path: str
    prompt_used: str
    duration_seconds: float
    is_stub: bool = False


class VideoGenerator:
    """Generates video clips for each step in a teaching script.

    Usage:
        generator = VideoGenerator()
        clips = generator.generate_clips(teaching_script)
    """

    def __init__(
        self,
        model: WanLoRAModel | None = None,
        output_dir: str = "./outputs/clips",
    ) -> None:
        self._model = model or WanLoRAModel(stub_mode=True)
        self._output_dir = Path(output_dir)
        self._output_dir.mkdir(parents=True, exist_ok=True)

    def generate_clip(
        self,
        step: TeachingStep,
        persona: str = "Professor Aria",
        config: GenerationConfig | None = None,
    ) -> GeneratedClip:
        """Generate a single video clip for a teaching step.

        Args:
            step: The TeachingStep to generate video for.
            persona: Name of the teacher persona.
            config: Video generation config.

        Returns:
            GeneratedClip with path to the generated video.
        """
        prompt = step.to_video_prompt(persona)
        ext = ".mp4" if not self._model.is_stub else ".txt"
        output_path = str(
            self._output_dir / f"step_{step.step_number:03d}{ext}"
        )

        video_path = self._model.generate(
            prompt=prompt,
            config=config,
            output_path=output_path,
        )

        return GeneratedClip(
            step_number=step.step_number,
            video_path=video_path,
            prompt_used=prompt,
            duration_seconds=step.duration_seconds,
            is_stub=self._model.is_stub,
        )

    def generate_clips(
        self,
        script: TeachingScript,
        config: GenerationConfig | None = None,
    ) -> list[GeneratedClip]:
        """Generate video clips for all steps in a teaching script.

        Args:
            script: Complete TeachingScript.
            config: Video generation config.

        Returns:
            List of GeneratedClips, one per step.
        """
        clips = []
        for step in script.steps:
            clip = self.generate_clip(
                step=step,
                persona=script.persona,
                config=config,
            )
            clips.append(clip)
        return clips
