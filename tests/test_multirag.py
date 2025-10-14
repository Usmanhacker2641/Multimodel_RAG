"""
Unit tests for MultiRAG components
"""

import unittest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock

from multirag.document_processor import DocumentProcessor
from multirag.response_aggregator import ResponseAggregator


class TestDocumentProcessor(unittest.TestCase):
    """Test DocumentProcessor functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.processor = DocumentProcessor(chunk_size=100, chunk_overlap=20)
    
    def test_initialization(self):
        """Test processor initialization."""
        self.assertEqual(self.processor.chunk_size, 100)
        self.assertEqual(self.processor.chunk_overlap, 20)
    
    def test_process_text(self):
        """Test text processing."""
        text = "This is a test. " * 50  # Long text to force chunking
        chunks = self.processor.process_text(text)
        
        self.assertIsInstance(chunks, list)
        self.assertGreater(len(chunks), 0)
    
    def test_load_text_file(self):
        """Test loading text file."""
        # Create temporary text file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Test document content for RAG system.")
            temp_path = f.name
        
        try:
            documents = self.processor.load_documents(temp_path)
            self.assertIsInstance(documents, list)
            self.assertGreater(len(documents), 0)
        finally:
            os.unlink(temp_path)
    
    def test_file_not_found(self):
        """Test handling of non-existent file."""
        with self.assertRaises(FileNotFoundError):
            self.processor.load_documents("/nonexistent/path/file.txt")


class TestResponseAggregator(unittest.TestCase):
    """Test ResponseAggregator functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.aggregator = ResponseAggregator(
            strategy="weighted_voting",
            weights={"model1": 1.0, "model2": 1.5}
        )
    
    def test_initialization(self):
        """Test aggregator initialization."""
        self.assertEqual(self.aggregator.strategy, "weighted_voting")
        self.assertEqual(self.aggregator.weights["model2"], 1.5)
    
    def test_weighted_voting(self):
        """Test weighted voting strategy."""
        responses = [
            {
                'model': 'model1',
                'response': 'Answer from model 1',
                'score': 0.8
            },
            {
                'model': 'model2',
                'response': 'Answer from model 2',
                'score': 0.7
            }
        ]
        
        result = self.aggregator.aggregate(responses)
        
        self.assertIn('response', result)
        self.assertIn('primary_model', result)
        self.assertIn('models_used', result)
        self.assertEqual(len(result['models_used']), 2)
    
    def test_majority_vote(self):
        """Test majority voting strategy."""
        aggregator = ResponseAggregator(strategy="majority_vote")
        
        responses = [
            {'model': 'model1', 'response': 'Answer A', 'score': 0.8},
            {'model': 'model2', 'response': 'Answer A', 'score': 0.7},
            {'model': 'model3', 'response': 'Answer B', 'score': 0.9},
        ]
        
        result = aggregator.aggregate(responses)
        
        self.assertEqual(result['response'], 'Answer A')
        self.assertEqual(result['vote_count'], 2)
    
    def test_best_score(self):
        """Test best score strategy."""
        aggregator = ResponseAggregator(strategy="best_score")
        
        responses = [
            {'model': 'model1', 'response': 'Answer 1', 'score': 0.8},
            {'model': 'model2', 'response': 'Answer 2', 'score': 0.9},
            {'model': 'model3', 'response': 'Answer 3', 'score': 0.7},
        ]
        
        result = aggregator.aggregate(responses)
        
        self.assertEqual(result['response'], 'Answer 2')
        self.assertEqual(result['score'], 0.9)
    
    def test_all_responses(self):
        """Test all responses strategy."""
        aggregator = ResponseAggregator(strategy="all_responses")
        
        responses = [
            {'model': 'model1', 'response': 'Answer 1', 'score': 0.8},
            {'model': 'model2', 'response': 'Answer 2', 'score': 0.9},
        ]
        
        result = aggregator.aggregate(responses)
        
        self.assertIn('responses', result)
        self.assertEqual(len(result['responses']), 2)
    
    def test_empty_responses(self):
        """Test handling of empty responses."""
        result = self.aggregator.aggregate([])
        
        self.assertIn('response', result)
        self.assertEqual(result['models_used'], [])
    
    def test_confidence_calculation(self):
        """Test confidence score calculation."""
        responses = [
            {'model': 'model1', 'response': 'Answer', 'score': 0.8},
            {'model': 'model2', 'response': 'Answer', 'score': 0.85},
        ]
        
        confidence = self.aggregator.calculate_confidence(responses)
        
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)


if __name__ == '__main__':
    unittest.main()
