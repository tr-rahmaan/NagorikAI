"""
GovPublicService & Grounded Civic Assistant (NagorikAI / CivicSphere).
Production-grade RAG Engine with instant deterministic knowledge fallback
and intelligent public service intent resolution.
"""

import os
import sys
import ssl
import concurrent.futures
from typing import Dict, Any, List, Optional

# Fix import path
try:
    from src.vector_store import HybridVectorStore, Chunk
    from src.dalal_detector import DalalDetector
except ModuleNotFoundError:
    _src_dir = os.path.dirname(os.path.abspath(__file__))
    _proj_dir = os.path.dirname(_src_dir)
    if _proj_dir not in sys.path:
        sys.path.insert(0, _proj_dir)
    from src.vector_store import HybridVectorStore, Chunk
    from src.dalal_detector import DalalDetector

try:
    ssl._create_default_https_context = ssl._create_unverified_context
except Exception:
    pass

SYSTEM_PROMPT = """আপনি 'CivicSphere' (নাগরিক সেবা পোর্টাল সহায়িকা) — গণপ্রজাতন্ত্রী বাংলাদেশ সরকারের অফিশিয়াল উন্মুক্ত তথ্যের ভিত্তিতে পরিচালিত দায়িত্বশীল সহকারী।

নির্দেশনা ও নিয়মাবলী:
১. নাগরিকের প্রশ্নের সরাসরি, তথ্যভিত্তিক ও সুনির্দিষ্ট উত্তর প্রমিত বাংলায় প্রদান করুন।
২. ভাষা হতে হবে প্রাতিষ্ঠানিক, মার্জিত, শ্রদ্ধাশীল এবং অপ্রয়োজনীয় ইমোজিমুক্ত।
৩. উত্তরের কাঠামো:
   - সরাসরি উত্তর (নির্ধারিত সরকারি ফি বা মূল সেবা তথ্য)
   - প্রয়োজনীয় ডকুমেন্টের তালিকা (যদি প্রাসঙ্গিক হয়)
   - আবেদনের সঠিক ধাপসমূহ (যদি আবেদন প্রক্রিয়া বা হারিয়ে যাওয়া বিষয় হয়)
   - সরকারি সতর্কতা (দালাল বা অননুমোদিত অর্থ লেনদেন সংক্রান্ত প্রশ্ন থাকলে)
   - অফিশিয়াল ওয়েবসাইট ও টোল-ফ্রি হেল্পলাইন
৪. দালাল বা ঘুষের কোনো প্রসঙ্গ থাকলে স্পষ্টভাবে সতর্ক করুন যে এটি আইনত দণ্ডনীয় এবং হটলাইন ১০৬ (দুদক) বা ৯৯৯ এ জানানোর পরামর্শ দিন।
৫. তথ্যের অতিরিক্ত কোনো কিছু মনগড়াভাবে লিখবেন না।
"""

_GLOBAL_EXECUTOR = concurrent.futures.ThreadPoolExecutor(max_workers=3)

