import unittest
from unittest.mock import patch, MagicMock
from utils.search import hybrid_search
from utils.rag import answer_question
from utils.gemini_service import GeminiServiceError

class TestIntegration(unittest.TestCase):
    def test_article_5_exact_retrieval(self):
        res = hybrid_search('Article 5 loyalty to State', 'Federal')
        self.assertTrue(len(res) > 0)
        self.assertEqual(res[0]['section_number'], '5')

    def test_article_8_exact_retrieval(self):
        res = hybrid_search('Explain Article 8 Fundamental Rights', 'Federal')
        self.assertTrue(len(res) > 0)
        self.assertEqual(res[0]['section_number'], '8')
        
    def test_article_number_boosting(self):
        # Even without other keywords, article 9 should jump to top
        res = hybrid_search('Article 9', 'Federal')
        self.assertTrue(len(res) > 0)
        self.assertEqual(res[0]['section_number'], '9')

    def test_federal_filtering(self):
        # Province filter should retain Federal laws
        res = hybrid_search('Article 5', 'Punjab')
        self.assertTrue(len(res) > 0)
        # Assuming the returned item is Federal because constitution is Federal
        self.assertEqual(res[0]['province'], 'Federal')

    @patch('utils.rag.hybrid_search')
    def test_unknown_law(self, mock_search):
        mock_search.return_value = []
        ans, sources = answer_question('What is the punishment for cyber terrorism under PECA?', 'Federal')
        self.assertIn("couldn't find sufficient legal information", ans)
        self.assertEqual(len(sources), 0)

    @patch('utils.rag.generate_answer')
    @patch('utils.rag.hybrid_search')
    def test_gemini_unavailable_with_valid_local_context(self, mock_search, mock_gen):
        # Mock search to return a valid local context
        mock_search.return_value = [{'section_number': '5', 'law_name': 'Constitution', 'section_text': 'Loyalty to state.'}]
        # Mock Gemini to throw 503
        mock_gen.side_effect = GeminiServiceError("503 UNAVAILABLE")
        
        ans, sources = answer_question('What is Article 5?', 'Federal')
        self.assertIn("Local Fallback Answer", ans)
        self.assertIn("Article/Section 5", ans)
        self.assertIn("Loyalty to state.", ans)
        self.assertEqual(len(sources), 1)

    @patch('utils.rag.generate_answer')
    @patch('utils.rag.hybrid_search')
    def test_hallucinated_citation_blocking(self, mock_search, mock_gen):
        mock_search.return_value = [{'section_number': '5', 'law_name': 'Constitution', 'section_text': 'Loyalty.'}]
        mock_gen.return_value = "According to Section 999, this is true."
        
        ans, sources = answer_question('What is Article 5?', 'Federal')
        self.assertIn("Warning", ans)
        self.assertIn("999", ans)
        
if __name__ == '__main__':
    unittest.main()
