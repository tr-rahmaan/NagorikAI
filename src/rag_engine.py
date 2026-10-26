"""
Core RAG Engine for NagorikAI: Grounded Bangla Q&A, Dalal Warning, and Citations.
Supports Gemini API (gemini-3.8-flash, gemini-2.5-flash fallback), OpenAI API, and Grounded Deterministic Generation.
"""

import os
import ssl
from typing import Dict, Any, List, Optional
from src.vector_store import HybridVectorStore, Chunk
from src.dalal_detector import DalalDetector

# Ensure unverified SSL context for environments with local cert issues
try:
    ssl._create_default_https_context = ssl._create_unverified_context
except Exception:
    pass

SYSTEM_PROMPT = """আপনি 'NagorikAI' (নাগরিক AI) - বাংলাদেশ সরকারের নাগরিক সেবার জন্য একটি দায়িত্বশীল, দালাল-মুক্ত ও নির্ভরযোগ্য এআই সহকারী।
আপনার প্রধান উদ্দেশ্য নাগরিকদের এনআইডি (NID) সংশোধন ও রি-ইস্যু, ই-পাসপোর্ট আবেদন ও নবায়ন এবং ভূমির ই-নামজারি সেবার সঠিক সরকারি তথ্য দেওয়া এবং মধ্যস্বত্বভোগী/দালালের প্রতারণা ও অতিরিক্ত ফি থেকে রক্ষা করা।

কঠোর নিয়মাবলী:
১. শুধুমাত্র নিচের প্রদত্ত [Official Context] থেকে পাওয়া তথ্যের ভিত্তিতে বাংলায় উত্তর দিন।
২. মনগড়া কোনো তথ্য, কাল্পনিক ফি বা অননুমোদিত নিয়মের কথা বলবেন না।
৩. তথ্যের মধ্যে উত্তর না থাকলে সরাসরি বলুন: "দুঃখিত, সরকারি তথ্যে এই নির্দিষ্ট বিষয়টি পাওয়া যায়নি। দয়া করে সংশ্লিষ্ট সরকারি হেল্পলাইনে যোগাযোগ করুন।"
৪. প্রতিটি উত্তরে অবশ্যই সংশ্লিষ্ট অফিসিয়াল ওয়েবসাইটের লিঙ্ক এবং সরকারি হেল্পলাইন নম্বর উল্লেখ করুন।
৫. ব্যবহারকারী কোনো অতিরিক্ত ফি বা দালালের কথা বললে কঠোরভাবে সতর্ক করুন এবং অফিশিয়াল ফি মনে করিয়ে দিন।
৬. উত্তরটি সুন্দর বুলেট পয়েন্ট ও ইমোজি দিয়ে সাজিয়ে লিখুন:
   - 📋 প্রয়োজনীয় কাগজপত্র
   - 💰 অফিশিয়াল সরকারি ফি (টাকা)
   - 📝 ধাপে ধাপে আবেদনের অফিসিয়াল নিয়ম
   - ⚠️ দালাল ও প্রতারণা সতর্কতা
   - 🔗 অফিশিয়াল ওয়েবসাইট ও হটলাইন
"""

