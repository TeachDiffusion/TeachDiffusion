"""Compositor — assembles final teaching videos using FFmpeg.

Combines: teacher video clips + math animation overlays + audio narration
into a single polished MP4 output.
"""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from teachdiffusion.video.generator import GeneratedClip
from teachdiffusion.video.voice_engine import AudioClip


@dataclass
class CompositeResult:
    """Result of video compositing."""

    output_path: str
    total_duration_seconds: float
    num_clips: int
    is_stub: bool = False


class Compositor:
    """Assembles final teaching videos from component clips.

    Usage:
        compositor = Compositor(output_dir="./outputs/final")
        result = compositor.composite(
            video_clips=video_clips,
            audio_clips=audio_clips,
            animation_paths=animation_paths,
            output_name="quadratic_lesson"
        )
    """

    def __init__(self, output_dir: str = "./outputs/final") -> None:
        self._output_dir = Path(output_dir)
        self._output_dir.mkdir(parents=True, exist_ok=True)
        self._ffmpeg_available = self._check_ffmpeg()

    def _check_ffmpeg(self) -> bool:
        """Check if FFmpeg is available."""
        return shutil.which("ffmpeg") is not None

    def composite(
        self,
        video_clips: list[GeneratedClip],
        audio_clips: list[AudioClip] | None = None,
        animation_paths: list[str] | None = None,
        output_name: str = "lesson",
    ) -> CompositeResult:
        """Composite all clips into a final video.

        Args:
            video_clips: Generated teacher video clips.
            audio_clips: Audio narration clips (matched by step number).
            animation_paths: Paths to Manim animation overlays.
            output_name: Base name for the output file.

        Returns:
            CompositeResult with path to final video.
        """
        if not self._ffmpeg_available or any(c.is_stub for c in video_clips):
            return self._composite_stub(
                video_clips, audio_clips, animation_paths, output_name
            )

        return self._composite_real(
            video_clips, audio_clips, animation_paths, output_name
        )

    def _composite_real(
        self,
        video_clips: list[GeneratedClip],
        audio_clips: list[AudioClip] | None,
        animation_paths: list[str] | None,
        output_name: str,
    ) -> CompositeResult:
        """Real compositing using FFmpeg."""
        # Create a concat file for FFmpeg
        concat_path = self._output_dir / f"{output_name}_concat.txt"
        with open(concat_path, "w") as f:
            for clip in video_clips:
                f.write(f"file '{clip.video_path}'\n")

        output_path = self._output_dir / f"{output_name}.mp4"

        # Step 1: Concatenate video clips
        concat_cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_path),
            "-c", "copy",
            str(output_path),
        ]

        try:
            subprocess.run(concat_cmd, capture_output=True, check=True, timeout=300)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            return self._composite_stub(
                video_clips, audio_clips, animation_paths, output_name
            )

        # Step 2: Add audio if available
        if audio_clips:
            audio_output = self._output_dir / f"{output_name}_with_audio.mp4"
            # Concatenate audio files first
            audio_concat = self._output_dir / f"{output_name}_audio_concat.txt"
            with open(audio_concat, "w") as f:
                for ac in audio_clips:
                    if not ac.is_stub and Path(ac.audio_path).suffix == ".wav":
                        f.write(f"file '{ac.audio_path}'\n")

            if Path(audio_concat).stat().st_size > 0:
                merged_audio = self._output_dir / f"{output_name}_audio.wav"
                subprocess.run(
                    ["ffmpeg", "-y", "-f", "concat", "-safe", "0",
                     "-i", str(audio_concat), "-c", "copy", str(merged_audio)],
                    capture_output=True, timeout=120,
                )

                # Merge audio with video
                subprocess.run(
                    ["ffmpeg", "-y",
                     "-i", str(output_path),
                     "-i", str(merged_audio),
                     "-c:v", "copy", "-c:a", "aac",
                     "-shortest", str(audio_output)],
                    capture_output=True, timeout=300,
                )

                if audio_output.exists():
                    output_path = audio_output

        # Clean up concat files
        concat_path.unlink(missing_ok=True)

        total_duration = sum(c.duration_seconds for c in video_clips)

        return CompositeResult(
            output_path=str(output_path),
            total_duration_seconds=total_duration,
            num_clips=len(video_clips),
        )

    def _composite_stub(
        self,
        video_clips: list[GeneratedClip],
        audio_clips: list[AudioClip] | None,
        animation_paths: list[str] | None,
        output_name: str,
    ) -> CompositeResult:
        """Create a stub composite report."""
        output_path = self._output_dir / f"{output_name}_composite_stub.txt"
        total_duration = sum(c.duration_seconds for c in video_clips)

        with open(output_path, "w") as f:
            f.write(f"TeachDiffusion Composite Stub — {output_name}\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Total clips: {len(video_clips)}\n")
            f.write(f"Total duration: {total_duration:.1f}s ({total_duration / 60:.1f}min)\n\n")

            f.write("Video Clips:\n")
            for clip in video_clips:
                f.write(f"  Step {clip.step_number}: {clip.video_path} ({clip.duration_seconds}s)\n")
                f.write(f"    Prompt: {clip.prompt_used[:100]}...\n")

            if audio_clips:
                f.write("\nAudio Clips:\n")
                for ac in audio_clips:
                    f.write(f"  Step {ac.step_number}: {ac.audio_path} ({ac.duration_seconds:.1f}s)\n")

            if animation_paths:
                f.write("\nAnimation Overlays:\n")
                for ap in animation_paths:
                    f.write(f"  {ap}\n")

            f.write(f"\nNote: Install FFmpeg for real compositing.\n")
            f.write(f"GPU required for actual video generation.\n")

        return CompositeResult(
            output_path=str(output_path),
            total_duration_seconds=total_duration,
            num_clips=len(video_clips),
            is_stub=True,
        )
