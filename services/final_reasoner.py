"""Simple aggregator/reasoner for combining multiple LLM outputs.

This is a placeholder: it concatenates answers and returns a simple consensus string.
"""
from typing import List, Dict


def reason_final_answer(multi_responses: List[Dict[str, str]]) -> str:
    """Combine multiple LLM responses into a single answer.

    Args:
        multi_responses: list or dict of model responses

    Returns:
        A final aggregated string
    """
    # Accept both dict and list inputs
    if isinstance(multi_responses, dict):
        parts = [f"[{k}] {v}" for k, v in multi_responses.items()]
    elif isinstance(multi_responses, list):
        parts = [str(item) for item in multi_responses]
    else:
        return "No responses to reason over."

    # Very naive aggregation: join and return
    combined = "\n\n".join(parts)
    return f"Aggregated answer:\n\n{combined}"
