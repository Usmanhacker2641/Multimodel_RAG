"""Compatibility shim for multi-LLM runner.
Exposes generate_multi_llm_responses(prompt, context) used by backend routes.
"""
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Lazy loading to avoid slow imports on startup
_runner_module = None

def _get_runner():
    global _runner_module
    if _runner_module is None:
        try:
            from . import multi_llm_runner
            _runner_module = multi_llm_runner
        except Exception as e:
            logger.warning(f"Could not import multi_llm_runner: {e}")
            _runner_module = False
    return _runner_module

# Provide the same function name expected by backend/query_routes
async def generate_multi_llm_responses_async(prompt, context=None):
    runner = _get_runner()
    if runner:
        return await runner.generate_multi_llm_responses(prompt, context)
    return []

def generate_multi_llm_responses(prompt, context=None):
    """Synchronous wrapper kept for compatibility: returns list of model responses."""
    runner = _get_runner()
    if runner and hasattr(runner, 'run_multi_llm'):
        try:
            return runner.run_multi_llm(prompt, context)
        except Exception as e:
            logger.warning(f"Multi-LLM execution failed: {e}")
    # Fallback to empty list if something fails
    return []

