# Contributing to TeachDiffusion

Thank you for your interest in contributing to TeachDiffusion! This project exists because we believe the right to understand is a fundamental right, and every contribution moves us closer to that goal.

## How to Contribute

### Reporting Bugs

1. Check existing [Issues](https://github.com/TeachDiffusion/TeachDiffusion/issues) first
2. Use the bug report template
3. Include: Python version, OS, steps to reproduce, expected vs actual behavior

### Suggesting Features

1. Open a feature request issue
2. Describe the use case — who benefits and how
3. If it involves a new layer or major change, describe the architectural impact

### Code Contributions

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Write tests for your changes
4. Ensure all tests pass: `pytest tests/`
5. Follow the code style (see below)
6. Submit a pull request

### Dataset Contributions

If you have access to CC-licensed math teaching videos or can help with caption quality, see the [teachdiffusion-data](https://github.com/TeachDiffusion/teachdiffusion-data) repo.

## Code Style

- Python 3.10+ with type hints
- Use `black` for formatting: `black src/ tests/`
- Use `isort` for imports: `isort src/ tests/`
- Docstrings on all public functions (Google style)
- Keep functions focused — one function, one responsibility

## Architecture

TeachDiffusion has 8 layers. Before contributing, understand which layer your change affects:

| Layer | Directory | Purpose |
|---|---|---|
| 1. Knowledge | `src/teachdiffusion/knowledge/` | Concept graph, definitions |
| 2. Reasoning | `src/teachdiffusion/reasoning/` | Inference, decomposition |
| 3. Pedagogy | `src/teachdiffusion/pedagogy/` | Lesson planning |
| 4. Student | `src/teachdiffusion/student/` | Knowledge tracking |
| 5. Explanation | `src/teachdiffusion/explanation/` | Content generation |
| 6. Visualization | `src/teachdiffusion/visualization/` | Manim animations |
| 7. Video | `src/teachdiffusion/video/` | Wan 2.2 generation |
| 8. Feedback | `src/teachdiffusion/feedback/` | Quizzes, evaluation |

## Testing

```bash
# Run all tests
pytest tests/

# Run tests for a specific layer
pytest tests/test_knowledge.py

# Run with coverage
pytest tests/ --cov=src/teachdiffusion
```

All tests must pass on CPU without a GPU or API keys.

## Pull Request Process

1. Update documentation if you changed any public API
2. Add tests for new functionality
3. Ensure CI passes
4. Request review from a maintainer
5. Squash commits before merge

## Code of Conduct

See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). Be kind, be constructive, be inclusive.

## Questions?

Open a discussion or issue. We're happy to help you get started.
