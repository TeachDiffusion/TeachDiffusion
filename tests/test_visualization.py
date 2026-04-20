"""Tests for Layer 6: Visualization Engine."""

import tempfile
from teachdiffusion.visualization.manim_renderer import ManimRenderer, AnimationSpec, AnimationType
from teachdiffusion.visualization.diagram_builder import DiagramBuilder
from teachdiffusion.visualization.simulation import SimulationEngine


class TestManimRenderer:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.renderer = ManimRenderer(output_dir=self.tmpdir)

    def test_render_stub(self):
        spec = AnimationSpec(
            animation_type=AnimationType.EQUATION,
            content=r"x = \frac{-b \pm \sqrt{b^2-4ac}}{2a}",
            title="quadratic_formula",
        )
        path = self.renderer.render(spec)
        assert len(path) > 0
        assert "stub" in path or "quadratic" in path

    def test_render_equation_convenience(self):
        path = self.renderer.render_equation(r"E = mc^2", title="einstein")
        assert len(path) > 0


class TestDiagramBuilder:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.builder = DiagramBuilder(output_dir=self.tmpdir)

    def test_build_number_line(self):
        path = self.builder.build_number_line(
            points=[-2, 0, 3], labels=["a", "0", "b"], title="Test Line"
        )
        assert path.endswith(".svg")
        with open(path) as f:
            svg = f.read()
        assert "<svg" in svg

    def test_build_coordinate_plane(self):
        path = self.builder.build_coordinate_plane(
            points=[(1, 2), (-1, 3)], title="Test Plane"
        )
        assert path.endswith(".svg")


class TestSimulationEngine:
    def test_quadratic_explorer(self):
        engine = SimulationEngine()
        spec = engine.create_quadratic_explorer()
        assert spec.concept_id == "quadratic_equations"
        assert len(spec.parameters) == 3

    def test_get_simulation(self):
        engine = SimulationEngine()
        spec = engine.get_simulation("derivatives")
        assert spec is not None
        assert spec.concept_id == "derivatives"

    def test_get_nonexistent_simulation(self):
        engine = SimulationEngine()
        spec = engine.get_simulation("nonexistent")
        assert spec is None
