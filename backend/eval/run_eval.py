#!/usr/bin/env python3
"""
Example script for running the evaluation framework.

This script demonstrates how to:
1. Generate evaluation scenarios
2. Run scenarios through different models
3. Score the results
4. Generate comparison reports

Usage:
    cd backend
    python -m eval.run_eval --scenarios 10 --mock
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from eval import (
    EvalReport,
    EvalRunner,
    MockModeRunner,
    ModelComparison,
    ScenarioGenerator,
    generate_eval_dataset,
    run_comparison,
)
from eval.scorers import DeterministicScorer, MockLLMJudgeScorer


def main():
    parser = argparse.ArgumentParser(
        description="Run activity agent evaluation"
    )
    parser.add_argument(
        "--scenarios",
        type=int,
        default=10,
        help="Number of scenarios to generate (default: 10)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)",
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Use mock mode (no API calls)",
    )
    parser.add_argument(
        "--models",
        nargs="+",
        default=["xiaomi/mimo-v2-flash:free"],
        help="Models to evaluate (default: mimo-v2-flash)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="eval_results",
        help="Directory for results (default: eval_results)",
    )
    parser.add_argument(
        "--report",
        type=str,
        default="eval_report.md",
        help="Report filename (default: eval_report.md)",
    )
    
    args = parser.parse_args()
    
    print("="*60)
    print("Activity Agent Evaluation Framework")
    print("="*60)
    
    # Step 1: Generate scenarios
    print(f"\n[1/4] Generating {args.scenarios} evaluation scenarios...")
    scenarios = generate_eval_dataset(
        count=args.scenarios,
        seed=args.seed,
    )
    print(f"      Generated {len(scenarios)} scenarios")
    
    # Show sample scenarios
    print("\n      Sample scenarios:")
    for scenario in scenarios[:3]:
        print(f"      - [{scenario.category}] {scenario.query[:50]}...")
    
    # Step 2: Run scenarios
    print(f"\n[2/4] Running scenarios through {len(args.models)} model(s)...")
    
    if args.mock:
        print("      (Using MOCK mode - no API calls)")
        runner = MockModeRunner(verbose=False)
        comparison = ModelComparison(results_path=args.output_dir)
        
        for scenario in scenarios:
            comparison.add_scenario(scenario)
        
        for model in args.models:
            print(f"\n      Running with model: {model}")
            results = runner.run_batch(scenarios, model=model, progress=True)
            comparison.add_results(results)
    else:
        print("      (Using LIVE mode - making API calls)")
        comparison = run_comparison(
            scenarios=scenarios,
            models=args.models,
            results_dir=args.output_dir,
            use_mock_llm=True,  # Still use mock LLM judge to save costs
            verbose=True,
        )
    
    # Step 3: Score results
    print("\n[3/4] Scoring results...")
    
    det_scorer = DeterministicScorer()
    llm_scorer = MockLLMJudgeScorer()
    
    for result in comparison.results:
        scenario = comparison.scenarios.get(result.scenario_id)
        if scenario:
            # Compute scores
            det_scores = det_scorer.score(scenario, result)
            llm_scores = llm_scorer.score(scenario, result)
            result.scores = {**det_scores, **llm_scores}
    
    # Step 4: Generate report
    print("\n[4/4] Generating report...")
    
    report = EvalReport(comparison)
    report_path = Path(args.output_dir) / args.report
    report.save_report(str(report_path), format="markdown")
    
    # Also save results
    results_path = comparison.save()
    
    print(f"\n      Report saved to: {report_path}")
    print(f"      Results saved to: {results_path}")
    
    # Print summary
    report.print_summary()
    
    print("\nEvaluation complete!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
