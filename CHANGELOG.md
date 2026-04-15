# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- 8-layer architecture: Knowledge, Reasoning, Pedagogy, Student, Explanation, Visualization, Video, Feedback
- Knowledge base with 34+ math concepts and prerequisite graph
- Reasoning engine with topic decomposition and analogy generation
- Pedagogical planner with Claude API integration
- Student model with knowledge state tracking and misconception detection
- Explanation generator with layered output (hook → intuition → formal → examples)
- Visualization engine with Manim integration
- Video generation pipeline with Wan 2.2 support (stub mode)
- Feedback system with adaptive quiz generation and learning gain measurement
- Full pipeline orchestrator connecting all 8 layers
- CLI interface with generate, quiz, info, and student commands
- Comprehensive test suite (all CPU, no GPU required)
- Apache 2.0 license

## [0.1.0] - TBD

### Planned
- First LoRA fine-tuned weights on Wan 2.2
- Curated math teaching video dataset
- HuggingFace Space demo
- Technical report
