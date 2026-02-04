"""
Model comparison utilities for evaluation.

Stores and compares results across different models and versions.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from eval.scenarios.models import Scenario, ScenarioResult
from eval.scorers.deterministic import DeterministicScorer, compute_aggregate_scores


class ModelComparison:
    """
    Compare different models/versions on the same scenario set.
    
    Stores results per (scenario_id, model_name, version_date) for
    tracking improvement over time.
    """
    
    def __init__(self, results_path: str = "eval_results"):
        """
        Initialize comparison.
        
        Args:
            results_path: Directory to store/load results
        """
        self.results_path = Path(results_path)
        self.results_path.mkdir(parents=True, exist_ok=True)
        
        self.results: list[ScenarioResult] = []
        self.scenarios: dict[str, Scenario] = {}  # scenario_id -> Scenario
    
    def add_scenario(self, scenario: Scenario) -> None:
        """Add a scenario to the comparison (for reference)."""
        self.scenarios[scenario.id] = scenario
    
    def add_result(self, result: ScenarioResult) -> None:
        """Add a result to the comparison."""
        self.results.append(result)
    
    def add_results(self, results: list[ScenarioResult]) -> None:
        """Add multiple results to the comparison."""
        self.results.extend(results)
    
    def get_results_for_model(self, model: str) -> list[ScenarioResult]:
        """Get all results for a specific model."""
        return [r for r in self.results if r.model == model]
    
    def get_results_for_scenario(self, scenario_id: str) -> list[ScenarioResult]:
        """Get all results for a specific scenario (across models)."""
        return [r for r in self.results if r.scenario_id == scenario_id]
    
    def get_unique_models(self) -> list[str]:
        """Get list of unique model names in results."""
        return list(set(r.model for r in self.results))
    
    def compare_models(
        self,
        model_a: str,
        model_b: str,
    ) -> dict[str, Any]:
        """
        Compare two models on all scenarios.
        
        Args:
            model_a: First model name
            model_b: Second model name
            
        Returns:
            Dict with comparison statistics
        """
        results_a = self.get_results_for_model(model_a)
        results_b = self.get_results_for_model(model_b)
        
        if not results_a or not results_b:
            return {
                "error": "Not enough results for comparison",
                "model_a_count": len(results_a),
                "model_b_count": len(results_b),
            }
        
        # Get scores for each model
        scores_a = [r.scores for r in results_a if r.scores]
        scores_b = [r.scores for r in results_b if r.scores]
        
        # Compute aggregates
        agg_a = compute_aggregate_scores(scores_a)
        agg_b = compute_aggregate_scores(scores_b)
        
        # Compute differences
        comparison = {
            "model_a": model_a,
            "model_b": model_b,
            "model_a_count": len(results_a),
            "model_b_count": len(results_b),
            "model_a_scores": agg_a,
            "model_b_scores": agg_b,
            "differences": {},
            "winner": None,
        }
        
        # Calculate differences for each metric
        all_keys = set(agg_a.keys()) | set(agg_b.keys())
        for key in all_keys:
            if key in agg_a and key in agg_b:
                mean_a = agg_a[key]["mean"]
                mean_b = agg_b[key]["mean"]
                diff = mean_b - mean_a
                comparison["differences"][key] = {
                    "model_a_mean": mean_a,
                    "model_b_mean": mean_b,
                    "difference": round(diff, 2),
                    "percent_change": round((diff / mean_a * 100) if mean_a != 0 else 0, 2),
                }
        
        # Determine overall winner (based on overall_deterministic or llm_overall)
        if "overall_deterministic" in comparison["differences"]:
            diff = comparison["differences"]["overall_deterministic"]["difference"]
            if diff > 2:  # Model B is better by 2+ points
                comparison["winner"] = model_b
            elif diff < -2:  # Model A is better
                comparison["winner"] = model_a
            else:
                comparison["winner"] = "tie"
        
        return comparison
    
    def get_model_scores(self, model: str) -> dict[str, float]:
        """
        Get aggregate scores for a model.
        
        Args:
            model: Model name
            
        Returns:
            Dict mapping score names to average values
        """
        results = self.get_results_for_model(model)
        scores_list = [r.scores for r in results if r.scores]
        
        if not scores_list:
            return {}
        
        aggregates = compute_aggregate_scores(scores_list)
        return {k: v["mean"] for k, v in aggregates.items()}
    
    def get_model_summary(self, model: str) -> dict[str, Any]:
        """
        Get detailed summary for a model.
        
        Args:
            model: Model name
            
        Returns:
            Comprehensive summary dict
        """
        results = self.get_results_for_model(model)
        
        if not results:
            return {"error": f"No results for model: {model}"}
        
        scores_list = [r.scores for r in results if r.scores]
        aggregates = compute_aggregate_scores(scores_list)
        
        # Group by category
        by_category: dict[str, list[ScenarioResult]] = {}
        for r in results:
            category = r.metadata.get("category", "unknown")
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(r)
        
        category_scores = {}
        for category, cat_results in by_category.items():
            cat_scores = [r.scores for r in cat_results if r.scores]
            if cat_scores:
                category_scores[category] = compute_aggregate_scores(cat_scores)
        
        # Calculate average duration
        durations = [
            r.metadata.get("duration_seconds", 0)
            for r in results
            if "duration_seconds" in r.metadata
        ]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        return {
            "model": model,
            "total_scenarios": len(results),
            "overall_scores": aggregates,
            "scores_by_category": category_scores,
            "average_duration_seconds": round(avg_duration, 2),
            "categories": list(by_category.keys()),
        }
    
    def save(self, filename: str | None = None) -> str:
        """
        Save results to disk.
        
        Args:
            filename: Optional filename (defaults to timestamped name)
            
        Returns:
            Path to saved file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"eval_results_{timestamp}.json"
        
        filepath = self.results_path / filename
        
        data = {
            "timestamp": datetime.now().isoformat(),
            "scenarios": {sid: s.to_dict() for sid, s in self.scenarios.items()},
            "results": [r.to_dict() for r in self.results],
        }
        
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        
        return str(filepath)
    
    def load(self, filename: str) -> None:
        """
        Load results from disk.
        
        Args:
            filename: Filename to load
        """
        filepath = self.results_path / filename
        
        with open(filepath, "r") as f:
            data = json.load(f)
        
        # Load scenarios
        for sid, sdata in data.get("scenarios", {}).items():
            self.scenarios[sid] = Scenario.from_dict(sdata)
        
        # Load results
        for rdata in data.get("results", []):
            self.results.append(ScenarioResult.from_dict(rdata))
    
    def load_latest(self) -> bool:
        """
        Load the most recent results file.
        
        Returns:
            True if a file was loaded, False otherwise
        """
        files = sorted(self.results_path.glob("eval_results_*.json"), reverse=True)
        if files:
            self.load(files[0].name)
            return True
        return False
    
    def list_saved_results(self) -> list[dict[str, Any]]:
        """
        List all saved result files.
        
        Returns:
            List of dicts with filename and metadata
        """
        files = sorted(self.results_path.glob("eval_results_*.json"), reverse=True)
        
        results = []
        for f in files:
            try:
                with open(f, "r") as fp:
                    data = json.load(fp)
                results.append({
                    "filename": f.name,
                    "timestamp": data.get("timestamp"),
                    "scenario_count": len(data.get("scenarios", {})),
                    "result_count": len(data.get("results", [])),
                })
            except Exception:
                results.append({
                    "filename": f.name,
                    "error": "Could not read file",
                })
        
        return results


