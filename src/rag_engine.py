"""
Core High-Speed RAG Engine for NagorikAI.
Fast, sub-second response times with direct model routing and zero timeout delays.
"""

import os
import sys
import ssl
from typing import Dict, Any, List, Optional

# Fix import path: works whether called from project root or from inside src/
try:
    from src.vector_store import HybridVectorStore, Chunk
    from src.dalal_detector import DalalDetector
except ModuleNotFoundError:
    # Running from inside the project root via app.py path
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

SYSTEM_PROMPT = """আপনি 'NagorikAI' (নাগরিক AI) - সাধারণ মানুষের জন্য সহজ, সুন্দর ও সরাসরি সরকারি তথ্য দেওয়ার স্মার্ট সহকারী।

উত্তর দেওয়ার নিয়মাবলী:
১. নাগরিকের নির্দিষ্ট প্রশ্নের সরাসরি, সংক্ষেপ ও পরিষ্কার উত্তর বাংলায় দিন।
২. উত্তরটি ছোট ও পরিচ্ছন্ন রাখুন:
   - 🎯 সরাসরি উত্তর (ফি বা মূল তথ্যটি এক নজরে)
   - 📋 কী কী কাগজপত্র লাগবে (সংক্ষিপ্ত বুলেট পয়েন্ট)
   - ⚠️ সতর্কতা (যদি দালাল বা অতিরিক্ত টাকার বিষয় থাকে)
   - 🔗 অফিশিয়াল ওয়েবসাইট ও হেল্পলাইন
৩. যদি তথ্যে উত্তর না থাকে, সরাসরি বলুন: "দুঃখিত, এই বিষয়টি সরকারি তথ্যে নেই। অনুগ্রহ করে সরকারি হেল্পলাইনে যোগাযোগ করুন।"
৪. ভাষা হতে হবে অত্যন্ত অমায়িক, সহজবোধ্য ও সাধারণ মানুষের জন্য বন্ধুভাবাপন্ন।
"""

class RAGEngine:
    def __init__(self, data_dir: str, api_key: Optional[str] = None):
        self.vector_store = HybridVectorStore(data_dir)
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or "AIzaSyDQzW0tny_EjMP-abBEYfqg445xhx-bDzw"
        self._init_llm_client()

    def _init_llm_client(self):
        """Initializes Gemini client with fast timeout options."""
        self.client_gemini = None
        gemini_key = self.api_key or os.getenv("GEMINI_API_KEY")
        if gemini_key:
            try:
                from google import genai
                # Configure client with 4-second timeout to avoid any freezing
                self.client_gemini = genai.Client(
                    api_key=gemini_key,
                    http_options={"timeout": 4.0}
                )
            except Exception:
                pass

    def query(self, user_query: str, top_k: int = 2) -> Dict[str, Any]:
        """
        Ultra-fast RAG query pipeline (<0.8s):
        1. Dalal Detector scan
        2. Semantic retrieval of top chunks
        3. Direct fast model call with instant fallback
        """
        dalal_alert = DalalDetector.scan_query(user_query)

        # Retrieve top chunks
        retrieved_items = self.vector_store.search(user_query, top_k=top_k)
        retrieved_chunks = [item[0] for item in retrieved_items]
        sources = list(set([c.source_url for c in retrieved_chunks if c.source_url]))

        context_str = "\n\n".join([
            f"--- [{c.title}] ---\n{c.content}"
            for c in retrieved_chunks
        ])

        answer = None
        generation_mode = "NagorikAI Grounded Knowledge Engine"

        # Safe fast generation with strict 0.8s timeout
        if self.client_gemini:
            import concurrent.futures
            prompt = (
                f"{SYSTEM_PROMPT}\n\n"
                f"[সরকারি তথ্য (Context)]:\n{context_str}\n\n"
                f"[নাগরিকের প্রশ্ন]:\n{user_query}\n\n"
                f"সংক্ষিপ্ত ও পরিচ্ছন্ন উত্তর:"
            )

            def _call_model():
                for model_name in ['gemini-3.8-flash', 'gemini-2.0-flash']:
                    try:
                        resp = self.client_gemini.models.generate_content(
                            model=model_name,
                            contents=prompt
                        )
                        if resp and resp.text:
                            return resp.text, f"Gemini ({model_name})"
                    except Exception:
                        continue
                return None, None

            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(_call_model)
                try:
                    res_text, mode_name = future.result(timeout=0.8)
                    if res_text:
                        answer = res_text
                        generation_mode = mode_name
                except Exception:
                    # Instant fallback if network times out or model errors
                    answer = None

        # Instant local grounded fallback (<0.001s)
        if not answer:
            answer = self._generate_grounded_fallback(user_query, retrieved_chunks, dalal_alert)

        return {
            "query": user_query,
            "answer": answer,
            "sources": sources,
            "dalal_alert": dalal_alert,
            "mode": generation_mode
        }

    def _generate_grounded_fallback(self, query: str, chunks: List[Chunk], dalal_alert: Optional[Dict[str, Any]]) -> str:
        """Instant (<1ms) direct answer synthesis from verified JSON chunks."""
        if not chunks:
            return (
                "দুঃখিত, সরকারি ডেটাবেজে এই সুনির্দিষ্ট তথ্যটি পাওয়া যায়নি।\n\n"
                "**প্রয়োজনে সরাসরি কল করুন:**\n"
                "- 🪪 NID: **১০৫** | 🛂 পাসপোর্ট: **১৬৪৪৫** | 🌾 ভূমিসেবা: **১৬১২২**"
            )

        # Prioritize general applicant requirements if asking general requirements
        chosen_chunk = chunks[0]
        q_lower = query.lower()
        if any(w in q_lower for w in ["dorka", "দরকার", "লাগে", "কাগজ", "ডকুমেন্ট", "notun", "নতুন"]) and "নবায়ন" not in q_lower and "renew" not in q_lower:
            for c in chunks:
                if "সাধারণ আবেদনকারী" in c.title:
                    chosen_chunk = c
                    break

        meta = chosen_chunk.metadata or {}
        response_parts = [
            f"### 🇧🇩 {chosen_chunk.title}\n",
            f"{chosen_chunk.content}\n"
        ]

        if "official_fee" in meta:
            response_parts.append(f"**💰 সরকারি ফি:** `{meta['official_fee']}`")

        if "helpline" in meta:
            response_parts.append(f"**📞 হেল্পলাইন:** `{meta['helpline']}`")

        if "official_url" in meta:
            response_parts.append(f"**🔗 ওয়েবসাইট:** [{meta['official_url']}]({meta['official_url']})")

        return "\n".join(response_parts)
