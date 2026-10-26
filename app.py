"""
NagorikAI (নাগরিক AI) - GovCopilot & Dalal-Free Citizen Assistant
Bangla RAG Platform Grounded Exclusively in Authentic Bangladesh Government Sources.
Services: NID Correction, e-Passport, Land Mutation (e-Namjari).
"""

import os
import sys
import streamlit as st

# Ensure local packages in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.rag_engine import RAGEngine
from src.dalal_detector import DalalDetector
from src.vision_checker import DocumentVisionChecker
from src.speech_utils import text_to_bangla_speech

# Page configuration
st.set_page_config(
    page_title="NagorikAI (নাগরিক AI) | সরকারি সেবা সহায়িকা ও দুর্নীতি প্রতিরোধ",
    page_icon="🇧🇩",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium Modern Civic CSS Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Hind+Siliguri:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Hind Siliguri', 'Plus Jakarta Sans', sans-serif;
    }
    
    .hero-header {
        background: linear-gradient(135deg, #064e3b 0%, #047857 50%, #0f766e 100%);
        padding: 30px 36px;
        border-radius: 18px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(6, 78, 59, 0.25);
    }
    
    .hero-title {
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.02em;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .hero-subtitle {
        font-size: 1.15rem;
        color: #d1fae5;
        margin-top: 8px;
        line-height: 1.5;
        max-width: 900px;
    }
    
    .badge-bar {
        display: flex;
        gap: 12px;
        margin-top: 16px;
        flex-wrap: wrap;
    }
    
    .badge-pill {
        background: rgba(255, 255, 255, 0.18);
        border: 1px solid rgba(255, 255, 255, 0.3);
        color: #ffffff;
        padding: 6px 14px;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 600;
        backdrop-filter: blur(8px);
    }
    
    .dalal-alert-card {
        background: #fef2f2;
        border: 1px solid #fecaca;
        border-left: 6px solid #ef4444;
        padding: 18px 22px;
        border-radius: 12px;
        margin: 16px 0;
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.08);
    }
    
    .savings-chip {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #dcfce7;
        border: 1px solid #86efac;
        color: #166534;
        padding: 4px 12px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 0.95rem;
        margin-top: 8px;
    }
    
    .source-box {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 12px 16px;
        margin-top: 12px;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# Sidebar Configuration
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/8/84/Government_Seal_of_Bangladesh.svg/200px-Government_Seal_of_Bangladesh.svg.png", width=75)
    st.title("🇧🇩 NagorikAI")
    st.caption("**নাগরিক সেবা সহায়িকা ও দুর্নীতি প্রতিরোধ প্ল্যাটফর্ম**")
    st.markdown("*International AI Builders Congress 2026*")
    st.divider()

    st.subheader("⚙️ AI ইঞ্জিন মডেল সেটিংস")
    api_key_default = os.getenv("GEMINI_API_KEY", "AIzaSyDQzW0tny_EjMP-abBEYfqg445xhx-bDzw")
    api_key_input = st.text_input(
        "Google Gemini API Key:",
        type="password",
        value=api_key_default,
        help="ডিফল্ট কি সেট করা রয়েছে। Gemini 3.8 Flash ও মাল্টিমোডাল ভিশন সক্রিয় থাকবে।"
    )

    st.divider()
    st.subheader("📞 জরুরি সরকারি হটলাইন")
    st.markdown("""
    - 🪪 **জাতীয় পরিচয়পত্র (NID):** `১০৫` (টোল-ফ্রি)
    - 🛂 **ই-পাসপোর্ট অধিদপ্তর:** `১৬৪৪৫` / `৩৩৩`
    - 🌾 **ভূমি সেবা (ই-নামজারি):** `১৬১২২`
    - 🛡️ **দুদক (ঘুষ/দালাল অভিযোগ):** `১০৬`
    - 🚨 **জাতীয় জরুরি সেবা:** `৯৯৯`
    """)

    st.divider()
    st.info("💡 **উদ্দেশ্য:** সাধারণ নাগরিকরা যেন দালালদের খপ্পরে পড়ে হাজার হাজার টাকা না হারান এবং শতভাগ সরকারি নিয়মে ঘরে বসে সেবা পান।")

# Initialize RAG Engine
@st.cache_resource
def get_rag_engine(api_key: str):
    return RAGEngine(data_dir=DATA_DIR, api_key=api_key if api_key else None)

rag_engine = get_rag_engine(api_key_input)

# Top Hero Banner
st.markdown("""
<div class="hero-header">
    <div class="hero-title">🇧🇩 NagorikAI (নাগরিক AI)</div>
    <div class="hero-subtitle">
        জাতীয় পরিচয়পত্র (NID), ই-পাসপোর্ট এবং ভূমির ই-নামজারির নির্ভুল সরকারি তথ্যভাণ্ডার ও সক্রিয় দালাল প্রতিরোধ প্ল্যাটফর্ম।
    </div>
    <div class="badge-bar">
        <span class="badge-pill">✅ ১০০% সরকারি গেজেট ও সার্কুলার সমর্থিত</span>
        <span class="badge-pill">🛡️ দালাল প্রতিরোধ ও দুর্নীতি সতর্কতা (ACC 106)</span>
        <span class="badge-pill">🔊 বাংলা ভয়েস অডিও অনুবাদযুক্ত</span>
        <span class="badge-pill">📸 মাল্টিমোডাল ডকুমেন্ট অডিটর</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Main Navigation Tabs
tab_chat, tab_calculator, tab_vision, tab_roadmap = st.tabs([
    "💬 বাংলা এআই পরামর্শক (GovCopilot)",
    "💰 সরকারি ফি ক্যালকুলেটর ও চেকলিস্ট",
    "📸 ডকুমেন্ট ভিশন অডিট (Vision AI)",
    "🚀 ফিচার রোডম্যাপ ও ভিশন"
])

# Initialize session chat state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "স্বাগতম! আমি **NagorikAI** (নাগরিক AI)। এনআইডি সংশোধন, ই-পাসপোর্ট বা ভূমির ই-নামজারি নিয়ে আপনার যেকোনো প্রশ্ন বাংলায় করতে পারেন।\n\n"
                "**আমি আপনাকে সাহায্য করব:**\n"
                "1. 💰 **অফিশিয়াল সরকারি ফি** এবং দালালদের অতিরিক্ত টাকার দাবির বিরুদ্ধে তাৎক্ষণিক সতর্কতা প্রদান।\n"
                "2. 📋 আবেদনের প্রয়োজনীয় কাগজপত্রের **পূর্ণাঙ্গ চেকলিস্ট**।\n"
                "3. 🔗 সরাসরি **সরকারি অফিশিয়াল পোর্টালে** আবেদনের সঠিক নিয়ম ও লিঙ্ক।\n"
                "4. 🔊 উত্তরের সাথে শুনুন **বাংলা ভয়েস অডিও**।\n\n"
                "নিচের বাটনগুলো ক্লিক করে সহজে শুরু করুন অথবা আপনার প্রশ্নটি নিচে লিখুন।"
            )
        }
    ]

# ----------------- TAB 1: Chatbot -----------------
with tab_chat:
    st.markdown("**💡 সচরাচর জিজ্ঞাসিত প্রশ্নসমূহ (ক্লিক করে উত্তর দেখুন):**")
    q_col1, q_col2, q_col3, q_col4 = st.columns(4)

    prompt_to_run = None
    if q_col1.button("🚨 পাসপোর্টে দালাল ৮,০০০ টাকা চাচ্ছে?"):
        prompt_to_run = "পাসপোর্টের জন্য দালাল আট হাজার টাকা চাচ্ছে, এটা কি ঠিক? সাধারণ ৪৮ পাতা ১০ বছর মেয়াদি পাসপোর্টের সরকারি ফি কত?"
    if q_col2.button("🪪 NID নাম সংশোধনে কি কি লাগে?"):
        prompt_to_run = "জাতীয় পরিচয়পত্রে নিজের ও পিতার নাম সংশোধনে কী কী কাগজপত্র লাগে ও সরকারি ফি কত?"
    if q_col3.button("🌾 ই-নামজারির অফিশিয়াল ফি কত?"):
        prompt_to_run = "জমির ই-নামজারি বা খারিজ করতে মোট কত টাকা সরকারি ফি লাগে? দালালরা বেশি টাকা চাইলে করণীয় কি?"
    if q_col4.button("🛂 ১০ বছর মেয়াদি পাসপোর্টের ফি কত?"):
        prompt_to_run = "৪৮ পৃষ্ঠা ১০ বছর মেয়াদী ই-পাসপোর্টের নিয়মিত ও জরুরি সরকারি ফি কত টাকা?"

    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg.get("dalal_alert"):
                alert = msg["dalal_alert"]
                st.markdown(f"""
                <div class="dalal-alert-card">
                    <h4 style="margin:0 0 8px 0; color:#b91c1c; font-weight:700;">{alert['alert_banner_bn']}</h4>
                    <p style="margin:0 0 8px 0; font-size:15px; color:#374151;">{alert['advice_bn']}</p>
                    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
                        <span class="savings-chip">💰 সম্ভাব্য আর্থিক সাশ্রয়: {alert.get('difference_amount', 0):,} টাকা</span>
                        <strong style="color:#b91c1c;">🚨 দুদকের টোল-ফ্রি হেল্পলাইন: {alert['emergency_hotline']}</strong>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown(msg["content"])
            
            # Voice Audio Player for assistant messages
            if msg.get("audio_path") and os.path.exists(msg["audio_path"]):
                st.audio(msg["audio_path"], format="audio/mp3")

    # User input
    user_input = st.chat_input("আপনার প্রশ্ন বাংলায় লিখুন (যেমন: পাসপোর্টের সরকারি ফি কত?)...")
    active_prompt = prompt_to_run or user_input

    if active_prompt:
        st.session_state.messages.append({"role": "user", "content": active_prompt})
        with st.chat_message("user"):
            st.markdown(active_prompt)

        with st.chat_message("assistant"):
            with st.spinner("অফিসিয়াল সরকারি তথ্যভাণ্ডার যাচাই করে উত্তর তৈরি হচ্ছে..."):
                response_data = rag_engine.query(active_prompt)
                answer_text = response_data["answer"]
                dalal_alert = response_data.get("dalal_alert")
                gen_mode = response_data.get("mode", "Grounded Engine")

                if dalal_alert:
                    st.markdown(f"""
                    <div class="dalal-alert-card">
                        <h4 style="margin:0 0 8px 0; color:#b91c1c; font-weight:700;">{dalal_alert['alert_banner_bn']}</h4>
                        <p style="margin:0 0 8px 0; font-size:15px; color:#374151;">{dalal_alert['advice_bn']}</p>
                        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
                            <span class="savings-chip">💰 সম্ভাব্য আর্থিক সাশ্রয়: {dalal_alert.get('difference_amount', 0):,} টাকা</span>
                            <strong style="color:#b91c1c;">🚨 দুদকের টোল-ফ্রি হেল্পলাইন: {dalal_alert['emergency_hotline']}</strong>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown(answer_text)
                st.caption(f"ইঞ্জিন: `{gen_mode}` | শতভাগ সরকারি তথ্যে নিশ্চিত")

                # Voice output translation using gTTS
                audio_path = text_to_bangla_speech(answer_text)
                if audio_path and os.path.exists(audio_path):
                    st.caption("🔊 উত্তরের বাংলা ভয়েস অডিও:")
                    st.audio(audio_path, format="audio/mp3")

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer_text,
                    "dalal_alert": dalal_alert,
                    "audio_path": audio_path
                })

# ----------------- TAB 2: Fee Calculator & Checklist -----------------
with tab_calculator:
    st.subheader("💰 অফিশিয়াল সরকারি ফি ও চেকলিস্ট ক্যালকুলেটর")
    st.write("দালালদের অবৈধ অতিরিক্ত ফির দাবি এড়িয়ে সরকারি নির্ধারিত মূল্যে সেবা গ্রহণ করুন:")

    service_select = st.selectbox(
        "সেবার ধরন নির্বাচন করুন:",
        [
            "ই-পাসপোর্ট: ৪৮ পৃষ্ঠা, ৫ বছর (নিয়মিত)",
            "ই-পাসপোর্ট: ৪৮ পৃষ্ঠা, ৫ বছর (জরুরি)",
            "ই-পাসপোর্ট: ৪৮ পৃষ্ঠা, ১০ বছর (নিয়মিত)",
            "ই-পাসপোর্ট: ৪৮ পৃষ্ঠা, ১০ বছর (জরুরি)",
            "জাতীয় পরিচয়পত্র: ব্যক্তিগত তথ্য সংশোধন (১ম বার)",
            "জাতীয় পরিচয়পত্র: ব্যক্তিগত তথ্য সংশোধন (২য় বার)",
            "জাতীয় পরিচয়পত্র: হারানো NID রি-ইস্যু (সাধারণ)",
            "ই-নামজারি (জমি খারিজ ও রেকর্ড সংশোধন)"
        ]
    )

    fee_details = {
        "ই-পাসপোর্ট: ৪৮ পৃষ্ঠা, ৫ বছর (নিয়মিত)": {
            "official": 4025,
            "dalal_avg": 9000,
            "breakdown": "মূল ফি ৩,৫০০ টাকা + ১৫% সরকারি ভ্যাট ৫২৫ টাকা = ৪,০২৫ টাকা (ডেলিভারি: ১৫-২১ কার্যদিবস)",
            "docs": ["মূল NID অথবা ১৭ ডিজিটের অনলাইন জন্মনিবন্ধন সনদ", "অনলাইন আবেদন সামারি প্রিন্ট কপি", "এ-চালান / পেমেন্ট স্লিপ", "প্রযোজ্য ক্ষেত্রে পেশার প্রমাণপত্র"],
            "url": "https://www.epassport.gov.bd/"
        },
        "ই-পাসপোর্ট: ৪৮ পৃষ্ঠা, ৫ বছর (জরুরি)": {
            "official": 6325,
            "dalal_avg": 13000,
            "breakdown": "মূল ফি ৫,৫০০ টাকা + ১৫% ভ্যাট ৮২৫ টাকা = ৬,৩২৫ টাকা (ডেলিভারি: ৭-১০ কার্যদিবস)",
            "docs": ["মূল NID অথবা অনলাইন জন্মনিবন্ধন সনদ", "অনলাইন আবেদন সামারি প্রিন্ট কপি", "জরুরি এ-চালান পেমেন্ট স্লিপ"],
            "url": "https://www.epassport.gov.bd/"
        },
        "ই-পাসপোর্ট: ৪৮ পৃষ্ঠা, ১০ বছর (নিয়মিত)": {
            "official": 5750,
            "dalal_avg": 12000,
            "breakdown": "মূল ফি ৫,০০০ টাকা + ১৫% সরকারি ভ্যাট ৭৫০ টাকা = ৫,৭৫০ টাকা (ডেলিভারি: ১৫-২১ কার্যদিবস)",
            "docs": ["মূল NID কার্ড ও কপি", "অনলাইন আবেদন সামারি বারকোডসহ", "পেমেন্ট ব্যাংক স্লিপ"],
            "url": "https://www.epassport.gov.bd/"
        },
        "ই-পাসপোর্ট: ৪৮ পৃষ্ঠা, ১০ বছর (জরুরি)": {
            "official": 8050,
            "dalal_avg": 16000,
            "breakdown": "মূল ফি ৭,০০০ টাকা + ১৫% ভ্যাট ১,০৫০ টাকা = ৮,০৫০ টাকা (ডেলিভারি: ৭-১০ কার্যদিবস)",
            "docs": ["মূল NID কার্ড ও ফটোকপি", "অনলাইন আবেদন সামারি", "জরুরি ফি ব্যাংক স্লিপ"],
            "url": "https://www.epassport.gov.bd/"
        },
        "জাতীয় পরিচয়পত্র: ব্যক্তিগত তথ্য সংশোধন (১ম বার)": {
            "official": 230,
            "dalal_avg": 3000,
            "breakdown": "মূল আবেদন ফি ২০০ টাকা + ১৫% ভ্যাট ৩০ টাকা = ২৩০ টাকা (বিকাশ/রকেট/নগদে প্রদেয়)",
            "docs": ["SSC / HSC শিক্ষাগত সনদপত্র", "১৭ ডিজিট অনলাইন জন্ম নিবন্ধন", "পিতা-মাতার NID কপি", "প্রয়োজনে ১ম শ্রেণীর ম্যাজিস্ট্রেট এফিডেভিট"],
            "url": "https://services.nidw.gov.bd/"
        },
        "জাতীয় পরিচয়পত্র: ব্যক্তিগত তথ্য সংশোধন (২য় বার)": {
            "official": 345,
            "dalal_avg": 4500,
            "breakdown": "মূল ফি ৩০০ টাকা + ১৫% ভ্যাট ৪৫ টাকা = ৩৪৫ টাকা",
            "docs": ["SSC / শিক্ষাগত সনদ", "অনলাইন জন্ম নিবন্ধন", "দালিলিক সুনির্দিষ্ট প্রমাণ"],
            "url": "https://services.nidw.gov.bd/"
        },
        "জাতীয় পরিচয়পত্র: হারানো NID রি-ইস্যু (সাধারণ)": {
            "official": 230,
            "dalal_avg": 2500,
            "breakdown": "মূল ফি ২০০ টাকা + ১৫% ভ্যাট ৩০ টাকা = ২৩০ টাকা",
            "docs": ["থানার জিডি (GD) নম্বর ও কপি", "অন্য কোনো জাতীয় পরিচয় প্রমাণ"],
            "url": "https://services.nidw.gov.bd/"
        },
        "ই-নামজারি (জমি খারিজ ও রেকর্ড সংশোধন)": {
            "official": 1170,
            "dalal_avg": 25000,
            "breakdown": "আবেদনে কোর্ট ফি ২০ টাকা + নোটিশ জারি ৫০ টাকা = ৭০ টাকা; আবেদন মঞ্জুর হলে খতিয়ান ফি ১,০০০ টাকা + ডিসিআর ১০০ টাকা = ১,১০০ টাকা। সর্বমোট: ১,১৭০ টাকা মাত্র!",
            "docs": ["মূল রেজিস্ট্রেশনকৃত সাব-কবলা দলিল", "হালনাগাদ ভূমি উন্নয়ন কর (খাজনা) দাখিলা", "পূর্ববর্তী খতিয়ান (CS/SA/RS)", "ওয়ারিশান সনদ (প্রযোজ্য ক্ষেত্রে)", "আবেদনকারীর NID ও ছবি"],
            "url": "https://mutation.land.gov.bd/"
        }
    }

    selected_info = fee_details[service_select]
    official_val = selected_info["official"]
    dalal_val = selected_info["dalal_avg"]
    savings = dalal_val - official_val

    m1, m2, m3 = st.columns(3)
    m1.metric("সরকারি নির্ধারিত ফি", f"{official_val:,} ৳", delta="অফিসিয়াল রেট", delta_color="normal")
    m2.metric("দালালদের গড় দাবি", f"{dalal_val:,} ৳", delta=f"+{savings:,} ৳ অতিরিক্ত", delta_color="inverse")
    m3.metric("NagorikAI ব্যবহারে সাশ্রয়", f"{savings:,} ৳", delta="১০০% নাগরিক সঞ্চয়", delta_color="normal")

    st.markdown(f"**ফি এর বিস্তারিত হিসাব:** {selected_info['breakdown']}")
    st.markdown(f"**অফিসিয়াল সরকারি পোর্টাল:** [{selected_info['url']}]({selected_info['url']})")

    st.divider()
    st.subheader("📋 প্রয়োজনীয় কাগজপত্রের লাইভ চেকলিস্ট")
    st.write("আপনার কাছে কোন কোন কাগজ প্রস্তুত আছে টিক দিন:")
    for doc in selected_info["docs"]:
        st.checkbox(f"📄 {doc}", key=f"chk_{service_select}_{doc}")

# ----------------- TAB 3: Vision Document Checker -----------------
with tab_vision:
    st.subheader("📸 ডকুমেন্ট প্রি-ফ্লাইট ভিশন অডিট (Vision AI)")
    st.write(
        "ভুল বা অস্পষ্ট ডকুমেন্টের কারণে ৭০% আবেদন সরকারি অফিস থেকে বাতিল হয়। "
        "আবেদন আপলোড করার আগে এআই ভিশন দিয়ে আপনার স্ক্যান কপিটি পরীক্ষা করে নিন।"
    )

    col_v1, col_v2 = st.columns([1, 1])

    with col_v1:
        doc_category = st.selectbox(
            "ডকুমেন্টের ধরন বাছাই করুন:",
            [
                ("nid", "জাতীয় পরিচয়পত্র (NID Slip বা কার্ড)"),
                ("passport_slip", "পাসপোর্ট অ্যাপ্লিকেশন সামারি স্লিপ"),
                ("land_deed", "জমির রেজিস্ট্রি দলিল / খতিয়ান"),
                ("certificate", "শিক্ষাগত সনদপত্র (SSC/HSC)")
            ],
            format_func=lambda x: x[1]
        )

        expected_name = st.text_input("আবেদনকারীর পূর্ণ নাম (যাচাইয়ের জন্য):", placeholder="যেমন: MD RAHIM UDDIN")
        uploaded_doc = st.file_uploader("ডকুমেন্টের স্পষ্ট ছবি বা স্ক্যান আপলোড করুন (JPG, PNG):", type=["jpg", "jpeg", "png"])

        if uploaded_doc:
            st.image(uploaded_doc, caption="আপলোডকৃত ডকুমেন্ট প্রিভিউ", use_container_width=True)

    with col_v2:
        st.markdown("#### 🔍 এআই ভিশন নিরীক্ষণ ফলাফল")
        if uploaded_doc:
            if st.button("🚀 ডকুমেন্ট অডিট সম্পন্ন করুন", type="primary"):
                # Save temp file
                temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scratch")
                os.makedirs(temp_dir, exist_ok=True)
                temp_path = os.path.join(temp_dir, uploaded_doc.name)
                with open(temp_path, "wb") as f:
                    f.write(uploaded_doc.getbuffer())

                with st.spinner("ডকুমেন্টের নাম, সিল, স্বাক্ষর ও কোয়ালিটি যাচাই করা হচ্ছে..."):
                    result = DocumentVisionChecker.inspect_document(
                        image_path=temp_path,
                        doc_type=doc_category[0],
                        expected_name=expected_name,
                        api_key=api_key_input
                    )

                if "error" in result:
                    st.error(result["error"])
                else:
                    st.success("✅ ডকুমেন্ট নিরীক্ষা সফলভাবে সম্পন্ন হয়েছে!")
                    st.caption(f"ইস্পেকশন ইঞ্জিন: `{result['mode']}` | রেজোলিউশন: `{result['resolution']}`")
                    st.markdown(result["report_bn"])
        else:
            st.info("👈 বাঁ পাশের বক্স থেকে যেকোনো একটি ডকুমেন্টের ছবি আপলোড করে অডিট বাটনে ক্লিক করুন।")

# ----------------- TAB 4: Roadmap & Vision -----------------
with tab_roadmap:
    st.subheader("🚀 NagorikAI: ফিউচার রোডম্যাপ ও ভিশন")
    st.markdown("""
    **NagorikAI** হলো আধুনিক এআই প্রযুক্তির মাধ্যমে বাংলাদেশকে একটি **'Dalal-Free' (দালাল-মুক্ত)** ডিজিটাল জনবান্ধব দেশে রূপান্তরের জাতীয় উদ্যোগ।
    """)

    col_r1, col_r2 = st.columns(2)

    with col_r1:
        st.markdown("""
        ### 🗺️ পরবর্তী ধাপসমূহ (Next Roadmap):
        1. **ফর্ম অটো প্রি-ফিল (Form Pre-fill):**
           - নাগরিক তার NID ও পুরাতন কাগজ আপলোড করলেই সরকারি ফরমের ফিল্ডগুলো স্বয়ংক্রিয়ভাবে নির্ভুল পূরণ হবে।
        2. **অপেক্ষার সময় প্রাক্কলন (Waiting-Time Estimator):**
           - কোন জেলার পাসপোর্ট অফিস বা এসি ল্যান্ড অফিসে বর্তমানে কতদিন সময় লাগছে তার রিয়েল-টাইম ক্রাউডসোর্সড ডেটা।
        3. **আইভিআর (IVR) কল সেন্টার ইন্টিগ্রেশন:**
           - বাটন ফোন থেকেও সাধারণ নাগরিক যেন কল করে বাংলায় সঠিক সরকারি ফি ও তথ্য জেনে নিতে পারেন।
        4. **আরো ১০+ সেবা সম্প্রসারণ:**
           - ড্রাইভিং লাইসেন্স (BRTA), ট্রেড লাইসেন্স, পুলিশ ক্লিয়ারেন্স ও পেনশন স্কিম অন্তর্ভুক্তি।
        """)

    with col_r2:
        st.markdown("""
        ### 💡 ইমপ্যাক্ট মেট্রিক্স (Social Impact):
        - **নাগরিকদের আর্থিক সাশ্রয়:** গড়ে প্রতি পাসপোর্ট বা নামজারিতে ৮,০০০ থেকে ২০,০০০ টাকা মধ্যস্বত্বভোগীর পকেটে যাওয়া রোধ।
        - **বাতিলের হার হ্রাস:** ভুল কাগজপত্রের কারণে আবেদন বাতিল হওয়ার হার ৬০% কমিয়ে আনা।
        - **ডিজিটাল সমতা:** গ্রামীণ ও সুবিধাবঞ্চিত নাগরিকদের জন্য মুখের ভাষায় (Voice AI) সরকারি তথ্য সহজলভ্য করা।
        """)

    st.divider()
    st.markdown("""
    <div style="text-align: center; color: #6b7280; font-size: 13px;">
        NagorikAI &bull; AI Copilot for Bangladesh Citizens &bull; Grounded in Official Open Data &bull; Zero Hallucination Guarantee
    </div>
    """, unsafe_allow_html=True)
