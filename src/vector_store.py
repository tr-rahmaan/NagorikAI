"""
Hybrid Vector Store & BM25 Knowledge Base for NagorikAI.
Features Banglish & English phonetic mapping, synonym expansion, and intent-aware retrieval.
"""

import os
import re
import json
import math
from typing import List, Dict, Any, Tuple, Optional
import numpy as np

BANGLISH_MAP = {
    # Services
    "passport": "পাসপোর্ট",
    "passpot": "পাসপোর্ট",
    "nid": "জাতীয় পরিচয়পত্র এনআইডি nid",
    "voter": "ভোটার আইডি কার্ড nid",
    "namjari": "নামজারি খারিজ",
    "namzari": "নামজারি খারিজ",
    "kharij": "খারিজ নামজারি",
    "jomi": "জমি ভূমি",
    "land": "জমি ভূমি খতিয়ান",
    "khatian": "খতিয়ান পরচা",

    # Requirements / Documents
    "dorkar": "প্রয়োজনীয় কাগজপত্র লাগবে দরকার নথি",
    "dorokar": "প্রয়োজনীয় কাগজপত্র লাগবে দরকার নথি",
    "lagbe": "প্রয়োজনীয় কাগজপত্র লাগবে দরকার",
    "kagoj": "কাগজপত্র দলিল সনদ নথিপত্র",
    "document": "কাগজপত্র দলিল সনদ নথিপত্র",
    "documents": "কাগজপত্র দলিল সনদ নথিপত্র",
    "docs": "কাগজপত্র দলিল সনদ নথিপত্র",
    "certificate": "সনদপত্র সার্টিফিকেট",

    # Fees / Cost
    "fee": "সরকারি ফি টাকা খরচ",
    "fees": "সরকারি ফি টাকা খরচ",
    "taka": "টাকা ফি",
    "khoroch": "খরচ ফি টাকা",
    "cost": "খরচ ফি টাকা",

    # Steps / Process
    "niyom": "নিয়ম পদ্ধতি আবেদন ধাপ",
    "rule": "নিয়ম পদ্ধতি আবেদন",
    "rules": "নিয়ম পদ্ধতি আবেদন",
    "poddhoti": "পদ্ধতি নিয়ম ধাপ",
    "abedon": "আবেদন নিয়ম",
    "how": "কিভাবে আবেদন নিয়ম পদ্ধতি",
    "kivabe": "কিভাবে আবেদন নিয়ম পদ্ধতি",

    # Corruption / Broker
    "dalal": "দালাল প্রতারণা ঘুষ অতিরিক্ত টাকা",
    "ghush": "ঘুষ দুর্নীতি দালাল",
    "bribe": "ঘুষ দুর্নীতি দালাল",
    "broker": "দালাল মধ্যস্বত্বভোগী"
}

class Chunk:
    def __init__(self, chunk_id: str, service: str, title: str, content: str, source_url: str = "", metadata: Dict[str, Any] = None):
        self.chunk_id = chunk_id
        self.service = service
        self.title = title
        self.content = content
        self.source_url = source_url
        self.metadata = metadata or {}
        self.embedding: Optional[List[float]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "service": self.service,
            "title": self.title,
            "content": self.content,
            "source_url": self.source_url,
            "metadata": self.metadata
        }

