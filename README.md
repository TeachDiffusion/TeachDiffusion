<p align="center">
  <img src="https://raw.githubusercontent.com/TeachDiffusion/.github/main/assets/teachdiffusion_logo.svg" alt="TeachDiffusion" width="320"/>
</p>

<h1 align="center">TeachDiffusion — Core</h1>

<p align="center">
  The Python package that powers the TeachDiffusion lesson-generation pipeline.
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg" alt="License"></a>
  <a href="https://github.com/TeachDiffusion/TeachDiffusion/actions"><img src="https://github.com/TeachDiffusion/TeachDiffusion/workflows/CI/badge.svg" alt="CI"></a>
  <a href="https://huggingface.co/TeachDiffusion"><img src="https://img.shields.io/badge/🤗-Models-yellow.svg" alt="HuggingFace"></a>
</p>

> For project mission, the full 8-layer architecture, sibling repositories, and roadmap, see the [TeachDiffusion organization profile](https://github.com/TeachDiffusion).

---

## About this repo

`TeachDiffusion` is the **core** repository of the project. It contains the Python package (`teachdiffusion`) that ties every layer of the system together — from concept lookup to lesson script to rendered video. Dataset tooling, LoRA training, and the demo Space live in their own sibling repositories (linked from the org profile).

If you want to **generate a lesson**, run inference, or build on top of the pipeline, this is the right repo.

## Installation

```bash
git clone https://github.com/TeachDiffusion/TeachDiffusion.git
cd TeachDiffusion
pip install -e .
```

**Requirements:** Python 3.10+, [Anthropic API key](https://console.anthropic.com/) for the reasoning and pedagogy layers, FFmpeg for compositing, Manim for math animations, and a 40GB+ VRAM GPU if you intend to run the video-diffusion layer (not needed for development).

## Usage

### CLI

```bash
teachdiffusion generate --topic "quadratic equations" --output lesson.mp4
teachdiffusion generate --topic "derivatives" --student student_01 --output lesson.mp4
teachdiffusion info --topic "eigenvalues"
```

### Python

```python
from teachdiffusion.pipeline.orchestrator import TeachDiffusionPipeline

pipeline = TeachDiffusionPipeline()
result = pipeline.generate_lesson(
    topic="quadratic equations",
    student_id="student_01",
    difficulty="intermediate",
)
```

The pedagogy-aware conditioning schema (the project's main novel contribution) lives here:

```python
from teachdiffusion.pedagogy.schema import TeachingStep, StepType, GestureType

step = TeachingStep(
    step_number=1,
    step_type=StepType.BUILD_INTUITION,
    content="Before we touch any formulas, let's understand what a quadratic really means...",
    gesture=GestureType.OPEN_HAND,
    pacing="slow",
    visual_cue="Show parabola forming from thrown ball trajectory",
)
```

## Package layout

Every layer of the architecture (see the [org profile](https://github.com/TeachDiffusion) for the full diagram) maps to one module under [`src/teachdiffusion/`](src/teachdiffusion):

| Module | Responsibility |
|---|---|
| [`knowledge/`](src/teachdiffusion/knowledge) | Concept graph, definitions, proofs |
| [`reasoning/`](src/teachdiffusion/reasoning) | Topic decomposition, analogy generation, inference |
| [`pedagogy/`](src/teachdiffusion/pedagogy) | Teaching-step schema, lesson planner, script engine |
| [`student/`](src/teachdiffusion/student) | Student model, progress tracker, misconception detector |
| [`explanation/`](src/teachdiffusion/explanation) | Layered explanation generator + analogy/example stores |
| [`visualization/`](src/teachdiffusion/visualization) | Manim renderer, diagram builder, simulations |
| [`video/`](src/teachdiffusion/video) | Wan 2.2 LoRA loader, generator, voice, compositor |
| [`feedback/`](src/teachdiffusion/feedback) | Quiz generator, evaluator, learning-gain scoring |
| [`pipeline/`](src/teachdiffusion/pipeline) | Orchestrator that wires the eight layers together |

Configs live in [`configs/`](configs), tests in [`tests/`](tests), runnable walkthroughs in [`notebooks/`](notebooks), and deeper documentation in [`docs/`](docs).

## Development

```bash
pip install -e .[dev]
pytest tests/
```

Inference and training configuration are kept separate: [`configs/inference.yaml`](configs/inference.yaml) and [`configs/train_lora.yaml`](configs/train_lora.yaml). The actual LoRA training code lives in [`teachdiffusion-training`](https://github.com/TeachDiffusion/teachdiffusion-training).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

Apache 2.0 — see [LICENSE](LICENSE).