class RAGEngine:
    def __init__(self, data_dir: str, api_key: Optional[str] = None):
        self.data_dir = data_dir
        self.vector_store = HybridVectorStore(data_dir)
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or "AIzaSyDQzW0tny_EjMP-abBEYfqg445xhx-bDzw"
        self._init_llm_client()

    def _init_llm_client(self):
        """Initializes Gemini client safely."""
        self.client_gemini = None
        gemini_key = self.api_key or os.getenv("GEMINI_API_KEY")
        if gemini_key:
            try:
                from google import genai
                self.client_gemini = genai.Client(api_key=gemini_key)
            except Exception:
                self.client_gemini = None

    def query(self, user_query: str, top_k: int = 3) -> Dict[str, Any]:
        """
        Processes citizen query:
        1. Middleman / Bribe detection
        2. Service-directed semantic retrieval
        3. LLM synthesis (fast timeout) with immediate grounded fallback
        """
        clean_query = (user_query or "").strip()
        dalal_alert = DalalDetector.scan_query(clean_query)

        # Retrieve top chunks
        retrieved_items = self.vector_store.search(clean_query, top_k=top_k)
        retrieved_chunks = [item[0] for item in retrieved_items]
        sources = list(set([c.source_url for c in retrieved_chunks if c.source_url]))

        context_str = "\n\n".join([
            f"--- [{c.title}] ---\n{c.content}"
            for c in retrieved_chunks
        ])

        answer = None
        generation_mode = "CivicSphere Grounded Public Knowledge Engine"

        # Safe LLM generation with 3.5s timeout
        if self.client_gemini:
            prompt = (
                f"{SYSTEM_PROMPT}\n\n"
                f"[সরকারি তথ্যাদি (Context)]:\n{context_str}\n\n"
                f"[নাগরিকের প্রশ্ন]:\n{clean_query}\n\n"
                f"সুনির্দিষ্ট প্রাতিষ্ঠানিক উত্তর:"
            )

            def _call_model():
                candidate_models = ['gemini-3.5-flash-lite', 'gemini-3.5-flash', 'gemini-3.1-flash-lite']
                for model_name in candidate_models:
                    try:
                        resp = self.client_gemini.models.generate_content(
                            model=model_name,
                            contents=prompt
                        )
                        if resp and resp.text and len(resp.text.strip()) > 20:
                            return resp.text.strip(), f"Gemini ({model_name})"
                    except Exception:
                        continue
                return None, None

            try:
                future = _GLOBAL_EXECUTOR.submit(_call_model)
                res_text, mode_name = future.result(timeout=3.5)
                if res_text:
                    answer = res_text
                    generation_mode = mode_name
            except Exception:
                answer = None

        # Deterministic instant fallback (<0.005s)
        if not answer:
            answer = self._generate_grounded_fallback(clean_query, retrieved_chunks, dalal_alert)

        return {
            "query": clean_query,
            "answer": answer,
            "sources": sources,
            "dalal_alert": dalal_alert,
            "mode": generation_mode
        }

    def _query_intents(self, query: str) -> Dict[str, bool]:
        q = (query or "").lower()
        doc_intent = any(w in q for w in [
            "কাগজ", "কাগজপত্র", "দলিল", "সনদ", "কি কি", "কী কী", "লাগে",
            "দরকার", "dorka", "lagbe", "docs", "document", "ডকুমেন্ট", "papers"
        ])
        fee_intent = any(w in q for w in [
            "ফি", "টাকা", "খরচ", "কত", "fee", "cost", "taka", "tk", "চার্জ", "কতো"
        ])
        steps_intent = any(w in q for w in [
            "কিভাবে", "কীভাবে", "নিয়ম", "নিয়ম", "পদ্ধতি", "ধাপ", "কি করব", "কী করব",
            "কি করবো", "কী করবো", "আবেদন", "how", "process", "step"
        ])
        lost_intent = any(w in q for w in [
            "হারিয়ে", "হারানো", "নষ্ট", "হারায়", "lost", "reissue", "রি-ইস্যু", "জিডি", "gd"
        ])
        time_intent = any(w in q for w in [
            "সময়", "দিন", "কতদিন", "মেয়াদ", "ডেলিভারি", "delivery", "days"
        ])

        if not any([doc_intent, fee_intent, steps_intent, lost_intent, time_intent]):
            fee_intent = True

        return {
            "doc": doc_intent,
            "fee": fee_intent,
            "steps": steps_intent,
            "lost": lost_intent,
            "time": time_intent
        }

    def _extract_relevant_fees(self, query: str, fees_data: Dict[str, Any]) -> List[str]:
        """Extracts exact statutory fees based on citizen request."""
        if not fees_data:
            return []

        if "total_official_cost" in fees_data:
            lines = [f"- মোট সরকারি ফি: **{fees_data['total_official_cost']}**"]
            if fees_data.get("important_rule"):
                lines.append(f"- সরকারি নিয়ম: {fees_data['important_rule']}")
            return lines

        want_10 = any(x in query for x in ["১০ বছর", "10 বছর", "10 year"])
        want_5 = any(x in query for x in ["৫ বছর", "5 বছর", "5 year"]) and not want_10
        want_48 = "৪৮" in query or "48" in query
        want_64 = "৬৪" in query or "64" in query
        want_reg = any(x in query for x in ["নিয়মিত", "নিয়মিত", "সাধারণ", "regular"])
        want_exp = any(x in query for x in ["জরুরি", "এক্সপ্রেস", "express", "urgent"])
        want_super = any(x in query.lower() for x in ["সুপার", "super"])
        want_reissue = any(x in query for x in ["হারানো", "রি-ইস্যু", "reissue", "lost"])
        want_name = "নাম" in query and not want_reissue
        want_second = any(x in query for x in ["২য়", "২য়", "দ্বিত"])

        candidates = []
        for key, val in fees_data.items():
            if key in ("note", "important_rule") or not isinstance(val, dict):
                continue
            ptype = val.get("type") or val.get("description") or key
            if want_10 and not ("১০" in ptype or "years_10" in key):
                continue
            if want_5 and not ("৫ বছর" in ptype or "years_5" in key):
                continue
            if want_48 and not ("৪৮" in ptype or "48" in key):
                continue
            if want_64 and not ("৬৪" in ptype or "64" in key):
                continue
            if want_reissue and "হারানো" not in ptype and "reissue" not in key:
                continue
            if want_name and "নাম" not in ptype:
                continue
            candidates.append((key, val, ptype))

        if not candidates:
            for key, val in fees_data.items():
                if isinstance(val, dict) and (val.get("type") or val.get("description")):
                    candidates.append((key, val, val.get("type") or val.get("description")))
                    if len(candidates) >= 2:
                        break

        lines = []
        for _, val, ptype in candidates[:3]:
            if val.get("regular") or val.get("express"):
                bits = []
                include_reg = want_reg or not (want_reg or want_exp)
                include_exp = want_exp or not (want_reg or want_exp)
                if include_reg and val.get("regular"):
                    bits.append(f"নিয়মিত: {val['regular']}")
                if include_exp and val.get("express"):
                    bits.append(f"জরুরি: {val['express']}")
                if want_super and val.get("super_express"):
                    bits.append(f"সুপার এক্সপ্রেস: {val['super_express']}")
                if bits:
                    lines.append(f"- **{ptype}:** {' | '.join(bits)}")
            elif val.get("first_time"):
                lines.append(f"- **{ptype}:** প্রথমবার {val['first_time']}")
                if want_second and val.get("second_time"):
                    lines.append(f"  - দ্বিতীয়বার: {val['second_time']}")
            elif val.get("regular_first_time"):
                lines.append(f"- **{ptype}:** নিয়মিত {val.get('regular_first_time')}")

        if fees_data.get("note") and lines:
            lines.append(f"- {fees_data['note']}")

        return lines

    def _generate_grounded_fallback(self, query: str, chunks: List[Chunk], dalal_alert: Optional[Dict[str, Any]]) -> str:
        """Instant formal public response generated from verified Government data."""
        if not chunks:
            return (
                "সরকারি তথ্যভাণ্ডারে এই বিষয়ে সুনির্দিষ্ট তথ্য পাওয়া যায়নি।\n\n"
                "**সরকারি জরুরি হেল্পলাইন:**\n"
                "- জাতীয় পরিচয়পত্র (NID): ১০৫\n"
                "- ই-পাসপোর্ট: ১৬৪৪৫ বা ৩৩৩\n"
                "- ভূমিসেবা (নামজারি): ১৬১২২\n"
                "- দুর্নীতি ও দালাল অভিযোগ (দুদক): ১০৬"
            )

        intents = self._query_intents(query)
        service_id = chunks[0].service
        all_svc = [c for c in self.vector_store.chunks if c.service == service_id]

        fees_chunk = next((c for c in all_svc if (c.metadata or {}).get("type") == "fees"), None)
        doc_chunks = [c for c in all_svc if (c.metadata or {}).get("type") == "documents"]
        steps_chunk = next((c for c in all_svc if (c.metadata or {}).get("type") == "steps"), None)

        meta = (fees_chunk or chunks[0]).metadata or {}
        service_name = meta.get("service_name") or chunks[0].title

        parts = [f"### গণপ্রজাতন্ত্রী বাংলাদেশ — {service_name}\n"]

        # 1. Lost or Reissue Intent
        if intents["lost"]:
            parts.append("**হারানো বা রি-ইস্যু সংক্রান্ত নির্দেশনা:**")
            if service_id == "epassport":
                parts.append("- নিকটস্থ থানায় অবিলম্বে একটি সাধারণ ডায়েরি (জিডি / GD) সম্পন্ন করুন অথবা অনলাইন জিডি পোর্টালে আবেদন করুন।")
                parts.append("- epassport.gov.bd পোর্টালে রি-ইস্যু / নবায়ন ক্যাটাগরিতে আবেদন ফরম পূরণ করুন।")
                parts.append("- মূল জিডি কপি, পুরাতন পাসপোর্টের ফটোকপি এবং মূল NID সহ নির্ধারিত তারিখে পাসপোর্ট অফিসে উপস্থিত হোন।")
            elif service_id == "nid_correction":
                parts.append("- অনলাইনে বা থানায় হারানো NID-র বিষয়ে জিডি (GD) সম্পন্ন করুন।")
                parts.append("- services.nidw.gov.bd ওয়েবসাইটে রি-ইস্যু অপশনে গিয়ে জিডি নম্বর ও বিবরণ দিয়ে আবেদন করুন।")
                parts.append("- নির্ধারিত সরকারি ফি (বিকাশ/রকেট/নগদে ২৩০ টাকা) জমা দিয়ে সামারি স্লিপ ডাউনলোড করুন।")
            elif service_id == "land_mutation":
                parts.append("- জমির মূল দলিল বা খতিয়ান হারিয়ে গেলে সংশ্লিষ্ট সাব-রেজিস্ট্রি অফিস বা জেলা রেকর্ড রুম থেকে সহি-মুহুরি (Certified Copy) সংগ্রহ করুন।")
            parts.append("")

        # 2. Statutory Fee Section
        if intents["fee"] or (not intents["doc"] and not intents["steps"] and not intents["lost"]):
            if fees_chunk:
                fee_lines = self._extract_relevant_fees(query, (fees_chunk.metadata or {}).get("official_fees") or {})
                if fee_lines:
                    parts.append("**নির্ধারিত সরকারি ফি:**")
                    parts.extend(fee_lines)
                    parts.append("")

        # 3. Steps & Procedure Section
        if intents["steps"]:
            if steps_chunk and steps_chunk.content:
                parts.append("**আবেদনের সঠিক সরকারি ধাপ:**")
                # Parse steps
                lines = [l.strip() for l in steps_chunk.content.split("\n") if l.strip().startswith(("১.", "২.", "৩.", "৪.", "৫.", "৬.", "৭.", "৮.", "1.", "2.", "3.", "4."))]
                if lines:
                    parts.extend(lines[:5])
                else:
                    parts.append(steps_chunk.content[:400])
                parts.append("")

        # 4. Required Documents Section
        if intents["doc"]:
            chosen_doc = None
            for c in doc_chunks:
                cat = ((c.metadata or {}).get("category") or "")
                if any(k in query for k in ["নাম", "জন্ম", "ঠিকানা", "নবায়ন", "সাধারণ"]):
                    if any(k in cat for k in ["নাম", "জন্ম", "ঠিকানা", "নবায়ন", "সাধারণ"]):
                        chosen_doc = c
                        break
            if not chosen_doc and doc_chunks:
                chosen_doc = doc_chunks[0]

            docs_list = ((chosen_doc.metadata or {}).get("docs") if chosen_doc else None) or []
            if docs_list:
                cat = (chosen_doc.metadata or {}).get("category") or "প্রয়োজনীয় নথিপত্র"
                parts.append(f"**প্রয়োজনীয় কাগজপত্র ({cat}):**")
                for item in docs_list[:5]:
                    parts.append(f"- {item}")
                parts.append("")

        # 5. Middleman / Bribe Warning
        if dalal_alert:
            parts.append("**সরকারি সতর্কতা ও পরামর্শ:**")
            parts.append("- সরকারি সেবায় কোনো দালাল বা মধ্যস্বত্বভোগী নিয়োগের প্রয়োজন নেই। দালালকে অতিরিক্ত টাকা প্রদান সম্পূর্ণ বেআইনি।")
            parts.append("- কোনো কর্মকর্তা বা দালাল অতিরিক্ত ফি দাবি করলে সরাসরি অভিযোগ জানান: **১০৬ (দুদক হটলাইন)** বা **৯৯৯ (বাংলাদেশ পুলিশ)**।")
            parts.append("")

        # 6. Official Portal & Helpline
        hotline = meta.get("hotline")
        url = meta.get("official_url") or chunks[0].source_url
        parts.append("**অফিশিয়াল সংযোগ ও তথ্য:**")
        if hotline:
            parts.append(f"- সরকারি হেল্পলাইন: `{hotline}`")
        if url:
            parts.append(f"- সরকারি ওয়েব পোর্টাল: [{url}]({url})")

        return "\n".join(parts)
