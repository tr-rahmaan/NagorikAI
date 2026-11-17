"""
CivicSphere (নাগরিক সেবা ও তথ্য পোর্টাল)
Official Citizen Public Service Assistant & Anti-Corruption Guidance Platform.
Production-ready, accessible, institutional design with verified Government data.
"""

import os
import sys
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.rag_engine import RAGEngine
from src.dalal_detector import DalalDetector
from src.vision_checker import DocumentVisionChecker
from src.speech_utils import text_to_bangla_speech

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(_BASE_DIR, "assets", "nagorik_logo.png")
DATA_DIR = os.path.join(_BASE_DIR, "data")

# Page Configuration
st.set_page_config(
    page_title="CivicSphere | নাগরিক সেবা ও তথ্য পোর্টাল",
    page_icon=LOGO_PATH if os.path.exists(LOGO_PATH) else "🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Formal, Institutional Public Service Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Hind+Siliguri:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"], div, span, p {
        font-family: 'Hind Siliguri', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }

    /* Page background — force white throughout */
    .stApp, .main, section.main, [data-testid="stAppViewContainer"],
    [data-testid="stMain"], .block-container {
        background-color: #ffffff !important;
    }

    /* Sidebar — light grey background */
    [data-testid="stSidebar"], [data-testid="stSidebarContent"] {
        background-color: #f8fafc !important;
        border-right: 1px solid #e2e8f0;
    }

    /* Government Institutional Header Banner */
    .gov-masthead {
        background: linear-gradient(135deg, #f0fdf4 0%, #ffffff 100%);
        border: 1px solid #d1fae5;
        border-left: 5px solid #006a4e;
        border-radius: 10px;
        padding: 22px 28px;
        margin-bottom: 24px;
        box-shadow: 0 1px 4px rgba(0, 106, 78, 0.08);
    }

    .gov-topline {
        font-size: 0.85rem;
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        color: #64748b;
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 6px;
    }

    .gov-badge-official {
        background: #006a4e;
        color: #ffffff;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 700;
    }

    .gov-title {
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
        color: #0f172a;
        letter-spacing: -0.02em;
    }

    .gov-subtitle {
        font-size: 1rem;
        color: #374151;
        margin-top: 6px;
        line-height: 1.5;
        max-width: 900px;
    }

    .gov-pills-row {
        display: flex;
        gap: 10px;
        margin-top: 14px;
        flex-wrap: wrap;
    }

    .gov-pill {
        background: #f1f5f9;
        border: 1px solid #e2e8f0;
        color: #374151;
        padding: 4px 12px;
        border-radius: 6px;
        font-size: 0.82rem;
        font-weight: 500;
    }

    /* Formal Middlemen / Fraud Warning Alert */
    .formal-alert-card {
        background: #fef2f2;
        border: 1px solid #fecaca;
        border-left: 4px solid #b91c1c;
        padding: 16px 20px;
        border-radius: 8px;
        margin: 16px 0;
    }

    .formal-alert-title {
        color: #991b1b;
        font-size: 0.95rem;
        font-weight: 700;
        margin-bottom: 6px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .formal-alert-body {
        font-size: 0.9rem;
        color: #334155;
        line-height: 1.5;
        margin-bottom: 8px;
    }

    .formal-alert-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        border-top: 1px dashed #fca5a5;
        padding-top: 8px;
        margin-top: 8px;
        font-size: 0.85rem;
    }

    .savings-pill {
        background: #ecfdf5;
        border: 1px solid #a7f3d0;
        color: #065f46;
        padding: 2px 10px;
        border-radius: 4px;
        font-weight: 700;
    }

    .hotline-pill {
        color: #991b1b;
        font-weight: 700;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        border-bottom: 1px solid #e2e8f0;
        margin-bottom: 18px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 6px 6px 0 0;
        padding: 10px 18px;
        font-weight: 600;
        color: #475569;
        font-size: 0.95rem;
    }

    .stTabs [aria-selected="true"] {
        background-color: transparent !important;
        color: #006a4e !important;
        border-bottom: 2px solid #006a4e !important;
    }

    /* Clean Card Layouts */
    .stat-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        padding: 16px;
        border-radius: 8px;
        margin-bottom: 12px;
    }

    /* Quick question pill buttons */
    .quick-query-label {
        font-size: 0.85rem;
        font-weight: 600;
        color: #475569;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }
</style>
""", unsafe_allow_html=True)

# Secret embedded API Key (checks Streamlit Secrets, environment variable, or fallback)
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyDQzW0tny_EjMP-abBEYfqg445xhx-bDzw")
try:
    if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
        GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass

# Initialize RAG Engine
@st.cache_resource
def get_rag_engine():
    return RAGEngine(data_dir=DATA_DIR, api_key=GEMINI_KEY)

rag_engine = get_rag_engine()

# Sidebar: Official Public Information & Emergency Contacts
with st.sidebar:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=75)
    st.markdown("### **NagorikAI**")
    st.caption("গণপ্রজাতন্ত্রী বাংলাদেশ — জাতীয় নাগরিক সেবা পোর্টাল")
    st.markdown("---")

    st.markdown("**জরুরি সরকারি হেল্পলাইন ডেস্ক**")
    st.markdown("""
    - **জাতীয় পরিচয়পত্র (NID):** `১০৫` (টোল-ফ্রি)
    - **ই-পাসপোর্ট সেবা:** `১৬৪৪৫` / `৩৩৩`
    - **ভূমিসেবায় নামজারি:** `১৬১২২`
    - **দুদক (দুর্নীতি ও দালাল দমন):** `১০৬`
    - **জাতীয় জরুরি সেবা:** `৯৯৯`
    """)

    st.markdown("---")
    st.markdown("""
    **আইনি সতর্কতা:**
    সরকারি সেবায় কোনো দালাল বা মধ্যস্বত্বভোগী নিয়োগের প্রয়োজন নেই। অতিরিক্ত অর্থ প্রদান বা দাবি করা দুর্নীতি দমন আইন অনুসারে দণ্ডনীয় অপরাধ।
    """)

    st.markdown("---")
    enable_voice = st.checkbox("বাংলা অডিও অনুবাদ সক্রিয় রাখুন", value=True)

    if st.button("কথোপকথন মুছে ফেলুন (Reset Chat)", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pending_prompt = None
        st.rerun()

# Institutional Masthead Header
st.markdown("""
<div class="gov-masthead">
    <div class="gov-topline">
        <span class="gov-badge-official">গণপ্রজাতন্ত্রী বাংলাদেশ</span>
        জাতীয় ডিজিটাল সেবা তথ্যকোষ ও সহায়তা প্ল্যাটফর্ম
    </div>
    <h1 class="gov-title">নাগরিক সেবা ও তথ্য পোর্টাল </h1>
    <div class="gov-subtitle">
        ই-পাসপোর্ট, জাতীয় পরিচয়পত্র (NID) এবং ভূমির ই-নামজারির সঠিক সরকারি ফি, প্রয়োজনীয় নথিপত্র এবং দালাল-মুক্ত সেবা নির্দেশিকা।
    </div>
    <div class="gov-pills-row">
        <span class="gov-pill">যাচাইকৃত উন্মুক্ত সরকারি তথ্যভাণ্ডার</span>
        <span class="gov-pill">মধ্যস্বত্বভোগী ও অতিরিক্ত ফি প্রতিরোধ</span>
        <span class="gov-pill">টোল-ফ্রি সরকারি হেল্পলাইন সংযুক্ত</span>
    </div>
</div>
""", unsafe_allow_html=True)

# 4 Core Public Service Tabs
tab_chat, tab_calculator, tab_vision, tab_directory = st.tabs([
    "নাগরিক সেবা পরামর্শক (Service Assistant)",
    "সরকারি ফি ও নথিপত্র নির্দেশিকা (Fees & Checklist)",
    "আবেদন নথি প্রাক-যাচাইকরণ (Document Verification)",
    "সরকারি পোর্টাল ও হটলাইন ডিরেক্টরি (Directory & Helplines)"
])

# Initialize chat session
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "স্বাগতম। আমি **NagorikAI** নাগরিক তথ্য সহায়িকা।\n\n"
                "ই-পাসপোর্ট, জাতীয় পরিচয়পত্র (NID) সংশোধন বা রি-ইস্যু এবং ভূমির ই-নামজারি সংক্রান্ত যেকোনো বিষয়ে সরাসরি প্রশ্ন করুন। "
                "আমি আপনাকে সঠিক সরকারি ফি, প্রয়োজনীয় কাগজপত্রের তালিকা এবং দাপ্তরিক নিয়মাবলী জানাতে প্রস্তুত।"
            )
        }
    ]

if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None

# ----------------- TAB 1: Chatbot -----------------
with tab_chat:
    st.markdown("<div class='quick-query-label'>সচরাচর জিজ্ঞাসিত প্রশ্নসমূহ (ক্লিক করে সরাসরি জানুন):</div>", unsafe_allow_html=True)
    q_col1, q_col2, q_col3, q_col4 = st.columns(4)

    if q_col1.button("পাসপোর্টে দালাল অতিরিক্ত ফি দাবি করলে?", use_container_width=True):
        st.session_state.pending_prompt = "পাসপোর্টের জন্য দালাল আট হাজার টাকা চাচ্ছে। এটা কি ঠিক? সরকারি ফি কত?"
        st.rerun()

    if q_col2.button("NID নাম সংশোধনে কী কী নথি লাগে?", use_container_width=True):
        st.session_state.pending_prompt = "জাতীয় পরিচয়পত্রে নাম সংশোধনে কী কী কাগজপত্র লাগে ও সরকারি ফি কত?"
        st.rerun()

    if q_col3.button("জমির ই-নামজারির মোট সরকারি ফি কত?", use_container_width=True):
        st.session_state.pending_prompt = "জমির ই-নামজারি খারিজ করতে মোট কত টাকা সরকারি ফি লাগে?"
        st.rerun()

    if q_col4.button("পাসপোর্ট হারিয়ে গেলে কী করণীয়?", use_container_width=True):
        st.session_state.pending_prompt = "আমার পাসপোর্ট হারিয়ে গেছে, নতুন পাসপোর্ট পেতে করণীয় কি?"
        st.rerun()

    # Auto-scroll chat to the latest message
    import streamlit.components.v1 as _components
    _components.html("""
<script>
(function() {
    function scrollToBottom() {
        var parent = window.parent.document;
        var msgs = parent.querySelectorAll('[data-testid="stChatMessage"]');
        if (msgs && msgs.length > 0) {
            msgs[msgs.length - 1].scrollIntoView({ behavior: 'smooth', block: 'end' });
        }
    }
    setTimeout(scrollToBottom, 150);
    setTimeout(scrollToBottom, 600);
})();
</script>
""", height=0)

    # Display chat conversation history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg.get("dalal_alert"):
                alert = msg["dalal_alert"]
                st.markdown(f"""
                <div class="formal-alert-card">
                    <div class="formal-alert-title">
                        {alert.get('alert_banner_bn', 'সরকারি সতর্কতা')}
                    </div>
                    <div class="formal-alert-body">
                        {alert.get('advice_bn', '')}
                    </div>
                    <div class="formal-alert-footer">
                        <span class="savings-pill">সম্ভাব্য নাগরিক সাশ্রয়: {alert.get('difference_amount', 0):,} টাকা</span>
                        <span class="hotline-pill">অভিযোগ জানান: ১০৬ (দুদক) | ৯৯৯ (বাংলাদেশ পুলিশ)</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown(msg["content"])

            if msg.get("audio_path") and os.path.exists(msg["audio_path"]):
                st.caption("অডিও শুনুন (বাংলা ভয়েস):")
                with open(msg["audio_path"], "rb") as _af:
                    st.audio(_af.read(), format="audio/mp3")

    # Handle active prompt (either from pending prompt button click or chat_input)
    user_input = st.chat_input("আপনার প্রশ্নটি বাংলায় লিখুন (যেমন: পাসপোর্টের ফি কত? NID হারালে কি করবো?)...")
    active_prompt = st.session_state.pending_prompt or user_input

    if active_prompt:
        st.session_state.pending_prompt = None

        # Fetch response before rendering anything
        with st.spinner("সরকারি তথ্যভাণ্ডার যাচাই করা হচ্ছে..."):
            response_data = rag_engine.query(active_prompt)
            answer_text = response_data["answer"]
            dalal_alert = response_data.get("dalal_alert")

            # Optional audio generation
            audio_path = None
            if enable_voice:
                try:
                    audio_path = text_to_bangla_speech(answer_text)
                except Exception:
                    audio_path = None

        # Append both messages to session state
        st.session_state.messages.append({"role": "user", "content": active_prompt})
        st.session_state.messages.append({
            "role": "assistant",
            "content": answer_text,
            "dalal_alert": dalal_alert,
            "audio_path": audio_path
        })

        # Rerun so all messages render through the loop above the input box
        st.rerun()

# ----------------- TAB 2: Fee Calculator & Checklist -----------------
with tab_calculator:
    st.subheader("সরকারি ফি ও প্রয়োজনীয় নথিপত্র নির্দেশিকা")
    st.write("যে কোনো নাগরিক সেবা নির্বাচন করে নির্ধারিত সরকারি ফি এবং প্রয়োজনীয় নথির আনুষ্ঠানিক তালিকা যাচাই করুন:")

    service_select = st.selectbox(
        "নাগরিক সেবা নির্বাচন করুন:",
        [
            "ই-পাসপোর্ট: ৪৮ পৃষ্ঠা, ৫ বছর (নিয়মিত)",
            "ই-পাসপোর্ট: ৪৮ পৃষ্ঠা, ৫ বছর (জরুরি)",
            "ই-পাসপোর্ট: ৪৮ পৃষ্ঠা, ১০ বছর (নিয়মিত)",
            "ই-পাসপোর্ট: ৪৮ পৃষ্ঠা, ১০ বছর (জরুরি)",
            "জাতীয় পরিচয়পত্র: তথ্য সংশোধন (১ম বার)",
            "জাতীয় পরিচয়পত্র: তথ্য সংশোধন (২য় বার)",
            "জাতীয় পরিচয়পত্র: হারানো NID রি-ইস্যু",
            "ই-নামজারি (জমি খারিজ ও রেকর্ড সংশোধন)"
        ]
    )

    fee_details = {
        "ই-পাসপোর্ট: ৪৮ পৃষ্ঠা, ৫ বছর (নিয়মিত)": {
            "official": 4025,
            "dalal_avg": 9000,
            "breakdown": "মূল ফি ৩,৫০০ টাকা + ১৫% সরকারি ভ্যাট ৫২৫ টাকা = সর্বমোট ৪,০২৫ টাকা (ডেলিভারি: ১৫-২১ কার্যদিবস)",
            "docs": ["মূল NID অথবা অনলাইন জন্মনিবন্ধন সনদ", "অনলাইন আবেদন সামারি প্রিন্ট কপি", "পেমেন্ট স্লিপ / এ-চালান"],
            "url": "https://www.epassport.gov.bd/"
        },
        "ই-পাসপোর্ট: ৪৮ পৃষ্ঠা, ৫ বছর (জরুরি)": {
            "official": 6325,
            "dalal_avg": 13000,
            "breakdown": "মূল ফি ৫,৫০০ টাকা + ১৫% সরকারি ভ্যাট ৮২৫ টাকা = সর্বমোট ৬,৩২৫ টাকা (ডেলিভারি: ৭-১০ কার্যদিবস)",
            "docs": ["মূল NID বা অনলাইন জন্মনিবন্ধন সনদ", "আবেদন সামারি", "জরুরি পেমেন্ট চালান"],
            "url": "https://www.epassport.gov.bd/"
        },
        "ই-পাসপোর্ট: ৪৮ পৃষ্ঠা, ১০ বছর (নিয়মিত)": {
            "official": 5750,
            "dalal_avg": 12000,
            "breakdown": "মূল ফি ৫,০০০ টাকা + ১৫% সরকারি ভ্যাট ৭৫০ টাকা = সর্বমোট ৫,৭৫০ টাকা (ডেলিভারি: ১৫-২১ কার্যদিবস)",
            "docs": ["মূল NID কার্ড ও কপি", "অনলাইন আবেদন সামারি", "পেমেন্ট চালান কপি"],
            "url": "https://www.epassport.gov.bd/"
        },
        "ই-পাসপোর্ট: ৪৮ পৃষ্ঠা, ১০ বছর (জরুরি)": {
            "official": 8050,
            "dalal_avg": 16000,
            "breakdown": "মূল ফি ৭,০০০ টাকা + ১৫% সরকারি ভ্যাট ১,০৫০ টাকা = সর্বমোট ৮,০৫০ টাকা (ডেলিভারি: ৭-১০ কার্যদিবস)",
            "docs": ["মূল NID কার্ড ও ফটোকপি", "অনলাইন আবেদন সামারি", "জরুরি চালান"],
            "url": "https://www.epassport.gov.bd/"
        },
        "জাতীয় পরিচয়পত্র: তথ্য সংশোধন (১ম বার)": {
            "official": 230,
            "dalal_avg": 3000,
            "breakdown": "মূল ফি ২০০ টাকা + ১৫% ভ্যাট ৩০ টাকা = ২৩০ টাকা (বিকাশ/রকেট/নগদে সরকারি ট্রেজারিতে প্রদেয়)",
            "docs": ["SSC / HSC শিক্ষাগত সনদ", "অনলাইন জন্ম নিবন্ধন", "পিতা-মাতার NID কপি"],
            "url": "https://services.nidw.gov.bd/"
        },
        "জাতীয় পরিচয়পত্র: তথ্য সংশোধন (২য় বার)": {
            "official": 345,
            "dalal_avg": 4500,
            "breakdown": "মূল ফি ৩০০ টাকা + ১৫% ভ্যাট ৪৫ টাকা = ৩৪৫ টাকা",
            "docs": ["শিক্ষাগত সনদ", "অনলাইন জন্ম নিবন্ধন", "দালিলিক সুনির্দিষ্ট প্রমাণ"],
            "url": "https://services.nidw.gov.bd/"
        },
        "জাতীয় পরিচয়পত্র: হারানো NID রি-ইস্যু": {
            "official": 230,
            "dalal_avg": 2500,
            "breakdown": "মূল ফি ২০০ টাকা + ভ্যাট ৩০ টাকা = ২৩০ টাকা",
            "docs": ["থানার অনলাইন জিডি (GD) কপি", "অন্য কোনো জাতীয় পরিচয় প্রমাণ"],
            "url": "https://services.nidw.gov.bd/"
        },
        "ই-নামজারি (জমি খারিজ ও রেকর্ড সংশোধন)": {
            "official": 1170,
            "dalal_avg": 25000,
            "breakdown": "আবেদনে কোর্ট ফি ২০ টাকা + নোটিশ ৫০ টাকা এবং মঞ্জুরের পর খতিয়ান ফি ১,০০০ টাকা + ডিসিআর ১০০ টাকা = সর্বমোট ১,১৭০ টাকা মাত্র",
            "docs": ["মূল সাব-কবলা দলিল", "হালনাগাদ ভূমি কর (খাজনা) দাখিলা", "পূর্ববর্তী খতিয়ান (CS/SA/RS)", "আবেদনকারীর NID ও ছবি"],
            "url": "https://mutation.land.gov.bd/"
        }
    }

    selected = fee_details[service_select]
    official_fee = selected["official"]
    dalal_fee = selected["dalal_avg"]
    savings = dalal_fee - official_fee

    m1, m2, m3 = st.columns(3)
    m1.metric("সরকারি নির্ধারিত ফি", f"{official_fee:,} ৳", delta="বিধিবদ্ধ ফি", delta_color="normal")
    m2.metric("দালালদের গড় অননুমোদিত দাবি", f"{dalal_fee:,} ৳", delta=f"+{savings:,} ৳ অতিরিক্ত", delta_color="inverse")
    m3.metric("নাগরিক সাশ্রয়", f"{savings:,} ৳", delta="অর্থ অপচয় রোধ", delta_color="normal")

    st.markdown(f"**ফি বিবরণ:** {selected['breakdown']}")
    st.markdown(f"**অফিশিয়াল পোর্টাল লিংক:** [{selected['url']}]({selected['url']})")

    st.divider()
    st.subheader("প্রয়োজনীয় কাগজপত্রের চেকলিস্ট")
    st.caption("আবেদন দাখিলের পূর্বে প্রয়োজনীয় নথিসমূহ প্রস্তুত রয়েছে কিনা যাচাই করে নিন:")
    for doc in selected["docs"]:
        st.checkbox(doc, key=f"c_{service_select}_{doc}")

# ----------------- TAB 3: Vision Document Checker -----------------
with tab_vision:
    st.subheader("আবেদন নথি প্রাক-যাচাইকরণ (Document Verification Pre-Audit)")
    st.write(
        "সরকারি অফিসে নথিপত্র দাখিলের পূর্বে স্ক্যান কপির স্পষ্টতা ও প্রয়োজনীয় তথ্য প্রস্তুত আছে কিনা তা স্বয়ংক্রিয়ভাবে পরীক্ষা করে নিন।"
    )

    col_v1, col_v2 = st.columns([1, 1])

    with col_v1:
        doc_category = st.selectbox(
            "নথির ধরন নির্বাচন করুন:",
            [
                ("nid", "জাতীয় পরিচয়পত্র (NID কার্ড বা স্লিপ)"),
                ("passport_slip", "পাসপোর্ট অ্যাপ্লিকেশন সামারি স্লিপ"),
                ("land_deed", "জমির রেজিস্ট্রি দলিল / খতিয়ান"),
                ("certificate", "শিক্ষাগত সনদপত্র (SSC / HSC)")
            ],
            format_func=lambda x: x[1]
        )

        expected_name = st.text_input("আবেদনকারীর পূর্ণ নাম (ঐচ্ছিক):", placeholder="যেমন: MD RAHIM UDDIN")
        uploaded_doc = st.file_uploader("নথির স্পষ্ট স্ক্যান বা ছবি সংযুক্ত করুন (JPG, PNG):", type=["jpg", "jpeg", "png"])

        if uploaded_doc:
            st.image(uploaded_doc, caption="সংযুক্তকৃত নথি", use_container_width=True)

    with col_v2:
        st.markdown("#### নিরীক্ষা ও যাচাই প্রতিবেদন")
        if uploaded_doc:
            if st.button("নথি নিরীক্ষা করুন", type="primary", use_container_width=True):
                temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scratch")
                os.makedirs(temp_dir, exist_ok=True)
                temp_path = os.path.join(temp_dir, uploaded_doc.name)
                with open(temp_path, "wb") as f:
                    f.write(uploaded_doc.getbuffer())

                with st.spinner("নথি নিরীক্ষা করা হচ্ছে..."):
                    result = DocumentVisionChecker.inspect_document(
                        image_path=temp_path,
                        doc_type=doc_category[0],
                        expected_name=expected_name,
                        api_key=GEMINI_KEY
                    )

                if "error" in result:
                    st.error(result["error"])
                else:
                    st.success("নিরীক্ষা সফলভাবে সম্পন্ন হয়েছে।")
                    st.markdown(result["report_bn"])
        else:
            st.info("একটি স্ক্যান কপি সংযুক্ত করে 'নথি নিরীক্ষা করুন' বোতামে চাপ দিন।")

# ----------------- TAB 4: Official Directory & Helplines -----------------
with tab_directory:
    st.subheader("সরকারি পোর্টাল ও জরুরি হেল্পলাইন ডিরেক্টরি")
    st.write("সকল নাগরিক সেবা কেবলমাত্র সরকার নির্ধারিত অফিসিয়াল ওয়েবসাইটে সম্পন্ন করুন:")

    col_d1, col_d2 = st.columns(2)

    with col_d1:
        st.markdown("""
        #### অফিসিয়াল সরকারি পোর্টালসমূহ:
        1. **ই-পাসপোর্ট অনলাইন পোর্টাল:**
           - ওয়েবসাইট: [epassport.gov.bd](https://www.epassport.gov.bd/)
           - কার্যক্রম: নতুন পাসপোর্ট আবেদন, নবায়ন, ট্র্যাকিং ও অ্যাপয়েন্টমেন্ট
        2. **জাতীয় পরিচয়পত্র (NID) উইং:**
           - ওয়েবসাইট: [services.nidw.gov.bd](https://services.nidw.gov.bd/)
           - কার্যক্রম: নাম সংশোধন, রি-ইস্যু, ভোটার তথ্য হালনাগাদ
        3. **জাতীয় ভূমি সেবা (ই-নামজারি):**
           - ওয়েবসাইট: [mutation.land.gov.bd](https://mutation.land.gov.bd/)
           - কার্যক্রম: নামজারি, জমাভাগ, অনলাইন ডিসিআর ও খাজনা প্রদান
        4. **অনলাইন জিডি পোর্টাল:**
           - ওয়েবসাইট: [gd.police.gov.bd](https://gd.police.gov.bd/)
           - কার্যক্রম: পাসপোর্ট বা এনআইডি হারানোর সাধারণ ডায়েরি
        """)

    with col_d2:
        st.markdown("""
        #### জরুরি সরকারি কল সেন্টার ও সহায়তা ডেস্ক:
        - **দুদক (দুর্নীতি দমন কমিশন):** হটলাইন `১০৬` (দালাল বা ঘুষ দাবির ক্ষেত্রে)
        - **জাতীয় তথ্য ও সেবা বাতায়ন:** হটলাইন `৩৩৩` (টোল-ফ্রি ২৪/৭)
        - **জাতীয় জরুরি সেবা:** হটলাইন `৯৯৯` (পুলিশ, ফায়ার সার্ভিস, অ্যাম্বুলেন্স)
        - **ই-পাসপোর্ট হেল্পডেস্ক:** হটলাইন `১৬৪৪৫`
        - **ভূমিসেবায় কল সেন্টার:** হটলাইন `১৬১২২` (সার্বক্ষণিক খোলা)
        - **নির্বাচন কমিশন এনআইডি ডেস্ক:** হটলাইন `১০৫`
        """)

    st.divider()
    st.markdown("""
    <div style="font-size: 13px; color: #64748b; line-height: 1.6;">
        <strong>বিধিবদ্ধ সতর্কবার্তা:</strong> কোনো সরকারি কর্মচারীর পক্ষ থেকে নির্ধারিত ফি ব্যতিরেকে অতিরিক্ত অর্থ দাবি করা আইনত দণ্ডনীয়। যেকোনো অনিয়ম পরিলক্ষিত হলে হটলাইন ১০৬ নম্বরে অবহিত করুন।
    </div>
    """, unsafe_allow_html=True)

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #64748b; font-size: 13px; padding: 12px 0;">
    NagorikAI &bull; গণপ্রজাতন্ত্রী বাংলাদেশ সরকারের অফিশিয়াল তথ্যের ভিত্তিতে পরিচালিত নাগরিক সেবা প্ল্যাটফর্ম &bull; সর্বস্বত্ব সংরক্ষিত
</div>
""", unsafe_allow_html=True)
