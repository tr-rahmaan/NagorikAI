# 🇧🇩 NagorikAI (নাগরিক AI)
### GovCopilot & Dalal-Free Citizen Assistant for Bangladesh Public Services
**Official Entry for International AI Builders Congress 2026**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://civicsphere-ai.streamlit.app)
[![Tests Passing](https://img.shields.io/badge/pytest-7%20passed-brightgreen.svg)](tests/test_rag.py)
[![Model](https://img.shields.io/badge/LLM-Gemini%203.8%20Flash-blue.svg)](https://ai.google.dev)
[![Hotline](https://img.shields.io/badge/ACC%20Hotline-106-red.svg)](https://acc.org.bd)

---

## 📌 Executive Summary
Every year, millions of citizens in Bangladesh need frontline public administrative services:
1. **জাতীয় পরিচয়পত্র (NID) সংশোধন ও রি-ইস্যু** (`services.nidw.gov.bd` | Helpline: `105`)
2. **ই-পাসপোর্ট আবেদন ও নবায়ন** (`epassport.gov.bd` | Helpline: `16445` / `333`)
3. **ই-নামজারি ও জমাভাগ (Land Mutation)** (`mutation.land.gov.bd` | Helpline: `16122`)

Due to confusing procedural circulars and fear of administrative rejection, an informal parallel economy of unauthorized middlemen (**দালাল / Dalals**) charges citizens **৳৫,০০০ to ৳৩০,০০০** for services whose statutory fees are legally capped at **৳১,১৭০** (Land Mutation) or **৳২৩০–৳৫৭৫** (NID).

**NagorikAI** solves this crisis through two integrated paradigms:
- **GovCopilot (The Working MVP):** A Bengali conversational AI assistant grounded strictly in verified Bangladesh government circulars and fee schedules, complete with voice audio translation and document checklists.
- **Dalal-Free (Anti-Corruption Guardrail):** An active rule-engine and pattern-matching scanner that intercepts extortionate demands, calculates citizen savings against statutory caps, and links directly to the Anti-Corruption Commission hotline (`106`).

---

## 🚀 Key Features

| Feature | Description | Status |
|---|---|---|
| **Bangla Q&A with Strict Grounding** | Answers generated strictly from verified government gazette chunks; zero hallucinations. | ✅ **Production Live** |
| **Dalal-Free Protection Alert** | Proactively detects broker rates, extra fees, or bribe mentions; triggers high-visibility alert banner. | ✅ **Production Live** |
| **Fee Calculator & Savings Metric** | Interactive calculator comparing official government fees vs. broker demands. | ✅ **Production Live** |
| **Live Document Checklist** | Interactive checkbox list tailored to the user's specific application category. | ✅ **Production Live** |
| **Bangla Voice Output (TTS)** | Natural Bengali voice audio playback via gTTS for rural/low-literacy accessibility. | ✅ **Production Live** |
| **Document Vision Inspector** | Multimodal AI pre-flight audit for uploaded NID, passport slips, certificates, and deeds. | ✅ **Production Live** |

---

## 🛠️ Architecture & Tech Stack

- **Frontend & App:** Python 3.10+, Streamlit (Custom styled Bengali Civic theme)
- **Vector Search & Retrieval:** Hybrid Vector Store with Bengali morphological stemmer & BM25 rank fusion
- **LLM / Generation:** Google Gemini 3.8 Flash (`gemini-3.8-flash`), OpenAI GPT-4o-mini, or Grounded Deterministic Engine (Zero-downtime offline fallback)
- **Voice Output:** Google Text-to-Speech (`gTTS`, `lang='bn'`)
- **Vision:** Multimodal Gemini Vision document auditor + local pre-flight heuristic checks

---

## 💻 How to Run Locally

### 1. Run the Application
```bash
streamlit run app.py
```
Your browser will open automatically at `http://localhost:8501`.

### 2. Run Automated Tests
```bash
python3 tests/test_rag.py
```
*Output: 7 passed in 1.77s (OK).*

---

