# GitHub Setup Guide

## Step 1: Create the Organization

1. Go to https://github.com/organizations/new
2. Organization name: `TeachDiffusion`
3. Contact email: your email
4. Select: "My personal account"
5. Click Next, skip inviting members

## Step 2: Create the Main Repository

1. Go to https://github.com/organizations/TeachDiffusion/repositories/new
2. Repository name: `TeachDiffusion`
3. Description: "Open-source video diffusion model for math education"
4. Public
5. Do NOT initialize with README (we have our own)
6. Create repository

## Step 3: Push Your First Commit

```bash
cd TeachDiffusion
git init
git add .
git commit -m "feat: initial commit — 8-layer math teaching video generation system

- Knowledge Base with 34+ math concepts and prerequisite graph
- Reasoning Engine with topic decomposition and analogy generation
- Pedagogical Planner with Claude API integration
- Student Model with knowledge tracking and misconception detection
- Explanation Generator with layered output
- Visualization Engine with Manim integration
- Video Generation pipeline with Wan 2.2 support (stub mode)
- Feedback system with adaptive quizzes and learning gain measurement
- Full pipeline orchestrator connecting all 8 layers
- CLI with generate, quiz, info, and student commands
- Comprehensive test suite (all CPU, no GPU required)

The right to understand is a fundamental right."

git branch -M main
git remote add origin https://github.com/TeachDiffusion/TeachDiffusion.git
git push -u origin main
```

## Step 4: Configure the Repository

1. Go to Settings → General
   - Add topics: `video-diffusion`, `math-education`, `teaching`, `ai`, `wan2`, `lora`, `open-source`
   - Set website: (your HuggingFace space URL later)

2. Go to Settings → Branches
   - Add branch protection for `main`
   - Require pull request reviews

## Step 5: Create HuggingFace Organization

1. Go to https://huggingface.co/organizations/new
2. Name: `TeachDiffusion`
3. This is where model weights will be hosted

## Step 6: Create Additional Repos (Later)

After the main repo is live, create:
- `teachdiffusion-data` — dataset pipeline
- `teachdiffusion-training` — training scripts
- `teachdiffusion-space` — HuggingFace demo

Push each the same way as Step 3.
