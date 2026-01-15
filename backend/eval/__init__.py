"""
Evaluation framework for the activity agent.

This module provides tools for evaluating agent response quality through
scenario-based testing with deterministic metrics and LLM-as-Judge scoring.

Quick Start:
    from eval import generate_eval_dataset, run_comparison, EvalReport
    
    # Generate scenarios
    scenarios = generate_eval_dataset(count=100)
    
    # Run comparison across models
    comparison = run_comparison(
        scenarios=scenarios,
        models=["xiaomi/mimo-v2-flash:free", "google/gemini-2.0-flash-exp:free"],
    )
    
    # Generate report
    report = EvalReport(comparison)
    report.save_report("eval_report.md")
"""

from eval.runner import EvalRunner, MockModeRunner
from eval.comparison import ModelComparison, run_comparison
from eval.report import EvalReport, generate_report_from_file
from eval.scenarios import ScenarioGenerator, Scenario, ScenarioResult, generate_eval_dataset
from eval.scorers import DeterministicScorer, LLMJudgeScorer, MockLLMJudgeScorer

__all__ = [
    # Runner
    "EvalRunner",
    "MockModeRunner",
    # Comparison
    "ModelComparison",
    "run_comparison",
    # Report
    "EvalReport",
    "generate_report_from_file",
    # Scenarios
    "ScenarioGenerator",
    "Scenario",
    "ScenarioResult",
    "generate_eval_dataset",
    # Scorers
    "DeterministicScorer",
    "LLMJudgeScorer",
    "MockLLMJudgeScorer",
]
