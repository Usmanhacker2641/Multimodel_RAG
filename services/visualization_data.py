import numpy as np
from typing import Dict, List, Any, Optional
import logging
from sklearn.decomposition import PCA

# visualization_data.py

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_similarity_scores(embeddings: np.ndarray) -> Dict[str, float]:
    """
    Calculate similarity scores from embeddings.
    
    Args:
        embeddings: Array of embeddings with shape (n_samples, embedding_dim)
    
    Returns:
        Dictionary containing mean and standard deviation of similarity scores
    """
    try:
        if embeddings is None or len(embeddings) == 0:
            logger.warning("Empty embeddings provided")
            return {"mean": 0.0, "std_dev": 0.0}
        
        # Calculate mean across samples
        mean_score = np.mean(embeddings, axis=0)
        
        # Calculate overall statistics
        result = {
            "mean": float(np.mean(mean_score)),
            "std_dev": float(np.std(mean_score)),
            "min": float(np.min(embeddings)),
            "max": float(np.max(embeddings))
        }
        
        logger.info(f"Similarity scores calculated: {result}")
        return result
    
    except Exception as e:
        logger.error(f"Error calculating similarity scores: {e}")
        return {"mean": 0.0, "std_dev": 0.0, "min": 0.0, "max": 0.0}


def prepare_model_comparison(multi_answers: Dict[str, str]) -> List[Dict[str, Any]]:
    """
    Prepare model comparison data for visualization.
    
    Args:
        multi_answers: Dictionary with model names as keys and answers as values
    
    Returns:
        List of dictionaries containing model comparison metrics
    """
    try:
        if not multi_answers:
            logger.warning("No model answers provided")
            return []
        
        comparison_data = []
        max_length = max(len(v) for v in multi_answers.values()) if multi_answers else 1
        
        for model_name, answer in multi_answers.items():
            answer_length = len(answer)
            
            # Calculate confidence based on answer length relative to max
            confidence = min(answer_length / max(max_length, 1), 1.0)
            
            comparison_data.append({
                "model": model_name,
                "length": answer_length,
                "confidence": round(confidence, 3),
                "word_count": len(answer.split()) if answer else 0
            })
        
        logger.info(f"Model comparison prepared for {len(comparison_data)} models")
        return comparison_data
    
    except Exception as e:
        logger.error(f"Error preparing model comparison: {e}")
        return []


def prepare_confidence_distribution(scores: List[float]) -> Dict[str, Any]:
    """
    Prepare confidence score distribution data.
    
    Args:
        scores: List of confidence scores
    
    Returns:
        Dictionary containing distribution statistics
    """
    try:
        if not scores:
            return {"bins": [], "counts": [], "statistics": {}}
        
        scores_array = np.array(scores)
        
        # Create histogram data
        counts, bins = np.histogram(scores_array, bins=10)
        
        distribution = {
            "bins": bins.tolist(),
            "counts": counts.tolist(),
            "statistics": {
                "mean": float(np.mean(scores_array)),
                "median": float(np.median(scores_array)),
                "std_dev": float(np.std(scores_array)),
                "min": float(np.min(scores_array)),
                "max": float(np.max(scores_array))
            }
        }
        
        logger.info("Confidence distribution prepared")
        return distribution
    
    except Exception as e:
        logger.error(f"Error preparing confidence distribution: {e}")
        return {"bins": [], "counts": [], "statistics": {}}


def prepare_cluster_graph_data(embeddings: np.ndarray, labels: Optional[np.ndarray] = None) -> Dict[str, Any]:
    """
    Prepare data for cluster visualization graph.
    
    Args:
        embeddings: Array of embeddings
        labels: Optional cluster labels
    
    Returns:
        Dictionary containing graph coordinates and labels
    """
    try:
        if embeddings is None or len(embeddings) == 0:
            return {"x": [], "y": [], "labels": []}
        
        # Use PCA for dimensionality reduction to 2D if needed
        
        if embeddings.shape[1] > 2:
            pca = PCA(n_components=2)
            coords_2d = pca.fit_transform(embeddings)
        else:
            coords_2d = embeddings
        
        graph_data = {
            "x": coords_2d[:, 0].tolist(),
            "y": coords_2d[:, 1].tolist(),
            "labels": labels.tolist() if labels is not None else list(range(len(embeddings)))
        }
        
        logger.info(f"Cluster graph data prepared for {len(embeddings)} points")
        return graph_data
    
    except Exception as e:
        logger.error(f"Error preparing cluster graph data: {e}")
        return {"x": [], "y": [], "labels": []}


def prepare_performance_metrics(metrics: Dict[str, float]) -> List[Dict[str, Any]]:
    """
    Prepare performance metrics for visualization.
    
    Args:
        metrics: Dictionary of metric names and values
    
    Returns:
        List of formatted metric dictionaries
    """
    try:
        performance_data = [
            {
                "metric": metric_name,
                "value": round(value, 4),
                "percentage": round(value * 100, 2) if 0 <= value <= 1 else None
            }
            for metric_name, value in metrics.items()
        ]
        
        logger.info(f"Performance metrics prepared: {len(performance_data)} metrics")
        return performance_data
    
    except Exception as e:
        logger.error(f"Error preparing performance metrics: {e}")
        return []


def prepare_time_series_data(timestamps: List[str], values: List[float]) -> Dict[str, List]:
    """
    Prepare time series data for visualization.
    
    Args:
        timestamps: List of timestamp strings
        values: List of corresponding values
    
    Returns:
        Dictionary with timestamps and values
    """
    try:
        if len(timestamps) != len(values):
            logger.warning("Timestamps and values length mismatch")
            return {"timestamps": [], "values": []}
        
        return {
            "timestamps": timestamps,
            "values": values
        }
    
    except Exception as e:
        logger.error(f"Error preparing time series data: {e}")
        return {"timestamps": [], "values": []}