class HybridVectorStore:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.chunks: List[Chunk] = []
        self.vocab: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}
        self.chunk_tf: List[Dict[str, float]] = []
        self.doc_lengths: List[int] = []
        self.avg_doc_len: float = 0.0
        self.load_and_index()

    def expand_query(self, query: str) -> str:
        """Translates and expands Banglish terms to Bengali synonyms."""
        q_lower = query.lower()
        expanded_parts = [query]
        for en_term, bn_synonyms in BANGLISH_MAP.items():
            if re.search(r'\b' + re.escape(en_term) + r'\b', q_lower):
                expanded_parts.append(bn_synonyms)
        return " ".join(expanded_parts)

    def tokenize(self, text: str) -> List[str]:
        """Simple tokenizer handling Bangla, English, Banglish and numbers with inflection stripping."""
        text = text.lower()
        tokens = re.findall(r'[\u0980-\u09ff0-9a-zA-Z]+', text)
        result = []
        suffixes = ["ের", "র", "কে", "তে", "টি", "টা", "গুলো", "সমূহ", "দের", "রা"]
        for t in tokens:
            if len(t) > 1:
                result.append(t)
                for s in suffixes:
                    if t.endswith(s) and len(t) - len(s) >= 2:
                        result.append(t[:-len(s)])
        return result

    def load_and_index(self):
        """Loads all JSON files from data_dir and creates searchable chunks."""
        self.chunks = []
        if not os.path.exists(self.data_dir):
            return

        for fname in sorted(os.listdir(self.data_dir)):
            if not fname.endswith(".json"):
                continue
            fpath = os.path.join(self.data_dir, fname)
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)

            service_id = data.get("service_id", fname.replace(".json", ""))
            service_name = data.get("service_name_bn", "")
            official_url = data.get("official_url", "")
            hotline = data.get("hotline", "")

            # 1. Required Documents Chunks (Indexed first and with rich keywords)
            req_docs = data.get("required_documents", [])
            for idx, doc_group in enumerate(req_docs):
                dtype = doc_group.get("type", "সাধারণ")
                dlist = doc_group.get("docs", [])
                docs_formatted = "\n".join([f"- {d}" for d in dlist])
                self.chunks.append(Chunk(
                    chunk_id=f"{service_id}_docs_{idx}",
                    service=service_id,
                    title=f"{service_name} - প্রয়োজনীয় কাগজপত্র ও নথিপত্র ({dtype})",
                    content=f"সেবা: {service_name}\nপ্রয়োজনীয় কাগজপত্র ও কি কি লাগবে:\n{docs_formatted}\nঅফিসিয়াল ওয়েবসাইট: {official_url}",
                    source_url=official_url,
                    metadata={"type": "documents", "category": dtype, "service_name": service_name, "service_id": service_id}
                ))

            # 2. Official Fees Chunk
            fees_data = data.get("official_fees", {})
            fees_text = json.dumps(fees_data, ensure_ascii=False, indent=2)
            self.chunks.append(Chunk(
                chunk_id=f"{service_id}_fees",
                service=service_id,
                title=f"{service_name} - সরকারি ফি ও খরচ তালিকা",
                content=f"সেবা: {service_name}\nঅফিসিয়াল সরকারি ফি তালিকা (টাকা ও খরচ):\n{fees_text}\nহটলাইন: {hotline}",
                source_url=official_url,
                metadata={"type": "fees", "service_name": service_name, "hotline": hotline, "service_id": service_id}
            ))

            # 3. Application Steps Chunk
            steps = data.get("steps", [])
            steps_formatted = "\n".join(steps)
            self.chunks.append(Chunk(
                chunk_id=f"{service_id}_steps",
                service=service_id,
                title=f"{service_name} - আবেদনের নিয়ম ও পদ্ধতি",
                content=f"সেবা: {service_name}\nআবেদনের সম্পূর্ণ নিয়ম, নিয়মাবলী ও ধাপসমূহ:\n{steps_formatted}\nঅফিসিয়াল ওয়েবসাইট: {official_url}",
                source_url=official_url,
                metadata={"type": "steps", "service_name": service_name, "service_id": service_id}
            ))

            # 4. Dalal Warning Chunk
            dalal = data.get("dalal_warning", {})
            if dalal:
                traps = "\n".join([f"- {t}" for t in dalal.get("middleman_traps", [])])
                dalal_content = (
                    f"দালাল সতর্কতা: {dalal.get('warning_title')}\n"
                    f"সরকারি ফি নিয়ম: {dalal.get('official_fee_reminder')}\n"
                    f"দালালদের প্রতারণার কৌশল:\n{traps}\n"
                    f"অভিযোগের উপায়: {dalal.get('complaint_action')}"
                )
                self.chunks.append(Chunk(
                    chunk_id=f"{service_id}_dalal",
                    service=service_id,
                    title=f"{service_name} - দালাল ও প্রতারণা রোধে সতর্কতা",
                    content=dalal_content,
                    source_url=official_url,
                    metadata={"type": "dalal_warning", "service_name": service_name, "hotline": hotline, "service_id": service_id}
                ))

        self._build_bm25_index()

    def _build_bm25_index(self):
        """Builds BM25 TF-IDF index for fast keyword/semantic retrieval."""
        num_docs = len(self.chunks)
        if num_docs == 0:
            return

        self.doc_lengths = []
        self.chunk_tf = []
        doc_freq: Dict[str, int] = {}

        for chunk in self.chunks:
            full_text = f"{chunk.title} {chunk.content} {chunk.service}"
            tokens = self.tokenize(full_text)
            self.doc_lengths.append(len(tokens))

            tf: Dict[str, float] = {}
            for t in tokens:
                tf[t] = tf.get(t, 0) + 1
            self.chunk_tf.append(tf)

            for t in set(tokens):
                doc_freq[t] = doc_freq.get(t, 0) + 1

        self.avg_doc_len = sum(self.doc_lengths) / num_docs if num_docs > 0 else 1.0

        self.idf = {}
        for t, freq in doc_freq.items():
            self.idf[t] = math.log(1.0 + (num_docs - freq + 0.5) / (freq + 0.5))

    def search(self, query: str, top_k: int = 3, service_filter: str = None) -> List[Tuple[Chunk, float]]:
        """
        Retrieves top_k chunks using query expansion, BM25 scoring, and intent boosting.
        """
        expanded = self.expand_query(query)
        tokens = self.tokenize(expanded)
        if not tokens:
            return [(c, 1.0) for c in self.chunks[:top_k]]

        q_lower = query.lower()
        # Intent detection
        is_doc_intent = any(w in q_lower or w in expanded for w in ["কাগজ", "কাগজপত্র", "দলিল", "সনদ", "কি কি", "কী কী", "লাগবে", "দরকার", "dorka", "lagbe", "docs", "document"])
        is_fee_intent = any(w in q_lower or w in expanded for w in ["ফি", "টাকা", "খরচ", "কত", "fee", "cost", "taka"])

        scores: List[float] = []
        k1 = 1.5
        b = 0.75

        for i, chunk in enumerate(self.chunks):
            if service_filter and chunk.service != service_filter:
                scores.append(-999.0)
                continue

            score = 0.0
            tf_dict = self.chunk_tf[i]
            doc_len = self.doc_lengths[i]

            for t in tokens:
                if t in tf_dict:
                    freq = tf_dict[t]
                    idf = self.idf.get(t, 0.5)
                    numerator = freq * (k1 + 1.0)
                    denominator = freq + k1 * (1.0 - b + b * (doc_len / (self.avg_doc_len + 1e-6)))
                    score += idf * (numerator / denominator)

            # Title matches give massive precision boosts
            title_lower = chunk.title.lower()
            for t in tokens:
                if t in title_lower:
                    score += 3.0

            # Intent boost
            ctype = chunk.metadata.get("type", "")
            if is_doc_intent and ctype == "documents":
                score += 5.0
            elif is_fee_intent and ctype == "fees":
                score += 5.0

            scores.append(score)

        ranked_indices = np.argsort(scores)[::-1]
        results = []
        for idx in ranked_indices[:top_k]:
            if scores[idx] > -100:
                results.append((self.chunks[idx], float(scores[idx])))

        return results
