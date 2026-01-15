"""
Data models for evaluation scenarios.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Scenario:
    """
    A single evaluation scenario bundling a query with its mock data.
    
    Attributes:
        id: Unique identifier for the scenario
        category: Category of the scenario (e.g., "date_activities", "outdoor")
        query: The user query to send to the orchestrator
        region: Region ID for geographically coherent mock data
        user_preferences: User preferences to set before running
        mock_tool_responses: Dict mapping tool names to their mock responses
        expected_tools: List of tools expected to be called
        ground_truth: Dict of expected behaviors for deterministic scoring
    """
    id: str
    category: str
    query: str
    region: str
    user_preferences: dict[str, Any] = field(default_factory=dict)
    mock_tool_responses: dict[str, Any] = field(default_factory=dict)
    expected_tools: list[str] = field(default_factory=list)
    ground_truth: dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "category": self.category,
            "query": self.query,
            "region": self.region,
            "user_preferences": self.user_preferences,
            "mock_tool_responses": self.mock_tool_responses,
            "expected_tools": self.expected_tools,
            "ground_truth": self.ground_truth,
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Scenario":
        """Create a Scenario from a dictionary."""
        return cls(
            id=data["id"],
            category=data["category"],
            query=data["query"],
            region=data["region"],
            user_preferences=data.get("user_preferences", {}),
            mock_tool_responses=data.get("mock_tool_responses", {}),
            expected_tools=data.get("expected_tools", []),
            ground_truth=data.get("ground_truth", {}),
        )


@dataclass
class ScenarioResult:
    """
    Result of running a scenario through the orchestrator.
    
    Attributes:
        scenario_id: ID of the scenario that was run
        model: Model used for the run
        response: Final response text from the orchestrator
        tool_calls: List of tool calls made (name, arguments)
        tool_results: Results returned by each tool
        scores: Dict of score name to score value
        metadata: Additional metadata (timestamps, versions, etc.)
    """
    scenario_id: str
    model: str
    response: str
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    tool_results: list[dict[str, Any]] = field(default_factory=list)
    scores: dict[str, float] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "scenario_id": self.scenario_id,
            "model": self.model,
            "response": self.response,
            "tool_calls": self.tool_calls,
            "tool_results": self.tool_results,
            "scores": self.scores,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ScenarioResult":
        """Create a ScenarioResult from a dictionary."""
        return cls(
            scenario_id=data["scenario_id"],
            model=data["model"],
            response=data["response"],
            tool_calls=data.get("tool_calls", []),
            tool_results=data.get("tool_results", []),
            scores=data.get("scores", {}),
            metadata=data.get("metadata", {}),
        )
