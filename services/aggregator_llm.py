# from transformers import pipeline  # Commented out to avoid heavy dependency on first run
import logging
from typing import Dict, Optional, List
# import torch

"""
Aggregator LLM Service
Combines responses from multiple models to produce a final, coherent answer using a reasoning LLM.
"""


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AggregatorLLM:
    """
    Aggregator LLM that combines multiple model responses into a unified answer.
    """
    
    def __init__(self, model_name: str = "tiiuae/falcon-7b-instruct"):
        """
        Initialize the aggregator with a reasoning model.
        
        Args:
            model_name: HuggingFace model identifier
        """
        self.model_name = model_name
        self.aggregator = None
        # self._initialize_model()  # Disabled for now, using stub aggregation
        logger.info(f"Aggregator initialized (using stub mode to avoid heavy model loading)")
    
    def _initialize_model(self):
        """Load the reasoning model pipeline."""
        # Commented out to avoid heavy loading
        # try:
        #     logger.info(f"Loading aggregator model: {self.model_name}")
        #     device = 0 if torch.cuda.is_available() else -1
        #     self.aggregator = pipeline(...)
        #     logger.info(f"Aggregator model loaded successfully on device: {'GPU' if device == 0 else 'CPU'}")
        # except Exception as e:
        #     logger.error(f"Error loading aggregator model: {str(e)}")
        #     raise
        pass
    
    def reason_final_answer(
        self, 
        multi_answers: Dict[str, str],
        max_length: int = 512,
        temperature: float = 0.5,
        top_p: float = 0.9
    ) -> str:
        """
        Combine multiple model answers and generate a unified response.
        
        Args:
            multi_answers: Dictionary of model outputs {model_name: response}
            max_length: Maximum length of generated text
            temperature: Sampling temperature (lower = more deterministic)
            top_p: Nucleus sampling parameter
            
        Returns:
            Unified, summarized answer
        """
        try:
            if not multi_answers:
                logger.warning("No answers provided to aggregate")
                return "No responses available to summarize."
            
            # STUB: Simple concatenation for now instead of LLM reasoning
            combined = self._combine_responses(multi_answers)
            
            # Return a simple summary instead of using heavy LLM
            summary = f"Combined insights from {len(multi_answers)} models:\n\n"
            for model_name, response in multi_answers.items():
                summary += f"• {model_name}: {response[:200]}...\n"
            
            logger.info("Generated stub aggregated answer (LLM-based aggregation disabled)")
            return summary.strip()
        
        except Exception as e:
            logger.error(f"Error generating unified answer: {str(e)}")
            return f"Error aggregating responses: {str(e)}"

    def aggregate(
        self,
        query: str,
        multi_answers: Dict[str, str] | List[Dict[str, str]],
        max_length: int = 512,
        temperature: float = 0.5,
        top_p: float = 0.9
    ) -> str:
        """Compatibility wrapper mirroring pipeline expectations."""
        if isinstance(multi_answers, list):
            prepared = {item.get("model_label", item.get("model_id", f"model_{idx}")): item.get("response", "")
                        for idx, item in enumerate(multi_answers)}
        else:
            prepared = multi_answers

        return self.reason_final_answer(
            multi_answers=prepared,
            max_length=max_length,
            temperature=temperature,
            top_p=top_p
        )
    
    def _combine_responses(self, multi_answers: Dict[str, str]) -> str:
        """
        Format multiple model responses into a combined string.
        
        Args:
            multi_answers: Dictionary of model responses
            
        Returns:
            Formatted combined string
        """
        combined_parts = []
        for idx, (model_name, response) in enumerate(multi_answers.items(), 1):
            combined_parts.append(f"Response {idx} ({model_name}):\n{response}")
        
        return "\n\n".join(combined_parts)
    
    def _create_prompt(self, combined_responses: str) -> str:
        """
        Create a reasoning prompt for the aggregator model.
        
        Args:
            combined_responses: Combined model responses
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""You are an expert analyst tasked with synthesizing multiple AI responses into a single, coherent answer.

Below are responses from different models:

{combined_responses}

Task: Analyze these responses and provide a unified, well-reasoned answer that:
1. Identifies common themes and agreements
2. Resolves any contradictions
3. Provides the most accurate and complete information
4. Is clear, concise, and well-structured

Unified Answer:"""
        
        return prompt


# Initialize global aggregator instance
aggregator_llm = AggregatorLLM()


def reason_final_answer(
    multi_answers: Dict[str, str],
    max_length: int = 512,
    temperature: float = 0.5
) -> str:
    """
    Convenience function to generate unified answer from multiple model responses.
    
    Args:
        multi_answers: Dictionary of model outputs {model_name: response}
        max_length: Maximum length of generated text
        temperature: Sampling temperature
        
    Returns:
        Unified, summarized answer
    """
    return aggregator_llm.reason_final_answer(
        multi_answers=multi_answers,
        max_length=max_length,
        temperature=temperature
    )


# Example usage
if __name__ == "__main__":
    # Test with sample responses
    sample_responses = {
        "model_1": "The capital of France is Paris. It's a beautiful city known for the Eiffel Tower.",
        "model_2": "Paris is the capital city of France, located in northern France.",
        "model_3": "France's capital is Paris, which is also its largest city."
    }
    
    print("Testing Aggregator LLM...")
    unified_answer = reason_final_answer(sample_responses)
    print(f"\nUnified Answer:\n{unified_answer}")