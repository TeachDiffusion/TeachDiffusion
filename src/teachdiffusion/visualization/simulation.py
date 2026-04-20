"""Simulation — interactive concept simulations.

Generates interactive HTML/JS widgets that let students explore
math concepts dynamically (e.g., dragging a slider to change
coefficients and see the parabola move in real-time).

Currently provides specification generation; rendering is planned
for v0.2.0 with integration into the HuggingFace Space demo.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SimulationParameter:
    """A parameter the student can adjust in the simulation."""

    name: str
    label: str
    min_value: float
    max_value: float
    default_value: float
    step: float = 0.1


@dataclass
class SimulationSpec:
    """Specification for an interactive math simulation."""

    concept_id: str
    title: str
    description: str
    parameters: list[SimulationParameter] = field(default_factory=list)
    visualization_type: str = "graph"  # graph, geometric, numeric
    expression: str = ""  # Math expression using parameter names as variables
    instructions: str = ""


class SimulationEngine:
    """Generates specifications for interactive math simulations.

    Usage:
        engine = SimulationEngine()
        spec = engine.create_quadratic_explorer()
    """

    def create_quadratic_explorer(self) -> SimulationSpec:
        """Create a quadratic equation explorer simulation."""
        return SimulationSpec(
            concept_id="quadratic_equations",
            title="Quadratic Explorer",
            description="Drag the sliders to change a, b, c and watch the parabola move.",
            parameters=[
                SimulationParameter("a", "a (curvature)", -3, 3, 1, 0.1),
                SimulationParameter("b", "b (shift)", -5, 5, 0, 0.5),
                SimulationParameter("c", "c (height)", -5, 5, 0, 0.5),
            ],
            visualization_type="graph",
            expression="a * x**2 + b * x + c",
            instructions=(
                "Notice: when a > 0 the parabola opens up, when a < 0 it opens down. "
                "The value of c shifts it up or down. Try making the discriminant "
                "b² - 4ac negative — the parabola won't touch the x-axis!"
            ),
        )

    def create_derivative_visualizer(self) -> SimulationSpec:
        """Create a derivative visualization simulation."""
        return SimulationSpec(
            concept_id="derivatives",
            title="Derivative Visualizer",
            description="See how the tangent line slope changes as you move along the curve.",
            parameters=[
                SimulationParameter("x0", "Point x₀", -3, 3, 1, 0.1),
            ],
            visualization_type="graph",
            expression="x**2",
            instructions=(
                "The red line is tangent to the curve at x₀. Its slope IS the derivative at that point. "
                "Notice: at x=0 the slope is 0 (horizontal tangent = minimum). "
                "As x increases, the slope increases — the derivative of x² is 2x."
            ),
        )

    def create_matrix_transform_visualizer(self) -> SimulationSpec:
        """Create a matrix transformation simulation."""
        return SimulationSpec(
            concept_id="matrices",
            title="Matrix Transformation",
            description="See how a 2x2 matrix transforms the unit square.",
            parameters=[
                SimulationParameter("a11", "a₁₁", -3, 3, 1, 0.1),
                SimulationParameter("a12", "a₁₂", -3, 3, 0, 0.1),
                SimulationParameter("a21", "a₂₁", -3, 3, 0, 0.1),
                SimulationParameter("a22", "a₂₂", -3, 3, 1, 0.1),
            ],
            visualization_type="geometric",
            instructions=(
                "The blue square is the original unit square. The red shape is what happens "
                "when you apply the matrix. Try: identity (1,0,0,1), rotation (0,-1,1,0), "
                "scaling (2,0,0,2), shear (1,1,0,1)."
            ),
        )

    def get_simulation(self, concept_id: str) -> SimulationSpec | None:
        """Get a simulation for a concept, if one exists."""
        sims = {
            "quadratic_equations": self.create_quadratic_explorer,
            "derivatives": self.create_derivative_visualizer,
            "matrices": self.create_matrix_transform_visualizer,
        }
        factory = sims.get(concept_id)
        return factory() if factory else None
