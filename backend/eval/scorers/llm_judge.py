"""
LLM-as-Judge scoring for evaluation.

Uses another LLM to evaluate response quality on multiple dimensions
with detailed rubrics.
"""

import json
import os
import re
from typing import Any

from openai import OpenAI

from eval.scenarios.models import Scenario, ScenarioResult


# Judge model configuration
JUDGE_API_KEY = os.getenv("OPENROUTER_API_KEY")
JUDGE_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_JUDGE_MODEL = "openai/gpt-4o-mini"


# Evaluation rubrics for each dimension
RUBRICS = {
    "coherence": """
Rate the COHERENCE of this response on a scale of 1-5:

1 - Incoherent: Response is confusing, jumps between topics randomly, or contradicts itself.
2 - Poor: Some logical flow but significant gaps or confusing sections.
3 - Adequate: Generally coherent but could be better organized.
4 - Good: Well-organized, easy to follow, minor issues only.
5 - Excellent: Crystal clear, logically structured, flows naturally from start to finish.

Focus on: logical flow, organization, clarity of expression.
""",
    
    "relevance": """
Rate the RELEVANCE of this response on a scale of 1-5:

1 - Off-topic: Response doesn't address the user's query at all.
2 - Tangential: Touches on the topic but misses the main point.
3 - Partially relevant: Addresses some aspects but misses key parts of the query.
4 - Mostly relevant: Addresses the main query with minor omissions.
5 - Perfectly relevant: Directly and fully addresses everything the user asked.

Focus on: Does it answer what was asked? Does it stay on topic?
""",
    
    "helpfulness": """
Rate the HELPFULNESS of this response on a scale of 1-5:

1 - Unhelpful: Provides no useful information or actionable suggestions.
2 - Slightly helpful: Some information but not actionable or practical.
3 - Moderately helpful: Provides useful info but could be more specific or actionable.
4 - Very helpful: Good recommendations with useful details.
5 - Extremely helpful: Excellent, specific recommendations with details that enable action.

Focus on: Can the user act on this advice? Is it practical and specific?
""",
    
    "grounding": """
Rate the GROUNDING of this response on a scale of 1-5:

Given the tool results (actual data) provided, rate how accurately the response reflects that data.

1 - Fabricated: Makes up information not in the tool results.
2 - Poor grounding: Mostly ignores tool results, invents details.
3 - Partial grounding: Uses some tool data but adds unsupported claims.
4 - Good grounding: Accurately represents tool data with minor liberties.
5 - Perfect grounding: All claims are supported by the tool results.

Focus on: Does the response accurately represent the provided data?
""",
    
    "tone": """
Rate the TONE of this response on a scale of 1-5:

1 - Inappropriate: Rude, dismissive, or unprofessional tone.
2 - Awkward: Stilted, overly formal, or oddly casual for context.
3 - Acceptable: Neutral tone, nothing remarkable.
4 - Good: Friendly and professional, appropriate for the context.
5 - Excellent: Warm, engaging, perfectly matches the conversational context.

Focus on: Is the tone appropriate for a helpful activity assistant?
""",
}


JUDGE_SYSTEM_PROMPT = """You are an expert evaluator assessing the quality of an AI assistant's responses.

You will be given:
1. The user's original query
2. The tool results (data available to the assistant)
3. The assistant's response

Your task is to rate the response on the specified dimension using the provided rubric.

IMPORTANT:
- Be objective and consistent
- Use the full 1-5 scale
- Provide a brief justification for your score
- Output ONLY valid JSON in this exact format:
{"score": <number 1-5>, "justification": "<brief explanation>"}
"""


