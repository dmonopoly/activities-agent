"""
Scoring modules for evaluation.

Provides both deterministic and LLM-as-Judge scoring.
"""

from eval.scorers.deterministic import DeterministicScorer, compute_aggregate_scores
from eval.scorers.llm_judge import LLMJudgeScorer, MockLLMJudgeScorer

__all__ = [
    "DeterministicScorer",
    "LLMJudgeScorer",
    "MockLLMJudgeScorer",
    "compute_aggregate_scores",
]
