import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any
import json
from pathlib import Path

class FeedbackDAO:
    """
    Data Access Object for managing user feedback and enabling self-improvement
    of the RAG system through adaptive learning.
    """
    
    def __init__(self, db_path: str = "feedback.db"):
        """Initialize feedback database connection."""
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Create feedback and analytics tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Main feedback table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                query TEXT NOT NULL,
                model_name TEXT NOT NULL,
                rating TEXT NOT NULL CHECK(rating IN ('positive', 'negative', 'neutral')),
                comment TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        """)
        
        # Model performance analytics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS model_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name TEXT NOT NULL,
                category TEXT,
                positive_count INTEGER DEFAULT 0,
                negative_count INTEGER DEFAULT 0,
                neutral_count INTEGER DEFAULT 0,
                total_count INTEGER DEFAULT 0,
                avg_rating REAL,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(model_name, category)
            )
        """)
        
        # Cluster feedback for DBSCAN refinement
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cluster_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cluster_id INTEGER NOT NULL,
                query TEXT NOT NULL,
                expected_category TEXT,
                actual_category TEXT,
                misclassified BOOLEAN DEFAULT 0,
                feedback_count INTEGER DEFAULT 1,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indices for faster queries
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_session ON feedback(session_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_model ON feedback(model_name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_rating ON feedback(rating)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON feedback(timestamp)")
        
        conn.commit()
        conn.close()
    
    def store_feedback(self, 
                       session_id: str,
                       query: str,
                       model_name: str,
                       rating: str,
                       comment: Optional[str] = None,
                       metadata: Optional[Dict[str, Any]] = None) -> int:
        """
        Store user feedback for a model response.
        
        Args:
            session_id: Unique session identifier
            query: User's original query
            model_name: Name of the model that generated the response
            rating: 'positive', 'negative', or 'neutral'
            comment: Optional textual feedback
            metadata: Additional context (category, retrieval score, etc.)
        
        Returns:
            Feedback ID
        """
        if rating not in ['positive', 'negative', 'neutral']:
            raise ValueError("Rating must be 'positive', 'negative', or 'neutral'")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        metadata_json = json.dumps(metadata) if metadata else None
        
        cursor.execute("""
            INSERT INTO feedback (session_id, query, model_name, rating, comment, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (session_id, query, model_name, rating, comment, metadata_json))
        
        feedback_id = cursor.lastrowid
        
        # Update model performance analytics
        category = metadata.get('category', 'general') if metadata else 'general'
        self._update_model_performance(cursor, model_name, category, rating)
        
        conn.commit()
        conn.close()
        
        return feedback_id
    
    def _update_model_performance(self, cursor, model_name: str, category: str, rating: str):
        """Update aggregated model performance metrics."""
        cursor.execute("""
            INSERT INTO model_performance (model_name, category, positive_count, negative_count, neutral_count, total_count)
            VALUES (?, ?, 0, 0, 0, 0)
            ON CONFLICT(model_name, category) DO NOTHING
        """, (model_name, category))
        
        # Increment appropriate counter
        rating_column = f"{rating}_count"
        cursor.execute(f"""
            UPDATE model_performance
            SET {rating_column} = {rating_column} + 1,
                total_count = total_count + 1,
                avg_rating = CAST(positive_count - negative_count AS REAL) / total_count,
                last_updated = CURRENT_TIMESTAMP
            WHERE model_name = ? AND category = ?
        """, (model_name, category))
    
    def store_cluster_feedback(self,
                               cluster_id: int,
                               query: str,
                               expected_category: str,
                               actual_category: str,
                               misclassified: bool = False):
        """
        Store feedback about clustering performance for DBSCAN refinement.
        
        Args:
            cluster_id: Cluster identifier
            query: Original query
            expected_category: What user indicated it should be
            actual_category: What the system classified it as
            misclassified: Whether this was a misclassification
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO cluster_feedback 
            (cluster_id, query, expected_category, actual_category, misclassified)
            VALUES (?, ?, ?, ?, ?)
        """, (cluster_id, query, expected_category, actual_category, misclassified))
        
        conn.commit()
        conn.close()
    
    def get_model_analytics(self, model_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get performance analytics for models.
        
        Args:
            model_name: Optional filter for specific model
        
        Returns:
            List of performance metrics by model and category
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if model_name:
            cursor.execute("""
                SELECT model_name, category, positive_count, negative_count, neutral_count,
                       total_count, avg_rating, last_updated
                FROM model_performance
                WHERE model_name = ?
                ORDER BY category
            """, (model_name,))
        else:
            cursor.execute("""
                SELECT model_name, category, positive_count, negative_count, neutral_count,
                       total_count, avg_rating, last_updated
                FROM model_performance
                ORDER BY model_name, category
            """)
        
        results = []
        for row in cursor.fetchall():
            total = row[5]
            results.append({
                'model_name': row[0],
                'category': row[1],
                'positive_count': row[2],
                'negative_count': row[3],
                'neutral_count': row[4],
                'total_count': total,
                'avg_rating': row[6],
                'positive_rate': (row[2] / total * 100) if total > 0 else 0,
                'negative_rate': (row[3] / total * 100) if total > 0 else 0,
                'last_updated': row[7]
            })
        
        conn.close()
        return results
    
    def get_misclassified_queries(self, min_count: int = 2) -> List[Dict[str, Any]]:
        """
        Get queries that were frequently misclassified for cluster refinement.
        
        Args:
            min_count: Minimum feedback count to consider
        
        Returns:
            List of misclassified queries with categories
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT cluster_id, query, expected_category, actual_category, 
                   COUNT(*) as feedback_count
            FROM cluster_feedback
            WHERE misclassified = 1
            GROUP BY cluster_id, expected_category, actual_category
            HAVING COUNT(*) >= ?
            ORDER BY feedback_count DESC
        """, (min_count,))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'cluster_id': row[0],
                'query': row[1],
                'expected_category': row[2],
                'actual_category': row[3],
                'feedback_count': row[4]
            })
        
        conn.close()
        return results
    
    def get_negative_feedback(self, 
                             model_name: Optional[str] = None,
                             limit: int = 100) -> List[Dict[str, Any]]:
        """
        Retrieve negative feedback for retraining and model refinement.
        
        Args:
            model_name: Optional filter for specific model
            limit: Maximum number of results
        
        Returns:
            List of negative feedback entries
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if model_name:
            cursor.execute("""
                SELECT id, session_id, query, model_name, comment, metadata, timestamp
                FROM feedback
                WHERE rating = 'negative' AND model_name = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (model_name, limit))
        else:
            cursor.execute("""
                SELECT id, session_id, query, model_name, comment, metadata, timestamp
                FROM feedback
                WHERE rating = 'negative'
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
        
        results = []
        for row in cursor.fetchall():
            metadata = json.loads(row[5]) if row[5] else {}
            results.append({
                'id': row[0],
                'session_id': row[1],
                'query': row[2],
                'model_name': row[3],
                'comment': row[4],
                'metadata': metadata,
                'timestamp': row[6]
            })
        
        conn.close()
        return results
    
    def generate_insights_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive insights for system optimization.
        
        Returns:
            Dictionary with key insights and recommendations
        """
        analytics = self.get_model_analytics()
        misclassified = self.get_misclassified_queries()
        
        # Find best performing models by category
        best_models = {}
        for entry in analytics:
            category = entry['category']
            if category not in best_models or entry['positive_rate'] > best_models[category]['positive_rate']:
                best_models[category] = {
                    'model_name': entry['model_name'],
                    'positive_rate': entry['positive_rate'],
                    'total_count': entry['total_count']
                }
        
        # Identify underperforming models
        underperforming = [
            entry for entry in analytics 
            if entry['total_count'] >= 10 and entry['positive_rate'] < 50
        ]
        
        # Clustering issues
        cluster_issues = len(misclassified)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'best_models_by_category': best_models,
            'underperforming_models': underperforming,
            'clustering_issues_count': cluster_issues,
            'misclassified_queries': misclassified[:10],  # Top 10
            'total_feedback_count': sum(entry['total_count'] for entry in analytics),
            'recommendations': self._generate_recommendations(best_models, underperforming, cluster_issues)
        }
    
    def _generate_recommendations(self, best_models, underperforming, cluster_issues):
        """Generate actionable recommendations based on feedback analysis."""
        recommendations = []
        
        if underperforming:
            recommendations.append({
                'type': 'model_optimization',
                'priority': 'high',
                'action': f'Review and retrain {len(underperforming)} underperforming models',
                'models': [m['model_name'] for m in underperforming]
            })
        
        if cluster_issues > 5:
            recommendations.append({
                'type': 'clustering',
                'priority': 'medium',
                'action': f'Adjust DBSCAN parameters - {cluster_issues} misclassification patterns detected',
                'suggestion': 'Consider reducing eps or increasing min_samples'
            })
        
        if best_models:
            recommendations.append({
                'type': 'model_prioritization',
                'priority': 'low',
                'action': 'Prioritize best-performing models by category',
                'models': {cat: data['model_name'] for cat, data in best_models.items()}
            })
        
        return recommendations
    
    def export_training_data(self, output_path: str, rating_filter: Optional[str] = None):
        """
        Export feedback data for model fine-tuning.
        
        Args:
            output_path: Path to save JSON file
            rating_filter: Optional filter ('positive', 'negative', 'neutral')
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT query, model_name, rating, comment, metadata FROM feedback"
        params = ()
        
        if rating_filter:
            query += " WHERE rating = ?"
            params = (rating_filter,)
        
        cursor.execute(query, params)
        
        training_data = []
        for row in cursor.fetchall():
            metadata = json.loads(row[4]) if row[4] else {}
            training_data.append({
                'query': row[0],
                'model_name': row[1],
                'rating': row[2],
                'comment': row[3],
                'metadata': metadata
            })
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(training_data, f, indent=2, ensure_ascii=False)
        
        conn.close()
        return len(training_data)