class LLMJudgeScorer:
    """
    Uses an LLM to score response quality.
    
    Scores (1-5 each):
    - coherence: Is the response well-organized and easy to follow?
    - relevance: Does the response address the user's query?
    - helpfulness: Does it provide actionable, useful recommendations?
    - grounding: Does the response accurately reflect the tool results?
    - tone: Is the tone appropriate and engaging?
    """
    
    def __init__(
        self,
        judge_model: str = DEFAULT_JUDGE_MODEL,
        api_key: str | None = None,
    ):
        """
        Initialize the LLM judge.
        
        Args:
            judge_model: Model to use for judging (OpenRouter format)
            api_key: API key (defaults to OPENROUTER_API_KEY env var)
        """
        self.judge_model = judge_model
        self.api_key = api_key or JUDGE_API_KEY
        
        if not self.api_key:
            raise ValueError("No API key provided for LLM judge")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=JUDGE_BASE_URL,
        )
    
    def _format_tool_results(self, tool_results: list[dict[str, Any]]) -> str:
        """Format tool results for the judge prompt."""
        if not tool_results:
            return "No tool results available."
        
        formatted = []
        for tr in tool_results:
            tool_name = tr.get("tool", "unknown")
            result = tr.get("result", {})
            
            # Truncate large results
            result_str = json.dumps(result, indent=2)
            if len(result_str) > 1000:
                result_str = result_str[:1000] + "...(truncated)"
            
            formatted.append(f"Tool: {tool_name}\nResult:\n{result_str}")
        
        return "\n\n".join(formatted)
    
    def _call_judge(
        self,
        query: str,
        tool_results: list[dict[str, Any]],
        response: str,
        dimension: str,
        rubric: str,
    ) -> dict[str, Any]:
        """
        Call the judge LLM for a single dimension.
        
        Args:
            query: User's original query
            tool_results: Tool results available to the assistant
            response: Assistant's response
            dimension: Dimension being evaluated
            rubric: Rubric for this dimension
            
        Returns:
            Dict with score and justification
        """
        tool_results_str = self._format_tool_results(tool_results)
        
        user_prompt = f"""
Evaluate the following response on the dimension: {dimension.upper()}

{rubric}

---
USER QUERY:
{query}

---
TOOL RESULTS (data available to the assistant):
{tool_results_str}

---
ASSISTANT'S RESPONSE:
{response}

---
Provide your evaluation as JSON: {{"score": <1-5>, "justification": "<explanation>"}}
"""
        
        try:
            completion = self.client.chat.completions.create(
                model=self.judge_model,
                messages=[
                    {"role": "system", "content": JUDGE_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.1,  # Low temperature for consistency
                max_tokens=200,
            )
            
            content = completion.choices[0].message.content or ""
            
            # Parse JSON response
            # Try to extract JSON from the response
            json_match = re.search(r'\{[^}]+\}', content)
            if json_match:
                result = json.loads(json_match.group())
                return {
                    "score": float(result.get("score", 3)),
                    "justification": result.get("justification", ""),
                }
            
            # Fallback: try to parse the whole response
            result = json.loads(content)
            return {
                "score": float(result.get("score", 3)),
                "justification": result.get("justification", ""),
            }
            
        except Exception as e:
            # On error, return neutral score
            return {
                "score": 3.0,
                "justification": f"Error during evaluation: {str(e)}",
            }
    
    def score(
        self,
        scenario: Scenario,
        result: ScenarioResult,
    ) -> dict[str, float]:
        """
        Compute all LLM-as-Judge scores.
        
        Args:
            scenario: The scenario that was run
            result: The result of running the scenario
            
        Returns:
            Dict mapping score names to values (1-5 scale, normalized to 0-100)
        """
        scores = {}
        justifications = {}
        
        for dimension, rubric in RUBRICS.items():
            eval_result = self._call_judge(
                query=scenario.query,
                tool_results=result.tool_results,
                response=result.response,
                dimension=dimension,
                rubric=rubric,
            )
            
            # Store raw 1-5 score and normalized 0-100 score
            raw_score = eval_result["score"]
            normalized_score = (raw_score - 1) * 25  # 1-5 -> 0-100
            
            scores[f"llm_{dimension}"] = normalized_score
            scores[f"llm_{dimension}_raw"] = raw_score
            justifications[dimension] = eval_result["justification"]
        
        # Compute overall LLM score (average of normalized scores)
        dimension_scores = [scores[f"llm_{dim}"] for dim in RUBRICS.keys()]
        scores["llm_overall"] = sum(dimension_scores) / len(dimension_scores)
        
        # Store justifications in metadata (optional, for debugging)
        scores["_justifications"] = justifications  # type: ignore
        
        return scores
    
    def score_single_dimension(
        self,
        scenario: Scenario,
        result: ScenarioResult,
        dimension: str,
    ) -> dict[str, Any]:
        """
        Score a single dimension.
        
        Args:
            scenario: The scenario that was run
            result: The result of running the scenario
            dimension: Which dimension to score
            
        Returns:
            Dict with score and justification
        """
        if dimension not in RUBRICS:
            raise ValueError(f"Unknown dimension: {dimension}")
        
        return self._call_judge(
            query=scenario.query,
            tool_results=result.tool_results,
            response=result.response,
            dimension=dimension,
            rubric=RUBRICS[dimension],
        )


class MockLLMJudgeScorer:
    """
    Mock LLM judge for testing without API calls.
    
    Returns random scores for testing the evaluation framework.
    """
    
    def __init__(self):
        """Initialize mock scorer."""
        import random
        self._random = random
    
    def score(
        self,
        scenario: Scenario,
        result: ScenarioResult,
    ) -> dict[str, float]:
        """Return mock scores."""
        scores = {}
        
        for dimension in RUBRICS.keys():
            # Generate semi-realistic scores based on response length
            base_score = 3.0
            if len(result.response) > 200:
                base_score += 0.5
            if len(result.response) > 500:
                base_score += 0.5
            
            raw_score = min(5.0, max(1.0, base_score + self._random.uniform(-0.5, 0.5)))
            normalized_score = (raw_score - 1) * 25
            
            scores[f"llm_{dimension}"] = normalized_score
            scores[f"llm_{dimension}_raw"] = raw_score
        
        dimension_scores = [scores[f"llm_{dim}"] for dim in RUBRICS.keys()]
        scores["llm_overall"] = sum(dimension_scores) / len(dimension_scores)
        
        return scores
