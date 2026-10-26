"""
Core RAG Engine for NagorikAI: Concise, Direct, Human-Friendly Bangla Guidance.
Optimized for direct answers without overwhelming the citizen.
"""

import os
import ssl
from typing import Dict, Any, List, Optional
from src.vector_store import HybridVectorStore, Chunk
from src.dalal_detector import DalalDetector

try:
    ssl._create_default_https_context = ssl._create_unverified_context
except Exception:
    pass

SYSTEM_PROMPT = """আপনি 'NagorikAI' (নাগরিক AI) - সাধারণ মানুষের জন্য সহজ, সুন্দর ও সরাসরি সরকারি তথ্য দেওয়ার স্মার্ট সহকারী।

উত্তর দেওয়ার নিয়মাবলী:
১. নাগরিকের নির্দিষ্ট প্রশ্নের সরাসরি, সংক্ষেপ ও পরিষ্কার উত্তর বাংলায় দিন। অপ্রয়োজনীয় বড় রচনা লিখবেন না।
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
        """Initializes Gemini client."""
        self.client_gemini = None
        gemini_key = self.api_key or os.getenv("GEMINI_API_KEY")
        if gemini_key:
            try:
                from google import genai
                self.client_gemini = genai.Client(api_key=gemini_key)
            except Exception:
                pass

    def query(self, user_query: str, top_k: int = 2) -> Dict[str, Any]:
        """
        Executes concise RAG pipeline:
        1. Dalal Detector scan
        2. Semantic retrieval of official knowledge chunks
        3. Concise LLM or Grounded generation
        """
        dalal_alert = DalalDetector.scan_query(user_query)

        # Retrieve top chunks (focused top 2)
        retrieved_items = self.vector_store.search(user_query, top_k=top_k)
        retrieved_chunks = [item[0] for item in retrieved_items]
        sources = list(set([c.source_url for c in retrieved_chunks if c.source_url]))

        context_str = "\n\n".join([
            f"--- [{c.title}] ---\n{c.content}"
            for c in retrieved_chunks
        ])

        answer = None
        generation_mode = "grounded_offline"

        if self.client_gemini:
            prompt = (
                f"{SYSTEM_PROMPT}\n\n"
                f"[সরকারি তথ্য (Context)]:\n{context_str}\n\n"
                f"[নাগরিকের প্রশ্ন]:\n{user_query}\n\n"
                f"সংক্ষিপ্ত ও পরিচ্ছন্ন উত্তর:"
            )
            for model_name in ['gemini-3.8-flash', 'gemini-2.5-flash', 'gemini-2.0-flash']:
                try:
                    response = self.client_gemini.models.generate_content(
                        model=model_name,
                        contents=prompt
                    )
                    if response and response.text:
                        answer = response.text
                        generation_mode = f"Gemini ({model_name})"
                        break
                except Exception:
                    continue

        if not answer:
            answer = self._generate_grounded_fallback(user_query, retrieved_chunks, dalal_alert)
            generation_mode = "NagorikAI Offline Engine"

        return {
            "query": user_query,
            "answer": answer,
            "sources": sources,
            "dalal_alert": dalal_alert,
            "mode": generation_mode
        }

    def _generate_grounded_fallback(self, query: str, chunks: List[Chunk], dalal_alert: Optional[Dict[str, Any]]) -> str:
        """Concise, human-friendly fallback synthesis directly from verified JSON chunks."""
        if not chunks:
            return (
                "দুঃখিত, সরকারি ডেটাবেজে এই সুনির্দিষ্ট তথ্যটি পাওয়া যায়নি।\n\n"
                "**প্রয়োজনে কল করুন:**\n"
                "- 🪪 NID: **১০৫** | 🛂 পাসপোর্ট: **১৬৪৪৫** | 🌾 ভূমিসেবা: **১৬১২২**"
            )

        top = chunks[0]
        meta = top.metadata or {}

        response_parts = [
            f"### 🇧🇩 {top.title}\n",
            f"{top.content}\n"
        ]

        if "official_fee" in meta:
            response_parts.append(f"**💰 সরকারি ফি:** `{meta['official_fee']}`")

        if "helpline" in meta:
            response_parts.append(f"**📞 হেল্পলাইন:** `{meta['helpline']}`")

        if "official_url" in meta:
            response_parts.append(f"**🔗 ওয়েবসাইট:** [{meta['official_url']}]({meta['official_url']})")

        return "\n".join(response_parts)
