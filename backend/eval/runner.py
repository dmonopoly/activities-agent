"""
Evaluation runner for executing scenarios through the orchestrator.

Injects scenario-specific mock data and captures tool calls, arguments,
and final responses for evaluation.
"""

import json
import os
import time
from datetime import datetime
from typing import Any, Callable
from unittest.mock import patch

from eval.scenarios.models import Scenario, ScenarioResult


class EvalRunner:
    """
    Runs evaluation scenarios through the orchestrator.
    
    Injects scenario-specific mock data and captures tool calls,
    arguments, and final responses.
    """
    
    def __init__(
        self,
        model: str | None = None,
        use_live_api: bool = True,
        verbose: bool = False,
    ):
        """
        Initialize the runner.
        
        Args:
            model: Model to use (defaults to orchestrator's default)
            use_live_api: Whether to use live API or mock mode
            verbose: Whether to print progress
        """
        self.model = model
        self.use_live_api = use_live_api
        self.verbose = verbose
        
        # Track captured data during runs
        self._captured_tool_calls: list[dict[str, Any]] = []
        self._captured_tool_results: list[dict[str, Any]] = []
    
    def _create_mock_tool(
        self,
        tool_name: str,
        mock_response: Any,
    ) -> Callable:
        """
        Create a mock tool function that returns scenario-specific data.
        
        Args:
            tool_name: Name of the tool
            mock_response: Response to return
            
        Returns:
            Mock function that logs calls and returns mock response
        """
        def mock_func(*args, **kwargs):
            # Capture the call
            self._captured_tool_calls.append({
                "name": tool_name,
                "arguments": kwargs,
                "timestamp": datetime.now().isoformat(),
            })
            
            # Return mock response
            result = mock_response
            self._captured_tool_results.append({
                "tool": tool_name,
                "result": result,
            })
            
            return result
        
        return mock_func
    
    def _inject_user_preferences(
        self,
        preferences: dict[str, Any],
        user_id: str = "eval_user",
    ) -> None:
        """
        Inject user preferences for the scenario.
        
        Args:
            preferences: Preferences dict
            user_id: User ID to use
        """
        # Import here to avoid circular imports
        from agents.tools.preferences import update_user_preferences
        
        # Set up the preferences
        update_user_preferences(user_id=user_id, preferences=preferences)
    
    def run_scenario(
        self,
        scenario: Scenario,
        model: str | None = None,
    ) -> ScenarioResult:
        """
        Run a single scenario through the orchestrator.
        
        This method:
        1. Sets up scenario-specific mock data for tools
        2. Injects user preferences
        3. Runs the query through the orchestrator
        4. Captures and returns all results
        
        Args:
            scenario: Scenario to run
            model: Override model for this run
            
        Returns:
            ScenarioResult with response and tool call data
        """
        # Reset capture state
        self._captured_tool_calls = []
        self._captured_tool_results = []
        
        # Import orchestrator
        from agents.orchestrator import AgentOrchestrator, OPENROUTER_DEFAULT_MODEL
        
        use_model = model or self.model or OPENROUTER_DEFAULT_MODEL
        
        if self.verbose:
            print(f"[EVAL] Running scenario {scenario.id}")
            print(f"[EVAL] Query: {scenario.query[:80]}...")
            print(f"[EVAL] Model: {use_model}")
        
        start_time = time.time()
        
        # Create mock tools for this scenario
        mock_tools = {}
        for tool_name, mock_response in scenario.mock_tool_responses.items():
            mock_tools[tool_name] = self._create_mock_tool(tool_name, mock_response)
        
        # Build patches for tool functions
        patches = []
        
        # Map tool names to their module paths
        tool_module_paths = {
            "search_places_for_dates": "agents.tools.google_maps.search_places_for_dates",
            "get_weather_for_location": "agents.tools.weather.get_weather_for_location",
            "scrape_activities": "agents.tools.scraper.scrape_activities",
            "save_to_sheets": "agents.tools.sheets.save_to_sheets",
            "get_user_preferences": "agents.tools.preferences.get_user_preferences",
            "update_user_preferences": "agents.tools.preferences.update_user_preferences",
        }
        
        # Also patch in orchestrator's TOOL_FUNCTIONS
        orchestrator_tool_paths = {
            "search_places_for_dates": "agents.orchestrator.search_places_for_dates",
            "get_weather_for_location": "agents.orchestrator.get_weather_for_location",
            "scrape_activities": "agents.orchestrator.scrape_activities",
            "save_to_sheets": "agents.orchestrator.save_to_sheets",
            "get_user_preferences": "agents.orchestrator.get_user_preferences",
            "update_user_preferences": "agents.orchestrator.update_user_preferences",
        }
        
        try:
            # Create patches for each mocked tool
            for tool_name, mock_func in mock_tools.items():
                if tool_name in tool_module_paths:
                    patches.append(patch(tool_module_paths[tool_name], mock_func))
                if tool_name in orchestrator_tool_paths:
                    patches.append(patch(orchestrator_tool_paths[tool_name], mock_func))
            
            # Apply patches
            for p in patches:
                p.start()
            
            # Inject user preferences
            user_id = f"eval_{scenario.id}"
            if scenario.user_preferences:
                self._inject_user_preferences(scenario.user_preferences, user_id)
            
            # Create orchestrator and run
            orchestrator = AgentOrchestrator(user_id=user_id)
            
            # Run the query
            result = orchestrator.process_message(scenario.query, model=use_model)
            
            response = result.get("response", "")
            tool_results = result.get("tool_results", [])
            
        finally:
            # Stop all patches
            for p in patches:
                p.stop()
        
        end_time = time.time()
        duration = end_time - start_time
        
        if self.verbose:
            print(f"[EVAL] Completed in {duration:.2f}s")
            print(f"[EVAL] Tool calls: {len(self._captured_tool_calls)}")
            print(f"[EVAL] Response length: {len(response)} chars")
        
        return ScenarioResult(
            scenario_id=scenario.id,
            model=use_model,
            response=response,
            tool_calls=self._captured_tool_calls,
            tool_results=tool_results or self._captured_tool_results,
            scores={},  # Scores are computed separately by scorers
            metadata={
                "duration_seconds": duration,
                "timestamp": datetime.now().isoformat(),
                "category": scenario.category,
                "region": scenario.region,
            },
        )
    
    def run_batch(
        self,
        scenarios: list[Scenario],
        model: str | None = None,
        progress: bool = True,
    ) -> list[ScenarioResult]:
        """
        Run multiple scenarios.
        
        Args:
            scenarios: List of scenarios to run
            model: Override model for all runs
            progress: Whether to show progress
            
        Returns:
            List of ScenarioResults
        """
        results = []
        total = len(scenarios)
        
        for i, scenario in enumerate(scenarios):
            if progress:
                print(f"[{i+1}/{total}] Running {scenario.id}...")
            
            try:
                result = self.run_scenario(scenario, model=model)
                results.append(result)
            except Exception as e:
                print(f"[ERROR] Scenario {scenario.id} failed: {e}")
                # Create failed result
                results.append(ScenarioResult(
                    scenario_id=scenario.id,
                    model=model or self.model or "unknown",
                    response="",
                    tool_calls=[],
                    tool_results=[],
                    scores={},
                    metadata={
                        "error": str(e),
                        "timestamp": datetime.now().isoformat(),
                    },
                ))
        
        return results
    
    def run_with_multiple_models(
        self,
        scenarios: list[Scenario],
        models: list[str],
        progress: bool = True,
    ) -> dict[str, list[ScenarioResult]]:
        """
        Run scenarios through multiple models for comparison.
        
        Args:
            scenarios: List of scenarios to run
            models: List of model names to compare
            progress: Whether to show progress
            
        Returns:
            Dict mapping model name to list of results
        """
        results_by_model = {}
        
        for model in models:
            print(f"\n{'='*60}")
            print(f"Running with model: {model}")
            print(f"{'='*60}")
            
            results = self.run_batch(scenarios, model=model, progress=progress)
            results_by_model[model] = results
        
        return results_by_model


