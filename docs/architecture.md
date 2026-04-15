# TeachDiffusion Architecture

## Overview

TeachDiffusion is an 8-layer Intelligent Tutoring System that generates math teaching videos using a fine-tuned video diffusion model. Each layer has a clear responsibility and communicates with adjacent layers through well-defined interfaces.

## System Flow

```
User Input (topic / question)
        │
        ▼
┌─────────────────────────┐
│  1. Knowledge Base       │  ConceptGraph + DefinitionStore + ProofStore
│     concept_graph.py     │  34+ concepts, prerequisites, formal + intuitive defs
└─────────┬───────────────┘
          ▼
┌─────────────────────────┐
│  2. Reasoning Engine     │  InferenceEngine + Decomposer + AnalogyBuilder
│     inference_engine.py  │  Gap detection, topic decomposition, analogy generation
└─────────┬───────────────┘
          ▼
┌─────────────────────────┐
│  3. Pedagogy Planner     │  PedagogicalPlanner + Schema + Difficulty
│     planner.py           │  Designs lessons: hook → intuition → formal → examples
└─────────┬───────────────┘
          ▼
┌─────────────────────────┐
│  4. Student Model        │  StudentModel + MisconceptionDetector + ProgressTracker
│     student_model.py     │  Per-student knowledge state, confidence, history
└─────────┬───────────────┘
          ▼
┌─────────────────────────┐
│  5. Explanation Gen      │  ExplanationGenerator + ExampleBuilder + AnalogyStore
│     generator.py         │  Layered explanations with multiple presentation styles
└─────────┬───────────────┘
          ▼
┌─────────────────────────┐
│  6. Visualization        │  ManimRenderer + DiagramBuilder + SimulationEngine
│     manim_renderer.py    │  Math animations, diagrams, interactive simulations
└─────────┬───────────────┘
          ▼
┌─────────────────────────┐
│  7. Video Diffusion      │  WanLoRAModel + VideoGenerator + VoiceEngine + Compositor
│     wan_lora.py          │  Wan 2.2 + LoRA → realistic AI teacher video
└─────────┬───────────────┘
          ▼
┌─────────────────────────┐
│  8. Feedback & Eval      │  QuizGenerator + Evaluator + LearningGainCalculator
│     quiz_generator.py    │  Adaptive quizzes, misconception detection, Hake's g
└─────────┬───────────────┘
          ▼
    Update Student Model (loop back to Layer 4)
```

## Key Design Decisions

**Pedagogy-Aware Conditioning**: The novel contribution. TeachingStep objects encode pedagogical intent (step type, gesture, pacing) into structured prompts that condition video generation. This is defined in `pedagogy/schema.py`.

**Stub Mode**: Every component that requires GPU or external services has a stub fallback. The entire system can run on a laptop with no GPU, no API keys — critical for development and testing.

**Claude API Integration**: Layers 2, 3, 4, 5, and 8 use the Anthropic Claude API for reasoning, planning, and content generation. All fall back gracefully when the API key is not set.

**Persistence**: Student profiles and progress are saved as JSON files. Lightweight, portable, no database required.

## Module Dependencies

```
knowledge ← reasoning ← pedagogy ← student ← explanation ← visualization ← video ← feedback
                                                                                        │
                                                                                        ▼
                                                                              pipeline/orchestrator
```

Each layer only depends on layers above it. The orchestrator connects everything.
