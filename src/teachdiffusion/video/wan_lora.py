"""Wan LoRA — LoRA adapter wrapper around Wan 2.2 video diffusion model.

Handles loading the base model, applying LoRA weights, and running
inference with pedagogy-conditioned prompts.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class GenerationConfig:
    """Configuration for video generation."""

    num_frames: int = 16
    fps: int = 8
    resolution: int = 480
    num_inference_steps: int = 50
    guidance_scale: float = 7.5
    seed: Optional[int] = None


class WanLoRAModel:
    """Wrapper around Wan 2.2 with LoRA for math teaching video generation.

    In stub mode (no GPU), returns placeholder paths.
    In full mode, loads the model and generates actual video frames.

    Usage:
        model = WanLoRAModel(lora_path="TeachDiffusion/teachdiffusion-v0.1")
        frames = model.generate("A teacher explaining quadratic equations...")
    """

    def __init__(
        self,
        base_model: str = "Wan-AI/Wan2.2-T2V-14B",
        lora_path: str = "",
        device: str = "auto",
        stub_mode: bool = True,
    ) -> None:
        self._base_model = base_model
        self._lora_path = lora_path
        self._device = device
        self._stub_mode = stub_mode or not self._gpu_available()
        self._pipeline = None

        if not self._stub_mode:
            self._load_model()

    def _gpu_available(self) -> bool:
        """Check if GPU is available."""
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            return False

    def _load_model(self) -> None:
        """Load the Wan 2.2 model with LoRA weights."""
        try:
            import torch
            from diffusers import DiffusionPipeline

            self._pipeline = DiffusionPipeline.from_pretrained(
                self._base_model,
                torch_dtype=torch.bfloat16,
            )

            if self._lora_path:
                self._pipeline.load_lora_weights(self._lora_path)

            if self._device == "auto":
                self._pipeline.to("cuda")
            else:
                self._pipeline.to(self._device)

        except Exception as e:
            print(f"Failed to load model: {e}")
            print("Falling back to stub mode.")
            self._stub_mode = True

    def generate(
        self,
        prompt: str,
        config: GenerationConfig | None = None,
        output_path: str = "",
    ) -> str:
        """Generate a video from a text prompt.

        Args:
            prompt: Text description of the video to generate.
            config: Generation configuration.
            output_path: Path to save the output video.

        Returns:
            Path to the generated video file.
        """
        config = config or GenerationConfig()

        if self._stub_mode:
            return self._generate_stub(prompt, config, output_path)

        return self._generate_real(prompt, config, output_path)

    def _generate_real(
        self, prompt: str, config: GenerationConfig, output_path: str
    ) -> str:
        """Generate video using the actual model."""
        import torch

        generator = None
        if config.seed is not None:
            generator = torch.Generator(device="cuda").manual_seed(config.seed)

        output = self._pipeline(
            prompt=prompt,
            num_frames=config.num_frames,
            num_inference_steps=config.num_inference_steps,
            guidance_scale=config.guidance_scale,
            generator=generator,
        )

        if not output_path:
            output_path = f"./outputs/generated/video_{id(prompt) % 10000:04d}.mp4"

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # Export frames to video
        from diffusers.utils import export_to_video
        export_to_video(output.frames[0], output_path, fps=config.fps)

        return output_path

    def _generate_stub(
        self, prompt: str, config: GenerationConfig, output_path: str
    ) -> str:
        """Generate a stub file when no GPU is available."""
        if not output_path:
            output_path = f"./outputs/generated/stub_{id(prompt) % 10000:04d}.txt"

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            f.write("TeachDiffusion Video Generation Stub\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Prompt: {prompt}\n\n")
            f.write(f"Config:\n")
            f.write(f"  Frames: {config.num_frames}\n")
            f.write(f"  FPS: {config.fps}\n")
            f.write(f"  Resolution: {config.resolution}p\n")
            f.write(f"  Steps: {config.num_inference_steps}\n")
            f.write(f"  Guidance: {config.guidance_scale}\n")
            f.write(f"  Seed: {config.seed}\n\n")
            f.write("Note: GPU required for actual video generation.\n")
            f.write("Install PyTorch + diffusers and run on a machine with 40GB+ VRAM.\n")

        return output_path

    @property
    def is_stub(self) -> bool:
        """Whether the model is running in stub mode."""
        return self._stub_mode
