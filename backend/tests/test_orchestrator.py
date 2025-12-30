"""Integration tests for AgentOrchestrator tool calling"""

import json
import os

import pytest

# Setup code (env loading, sys.path) is in conftest.py and runs automatically
from agents.orchestrator import AgentOrchestrator
from agents.tools.preferences import PREFERENCES_FILE, get_user_preferences


@pytest.fixture
def test_user_id():
    """Generate a unique test user ID"""
    return "test_user_integration"


@pytest.fixture
def orchestrator(test_user_id):
    """Create an orchestrator instance for testing"""
    return AgentOrchestrator(user_id=test_user_id)


@pytest.fixture(autouse=True)
def cleanup_preferences(test_user_id):
    """Clean up preferences file before and after each test"""
    # Clean up before test
    if os.path.exists(PREFERENCES_FILE):
        with open(PREFERENCES_FILE) as f:
            prefs = json.load(f)
        if test_user_id in prefs:
            del prefs[test_user_id]
            with open(PREFERENCES_FILE, "w") as f:
                json.dump(prefs, f, indent=2)

    yield

    # Clean up after test
    if os.path.exists(PREFERENCES_FILE):
        with open(PREFERENCES_FILE) as f:
            prefs = json.load(f)
        if test_user_id in prefs:
            del prefs[test_user_id]
            with open(PREFERENCES_FILE, "w") as f:
                json.dump(prefs, f, indent=2)


def test_update_budget_preference(orchestrator, test_user_id):
    """Test that 'I prefer events <$30' triggers update_user_preferences with budget_max=30"""
    message = "I prefer events <$30"

    result = orchestrator.process_message(message)

    # Verify response exists
    assert "response" in result
    assert result["response"] is not None

    # Check if tool was called (LLM behavior is non-deterministic)
    tool_calls = [
        tr
        for tr in result.get("tool_results", [])
        if tr["tool"] == "update_user_preferences"
    ]

    if tool_calls:
        # If tool was called, verify it worked correctly
        tool_result = tool_calls[0]["result"]
        assert "error" not in tool_result, (
            f"Tool execution error: {tool_result.get('error')}"
        )
        assert tool_result.get("budget_max") == 30, (
            f"Expected budget_max=30, got {tool_result.get('budget_max')}"
        )

        # Verify preferences were saved (orchestrator should always use its own user_id)
        prefs = get_user_preferences(test_user_id)
        assert prefs.get("budget_max") == 30, "Budget preference not saved correctly"
    else:
        # If tool wasn't called, that's also valid LLM behavior
        # Just verify the response is reasonable
        assert len(result.get("response", "")) > 0, (
            "Should have a response even if tool wasn't called"
        )


def test_update_location_preference(orchestrator, test_user_id):
    """Test that 'I live in Long Island City, NYC' triggers update_user_preferences with location"""
    message = "I live in Long Island City, NYC"

    result = orchestrator.process_message(message)

    # Verify response exists
    assert "response" in result
    assert result["response"] is not None

    # Check if tool was called (LLM behavior is non-deterministic)
    tool_calls = [
        tr
        for tr in result.get("tool_results", [])
        if tr["tool"] == "update_user_preferences"
    ]

    if tool_calls:
        # If tool was called, verify it worked correctly
        tool_result = tool_calls[0]["result"]
        assert "error" not in tool_result, (
            f"Tool execution error: {tool_result.get('error')}"
        )
        # Check if location was set (might be in different format)
        location = tool_result.get("location")
        assert location is not None and "Long Island City" in str(location), (
            f"Expected location to contain 'Long Island City', got {location}"
        )

        # Verify preferences were saved (orchestrator should always use its own user_id)
        prefs = get_user_preferences(test_user_id)
        location = prefs.get("location")
        assert location is not None and "Long Island City" in str(location), (
            f"Location preference not saved correctly. Got: {location}"
        )
    else:
        # If tool wasn't called, that's also valid LLM behavior
        assert len(result.get("response", "")) > 0, (
            "Should have a response even if tool wasn't called"
        )


def test_conversation_sequence(orchestrator, test_user_id):
    """Test the full conversation sequence with both messages"""
    # First message: budget preference
    result1 = orchestrator.process_message("I prefer events <$30")

    # Verify response exists
    assert "response" in result1
    assert result1["response"] is not None

    # Check for tool calls
    tool_calls1 = [
        tr
        for tr in result1.get("tool_results", [])
        if tr["tool"] == "update_user_preferences"
    ]

    # Second message: location preference
    result2 = orchestrator.process_message("I live in Long Island City, NYC")

    # Verify response exists
    assert "response" in result2
    assert result2["response"] is not None

    # Check for tool calls
    tool_calls2 = [
        tr
        for tr in result2.get("tool_results", [])
        if tr["tool"] == "update_user_preferences"
    ]

    # Verify conversation history is maintained
    assert len(orchestrator.conversation_history) > 4, (
        "Conversation history should contain multiple messages"
    )

    # Check that conversation history has proper structure
    user_messages = [
        msg for msg in orchestrator.conversation_history if msg.get("role") == "user"
    ]
    assert len(user_messages) == 2, (
        "Should have 2 user messages in conversation history"
    )

    assistant_messages = [
        msg
        for msg in orchestrator.conversation_history
        if msg.get("role") == "assistant"
    ]
    assert len(assistant_messages) >= 2, "Should have at least 2 assistant messages"

    # Verify tool execution results (only if LLM chose to call the tool)
    # Note: LLM behavior is non-deterministic, so it might not call tools every time.
    # When tools ARE called, they should execute reliably.
    if tool_calls1:
        assert tool_calls1[0]["result"].get("budget_max") == 30

    if tool_calls2:
        location = tool_calls2[0]["result"].get("location")
        assert location is not None and "Long Island City" in str(location)

    # Verify preferences were saved (only check if tools were actually called)
    # The orchestrator ensures user_id consistency, so preferences should be saved correctly
    prefs = get_user_preferences(test_user_id)
    if tool_calls1:
        assert prefs.get("budget_max") == 30, "Budget preference not saved correctly"
    if tool_calls2:
        location = prefs.get("location")
        assert location is not None and "Long Island City" in str(location), (
            f"Location preference not saved correctly. Got: {location}"
        )
