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
    "passport": "পাসপোর্ট epassport ই-পাসপোর্ট",
    "passpot": "পাসপোর্ট epassport",
    "pasport": "পাসপোর্ট epassport",
    "nid": "জাতীয় পরিচয়পত্র এনআইডি nid স্মার্টকার্ড",
    "voter": "ভোটার আইডি কার্ড nid জাতীয় পরিচয়পত্র",
    "id": "জাতীয় পরিচয়পত্র এনআইডি",
    "namjari": "নামজারি খারিজ জমি ভূমি",
    "namzari": "নামজারি খারিজ জমি ভূমি",
    "kharij": "খারিজ নামজারি জমি ভূমি",
    "jomi": "জমি ভূমি খতিয়ান নামজারি",
    "land": "জমি ভূমি খতিয়ান নামজারি mutation",
    "khatian": "খতিয়ান পরচা জমি",
    "porcha": "পর্চা খতিয়ান জমি",

    # Requirements / Documents
    "dorkar": "প্রয়োজনীয় কাগজপত্র লাগবে দরকার নথি",
    "dorokar": "প্রয়োজনীয় কাগজপত্র লাগবে দরকার নথি",
    "lagbe": "প্রয়োজনীয় কাগজপত্র লাগবে দরকার",
    "kagoj": "কাগজপত্র দলিল সনদ নথিপত্র",
    "document": "কাগজপত্র দলিল সনদ নথিপত্র",
    "documents": "কাগজপত্র দলিল সনদ নথিপত্র",
    "docs": "কাগজপত্র দলিল সনদ নথিপত্র",
    "certificate": "সনদপত্র সার্টিফিকেট",
    "papers": "কাগজপত্র নথি দলিল",

    # Fees / Cost
    "fee": "সরকারি ফি টাকা খরচ",
    "fees": "সরকারি ফি টাকা খরচ",
    "fi": "ফি সরকারি ফি খরচ টাকা",
    "taka": "টাকা সরকারি ফি",
    "tk": "টাকা ফি",
    "khoroch": "খরচ ফি টাকা",
    "cost": "খরচ ফি টাকা",
    "koto": "কত টাকা ফি খরচ",

    # Steps / Process / Lost
    "niyom": "নিয়ম পদ্ধতি আবেদন ধাপ",
    "rule": "নিয়ম পদ্ধতি আবেদন",
    "rules": "নিয়ম পদ্ধতি আবেদন",
    "poddhoti": "পদ্ধতি নিয়ম ধাপ",
    "abedon": "আবেদন নিয়ম পদ্ধতি",
    "how": "কিভাবে আবেদন নিয়ম পদ্ধতি",
    "kivabe": "কিভাবে আবেদন নিয়ম পদ্ধতি",
    "process": "আবেদনের নিয়ম পদ্ধতি ধাপ",
    "harano": "হারানো রি-ইস্যু জিডি gd",
    "haraye": "হারানো রি-ইস্যু জিডি gd",
    "lost": "হারানো রি-ইস্যু জিডি gd",
    "reissue": "রি-ইস্যু হারানো",
    "somoy": "সময় কার্যদিবস ডেলিভারি",
    "time": "সময় কার্যদিবস ডেলিভারি",
    "delivery": "ডেলিভারি কার্যদিবস সময়",
    "urgent": "জরুরি এক্সপ্রেস",
    "regular": "নিয়মিত সাধারণ",

    # Corruption / Broker
    "dalal": "দালাল প্রতারণা ঘুষ অতিরিক্ত টাকা",
    "ghush": "ঘুষ দুর্নীতি দালাল অতিরিক্ত",
    "bribe": "ঘুষ দুর্নীতি দালাল",
    "broker": "দালাল মধ্যস্বত্বভোগী"
}

