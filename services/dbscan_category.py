from sklearn.cluster import DBSCAN
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from typing import List, Dict, Tuple, Optional
import logging

# dbscan_category.py

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def cluster_embeddings(
    embeddings: np.ndarray, 
    eps: float = 0.5, 
    min_samples: int = 3
) -> np.ndarray:
    """
    Apply DBSCAN clustering on embeddings.
    
    Args:
        embeddings: Array of shape (n_samples, n_features)
        eps: Maximum distance between samples for clustering
        min_samples: Minimum samples in a neighborhood for a core point
    
    Returns:
        Array of cluster labels (-1 for noise)
    """
    logger.info(f"Clustering {len(embeddings)} embeddings with eps={eps}, min_samples={min_samples}")
    
    db = DBSCAN(eps=eps, min_samples=min_samples, metric="cosine")
    labels = db.fit_predict(embeddings)
    
    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise = list(labels).count(-1)
    
    logger.info(f"Found {n_clusters} clusters and {n_noise} noise points")
    
    return labels


def get_cluster_centroids(
    embeddings: np.ndarray, 
    labels: np.ndarray
) -> Dict[int, np.ndarray]:
    """
    Calculate centroid for each cluster.
    
    Args:
        embeddings: Original embeddings
        labels: Cluster labels from DBSCAN
    
    Returns:
        Dictionary mapping cluster_id to centroid embedding
    """
    centroids = {}
    unique_labels = set(labels)
    
    for label in unique_labels:
        if label == -1:  # Skip noise points
            continue
        
        mask = labels == label
        cluster_embeddings = embeddings[mask]
        centroids[label] = np.mean(cluster_embeddings, axis=0)
    
    logger.info(f"Calculated centroids for {len(centroids)} clusters")
    return centroids


def classify_query_category(
    query_embedding: np.ndarray, 
    cluster_centroids: Dict[int, np.ndarray]
) -> Tuple[int, float]:
    """
    Classify a query to the most similar cluster.
    
    Args:
        query_embedding: Embedding of the query (1D or 2D array)
        cluster_centroids: Dictionary of cluster centroids
    
    Returns:
        Tuple of (cluster_id, similarity_score)
    """
    if len(cluster_centroids) == 0:
        logger.warning("No clusters available for classification")
        return -1, 0.0
    
    # Ensure query_embedding is 2D
    if query_embedding.ndim == 1:
        query_embedding = query_embedding.reshape(1, -1)
    
    # Stack all centroids
    cluster_ids = list(cluster_centroids.keys())
    centroid_matrix = np.vstack([cluster_centroids[cid] for cid in cluster_ids])
    
    # Calculate similarities
    similarities = cosine_similarity(query_embedding, centroid_matrix)[0]
    
    # Get best match
    best_idx = np.argmax(similarities)
    best_cluster = cluster_ids[best_idx]
    best_score = similarities[best_idx]
    
    logger.info(f"Query classified to cluster {best_cluster} with similarity {best_score:.3f}")
    
    return best_cluster, best_score


def assign_cluster_labels(
    labels: np.ndarray, 
    texts: List[str], 
    category_names: Optional[Dict[int, str]] = None
) -> Dict[int, Dict]:
    """
    Assign semantic labels to clusters.
    
    Args:
        labels: Cluster labels
        texts: Original text chunks
        category_names: Optional manual mapping of cluster_id to category name
    
    Returns:
        Dictionary with cluster information
    """
    cluster_info = {}
    unique_labels = set(labels)
    
    for label in unique_labels:
        if label == -1:
            continue
        
        mask = labels == label
        cluster_texts = [texts[i] for i in range(len(texts)) if mask[i]]
        
        cluster_info[label] = {
            "cluster_id": label,
            "size": len(cluster_texts),
            "category_name": category_names.get(label, f"Category_{label}") if category_names else f"Category_{label}",
            "sample_texts": cluster_texts[:3]  # Store sample texts
        }
    
    return cluster_info


def filter_by_category(
    query_embedding: np.ndarray,
    embeddings: np.ndarray,
    labels: np.ndarray,
    cluster_centroids: Dict[int, np.ndarray],
    threshold: float = 0.7
) -> np.ndarray:
    """
    Filter embeddings by relevant category.
    
    Args:
        query_embedding: Query embedding
        embeddings: All document embeddings
        labels: Cluster labels for embeddings
        cluster_centroids: Cluster centroids
        threshold: Minimum similarity threshold
    
    Returns:
        Boolean mask for relevant embeddings
    """
    cluster_id, similarity = classify_query_category(query_embedding, cluster_centroids)
    
    if similarity < threshold:
        logger.info("No strong category match, returning all embeddings")
        return np.ones(len(embeddings), dtype=bool)
    
    # Return embeddings from the matched cluster
    mask = labels == cluster_id
    logger.info(f"Filtered to {mask.sum()} embeddings from cluster {cluster_id}")
    
    return mask


class DBSCANCategory:
    """Stateful wrapper handling clustering and centroid management."""

    def __init__(self, eps: float = 0.5, min_samples: int = 3):
        self.eps = eps
        self.min_samples = min_samples
        self.labels: Optional[np.ndarray] = None
        self.centroids: Dict[int, np.ndarray] = {}
        self.embeddings: Optional[np.ndarray] = None
        self.texts: List[str] = []

    def update_clusters(self, embeddings: np.ndarray, texts: List[str]) -> np.ndarray:
        if embeddings.size == 0:
            logger.info("No embeddings provided for clustering")
            self.labels = None
            self.centroids = {}
            return np.array([])

        self.embeddings = embeddings
        self.texts = texts
        self.labels = cluster_embeddings(embeddings, eps=self.eps, min_samples=self.min_samples)
        self.centroids = get_cluster_centroids(embeddings, self.labels)
        return self.labels

    def classify(self, query_embedding: np.ndarray) -> Tuple[int, float]:
        if self.centroids:
            return classify_query_category(query_embedding, self.centroids)
        return -1, 0.0

    def mask_by_category(self, query_embedding: np.ndarray, threshold: float = 0.7) -> np.ndarray:
        if self.labels is None or self.embeddings is None:
            return np.ones(len(self.texts), dtype=bool)
        return filter_by_category(query_embedding, self.embeddings, self.labels, self.centroids, threshold)