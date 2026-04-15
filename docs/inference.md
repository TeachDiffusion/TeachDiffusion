# Inference Guide

## Quick Start

```bash
# Generate a lesson (stub mode — no GPU needed)
teachdiffusion generate --topic "quadratic equations"

# With student personalization
teachdiffusion generate --topic "derivatives" --student student_01

# Get concept info
teachdiffusion info --topic "eigenvalues"
```

## Python API

```python
from teachdiffusion.pipeline.orchestrator import TeachDiffusionPipeline

pipeline = TeachDiffusionPipeline()
result = pipeline.generate_lesson("quadratic equations")

# Access the teaching script
for step in result.script.steps:
    print(f"Step {step.step_number}: {step.step_type.value}")
    print(f"  Content: {step.content}")
    print(f"  Video prompt: {step.to_video_prompt()}")
```

## Stub Mode vs Full Mode

**Stub Mode** (default): Runs on CPU with no GPU. Generates text descriptions of what the video would contain. Use this for development, testing, and script iteration.

**Full Mode**: Requires GPU with 40GB+ VRAM and fine-tuned Wan 2.2 weights. Set `TEACHDIFFUSION_STUB_MODE=false` and ensure weights are downloaded.

## Output Structure

```
outputs/
├── clips/          # Individual video clips per teaching step
├── audio/          # Voice narration per step
├── animations/     # Manim math animation renders
├── final/          # Composited final videos
├── students/       # Student profile JSON files
└── progress/       # Learning session logs
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| ANTHROPIC_API_KEY | (none) | Required for LLM-powered planning |
| TEACHDIFFUSION_STUB_MODE | true | Set false for GPU inference |
| TEACHDIFFUSION_OUTPUT_DIR | ./outputs | Where to save generated files |