def run_comparison(
    scenarios: list[Scenario],
    models: list[str],
    results_dir: str = "eval_results",
    use_mock_llm: bool = True,
    verbose: bool = True,
) -> ModelComparison:
    """
    Convenience function to run a full comparison across multiple models.
    
    Args:
        scenarios: List of scenarios to run
        models: List of model names to compare
        results_dir: Directory to save results
        use_mock_llm: Whether to use mock LLM for judging (saves API calls)
        verbose: Whether to print progress
        
    Returns:
        ModelComparison with all results
    """
    from eval.runner import EvalRunner
    from eval.scorers.deterministic import DeterministicScorer
    from eval.scorers.llm_judge import LLMJudgeScorer, MockLLMJudgeScorer
    
    comparison = ModelComparison(results_path=results_dir)
    
    # Add scenarios to comparison
    for scenario in scenarios:
        comparison.add_scenario(scenario)
    
    # Initialize scorers
    det_scorer = DeterministicScorer()
    llm_scorer = MockLLMJudgeScorer() if use_mock_llm else LLMJudgeScorer()
    
    # Run for each model
    runner = EvalRunner(verbose=verbose)
    
    for model in models:
        if verbose:
            print(f"\n{'='*60}")
            print(f"Running {len(scenarios)} scenarios with model: {model}")
            print(f"{'='*60}")
        
        results = runner.run_batch(scenarios, model=model, progress=verbose)
        
        # Score each result
        for result, scenario in zip(results, scenarios):
            # Compute deterministic scores
            det_scores = det_scorer.score(scenario, result)
            
            # Compute LLM scores
            llm_scores = llm_scorer.score(scenario, result)
            
            # Merge scores
            result.scores = {**det_scores, **llm_scores}
        
        comparison.add_results(results)
    
    # Save results
    saved_path = comparison.save()
    if verbose:
        print(f"\nResults saved to: {saved_path}")
    
    return comparison
