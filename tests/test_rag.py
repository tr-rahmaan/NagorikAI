"""
Automated unit tests for CivicSphere AI RAG Engine, Dalal Detector, and Vision Checker.
"""

import os
import sys
import unittest
from PIL import Image

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.vector_store import HybridVectorStore
from src.dalal_detector import DalalDetector
from src.rag_engine import RAGEngine
from src.vision_checker import DocumentVisionChecker

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))

class TestCivicSphereAI(unittest.TestCase):
    def setUp(self):
        self.rag = RAGEngine(data_dir=DATA_DIR)
        self.vector_store = HybridVectorStore(data_dir=DATA_DIR)

    def test_vector_store_chunks(self):
        """Verifies chunks loaded from all 3 services."""
        self.assertGreater(len(self.vector_store.chunks), 8)
        services = set([c.service for c in self.vector_store.chunks])
        self.assertIn("nid_correction", services)
        self.assertIn("epassport", services)
        self.assertIn("land_mutation", services)

    def test_passport_fee_retrieval(self):
        """Verifies retrieval for passport fee queries."""
        results = self.vector_store.search("ই-পাসপোর্টের সরকারি ফি কত?", top_k=2)
        self.assertTrue(len(results) > 0)
        top_chunk = results[0][0]
        self.assertEqual(top_chunk.service, "epassport")
        self.assertIn("epassport.gov.bd", top_chunk.source_url)

    def test_land_mutation_retrieval(self):
        """Verifies retrieval for land mutation fees and 1170 BDT breakdown."""
        results = self.vector_store.search("জমির নামজারি বা খারিজ ফি কত?", top_k=2)
        self.assertTrue(len(results) > 0)
        top_chunk = results[0][0]
        self.assertEqual(top_chunk.service, "land_mutation")
        self.assertIn("mutation.land.gov.bd", top_chunk.source_url)

    def test_dalal_detector_detection(self):
        """Verifies detection of middleman / bribe demands."""
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
        res = self.rag.query("NID কার্ডে জন্ম তারিখ সংশোধনে সরকারি ফি কত?")
        self.assertIn("answer", res)
        self.assertIn("২৩০", res["answer"])
        self.assertTrue(len(res["official_sources"]) > 0)
        self.assertIn("https://services.nidw.gov.bd/", res["official_sources"][0])

    def test_vision_checker_synthetic_doc(self):
        """Verifies document pre-flight audit runs and produces report."""
        test_img_path = "/tmp/test_civic_doc.png"
        img = Image.new("RGB", (1000, 800), color=(255, 255, 255))
        img.save(test_img_path)

        res = DocumentVisionChecker.inspect_document(test_img_path, doc_type="nid")
        self.assertEqual(res["status"], "success")
        self.assertIn("ডকুমেন্ট প্রি-ফ্লাইট অডিট রিপোর্ট", res["report_bn"])

        if os.path.exists(test_img_path):
            os.remove(test_img_path)

if __name__ == "__main__":
    unittest.main()