class MockModeRunner(EvalRunner):
    """
    Evaluation runner that operates entirely in mock mode.
    
    Does not make any real API calls - useful for testing the
    evaluation framework itself.
    """
    
    def __init__(self, verbose: bool = False):
        """Initialize mock mode runner."""
        super().__init__(use_live_api=False, verbose=verbose)
    
    def run_scenario(
        self,
        scenario: Scenario,
        model: str | None = None,
    ) -> ScenarioResult:
        """
        Run a scenario in pure mock mode.
        
        Simulates the orchestrator behavior without making any API calls.
        """
        # Reset capture state
        self._captured_tool_calls = []
        self._captured_tool_results = []
        
        start_time = time.time()
        use_model = model or self.model or "mock-model"
        
        if self.verbose:
            print(f"[MOCK] Running scenario {scenario.id}")
        
        # Simulate tool calls based on expected tools
        for tool_name in scenario.expected_tools:
            if tool_name in scenario.mock_tool_responses:
                self._captured_tool_calls.append({
                    "name": tool_name,
                    "arguments": {},
                    "timestamp": datetime.now().isoformat(),
                })
                self._captured_tool_results.append({
                    "tool": tool_name,
                    "result": scenario.mock_tool_responses[tool_name],
                })
        
        # Generate mock response based on scenario
        mock_response = self._generate_mock_response(scenario)
        
        end_time = time.time()
        
        return ScenarioResult(
            scenario_id=scenario.id,
            model=use_model,
            response=mock_response,
            tool_calls=self._captured_tool_calls,
            tool_results=self._captured_tool_results,
            scores={},
            metadata={
                "duration_seconds": end_time - start_time,
                "timestamp": datetime.now().isoformat(),
                "mock_mode": True,
            },
        )
    
    def _generate_mock_response(self, scenario: Scenario) -> str:
        """Generate a mock response for testing."""
        # Get places from mock data
        places_data = scenario.mock_tool_responses.get("search_places_for_dates", {})
        places = places_data.get("activities", [])
        
        if not places:
            return "I couldn't find any activities matching your request."
        
        # Build a mock response
        place_names = [p.get("name", "Unknown") for p in places[:3]]
        
        return (
            f"I found some great options for you! Here are a few recommendations: "
            f"{', '.join(place_names)}. "
            f"Would you like more details on any of these?"
        )