class RAGEngine:
    def __init__(self, data_dir: str, api_key: Optional[str] = None, provider: str = "auto"):
        self.vector_store = HybridVectorStore(data_dir)
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or "AIzaSyDQzW0tny_EjMP-abBEYfqg445xhx-bDzw"
        self.provider = provider
        self._init_llm_client()

    def _init_llm_client(self):
        """Initializes Gemini or OpenAI client if keys are present."""
        self.client_gemini = None
        self.client_openai = None

        gemini_key = self.api_key or os.getenv("GEMINI_API_KEY")
        if gemini_key:
            try:
                from google import genai
                self.client_gemini = genai.Client(api_key=gemini_key)
            except Exception:
                pass

        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            try:
                from openai import OpenAI
                self.client_openai = OpenAI(api_key=openai_key)
            except Exception:
                pass

    def query(self, user_query: str, top_k: int = 3) -> Dict[str, Any]:
        """
        Executes the full RAG pipeline:
        1. Dalal / Middleman check
        2. Semantic retrieval of official knowledge chunks
        3. LLM or Grounded generation with strict citations
        """
        # 1. Dalal Detector scan
        dalal_alert = DalalDetector.scan_query(user_query)

        # 2. Retrieve top chunks
        retrieved_items = self.vector_store.search(user_query, top_k=top_k)
        retrieved_chunks = [item[0] for item in retrieved_items]

        # Extract unique official source links
        sources = list(set([c.source_url for c in retrieved_chunks if c.source_url]))

        # 3. Context string
        context_str = "\n\n".join([
            f"--- [উৎস: {c.title} | লিঙ্ক: {c.source_url}] ---\n{c.content}"
            for c in retrieved_chunks
        ])

        # 4. Generate answer
        answer = None
        generation_mode = "grounded_offline"

        if self.client_gemini:
            prompt = (
                f"{SYSTEM_PROMPT}\n\n"
                f"[Official Context]:\n{context_str}\n\n"
                f"[User Query]:\n{user_query}\n\n"
                f"উত্তর:"
            )
            # Try gemini-3.8-flash first, fallback to gemini-2.5-flash or gemini-2.0-flash
            for model_name in ['gemini-3.8-flash', 'gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-1.5-flash']:
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

        if not answer and self.client_openai:
            try:
                response = self.client_openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": f"[Official Context]:\n{context_str}\n\n[User Query]:\n{user_query}"}
                    ],
                    temperature=0.2
                )
                if response.choices and response.choices[0].message.content:
                    answer = response.choices[0].message.content
                    generation_mode = "gpt-4o-mini"
            except Exception:
                pass

        # 5. Offline Grounded Deterministic Generation fallback
        if not answer:
            answer = self._generate_grounded_fallback(user_query, retrieved_chunks, dalal_alert)
            generation_mode = "Grounded Knowledge Engine (Zero-Downtime)"

        return {
            "query": user_query,
            "answer": answer,
            "sources": sources,
            "dalal_alert": dalal_alert,
            "mode": generation_mode
        }

    def _generate_grounded_fallback(self, query: str, chunks: List[Chunk], dalal_alert: Optional[Dict[str, Any]]) -> str:
        """Structured fallback synthesis directly from verified JSON chunks."""
        if not chunks:
            return (
                "দুঃখিত, সরকারি ডেটাবেজে আপনার প্রশ্নের সাথে হুবহু তথ্য মেলেনি।\n\n"
                "**জরুরি সহায়তা পেতে সরকারি হেল্পলাইনে যোগাযোগ করুন:**\n"
                "- 🪪 জাতীয় পরিচয়পত্র (NID): **১০৫** (টোল-ফ্রি)\n"
                "- 🛂 ই-পাসপোর্ট: **১৬৪৪৫** অথবা **৩৩৩**\n"
                "- 🌾 ভূমিসেবা (ই-নামজারি): **১৬১২২**\n"
                "- 🛡️ দুদক (ঘুষ/দালাল অভিযোগ): **১০৬**"
            )

        top = chunks[0]
        meta = top.metadata or {}

        response_parts = [
            f"### 🇧🇩 NagorikAI অফিশিয়াল তথ্য: {top.title}\n",
            f"{top.content}\n"
        ]

        if "official_fee" in meta:
            response_parts.append(f"**💰 নির্ধারিত সরকারি ফি:** `{meta['official_fee']}`")

        if "helpline" in meta:
            response_parts.append(f"**📞 জরুরি সরকারি হটলাইন:** `{meta['helpline']}`")

        if "official_url" in meta:
            response_parts.append(f"**🔗 অফিশিয়াল ওয়েবসাইট:** [{meta['official_url']}]({meta['official_url']})")

        response_parts.append("\n> 💡 **নাগরিক সতর্কতা:** দালাল বা কোনো ব্যক্তিকে অতিরিক্ত টাকা দেওয়া আইনত দণ্ডনীয়। সরকারি সেবা সরাসরি অফিশিয়াল পোর্টালে আবেদন করে গ্রহণ করুন।")

        return "\n".join(response_parts)
