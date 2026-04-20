"""Manim Renderer — generates math animations using the Manim library.

Renders equations, graphs, step-by-step derivations, and geometric diagrams
as video clips that get composited into the final teaching video.
"""

from __future__ import annotations

import os
import subprocess
import tempfile
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class AnimationType(str, Enum):
    """Types of math animations we can render."""

    EQUATION = "equation"
    EQUATION_TRANSFORM = "equation_transform"
    GRAPH = "graph"
    STEP_BY_STEP = "step_by_step"
    NUMBER_LINE = "number_line"
    COORDINATE_PLANE = "coordinate_plane"
    GEOMETRIC = "geometric"


@dataclass
class AnimationSpec:
    """Specification for a math animation."""

    animation_type: AnimationType
    content: str  # LaTeX equation, function expression, etc.
    title: str = ""
    duration_seconds: float = 5.0
    color_scheme: str = "dark"  # dark or light
    resolution: str = "720p"

    # Type-specific parameters
    transform_to: str = ""  # For equation transforms
    x_range: tuple[float, float] = (-5, 5)  # For graphs
    y_range: tuple[float, float] = (-5, 5)
    steps: list[str] | None = None  # For step-by-step


class ManimRenderer:
    """Renders math animations using Manim.

    Usage:
        renderer = ManimRenderer(output_dir="./outputs/animations")
        spec = AnimationSpec(
            animation_type=AnimationType.EQUATION,
            content=r"x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}"
        )
        video_path = renderer.render(spec)
    """

    def __init__(self, output_dir: str = "./outputs/animations") -> None:
        self._output_dir = Path(output_dir)
        self._output_dir.mkdir(parents=True, exist_ok=True)
        self._manim_available = self._check_manim()

    def _check_manim(self) -> bool:
        """Check if Manim is installed."""
        try:
            import manim  # noqa: F401
            return True
        except ImportError:
            return False

    def render(self, spec: AnimationSpec) -> str:
        """Render an animation and return the path to the video file.

        Args:
            spec: AnimationSpec describing what to render.

        Returns:
            Path to the rendered video file, or empty string if rendering fails.
        """
        if not self._manim_available:
            return self._render_stub(spec)

        try:
            return self._render_with_manim(spec)
        except Exception as e:
            print(f"Manim render failed: {e}")
            return self._render_stub(spec)

    def _render_with_manim(self, spec: AnimationSpec) -> str:
        """Render using actual Manim."""
        script = self._generate_manim_script(spec)

        # Write script to temp file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, dir=str(self._output_dir)
        ) as f:
            f.write(script)
            script_path = f.name

        # Run Manim
        quality_flag = "-ql" if spec.resolution == "480p" else "-qm"
        output_name = spec.title.replace(" ", "_") or "animation"

        try:
            result = subprocess.run(
                ["manim", quality_flag, script_path, "TeachScene", "-o", output_name],
                capture_output=True,
                text=True,
                timeout=120,
            )

            if result.returncode == 0:
                # Find the output file
                media_dir = self._output_dir / "media" / "videos"
                for video_file in media_dir.rglob("*.mp4"):
                    return str(video_file)

            return self._render_stub(spec)
        finally:
            os.unlink(script_path)

    def _generate_manim_script(self, spec: AnimationSpec) -> str:
        """Generate a Manim Python script for the given spec."""
        if spec.animation_type == AnimationType.EQUATION:
            return self._script_equation(spec)
        elif spec.animation_type == AnimationType.EQUATION_TRANSFORM:
            return self._script_equation_transform(spec)
        elif spec.animation_type == AnimationType.GRAPH:
            return self._script_graph(spec)
        elif spec.animation_type == AnimationType.STEP_BY_STEP:
            return self._script_step_by_step(spec)
        else:
            return self._script_equation(spec)

    def _script_equation(self, spec: AnimationSpec) -> str:
        """Generate script to display an equation."""
        return f'''from manim import *

class TeachScene(Scene):
    def construct(self):
        eq = MathTex(r"{spec.content}")
        eq.scale(1.5)
        self.play(Write(eq), run_time=2)
        self.wait({spec.duration_seconds - 2})
'''

    def _script_equation_transform(self, spec: AnimationSpec) -> str:
        """Generate script to transform one equation into another."""
        return f'''from manim import *

class TeachScene(Scene):
    def construct(self):
        eq1 = MathTex(r"{spec.content}")
        eq2 = MathTex(r"{spec.transform_to}")
        eq1.scale(1.3)
        eq2.scale(1.3)
        self.play(Write(eq1), run_time=1.5)
        self.wait(1)
        self.play(TransformMatchingTex(eq1, eq2), run_time=2)
        self.wait({max(spec.duration_seconds - 4.5, 1)})
'''

    def _script_graph(self, spec: AnimationSpec) -> str:
        """Generate script to plot a function."""
        return f'''from manim import *
import numpy as np

class TeachScene(Scene):
    def construct(self):
        axes = Axes(
            x_range=[{spec.x_range[0]}, {spec.x_range[1]}, 1],
            y_range=[{spec.y_range[0]}, {spec.y_range[1]}, 1],
            x_length=8,
            y_length=5,
            axis_config={{"include_tip": True}},
        )
        labels = axes.get_axis_labels(x_label="x", y_label="y")
        graph = axes.plot(lambda x: {spec.content}, color=BLUE)

        self.play(Create(axes), Write(labels), run_time=1.5)
        self.play(Create(graph), run_time=2)
        self.wait({max(spec.duration_seconds - 3.5, 1)})
'''

    def _script_step_by_step(self, spec: AnimationSpec) -> str:
        """Generate script for step-by-step derivation."""
        steps = spec.steps or [spec.content]
        step_lines = []
        y_pos = 2.0
        for i, step in enumerate(steps):
            step_lines.append(
                f'        step{i} = MathTex(r"{step}").move_to(UP * {y_pos})'
            )
            step_lines.append(
                f'        self.play(Write(step{i}), run_time=1)'
            )
            step_lines.append('        self.wait(0.5)')
            y_pos -= 1.0

        steps_code = "\n".join(step_lines)
        return f'''from manim import *

class TeachScene(Scene):
    def construct(self):
{steps_code}
        self.wait(1)
'''

    def _render_stub(self, spec: AnimationSpec) -> str:
        """Create a stub placeholder when Manim isn't available."""
        stub_path = self._output_dir / f"{spec.title or 'animation'}_stub.txt"
        with open(stub_path, "w") as f:
            f.write(f"Animation Stub\n")
            f.write(f"Type: {spec.animation_type.value}\n")
            f.write(f"Content: {spec.content}\n")
            f.write(f"Duration: {spec.duration_seconds}s\n")
            f.write(f"\nNote: Install Manim to render actual animations: pip install manim\n")
        return str(stub_path)

    def render_equation(self, latex: str, title: str = "equation") -> str:
        """Convenience: render a single equation."""
        return self.render(AnimationSpec(
            animation_type=AnimationType.EQUATION,
            content=latex,
            title=title,
        ))

    def render_graph(
        self, expression: str, title: str = "graph",
        x_range: tuple = (-5, 5), y_range: tuple = (-5, 5)
    ) -> str:
        """Convenience: render a function graph."""
        return self.render(AnimationSpec(
            animation_type=AnimationType.GRAPH,
            content=expression,
            title=title,
            x_range=x_range,
            y_range=y_range,
        ))
