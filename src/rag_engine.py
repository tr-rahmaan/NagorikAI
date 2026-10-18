"""
Core RAG Engine for CivicSphere AI: Grounded Bangla Q&A, Dalal Warning, and Citations.
Supports Gemini API, OpenAI API, and Grounded Deterministic Generation (offline-ready).
"""

import os
from typing import Dict, Any, List, Optional
from src.vector_store import HybridVectorStore, Chunk
from src.dalal_detector import DalalDetector

SYSTEM_PROMPT = """আপনি 'CivicSphere AI' (GovCopilot) - বাংলাদেশ সরকারের নাগরিক সেবার জন্য একটি দায়িত্বশীল, দালাল-মুক্ত এআই সহকারী।
আপনার প্রধান উদ্দেশ্য নাগরিকদের এনআইডি (NID) সংশোধন, ই-পাসপোর্ট এবং ই-নামজারি সেবার সঠিক সরকারি তথ্য দেওয়া এবং মধ্যস্বত্বভোগী/দালালের প্রতারণা থেকে রক্ষা করা।

কঠোর নিয়মাবলী:
১. শুধুমাত্র নিচের প্রদত্ত [Official Context] থেকে পাওয়া তথ্যের ভিত্তিতে বাংলায় উত্তর দিন।
২. মনগড়া কোনো তথ্য, কাল্পনিক ফি বা অননুমোদিত নিয়মের কথা বলবেন না।
৩. তথ্যের মধ্যে উত্তর না থাকলে সরাসরি বলুন: "দুঃখিত, সরকারি তথ্যে এই নির্দিষ্ট বিষয়টি পাওয়া যায়নি। দয়া করে সংশ্লিষ্ট সরকারি হটলাইনে যোগাযোগ করুন।"
৪. প্রতিটি উত্তরে অবশ্যই সংশ্লিষ্ট অফিসিয়াল ওয়েবসাইটের লিঙ্ক এবং সরকারি হেল্পলাইন নম্বর উল্লেখ করুন।
৫. ব্যবহারকারী কোনো অতিরিক্ত ফি বা দালালের কথা বললে কঠোরভাবে সতর্ক করুন এবং অফিশিয়াল ফি মনে করিয়ে দিন।
৬. উত্তরটি সুন্দর বুলেট পয়েন্ট ও ইমোজি দিয়ে সাজিয়ে লিখুন:
   - 📋 প্রয়োজনীয় কাগজপত্র
   - 💰 অফিশিয়াল সরকারি ফি
   - 📝 ধাপে ধাপে আবেদনের নিয়ম
   - ⚠️ দালাল ও প্রতারণা সতর্কতা
   - 🔗 অফিশিয়াল ওয়েবসাইট ও হটলাইন
"""

class RAGEngine:
    def __init__(self, data_dir: str, api_key: Optional[str] = None, provider: str = "auto"):
        self.vector_store = HybridVectorStore(data_dir)
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")
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
            try:
                prompt = (
                    f"{SYSTEM_PROMPT}\n\n"
                    f"[Official Context]:\n{context_str}\n\n"
                    f"[User Query]:\n{user_query}\n\n"
                    f"উত্তর:"
                )
                response = self.client_gemini.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt
                )
                if response and response.text:
                    answer = response.text
                    generation_mode = "gemini-2.5-flash"
            except Exception as e:
                pass

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
                answer = response.choices[0].message.content
                generation_mode = "openai-gpt4o"
            except Exception:
                pass

        # Offline / Zero-API Fallback: High-precision grounded synthesis
        if not answer:
            answer = self._generate_grounded_fallback(user_query, retrieved_chunks, dalal_alert)
            generation_mode = "grounded_rule_engine"

        return {
            "query": user_query,
            "answer": answer,
            "dalal_alert": dalal_alert,
            "retrieved_chunks": [c.to_dict() for c in retrieved_chunks],
            "official_sources": sources,
            "generation_mode": generation_mode
        }

    def _generate_grounded_fallback(self, query: str, chunks: List[Chunk], dalal_alert: Optional[Dict[str, Any]]) -> str:
        """
        Deterministic, official grounded response generation when running without external LLM API key.
        Synthesizes information strictly from retrieved official chunks.
        """
        if not chunks:
            return (
                "দুঃখিত, সরকারি নির্দেশিকায় এই বিষয়ে নির্দিষ্ট কোনো তথ্য পাওয়া যায়নি।\n\n"
                "সঠিক তথ্যের জন্য দয়া করে জাতীয় কল সেন্টার **৩৩৩**, ভূমি সেবা **১৬১২২**, "
                "বা পাসপোর্ট হেল্পলাইন **১৬৪৪৫**-এ যোগাযোগ করুন।"
            )

        # Collect sections
        sections = []
        
        # Primary service header
        service_name = chunks[0].metadata.get("service_name", "সরকারি সেবা")
        hotline = chunks[0].metadata.get("hotline", "৩৩৩")
        source_url = chunks[0].source_url

        sections.append(f"### 🇧🇩 {service_name} সম্পর্কিত অফিসিয়াল তথ্য ও নির্দেশিকা\n")

        # Dalal alert emphasis if present
        if dalal_alert:
            sections.append(
                f"> **⚠️ দালাল ও বাড়তি ফি সতর্কতা:**\n"
                f"> {dalal_alert['advice_bn']}\n"
                f"> অফিশিয়াল ফি যাচাই না করে কাউকে নগদ টাকা বা ঘুষ দেবেন না। অভিযোগ নম্বর: **{dalal_alert['emergency_hotline']}**।\n"
            )

        # Add chunk contents formatted nicely
        for c in chunks:
            sections.append(f"#### 📌 {c.title}")
            sections.append(c.content)
            sections.append("")

        # Official citations & anti-corruption footer
        sections.append("---")
        sections.append("### 🔗 অফিসিয়াল সোর্স ও হেল্পলাইন")
        sections.append(f"- 🌐 **অফিসিয়াল পোর্টাল:** [{source_url}]({source_url})")
        sections.append(f"- 📞 **সরকারি হটলাইন:** {hotline}")
        sections.append("- 🛡️ **দুর্নীতি দমন কমিশন (দুদক):** ১০৬")
        sections.append("- ℹ️ **জাতীয় তথ্য ও সেবা:** ৩৩৩")
        sections.append("\n*সতর্কবার্তা: সরকারি ফি শুধুমাত্র অনুমোদিত ব্যাংক চালান বা অনলাইন পেমেন্ট গেটওয়ের মাধ্যমে দিন। কাউকে কোনো নগদ ঘুষ দেবেন না।*")

        return "\n\n".join(sections)
