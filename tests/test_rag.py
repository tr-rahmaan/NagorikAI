"""
Automated Pytest / Unittest Suite for NagorikAI (GovCopilot).
Validates Hybrid Vector Store, Dalal-Free anti-bribery guardrail, and Vision document auditor.
"""

import os
import sys
import unittest
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.vector_store import HybridVectorStore
from src.dalal_detector import DalalDetector
from src.rag_engine import RAGEngine
from src.vision_checker import DocumentVisionChecker

class TestNagorikAI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
        cls.store = HybridVectorStore(cls.data_dir)
        cls.rag = RAGEngine(cls.data_dir)

    def test_vector_store_initialization(self):
        """Knowledge base should load chunks from JSON files."""
        self.assertGreater(len(self.store.chunks), 5)

    def test_search_nid_fee(self):
        """Querying NID fee should prioritize NID correction chunk."""
        results = self.store.search("NID সংশোধনে সরকারি ফি কত?")
        self.assertGreater(len(results), 0)
        top_chunk = results[0][0]
        self.assertIn("NID", top_chunk.title)

    def test_search_land_mutation(self):
        """Querying land mutation should surface 1170 Taka statutory fee chunk."""
        results = self.store.search("জমির নামজারি খারিজ ফি")
        self.assertGreater(len(results), 0)
        top_chunk = results[0][0]
        self.assertIn("নামজারি", top_chunk.title)

    def test_dalal_detector_flagged_bribe(self):
        """Mentions of brokers/dalals demanding extra fees must be caught."""
        query = "পাসপোর্টের জন্য দালাল আট হাজার টাকা চাচ্ছে, এটা কি দেওয়া ঠিক হবে?"
        alert = DalalDetector.scan_query(query)
        self.assertIsNotNone(alert)
        self.assertTrue(alert["flagged"])
        self.assertEqual(alert["service"], "passport")
        self.assertIn("১০৬", alert["emergency_hotline"])

    def test_dalal_detector_clean_query(self):
        """Clean queries should not trigger false positive alarms."""
        query = "জাতীয় পরিচয়পত্র সংশোধনে কি কি শিক্ষাগত সনদ লাগবে?"
        alert = DalalDetector.scan_query(query)
        self.assertIsNone(alert)

    def test_rag_query_response(self):
        """Verifies end-to-end RAG response has citations and official links."""
        res = self.rag.query("জাতীয় পরিচয়পত্র এনআইডি সংশোধনে কি কি লাগে?")
        self.assertIn("answer", res)
        self.assertTrue("services.nidw.gov.bd" in res["answer"] or len(res["sources"]) > 0)

    def test_vision_checker_synthetic_doc(self):
        """Verifies document pre-flight audit runs and produces report."""
        test_img_path = "/tmp/test_civic_doc.png"
        img = Image.new("RGB", (1000, 800), color=(255, 255, 255))
        img.save(test_img_path)

        res = DocumentVisionChecker.inspect_document(test_img_path, doc_type="nid")
        self.assertEqual(res["status"], "success")
        self.assertIn("ডকুমেন্ট", res["report_bn"])

        if os.path.exists(test_img_path):
            os.remove(test_img_path)

if __name__ == "__main__":
    unittest.main()
