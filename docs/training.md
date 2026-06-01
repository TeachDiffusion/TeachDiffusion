# Training Guide

## Overview

TeachDiffusion uses LoRA (Low-Rank Adaptation) to fine-tune Wan 2.2 on math teaching video data. This keeps training feasible on a single A100 80GB GPU.

## Prerequisites

- GPU with 40GB+ VRAM (A100 80GB recommended)
- Python 3.10+
- PyTorch 2.0+
- HuggingFace Diffusers, Accelerate, PEFT

## Dataset

Prepare your dataset using the `teachdiffusion-data` pipeline:
1. Download CC-licensed math teaching videos
2. Transcribe with Whisper
3. Segment into 5-30 second clips
4. Filter for quality
5. Generate pedagogy-aware captions

Target: 5,000-20,000 clips minimum.

## Training

```bash
# Using RunPod
cd teachdiffusion-training
bash runpod/setup.sh
bash runpod/train.sh

# Or directly
python scripts/train_lora.py --config configs/wan2_lora_480p.yaml
```

## Key Hyperparameters

| Parameter | Value | Notes |
|-----------|-------|-------|
| LoRA rank | 64 | Higher = more capacity, more VRAM |
| Learning rate | 1e-4 | Standard for LoRA |
| Batch size | 1 | Video is memory-heavy |
| Gradient accumulation | 4 | Effective batch size = 4 |
| Max steps | 5,000 | Monitor quality every 500 steps |
| Resolution | 480p | Keeps VRAM manageable |

## Monitoring

Training logs to TensorBoard. Monitor:
- Loss curve (should decrease steadily)
- Generated samples every 500 steps
- VRAM usage

## Expected Costs

| Platform | Cost per hour | Estimated total |
|----------|--------------|-----------------|
| RunPod A100 80GB | ~$2.50 | $50-150 |
| Vast.ai A100 | ~$1.50 | $30-100 |
| University HPC | Free | $0 |

## After Training

1. Export weights: `python scripts/export_weights.py`
2. Upload to HuggingFace: `huggingface-cli upload TeachDiffusion/teachdiffusion-v0.1`
3. Update `configs/inference.yaml` with the new model path
