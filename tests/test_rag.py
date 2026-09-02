import unittest
from unittest.mock import patch
from typing import Dict, Any

from utils.search import hybrid_search, keyword_search
from utils.rag import validate_sources
from utils.vector_store import vector_store

class TestRAGPipeline(unittest.TestCase):
    def setUp(self):
        # Mock vector store data so we don't need real JSONs or APIs for these tests
        vector_store.metadata = [
            {"law_name": "Test Law 1", "year": "2020", "section_number": "1", "province": "Federal", "section_text": "This is a federal test."},
            {"law_name": "Test Law 1", "year": "2020", "section_number": "2", "province": "Federal", "section_text": "Federal rules apply here."},
            {"law_name": "Provincial Law", "year": "2021", "section_number": "12", "province": "Punjab", "section_text": "Punjab specific rules."},
            {"law_name": "Sindh Act", "year": "2019", "section_number": "4", "province": "Sindh", "section_text": "Sindh tax laws."}
        ]
        vector_store.is_loaded = True
        
    def test_keyword_search_ranking(self):
        """Test keyword search returns correct results and deduplicates."""
        results = keyword_search("federal rules", province="Federal", top_k=5)
        # Should match the first two since they are federal
        self.assertEqual(len(results), 2)
        # The second one has the word "rules" and "federal", should score higher or same
        self.assertTrue(any("Federal rules apply here" in r['section_text'] for r in results))
        
    def test_province_filtering(self):
        """Test that search respects the province filter."""
        results = keyword_search("rules", province="Punjab", top_k=5)
        # Should return Punjab laws (or Federal if we allowed it, but keyword_search currently requires exact match or Federal)
        # Our implementation allows Federal even when a province is selected.
        provinces = [r['province'] for r in results]
        self.assertNotIn("Sindh", provinces)
        self.assertTrue("Punjab" in provinces or "Federal" in provinces)

    @patch('utils.vector_store.VectorStore.semantic_search')
    def test_hybrid_search(self, mock_semantic):
        """Test hybrid search merges semantic and keyword results and deduplicates."""
        # Semantic returns section 1 and 12
        mock_semantic.return_value = [
            (vector_store.metadata[0], 0.9), 
            (vector_store.metadata[2], 0.8)
        ]
        
        results = hybrid_search("test", province=None, top_k=3)
        # Keyword would also find section 1. Deduplication should ensure no duplicates.
        signatures = [f"{r['law_name']}_{r['section_number']}" for r in results]
        self.assertEqual(len(signatures), len(set(signatures)))
        
    def test_source_validation_valid(self):
        """Test that correct citations pass validation."""
        answer = "According to Section 12, this is the rule."
        retrieved = [{"section_number": "12"}, {"section_number": "4"}]
        validated_answer, is_valid = validate_sources(answer, retrieved)
        self.assertTrue(is_valid)
        self.assertNotIn("Warning", validated_answer)

    def test_source_validation_hallucination(self):
        """Test that fake citations trigger a warning."""
        answer = "According to Section 99, you must pay a fine."
        retrieved = [{"section_number": "12"}, {"section_number": "4"}]
        validated_answer, is_valid = validate_sources(answer, retrieved)
        self.assertFalse(is_valid)
        self.assertIn("Warning (System Validation)", validated_answer)
        self.assertIn("Section 99", validated_answer)

if __name__ == '__main__':
    unittest.main()
