"""
Response Aggregator Module

Aggregates and combines responses from multiple models.
"""

from typing import List, Dict, Tuple
from collections import Counter
import numpy as np


class ResponseAggregator:
    """Aggregate responses from multiple models."""
    
    def __init__(
        self,
        strategy: str = "weighted_voting",
        weights: Dict[str, float] = None
    ):
        """
        Initialize response aggregator.
        
        Args:
            strategy: Aggregation strategy 
                     ('weighted_voting', 'majority_vote', 'best_score', 'all_responses')
            weights: Model weights for weighted voting
        """
        self.strategy = strategy
        self.weights = weights or {}
    
    def aggregate(
        self,
        responses: List[Dict[str, any]]
    ) -> Dict[str, any]:
        """
        Aggregate multiple model responses.
        
        Args:
            responses: List of response dictionaries with keys:
                      - 'model': model name
                      - 'response': generated text
                      - 'score': confidence score (optional)
                      - 'sources': source documents (optional)
                      
        Returns:
            Aggregated response dictionary
        """
        if not responses:
            return {
                "response": "No responses available",
                "models_used": [],
                "strategy": self.strategy
            }
        
        if self.strategy == "weighted_voting":
            return self._weighted_voting(responses)
        elif self.strategy == "majority_vote":
            return self._majority_vote(responses)
        elif self.strategy == "best_score":
            return self._best_score(responses)
        elif self.strategy == "all_responses":
            return self._all_responses(responses)
        else:
            # Default to all responses
            return self._all_responses(responses)
    
    def _weighted_voting(self, responses: List[Dict]) -> Dict:
        """
        Aggregate using weighted voting.
        Selects response with highest weighted score.
        """
        best_response = None
        best_weighted_score = -float('inf')
        
        for resp in responses:
            model = resp.get('model', 'unknown')
            score = resp.get('score', 1.0)
            weight = self.weights.get(model, 1.0)
            weighted_score = score * weight
            
            if weighted_score > best_weighted_score:
                best_weighted_score = weighted_score
                best_response = resp
        
        return {
            "response": best_response.get('response', ''),
            "primary_model": best_response.get('model', 'unknown'),
            "weighted_score": best_weighted_score,
            "models_used": [r.get('model') for r in responses],
            "strategy": "weighted_voting",
            "sources": best_response.get('sources', [])
        }
    
    def _majority_vote(self, responses: List[Dict]) -> Dict:
        """
        Aggregate using majority voting.
        Selects most common response.
        """
        response_texts = [r.get('response', '') for r in responses]
        
        if not response_texts:
            return self._all_responses(responses)
        
        # Count occurrences
        counter = Counter(response_texts)
        most_common_response, count = counter.most_common(1)[0]
        
        # Find the model that gave this response
        primary_model = None
        sources = []
        for resp in responses:
            if resp.get('response') == most_common_response:
                primary_model = resp.get('model', 'unknown')
                sources = resp.get('sources', [])
                break
        
        return {
            "response": most_common_response,
            "primary_model": primary_model,
            "vote_count": count,
            "total_models": len(responses),
            "models_used": [r.get('model') for r in responses],
            "strategy": "majority_vote",
            "sources": sources
        }
    
    def _best_score(self, responses: List[Dict]) -> Dict:
        """
        Select response with highest confidence score.
        """
        best_response = max(
            responses,
            key=lambda x: x.get('score', 0.0)
        )
        
        return {
            "response": best_response.get('response', ''),
            "primary_model": best_response.get('model', 'unknown'),
            "score": best_response.get('score', 0.0),
            "models_used": [r.get('model') for r in responses],
            "strategy": "best_score",
            "sources": best_response.get('sources', [])
        }
    
    def _all_responses(self, responses: List[Dict]) -> Dict:
        """
        Return all responses from all models.
        """
        return {
            "responses": [
                {
                    "model": r.get('model', 'unknown'),
                    "response": r.get('response', ''),
                    "score": r.get('score'),
                    "sources": r.get('sources', [])
                }
                for r in responses
            ],
            "models_used": [r.get('model') for r in responses],
            "strategy": "all_responses"
        }
    
    def calculate_confidence(self, responses: List[Dict]) -> float:
        """
        Calculate overall confidence score from multiple responses.
        
        Args:
            responses: List of response dictionaries
            
        Returns:
            Confidence score between 0 and 1
        """
        if not responses:
            return 0.0
        
        scores = [r.get('score', 0.5) for r in responses]
        
        # Average with slight boost for agreement
        avg_score = np.mean(scores)
        std_score = np.std(scores) if len(scores) > 1 else 0.0
        
        # Lower standard deviation means more agreement, so higher confidence
        confidence = avg_score * (1 - 0.1 * std_score)
        
        return max(0.0, min(1.0, confidence))
