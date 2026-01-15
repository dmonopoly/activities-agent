"""
Deterministic scoring for evaluation.

Provides rule-based scoring for tool selection, preference adherence,
response structure, and other measurable qualities.
"""

import re
from typing import Any

from eval.scenarios.models import Scenario, ScenarioResult


class DeterministicScorer:
    """
    Computes deterministic scores based on rules and patterns.
    
    Scores (0-100 each):
    - tool_selection: Precision/recall vs expected tools
    - preference_adherence: Check if response references user interests
    - response_structure: Has greeting, recommendations, call-to-action
    - ground_truth_match: Matches scenario's ground truth expectations
    """
    
    def __init__(self):
        """Initialize the scorer."""
        pass
    
    def score(
        self,
        scenario: Scenario,
        result: ScenarioResult,
    ) -> dict[str, float]:
        """
        Compute all deterministic scores.
        
        Args:
            scenario: The scenario that was run
            result: The result of running the scenario
            
        Returns:
            Dict mapping score names to values (0-100)
        """
        scores = {}
        
        # Get actual tool names called
        actual_tools = [tc.get("name", "") for tc in result.tool_calls]
        
        # Tool selection score
        scores["tool_selection"] = self.score_tool_selection(
            expected=scenario.expected_tools,
            actual=actual_tools,
        )
        
        # Preference adherence score
        scores["preference_adherence"] = self.score_preference_adherence(
            preferences=scenario.user_preferences,
            response=result.response,
        )
        
        # Response structure score
        scores["response_structure"] = self.score_response_structure(
            response=result.response,
        )
        
        # Ground truth match score
        scores["ground_truth_match"] = self.score_ground_truth(
            ground_truth=scenario.ground_truth,
            result=result,
        )
        
        # Response length score (penalize too short or too long)
        scores["response_length"] = self.score_response_length(
            response=result.response,
        )
        
        # Compute overall score (weighted average)
        weights = {
            "tool_selection": 0.25,
            "preference_adherence": 0.20,
            "response_structure": 0.20,
            "ground_truth_match": 0.25,
            "response_length": 0.10,
        }
        
        overall = sum(scores[k] * weights[k] for k in weights)
        scores["overall_deterministic"] = overall
        
        return scores
    
    def score_tool_selection(
        self,
        expected: list[str],
        actual: list[str],
    ) -> float:
        """
        Score tool selection accuracy using F1-like metric.
        
        Args:
            expected: List of expected tool names
            actual: List of actually called tool names
            
        Returns:
            Score 0-100
        """
        if not expected and not actual:
            return 100.0  # No tools expected, none called
        
        if not expected:
            # Called tools when none expected
            return 50.0
        
        if not actual:
            # Expected tools but none called
            return 0.0
        
        expected_set = set(expected)
        actual_set = set(actual)
        
        # Calculate precision and recall
        true_positives = len(expected_set & actual_set)
        
        precision = true_positives / len(actual_set) if actual_set else 0
        recall = true_positives / len(expected_set) if expected_set else 0
        
        # F1 score
        if precision + recall == 0:
            f1 = 0
        else:
            f1 = 2 * (precision * recall) / (precision + recall)
        
        return f1 * 100
    
    def score_preference_adherence(
        self,
        preferences: dict[str, Any],
        response: str,
    ) -> float:
        """
        Score how well the response reflects user preferences.
        
        Checks if user interests are mentioned or reflected in the response.
        
        Args:
            preferences: User preferences dict
            response: Agent's response text
            
        Returns:
            Score 0-100
        """
        if not preferences:
            return 100.0  # No preferences to check
        
        interests = preferences.get("interests", [])
        if not interests:
            return 100.0
        
        response_lower = response.lower()
        
        # Check how many interests are reflected
        # Map interest keywords to related terms
        interest_keywords = {
            "coffee": ["coffee", "cafe", "espresso", "latte", "brew"],
            "cafes": ["cafe", "coffee", "bakery", "pastry"],
            "outdoor": ["outdoor", "park", "outside", "nature", "walk", "garden"],
            "nature": ["nature", "park", "garden", "outdoor", "trail", "trees"],
            "parks": ["park", "garden", "outdoor", "green space"],
            "food": ["food", "restaurant", "eat", "dining", "cuisine", "meal"],
            "restaurants": ["restaurant", "dining", "eat", "food", "cuisine"],
            "art": ["art", "museum", "gallery", "exhibition", "sculpture"],
            "museums": ["museum", "exhibition", "art", "gallery", "collection"],
            "galleries": ["gallery", "art", "exhibition", "show"],
            "nightlife": ["bar", "nightlife", "club", "drinks", "cocktail"],
            "bars": ["bar", "drinks", "cocktail", "pub", "tavern"],
            "games": ["game", "arcade", "board game", "escape room", "fun"],
            "entertainment": ["entertainment", "show", "performance", "fun"],
            "music": ["music", "concert", "live", "jazz", "show"],
            "shows": ["show", "theater", "performance", "broadway", "concert"],
            "bookstores": ["book", "bookstore", "reading", "library"],
        }
        
        matched_interests = 0
        for interest in interests:
            interest_lower = interest.lower()
            keywords = interest_keywords.get(interest_lower, [interest_lower])
            
            for keyword in keywords:
                if keyword in response_lower:
                    matched_interests += 1
                    break
        
        if not interests:
            return 100.0
        
        return (matched_interests / len(interests)) * 100
    
    def score_response_structure(self, response: str) -> float:
        """
        Score the structure and format of the response.
        
        Checks for:
        - Has substantial content (not just a short phrase)
        - Has recommendations/suggestions
        - Offers follow-up or call-to-action
        - Proper formatting
        
        Args:
            response: Agent's response text
            
        Returns:
            Score 0-100
        """
        if not response or len(response.strip()) < 10:
            return 0.0
        
        score = 0.0
        response_lower = response.lower()
        
        # Has substantial content (20 points)
        if len(response) >= 100:
            score += 20
        elif len(response) >= 50:
            score += 10
        
        # Contains recommendations/suggestions (25 points)
        recommendation_patterns = [
            r"recommend",
            r"suggest",
            r"here are",
            r"you could",
            r"you might",
            r"check out",
            r"try",
            r"consider",
            r"options",
            r"i found",
        ]
        for pattern in recommendation_patterns:
            if re.search(pattern, response_lower):
                score += 25
                break
        
        # Mentions specific places (25 points)
        # Look for capitalized multi-word names or quotes
        place_patterns = [
            r"[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+",  # Multi-word proper nouns
            r'"[^"]+"|\'[^\']+\'',  # Quoted names
        ]
        has_places = False
        for pattern in place_patterns:
            if re.search(pattern, response):
                has_places = True
                break
        if has_places:
            score += 25
        
        # Contains follow-up/call-to-action (15 points)
        cta_patterns = [
            r"would you like",
            r"let me know",
            r"want me to",
            r"shall i",
            r"more details",
            r"more information",
            r"any questions",
            r"happy to help",
        ]
        for pattern in cta_patterns:
            if re.search(pattern, response_lower):
                score += 15
                break
        
        # Proper sentence structure (15 points)
        if response.strip()[-1] in ".!?":
            score += 8
        if response[0].isupper():
            score += 7
        
        return min(score, 100.0)
    
    def score_ground_truth(
        self,
        ground_truth: dict[str, Any],
        result: ScenarioResult,
    ) -> float:
        """
        Score how well the result matches ground truth expectations.
        
        Args:
            ground_truth: Expected behaviors from scenario
            result: Actual result
            
        Returns:
            Score 0-100
        """
        if not ground_truth:
            return 100.0  # No ground truth to check
        
        checks_passed = 0
        total_checks = 0
        
        response_lower = result.response.lower()
        
        # Check: should_mention_weather
        if "should_mention_weather" in ground_truth:
            total_checks += 1
            expected = ground_truth["should_mention_weather"]
            has_weather = any(
                word in response_lower
                for word in ["weather", "temperature", "sunny", "rainy", "cold", "hot", "warm", "cloudy"]
            )
            if has_weather == expected:
                checks_passed += 1
        
        # Check: should_recommend_outdoor
        if "should_recommend_outdoor" in ground_truth:
            total_checks += 1
            expected = ground_truth["should_recommend_outdoor"]
            has_outdoor = any(
                word in response_lower
                for word in ["outdoor", "outside", "park", "garden", "nature", "walk"]
            )
            if has_outdoor == expected:
                checks_passed += 1
        
        # Check: min_places_mentioned
        if "min_places_mentioned" in ground_truth:
            total_checks += 1
            min_places = ground_truth["min_places_mentioned"]
            # Count capitalized multi-word phrases as potential place names
            place_matches = re.findall(r"[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*", result.response)
            # Filter out common non-place words
            non_places = {"I", "The", "Here", "Would", "Let", "You", "Great", "Thanks"}
            places = [p for p in place_matches if p not in non_places]
            if len(places) >= min_places:
                checks_passed += 1
        
        # Check: should_mention_price
        if "should_mention_price" in ground_truth:
            total_checks += 1
            expected = ground_truth["should_mention_price"]
            has_price = any(
                word in response_lower
                for word in ["$", "price", "cost", "free", "cheap", "budget", "affordable", "expensive"]
            )
            if has_price == expected:
                checks_passed += 1
        
        # Check: should_mention_both_regions
        if "should_mention_both_regions" in ground_truth:
            total_checks += 1
            # This is a loose check - just verify response isn't too short
            if len(result.response) > 100:
                checks_passed += 1
        
        if total_checks == 0:
            return 100.0
        
        return (checks_passed / total_checks) * 100
    
    def score_response_length(
        self,
        response: str,
        min_length: int = 50,
        ideal_length: int = 300,
        max_length: int = 1500,
    ) -> float:
        """
        Score response length (penalize too short or too long).
        
        Args:
            response: Agent's response
            min_length: Minimum acceptable length
            ideal_length: Ideal length (100 score)
            max_length: Maximum before penalty
            
        Returns:
            Score 0-100
        """
        length = len(response)
        
        if length < min_length:
            # Too short - linear penalty
            return (length / min_length) * 50
        
        if length <= ideal_length:
            # Between min and ideal - scale from 50 to 100
            return 50 + ((length - min_length) / (ideal_length - min_length)) * 50
        
        if length <= max_length:
            # Between ideal and max - scale from 100 to 70
            return 100 - ((length - ideal_length) / (max_length - ideal_length)) * 30
        
        # Too long - fixed penalty
        return 50


def compute_aggregate_scores(
    scores_list: list[dict[str, float]],
) -> dict[str, dict[str, float]]:
    """
    Compute aggregate statistics over multiple score dicts.
    
    Args:
        scores_list: List of score dicts from multiple scenarios
        
    Returns:
        Dict with mean, min, max, std for each score type
    """
    if not scores_list:
        return {}
    
    # Collect all score names
    all_keys = set()
    for scores in scores_list:
        all_keys.update(scores.keys())
    
    aggregates = {}
    for key in all_keys:
        values = [s.get(key, 0) for s in scores_list if key in s]
        if not values:
            continue
        
        mean = sum(values) / len(values)
        min_val = min(values)
        max_val = max(values)
        
        # Compute std
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        std = variance ** 0.5
        
        aggregates[key] = {
            "mean": round(mean, 2),
            "min": round(min_val, 2),
            "max": round(max_val, 2),
            "std": round(std, 2),
            "count": len(values),
        }
    
    return aggregates
