# Knowledge Base

## Overview

The Knowledge Base (Layer 1) is a directed acyclic graph of 34+ math concepts. Each concept has prerequisites, definitions (formal and intuitive), common misconceptions, and estimated teaching time.

## Structure

- **ConceptGraph** (`concept_graph.py`): DAG of concepts with prerequisite edges. Built on NetworkX.
- **DefinitionStore** (`definition_store.py`): Formal and intuitive definitions, misconceptions, analogies, and examples per concept.
- **ProofStore** (`proof_store.py`): Step-by-step proofs with justifications and intuitive explanations.
- **math_topics.json**: Seed data defining domains, concept lists, and recommended learning paths.

## Domains Covered

| Domain | Concepts | Examples |
|--------|----------|---------|
| Arithmetic | 6 | Fractions, Exponents, Square Roots |
| Algebra | 12 | Quadratics, Functions, Logarithms |
| Geometry | 3 | Coordinate Geometry, Pythagorean Theorem |
| Trigonometry | 3 | Unit Circle, Trig Identities |
| Calculus | 5 | Limits, Derivatives, Integrals, FTC |
| Linear Algebra | 4 | Vectors, Matrices, Eigenvalues |
| Probability | 2 | Basic Probability, Combinations |

## Adding New Concepts

Add to `_build_default_concepts()` in `concept_graph.py`:

```python
Concept(
    id="your_concept_id",
    name="Your Concept Name",
    domain=MathDomain.ALGEBRA,
    difficulty=DifficultyLevel.INTERMEDIATE,
    description="What this concept is about.",
    prerequisites=["existing_concept_id"],
    keywords=["keyword1", "keyword2"],
    typical_misconceptions=["Common error students make"],
    estimated_minutes=15,
)
```

Then add a corresponding definition in `definition_store.py`.

## Validation

Run `graph.validate()` to check for cycles and missing prerequisites. The test suite also validates graph integrity automatically.
