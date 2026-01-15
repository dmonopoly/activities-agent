"""
Scenario management for evaluation.

Scenarios bundle queries with mock data for reproducible testing.
"""

from eval.scenarios.generator import ScenarioGenerator, generate_eval_dataset
from eval.scenarios.models import Scenario, ScenarioResult

__all__ = ["ScenarioGenerator", "Scenario", "ScenarioResult", "generate_eval_dataset"]
