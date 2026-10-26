# 🇧🇩 International AI Builders Congress 2026 — Official Submission Dossier
**Project:** CivicSphere AI (GovCopilot & Dalal-Free Citizen Assistant)  
**Event:** International AI Builders Congress (`bbbf4c45-c600-4ae6-8abf-b59e21f93076`)  
**Phase:** Idea to Unicorn — Preliminary Submission (`b4261d40-df30-4db0-89ab-782ad8d1e357`)  
**Deadline:** October 31, 2026, 11:59 PM BST  
**Submission Portal:** [CloudCamp Bangladesh Submission Page](https://cloudcampbd.com/submissions/new?event=bbbf4c45-c600-4ae6-8abf-b59e21f93076&phase=b4261d40-df30-4db0-89ab-782ad8d1e357&team=d4578244-3349-4cb8-baba-6b00c7028aff)

---

## 📌 TAB 1: STORY (Project Overview & Narrative)

### 1. Project Name
```text
CivicSphere AI
```

### 2. One-Liner Pitch (Elevator Pitch)
```text
A Bangla AI assistant that provides citizens with exact, officially grounded guidance for government services, eliminating reliance on corrupt middlemen (dalals).
```

### 3. Public Summary
```text
In Bangladesh, millions of citizens struggle to navigate bureaucratic government services such as National ID (NID) corrections, e-Passport applications, and Land Mutation (e-Namjari). The resulting confusion creates an extortionate parallel economy of unauthorized middlemen (dalals) who demand thousands of Takas for standard public procedures.

CivicSphere AI is an AI-first citizen copilot built specifically for Bangladesh. Grounded strictly in verified government circulars and fee schedules, it delivers step-by-step Bangla guidance via voice and text, provides dynamic document checklists, flags extortionate broker demands through its Dalal-Free Guardrail, and audits citizen documents prior to submission. By democratizing access to public administrative processes, CivicSphere AI restores digital trust and financial sovereignty to 170 million citizens.
```

### 4. Domain & Challenge Selection
- **Domain:** `CivicSphere AI` (`dec1e9e4-8be5-499c-b7b4-e489852e43bb`)
  - *Description:* Trustworthy digital public infrastructure, citizen services, and transparent governance.
- **Challenge:** `Citizen First` (`41bfaafd-6619-4be4-a8af-d7900c3ae473`)
  - *Description:* Unified, multilingual citizen-service assistant.  
  *(Alternative selections: `GovCopilot` or `Transparent Government`)*

### 5. Problem Statement
```text
Every year, millions of citizens across Bangladesh interact with frontline public services—most notably NID correction (services.nidw.gov.bd), e-Passport issuance (epassport.gov.bd), and land mutation (mutation.land.gov.bd). Despite government digitization, the citizen experience remains plagued by three systemic failures:

1. Information Asymmetry & Fragmented Rules: Procedures, category classifications (e.g., NID Category A vs. C), and document prerequisites are scattered across ambiguous PDFs, official gazettes, and complex portals. Citizens rarely know the exact documentation required, leading to frequent rejections and repeated office visits.

2. The Middleman (Dalal) Exploitation Economy: Because citizens fear bureaucratic rejection or procedural delays, predatory middlemen thrive outside every passport office, election commission center, and AC Land office. Dalals regularly charge ৳৫,০০০ to ৳৩০,০০০ for services where the government fee is capped at ৳১,১৭০ (Land Mutation) or ৳২৩০–৳৫৭৫ (NID). This imposes an informal "corruption tax" that disproportionately burdens rural citizens, low-income earners, and daily wage laborers.

3. High Barrier of Digital Literacy & Language Access: Official forms and notices frequently use complex administrative Bangla or English terminology. Furthermore, millions of low-literacy citizens cannot read lengthy web portals, making conversational voice interaction a fundamental necessity rather than a luxury.
```

### 6. Solution Description
```text
CivicSphere AI solves these problems through an AI-powered, bilingual, voice-enabled citizen copilot grounded strictly in verified government truth:

1. Strict Retrieval-Augmented Generation (RAG) with Zero Hallucination: The core engine indexes verified circulars, government gazettes, fee structures, and procedural workflows into a hybrid vector store combining BM25 keyword matching and Bengali morphological stemming. Unlike general-purpose LLMs that hallucinate administrative rules, CivicSphere AI answers only from retrieved official context and provides direct citations to official portals and hotlines (105, 16445, 16122, 106).

2. "Dalal-Free" Anti-Corruption Guardrail & Savings Calculator: An integrated heuristic and pattern-matching guardrail scans citizen queries for mentions of unofficial fees or broker demands. When detected, the system immediately triggers a high-visibility Red Dalal Alert, calculates exact citizen savings compared to the statutory government fee, and offers a 1-click speed-dial to the Anti-Corruption Commission hotline (106).

3. Multimodal Document Pre-Flight Inspector: Citizens can photograph their NID, birth certificate, SSC certificate, or land deed. CivicSphere AI's Vision Auditor checks for document legibility, missing signatures, matching Bengali names, and required gazetted attestations before the citizen travels to the government counter.

4. Voice Accessibility for All: Integrated HTML5 Web Speech API (bn-BD) and Google Text-to-Speech (gTTS) allow rural or non-literate citizens to speak naturally in Bangla and listen to spoken instructions.
```

---

## 📌 TAB 2: PROOF (Repository, Live Demo & Video Pitch)

### 1. GitHub Repository URL
```text
https://github.com/tamimarahmanchoity/CivicSphere-AI
```
*(Code is located locally at `/Users/tamimarahmanchoity/Desktop/CivicSphere-AI`)*

### 2. Live Demo URL
```text
https://civicsphere-ai.streamlit.app
```
*(Or local demo: `http://localhost:8501`)*

### 3. YouTube Video Link (2-Minute Demo Pitch)
*(Upload your video and paste the URL. Below is the 2-minute video script)*
- **0:00 - 0:25 (The Problem):** "In Bangladesh, getting an e-Passport or fixing an NID or completing a land mutation often means falling prey to dalals charging 5,000 to 30,000 Taka. Citizens don't know the real rules or fees."
- **0:25 - 0:50 (The Solution):** "Meet CivicSphere AI (GovCopilot). A Bangla assistant grounded strictly in official Bangladesh government data with zero hallucinations and total citizen transparency."
- **0:50 - 1:15 (Live Demo - Anti-Dalal Alert):** Type: *"পাসপোর্টের জন্য দালাল ৮,০০০ টাকা চাচ্ছে, এটা কি ঠিক?"* Show the instant Red Dalal Alert banner highlighting the real official fee (৳৪,০২৫) and the 106 Anti-Corruption hotline.
- **1:15 - 1:35 (Voice & Fee Calculator):** Demonstrate the Bangla voice input, voice output, and the Fee Calculator showing how much money citizens save in real time.
- **1:35 - 1:50 (Vision Document Audit):** Upload a document photo and show the instant pre-flight check for missing signatures, resolution, and name consistency.
- **1:50 - 2:00 (Vision & Conclusion):** "CivicSphere AI: Transparent, accessible, and Dalal-Free public services for 170 million citizens."

### 4. Test Credentials / Access Notes
```text
No login required. The app is publicly accessible with an intuitive Bangla interface. An optional Gemini API Key can be entered in the sidebar to enable live Gemini 2.5 Flash responses; otherwise, the system automatically falls back to its built-in offline Grounded Deterministic RAG engine.
```

---

## 📌 TAB 3: AI-NATIVE BUILD (Architecture, Models & Orchestration)

### 1. AI Models Used
- **Primary LLM:** Google Gemini 2.5 Flash (`gemini-2.5-flash`) via `google-genai` SDK
- **Secondary / Alternative LLM:** OpenAI GPT-4o-mini (`gpt-4o-mini`) via `openai` SDK
- **Vision Model:** Google Gemini Multimodal Vision API
- **Fallback Engine:** Embedded Grounded Deterministic Engine (Offline Zero-Downtime)

### 2. Frameworks & Orchestration
- **Application Framework:** Streamlit (Python 3.10+)
- **Retrieval Engine:** Custom Hybrid Vector Store (BM25 + Bengali morphological token stemmer)
- **Speech Engine:** HTML5 Web Speech API (`bn-BD`) + `gTTS` (`lang='bn'`)
- **Testing:** Pytest automated test suite (`tests/test_rag.py`)

### 3. Guardrails & Safety
- **DalalDetector:** Proactive regex/keyword scanner identifying corrupt broker rates and illegal fees.
- **Strict Grounding:** Zero-hallucination constraint; returns safe refusals when queried out-of-scope.
- **Zero-PII Storage:** Ephemeral document inspection; citizen files are never stored or logged.

---

## 📌 TAB 4: DATA LIFECYCLE (Sources, Ingestion & Governance)

### 1. Official Data Sources
- **NID Wing (Election Commission):** `services.nidw.gov.bd` (Helpline: `105`)
- **Department of Immigration & Passports:** `epassport.gov.bd` (Helpline: `16445` / `333`)
- **Ministry of Land (e-Mutation):** `mutation.land.gov.bd` (Helpline: `16122`)
- **Anti-Corruption Commission (ACC):** Hotline `106`

### 2. Processing & Storage
- Structured JSON format with verified schema (`category`, `official_fee`, `required_docs`, `helpline`, `official_url`).
- Semantic chunking by citizen service category.
- Top-2 chunk selection for minimal token overhead (<500 tokens context window).

---

## 📌 TAB 5: PROMPT LIBRARY & PROVENANCE

### Core Grounded System Prompt
```text
তুমি 'CivicSphere AI' (GovCopilot), বাংলাদেশ সরকারের বিভিন্ন নাগরিক সেবার (যেমন: NID সংশোধন, ই-পাসপোর্ট, ই-নামজারি ইত্যাদি) একজন বিশ্বস্ত ও নিরপেক্ষ সহায়ক।

তোমার দায়িত্ব:
১. শুধুমাত্র নিচে দেওয়া 'অফিসিয়াল তথ্য' (Context) ব্যবহার করে নাগরিকের প্রশ্নের স্পষ্ট, সঠিক ও সম্পূর্ণ উত্তর বাংলায় দাও।
২. কোন অবস্থাতেই কনটেক্সটের বাইরে থেকে তথ্য বা মনগড়া ফি/নিয়ম বানাবে না। যদি কনটেক্সটে উত্তর না থাকে, স্পষ্টভাবে বলো যে তথ্যটি জানা নেই এবং সংশ্লিষ্ট সরকারি হেল্পলাইনে যোগাযোগ করতে বলো।
৩. সরকারি নির্ধারিত ফি, প্রয়োজনীয় কাগজপত্র ও অফিশিয়াল লিংক স্পষ্টভাবে উল্লেখ করো।
৪. যদি কোনো দালাল বা অতিরিক্ত টাকার বিষয় আসে, তবে দৃঢ়ভাবে জানাও যে এটি অবৈধ এবং হটলাইন ১০৬ (দুদক)-এ অভিযোগ করার পরামর্শ দাও।
```
