"""
Reporting utilities for evaluation results.

Generates markdown and JSON reports with score breakdowns and trends.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from eval.comparison import ModelComparison
from eval.scenarios.models import ScenarioResult
from eval.scorers.deterministic import compute_aggregate_scores


class EvalReport:
    """
    Generate evaluation reports from comparison results.
    
    Outputs markdown/JSON reports with score breakdowns and trends.
    """
    
    def __init__(self, comparison: ModelComparison):
        """
        Initialize report generator.
        
        Args:
            comparison: ModelComparison with results to report on
        """
        self.comparison = comparison
    
    def generate_summary(self) -> dict[str, Any]:
        """
        Generate summary statistics.
        
        Returns:
            Dict with overall scores, breakdowns by category, etc.
        """
        models = self.comparison.get_unique_models()
        
        summary = {
            "generated_at": datetime.now().isoformat(),
            "total_scenarios": len(self.comparison.scenarios),
            "total_results": len(self.comparison.results),
            "models": models,
            "model_summaries": {},
            "best_model": None,
            "comparison_matrix": {},
        }
        
        # Generate summary for each model
        best_score = 0
        best_model = None
        
        for model in models:
            model_summary = self.comparison.get_model_summary(model)
            summary["model_summaries"][model] = model_summary
            
            # Track best model by overall deterministic score
            overall_scores = model_summary.get("overall_scores", {})
            if "overall_deterministic" in overall_scores:
                score = overall_scores["overall_deterministic"].get("mean", 0)
                if score > best_score:
                    best_score = score
                    best_model = model
        
        summary["best_model"] = best_model
        
        # Generate comparison matrix for all model pairs
        for i, model_a in enumerate(models):
            for model_b in models[i+1:]:
                comparison_result = self.comparison.compare_models(model_a, model_b)
                key = f"{model_a}_vs_{model_b}"
                summary["comparison_matrix"][key] = comparison_result
        
        return summary
    
    def generate_markdown(self) -> str:
        """
        Generate a markdown report.
        
        Returns:
            Markdown string with formatted report
        """
        summary = self.generate_summary()
        
        lines = [
            "# Activity Agent Evaluation Report",
            "",
            f"**Generated:** {summary['generated_at']}",
            "",
            f"**Total Scenarios:** {summary['total_scenarios']}",
            f"**Total Results:** {summary['total_results']}",
            f"**Models Evaluated:** {', '.join(summary['models'])}",
            "",
        ]
        
        # Best model highlight
        if summary["best_model"]:
            lines.extend([
                "## Best Performing Model",
                "",
                f"**{summary['best_model']}** achieved the highest overall score.",
                "",
            ])
        
        # Model summaries
        lines.extend([
            "## Model Summaries",
            "",
        ])
        
        for model, model_summary in summary["model_summaries"].items():
            lines.extend([
                f"### {model}",
                "",
                f"- **Scenarios Run:** {model_summary.get('total_scenarios', 0)}",
                f"- **Avg Duration:** {model_summary.get('average_duration_seconds', 0):.2f}s",
                "",
            ])
            
            # Overall scores table
            overall_scores = model_summary.get("overall_scores", {})
            if overall_scores:
                lines.extend([
                    "#### Overall Scores",
                    "",
                    "| Metric | Mean | Min | Max | Std |",
                    "|--------|------|-----|-----|-----|",
                ])
                
                # Sort by metric name, put overall scores first
                sorted_metrics = sorted(
                    overall_scores.keys(),
                    key=lambda x: (0 if "overall" in x else 1, x)
                )
                
                for metric in sorted_metrics:
                    if metric.startswith("_"):  # Skip private fields
                        continue
                    stats = overall_scores[metric]
                    lines.append(
                        f"| {metric} | {stats['mean']:.1f} | {stats['min']:.1f} | "
                        f"{stats['max']:.1f} | {stats['std']:.1f} |"
                    )
                
                lines.append("")
            
            # Category breakdown
            cat_scores = model_summary.get("scores_by_category", {})
            if cat_scores:
                lines.extend([
                    "#### Scores by Category",
                    "",
                ])
                
                for category, cat_stats in cat_scores.items():
                    if "overall_deterministic" in cat_stats:
                        score = cat_stats["overall_deterministic"]["mean"]
                        lines.append(f"- **{category}:** {score:.1f}")
                
                lines.append("")
        
        # Comparison matrix
        if summary["comparison_matrix"]:
            lines.extend([
                "## Model Comparisons",
                "",
            ])
            
            for comparison_key, comparison_result in summary["comparison_matrix"].items():
                if "error" in comparison_result:
                    continue
                
                model_a = comparison_result["model_a"]
                model_b = comparison_result["model_b"]
                winner = comparison_result.get("winner", "tie")
                
                lines.extend([
                    f"### {model_a} vs {model_b}",
                    "",
                    f"**Winner:** {winner}",
                    "",
                ])
                
                diffs = comparison_result.get("differences", {})
                if diffs:
                    lines.extend([
                        "| Metric | Model A | Model B | Difference |",
                        "|--------|---------|---------|------------|",
                    ])
                    
                    for metric, diff_stats in diffs.items():
                        mean_a = diff_stats["model_a_mean"]
                        mean_b = diff_stats["model_b_mean"]
                        diff = diff_stats["difference"]
                        
                        # Add arrow to show direction
                        arrow = "↑" if diff > 0 else "↓" if diff < 0 else "="
                        
                        lines.append(
                            f"| {metric} | {mean_a:.1f} | {mean_b:.1f} | "
                            f"{arrow} {abs(diff):.1f} |"
                        )
                    
                    lines.append("")
        
        # Footer
        lines.extend([
            "---",
            "",
            "*Report generated by Activity Agent Eval Framework*",
        ])
        
        return "\n".join(lines)
    
    def generate_json(self) -> str:
        """
        Generate a JSON report.
        
        Returns:
            JSON string with detailed results
        """
        summary = self.generate_summary()
        
        # Add detailed results
        report = {
            **summary,
            "detailed_results": [r.to_dict() for r in self.comparison.results],
        }
        
        return json.dumps(report, indent=2)
    
    def save_report(
        self,
        path: str,
        format: str = "markdown",
    ) -> None:
        """
        Save report to file.
        
        Args:
            path: Output file path
            format: "markdown" or "json"
        """
        if format == "markdown":
            content = self.generate_markdown()
        elif format == "json":
            content = self.generate_json()
        else:
            raise ValueError(f"Unknown format: {format}")
        
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, "w") as f:
            f.write(content)
    
    def print_summary(self) -> None:
        """Print a brief summary to stdout."""
        summary = self.generate_summary()
        
        print("\n" + "="*60)
        print("EVALUATION SUMMARY")
        print("="*60)
        print(f"Total Scenarios: {summary['total_scenarios']}")
        print(f"Total Results: {summary['total_results']}")
        print(f"Models: {', '.join(summary['models'])}")
        
        if summary["best_model"]:
            print(f"\nBest Model: {summary['best_model']}")
        
        print("\nModel Scores (overall_deterministic):")
        print("-"*40)
        
        for model, model_summary in summary["model_summaries"].items():
            overall_scores = model_summary.get("overall_scores", {})
            if "overall_deterministic" in overall_scores:
                score = overall_scores["overall_deterministic"]["mean"]
                print(f"  {model}: {score:.1f}")
        
        print("="*60 + "\n")


def generate_report_from_file(
    results_file: str,
    output_path: str | None = None,
    format: str = "markdown",
) -> str:
    """
    Generate a report from a saved results file.
    
    Args:
        results_file: Path to saved results JSON
        output_path: Optional output path for report
        format: "markdown" or "json"
        
    Returns:
        Report content as string
    """
    comparison = ModelComparison()
    comparison.load(results_file)
    
    report = EvalReport(comparison)
    
    if format == "markdown":
        content = report.generate_markdown()
        ext = ".md"
    else:
        content = report.generate_json()
        ext = ".json"
    
    if output_path:
        with open(output_path, "w") as f:
            f.write(content)
        print(f"Report saved to: {output_path}")
    elif output_path is None:
        # Auto-generate output path
        from pathlib import Path
        results_path = Path(results_file)
        output_path = str(results_path.with_suffix(ext).with_stem(
            results_path.stem.replace("eval_results", "eval_report")
        ))
        with open(output_path, "w") as f:
            f.write(content)
        print(f"Report saved to: {output_path}")
    
    return content
