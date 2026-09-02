import os
import unittest
from pathlib import Path
from utils.law_processor import clean_law_text, split_into_sections

class TestLawProcessor(unittest.TestCase):
    def test_clean_law_text(self):
        """Test that page numbers and empty lines are removed."""
        raw_text = "Page 1\n\nThis is a law.\n\n2\n\nIt is valid."
        cleaned = clean_law_text(raw_text)
        self.assertNotIn("\n\n", cleaned)
        # Should filter standalone "2" which acts as page number
        self.assertNotIn("\n2\n", "\n"+cleaned+"\n")

    def test_split_into_sections(self):
        """Test that text is correctly split by section headings without word counts."""
        sample_text = (
            "An act to provide for something.\n"
            "1. Short title.\n"
            "This act may be called the Test Act.\n"
            "2. Definitions.\n"
            "In this act, context means context.\n"
            "This section continues here."
        )
        sections = split_into_sections(sample_text)
        
        # We expect 3 parts: Preamble, Section 1, Section 2
        self.assertEqual(len(sections), 3)
        
        self.assertEqual(sections[0]["section_number"], "Preamble")
        self.assertEqual(sections[1]["section_number"], "1")
        self.assertTrue("Test Act" in sections[1]["section_text"])
        self.assertEqual(sections[2]["section_number"], "2")
        self.assertTrue("context means context" in sections[2]["section_text"])
        self.assertTrue("continues here" in sections[2]["section_text"])

if __name__ == "__main__":
    unittest.main()