def _format_fees_as_bangla(fees_data: dict) -> str:
    """Convert nested JSON fees dict to clean human-readable Bengali text."""
    if not fees_data:
        return "সরকারি ফি তথ্য পাওয়া যায়নি।"

    lines = []

    for key, val in fees_data.items():
        if key == "note":
            lines.append(f"📌 বিশেষ নোট: {val}")
        elif key == "important_rule":
            lines.append(f"⚠️ গুরুত্বপূর্ণ নিয়ম: {val}")
        elif key == "total_official_cost":
            lines.append(f"✅ মোট সরকারি খরচ: {val}")
        elif key == "breakdown" and isinstance(val, dict):
            lines.append("ফি ভাঙন:")
            for sub_key, sub_val in val.items():
                if isinstance(sub_val, dict):
                    amt = sub_val.get("amount", "")
                    when = sub_val.get("when_to_pay", "")
                    items = sub_val.get("items", [])
                    label = "আবেদনের সময়" if "initial" in sub_key else "অনুমোদনের পর"
                    lines.append(f"  • {label}: {amt}")
                    for item in items:
                        lines.append(f"    - {item}")
                    if when:
                        lines.append(f"    কখন দিতে হবে: {when}")
        elif isinstance(val, dict):
            # Passport-style (type/regular/express/super_express)
            ptype = val.get("type", "")
            reg = val.get("regular", "")
            exp = val.get("express", "")
            sup = val.get("super_express", "")
            # NID-style (description/first_time/second_time/subsequent)
            desc = val.get("description", "")
            first = val.get("first_time", "")
            second = val.get("second_time", "")
            subseq = val.get("subsequent", "")
            note_val = val.get("note", "")

            if ptype or reg or exp or sup:
                lines.append(f"📋 {ptype or key}:")
                if reg: lines.append(f"  - সাধারণ: {reg}")
                if exp: lines.append(f"  - এক্সপ্রেস: {exp}")
                if sup: lines.append(f"  - সুপার এক্সপ্রেস: {sup}")
            elif desc or first or second:
                lines.append(f"📋 {desc or key}:")
                if first:  lines.append(f"  - প্রথমবার: {first}")
                if second: lines.append(f"  - দ্বিতীয়বার: {second}")
                if subseq: lines.append(f"  - পরবর্তীবার: {subseq}")
                if note_val: lines.append(f"    📌 {note_val}")
            else:
                # Generic fallback: show key-value pairs from inner dict
                lines.append(f"📋 {key}:")
                for k2, v2 in val.items():
                    if isinstance(v2, str):
                        lines.append(f"  - {k2}: {v2}")

    return "\n".join(lines) if lines else "ফি তথ্য উপলব্ধ নেই।"


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
                    metadata={
                        "type": "documents",
                        "category": dtype,
                        "docs": dlist,
                        "service_name": service_name,
                        "service_id": service_id,
                        "hotline": hotline,
                        "official_url": official_url,
                    }
                ))


            # 2. Official Fees Chunk — formatted as clean Bengali text (no raw JSON)
            fees_data = data.get("official_fees", {})
            fees_text = _format_fees_as_bangla(fees_data)
            self.chunks.append(Chunk(
                chunk_id=f"{service_id}_fees",
                service=service_id,
                title=f"{service_name} - সরকারি ফি ও খরচ তালিকা",
                content=f"সেবা: {service_name}\nসরকারি ফি ও খরচ:\n{fees_text}\nহটলাইন: {hotline}",
                source_url=official_url,
                metadata={
                    "type": "fees",
                    "service_name": service_name,
                    "hotline": hotline,
                    "service_id": service_id,
                    "official_url": official_url,
                    "official_fees": fees_data,
                }
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

    def detect_service(self, text: str) -> Optional[str]:
        """Identifies target civic service from query text."""
        t = text.lower()
        if any(w in t for w in ["পাসপোর্ট", "passport", "ই-পাসপোর্ট", "epassport", "এমআরপি", "mrp"]):
            return "epassport"
        if any(w in t for w in ["এনআইডি", "nid", "ভোটার", "voter", "পরিচয়পত্র", "পরিচয়পত্র", "স্মার্টকার্ড", "স্মার্ট কার্ড", "স্মার্ট"]):
            return "nid_correction"
        if any(w in t for w in ["নামজারি", "খারিজ", "নামপত্তন", "জমি", "ভূমি", "খতিয়ান", "খতিয়ান", "পর্চা", "mutation", "land", "দখল", "ডিসিআর", "dcr", "খাজনা"]):
            return "land_mutation"
        return None

    def search(self, query: str, top_k: int = 3, service_filter: str = None) -> List[Tuple[Chunk, float]]:
        """
        Retrieves top_k chunks using query expansion, BM25 scoring, service-awareness, and intent boosting.
        """
        expanded = self.expand_query(query)
        tokens = self.tokenize(expanded)
        if not tokens:
            return [(c, 1.0) for c in self.chunks[:top_k]]

        q_lower = query.lower()
        
        # Detect targeted civic service
        detected_svc = service_filter or self.detect_service(f"{q_lower} {expanded}")

        # Intent detection
        is_doc_intent = any(w in q_lower or w in expanded for w in [
            "কাগজ", "কাগজপত্র", "দলিল", "সনদ", "কি কি", "কী কী", "লাগবে", "দরকার", "dorka", "lagbe", "docs", "document", "papers"
        ])
        is_fee_intent = any(w in q_lower or w in expanded for w in [
            "ফি", "টাকা", "খরচ", "কত", "fee", "cost", "taka", "tk", "চার্জ", "কতো"
        ])
        is_steps_intent = any(w in q_lower or w in expanded for w in [
            "কিভাবে", "কীভাবে", "নিয়ম", "নিয়ম", "পদ্ধতি", "ধাপ", "কি করব", "কী করব", "কি করবো", "কী করবো", "আবেদন", "how", "process", "step"
        ])
        is_lost_intent = any(w in q_lower or w in expanded for w in [
            "হারিয়ে", "হারানো", "নষ্ট", "হারায়", "lost", "reissue", "রি-ইস্যু", "জিডি", "gd"
        ])
        is_dalal_intent = any(w in q_lower or w in expanded for w in [
            "দালাল", "ঘুষ", "টাকা চাচ্ছে", "অতিরিক্ত টাকা", "অতিরিক্ত ফি", "প্রতারণা", "bribe", "broker"
        ])

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

            # Title matches give strong precision boosts
            title_lower = chunk.title.lower()
            for t in tokens:
                if t in title_lower:
                    score += 3.0

            # Service boosting: ensure matching service chunks dominate
            if detected_svc:
                if chunk.service == detected_svc:
                    score += 30.0
                else:
                    score -= 15.0

            # Intent boost
            ctype = chunk.metadata.get("type", "")
            if is_doc_intent and ctype == "documents":
                score += 8.0
            elif (is_steps_intent or is_lost_intent) and ctype == "steps":
                score += 10.0
            elif is_fee_intent and ctype == "fees":
                score += 8.0
            elif is_dalal_intent and ctype == "dalal_warning":
                score += 7.0

            scores.append(score)

        ranked_indices = np.argsort(scores)[::-1]
        results = []
        for idx in ranked_indices[:top_k]:
            if scores[idx] > -100:
                results.append((self.chunks[idx], float(scores[idx])))

        return results
