"""
NagorikAI (নাগরিক AI) - GovCopilot & Dalal-Free Citizen Assistant
Human-Friendly, Clean, Modern UI with Natural Bengali Voice Translation.
"""

import os
import sys
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.rag_engine import RAGEngine
from src.dalal_detector import DalalDetector
from src.vision_checker import DocumentVisionChecker
from src.speech_utils import text_to_bangla_speech

# Page Configuration
st.set_page_config(
    page_title="NagorikAI (নাগরিক AI)",
    page_icon="🇧🇩",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Human-Friendly Modern UI Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Hind+Siliguri:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Hind Siliguri', 'Plus Jakarta Sans', sans-serif;
    }

    /* Minimalist Human-Friendly Banner */
    .hero-container {
        background: linear-gradient(135deg, #064e3b 0%, #047857 60%, #0d9488 100%);
        padding: 24px 30px;
        border-radius: 16px;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0 8px 20px -4px rgba(6, 78, 59, 0.2);
    }

    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .hero-tagline {
        font-size: 1.05rem;
        color: #d1fae5;
        margin-top: 6px;
        line-height: 1.4;
    }

    .badge-bar {
        display: flex;
        gap: 10px;
        margin-top: 14px;
        flex-wrap: wrap;
    }

    .badge-pill {
        background: rgba(255, 255, 255, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.35);
        color: #ffffff;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        backdrop-filter: blur(6px);
    }

    /* Soft Alert Box */
    .dalal-alert-card {
        background: #fff1f2;
        border: 1px solid #fecdd3;
        border-left: 5px solid #e11d48;
        padding: 14px 18px;
        border-radius: 10px;
        margin: 12px 0;
    }

    .savings-chip {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #ecfdf5;
        border: 1px solid #a7f3d0;
        color: #047857;
        padding: 3px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.9rem;
    }

    /* Clean Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
LOGO_PATH = os.path.join(ASSETS_DIR, "nagorik_logo.png")

GEMINI_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyDQzW0tny_EjMP-abBEYfqg445xhx-bDzw")

# Clean Sidebar with Local Custom High-Res Logo
with st.sidebar:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=85)
    else:
        st.markdown("<div style='font-size: 48px;'>🇧🇩</div>", unsafe_allow_html=True)
    st.title("NagorikAI")
    st.caption("**নাগরিক সেবা সহায়িকা ও দুর্নীতি প্রতিরোধ**")
    st.divider()

    st.subheader("📞 জরুরি সরকারি হটলাইন")
    st.markdown("""
    - 🪪 **NID উইং:** `১০৫` (টোল-ফ্রি)
    - 🛂 **ই-পাসপোর্ট:** `১৬৪৪৫` / `৩৩৩`
    - 🌾 **ভূমি সেবা (নামজারি):** `১৬১২২`
    - 🛡️ **দুদক (ঘুষ/দালাল অভিযোগ):** `১০৬`
    - 🚨 **পুলিশ/জরুরি সেবা:** `৯৯৯`
    """)

    st.divider()
    st.markdown("""
    <div style="font-size: 13px; color: #475569; line-height: 1.5;">
        💡 <strong>সরাসরি সরকারি সেবা গ্রহণ করুন:</strong> দালালদের অতিরিক্ত টাকা দেওয়া সম্পূর্ণ বেআইনি। যেকোনো সন্দেহ হলে সরাসরি ১০৬ হটলাইনে জানান।
    </div>
    """, unsafe_allow_html=True)

# Initialize RAG Engine
@st.cache_resource
def get_rag_engine():
    return RAGEngine(data_dir=DATA_DIR, api_key=GEMINI_KEY)

rag_engine = get_rag_engine()

# Hero Banner
st.markdown("""
<div class="hero-container">
    <div class="hero-title">🇧🇩 NagorikAI (নাগরিক AI)</div>
    <div class="hero-tagline">
        পাসপোর্ট, এনআইডি (NID) ও ভূমির ই-নামজারির সঠিক সরকারি ফি জানুন ও মধ্যস্বত্বভোগীদের প্রতারণা থেকে সুরক্ষিত থাকুন।
    </div>
    <div class="badge-bar">
        <span class="badge-pill">✅ ১০০% অফিশিয়াল তথ্যে যাচাইকৃত</span>
        <span class="badge-pill">🛡️ দালাল-মুক্ত সুরক্ষা ও সঞ্চয় মেট্রিক্স</span>
        <span class="badge-pill">🔊 সহজ বাংলা ভয়েস অডিও অনুবাদ</span>
    </div>
</div>
""", unsafe_allow_html=True)

# 4 Essential Tabs
tab_chat, tab_calculator, tab_vision, tab_roadmap = st.tabs([
    "💬 বাংলা এআই পরামর্শক",
    "💰 সরকারি ফি ক্যালকুলেটর ও চেকলিস্ট",
    "📸 ডকুমেন্ট ভিশন অডিট (Vision AI)",
    "🚀 ফিচার রোডম্যাপ ও ভিশন"
])

# Initialize chat session
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "স্বাগতম! আমি **NagorikAI**।\n\n"
                "এনআইডি সংশোধন, নতুন পাসপোর্ট কিংবা জমির নামজারি—যে কোনো বিষয়ে সরাসরি বাংলায় প্রশ্ন করুন। আমি আপনাকে সঠিক সরকারি ফি এবং প্রয়োজনীয় কাগজের তালিকা জানিয়ে দেব।"
            )
        }
    ]

# ----------------- TAB 1: Chatbot -----------------
with tab_chat:
    st.markdown("<p style='font-weight:600; font-size:14px; margin-bottom:8px;'>💡 সরাসরি জানতে বাটনগুলোতে চাপ দিন:</p>", unsafe_allow_html=True)
    q_col1, q_col2, q_col3, q_col4 = st.columns(4)

    prompt_to_run = None
    if q_col1.button("🚨 দালাল ৮,০০০ টাকা চাচ্ছে?"):
        prompt_to_run = "পাসপোর্টের জন্য দালাল আট হাজার টাকা চাচ্ছে। এটা কি ঠিক? সরকারি ফি কত?"
    if q_col2.button("🪪 NID নাম সংশোধনে কি লাগে?"):
        prompt_to_run = "জাতীয় পরিচয়পত্রে নাম সংশোধনে কী কী কাগজপত্র লাগে ও সরকারি ফি কত?"
    if q_col3.button("🌾 ই-নামজারির সরকারি ফি কত?"):
        prompt_to_run = "জমির ই-নামজারি খারিজ করতে মোট কত টাকা সরকারি ফি লাগে?"
    if q_col4.button("🛂 ১০ বছর মেয়াদি পাসপোর্টের ফি?"):
        prompt_to_run = "৪৮ পৃষ্ঠা ১০ বছর মেয়াদী ই-পাসপোর্টের নিয়মিত ও জরুরি সরকারি ফি কত?"

    # Display chat conversation
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg.get("dalal_alert"):
                alert = msg["dalal_alert"]
                st.markdown(f"""
                <div class="dalal-alert-card">
                    <strong style="color:#b91c1c; font-size:15px;">⚠️ {alert['alert_banner_bn']}</strong>
                    <p style="margin:6px 0; font-size:14px; color:#334151;">{alert['advice_bn']}</p>
                    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; margin-top:4px;">
                        <span class="savings-chip">💰 আপনি বাঁচাতে পারেন: {alert.get('difference_amount', 0):,} টাকা</span>
                        <span style="font-weight:700; color:#b91c1c; font-size:13px;">🚨 অভিযোগ: ১০৬ (দুদক)</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown(msg["content"])

            if msg.get("audio_path") and os.path.exists(msg["audio_path"]):
                st.audio(msg["audio_path"], format="audio/mp3")

    # User Input
    user_input = st.chat_input("আপনার প্রশ্নটি বাংলায় লিখুন (যেমন: পাসপোর্টের ফি কত?)...")
    active_prompt = prompt_to_run or user_input

    if active_prompt:
        st.session_state.messages.append({"role": "user", "content": active_prompt})
        with st.chat_message("user"):
            st.markdown(active_prompt)

        with st.chat_message("assistant"):
            with st.spinner("উত্তর তৈরি হচ্ছে..."):
                response_data = rag_engine.query(active_prompt)
                answer_text = response_data.get("answer", "")
                if not answer_text:
                    answer_text = "দুঃখিত, কোনো তথ্য পাওয়া যায়নি। অনুগ্রহ করে সরকারি হেল্পলাইন ১০৫, ১৬৪৪৫ বা ১৬১২২ এ যোগাযোগ করুন।"

                dalal_alert = response_data.get("dalal_alert")

                if dalal_alert:
                    st.markdown(f"""
                    <div class="dalal-alert-card">
                        <strong style="color:#b91c1c; font-size:15px;">⚠️ {dalal_alert['alert_banner_bn']}</strong>
                        <p style="margin:6px 0; font-size:14px; color:#334151;">{dalal_alert['advice_bn']}</p>
                        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; margin-top:4px;">
                            <span class="savings-chip">💰 আপনি বাঁচাতে পারেন: {dalal_alert.get('difference_amount', 0):,} টাকা</span>
                            <span style="font-weight:700; color:#b91c1c; font-size:13px;">🚨 অভিযোগ: ১০৬ (দুদক)</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown(answer_text)

                # Voice output translation
                audio_path = text_to_bangla_speech(answer_text)
                if audio_path and os.path.exists(audio_path):
                    st.caption("🔊 শুনুন (বাংলা অডিও):")
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
    st.write("যে কোনো সেবার ওপর ক্লিক করে সরকারি ফি এবং দালালদের চেয়ে কত টাকা সাশ্রয় হচ্ছে তা এক নজরে দেখে নিন:")

    service_select = st.selectbox(
        "সেবা নির্বাচন করুন:",
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
            "breakdown": "মূল ফি ৩,৫০০ টাকা + ১৫% ভ্যাট ৫২৫ টাকা = ৪,০২৫ টাকা (ডেলিভারি: ১৫-২১ কার্যদিবস)",
            "docs": ["মূল NID অথবা অনলাইন জন্মনিবন্ধন সনদ", "অনলাইন আবেদন সামারি প্রিন্ট কপি", "পেমেন্ট স্লিপ / চালান"],
            "url": "https://www.epassport.gov.bd/"
        },
        "ই-পাসপোর্ট: ৪৮ পৃষ্ঠা, ৫ বছর (জরুরি)": {
            "official": 6325,
            "dalal_avg": 13000,
            "breakdown": "মূল ফি ৫,৫০০ টাকা + ১৫% ভ্যাট ৮২৫ টাকা = ৬,৩২৫ টাকা (ডেলিভারি: ৭-১০ কার্যদিবস)",
            "docs": ["মূল NID বা জন্মনিবন্ধন সনদ", "আবেদন সামারি", "জরুরি পেমেন্ট চালান"],
            "url": "https://www.epassport.gov.bd/"
        },
        "ই-পাসপোর্ট: ৪৮ পৃষ্ঠা, ১০ বছর (নিয়মিত)": {
            "official": 5750,
            "dalal_avg": 12000,
            "breakdown": "মূল ফি ৫,০০০ টাকা + ১৫% ভ্যাট ৭৫০ টাকা = ৫,৭৫০ টাকা (ডেলিভারি: ১৫-২১ কার্যদিবস)",
            "docs": ["মূল NID কার্ড ও কপি", "অনলাইন আবেদন সামারি", "পেমেন্ট চালান কপি"],
            "url": "https://www.epassport.gov.bd/"
        },
        "ই-পাসপোর্ট: ৪৮ পৃষ্ঠা, ১০ বছর (জরুরি)": {
            "official": 8050,
            "dalal_avg": 16000,
            "breakdown": "মূল ফি ৭,০০০ টাকা + ১৫% ভ্যাট ১,০৫০ টাকা = ৮,০৫০ টাকা (ডেলিভারি: ৭-১০ কার্যদিবস)",
            "docs": ["মূল NID কার্ড ও ফটোকপি", "অনলাইন আবেদন সামারি", "জরুরি চালান"],
            "url": "https://www.epassport.gov.bd/"
        },
        "জাতীয় পরিচয়পত্র: তথ্য সংশোধন (১ম বার)": {
            "official": 230,
            "dalal_avg": 3000,
            "breakdown": "মূল ফি ২০০ টাকা + ১৫% ভ্যাট ৩০ টাকা = ২৩০ টাকা (বিকাশ/রকেট/নগদে প্রদেয়)",
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
            "breakdown": "কোর্ট ফি ২০ টাকা + নোটিশ ৫০ টাকা + খতিয়ান ফি ১,০০০ টাকা + ডিসিআর ১০০ টাকা = সর্বমোট ১,১৭০ টাকা মাত্র!",
            "docs": ["মূল সাব-কবলা দলিল", "হালনাগাদ ভূমি কর (খাজনা) দাখিলা", "পূর্ববর্তী খতিয়ান (CS/SA/RS)", "আবেদনকারীর NID ও ছবি"],
            "url": "https://mutation.land.gov.bd/"
        }
    }

    selected = fee_details[service_select]
    official_fee = selected["official"]
    dalal_fee = selected["dalal_avg"]
    savings = dalal_fee - official_fee

    m1, m2, m3 = st.columns(3)
    m1.metric("সরকারি নির্ধারিত ফি", f"{official_fee:,} ৳", delta="অফিসিয়াল", delta_color="normal")
    m2.metric("দালালদের গড় দাবি", f"{dalal_fee:,} ৳", delta=f"+{savings:,} ৳ অতিরিক্ত", delta_color="inverse")
    m3.metric("NagorikAI ব্যবহারে সাশ্রয়", f"{savings:,} ৳", delta="আপনার সঞ্চয়", delta_color="normal")

    st.markdown(f"**ফি এর স্পষ্ট হিসাব:** {selected['breakdown']}")
    st.markdown(f"**অফিসিয়াল পোর্টাল:** [{selected['url']}]({selected['url']})")

    st.divider()
    st.subheader("📋 প্রয়োজনীয় কাগজপত্রের চেকলিস্ট")
    for doc in selected["docs"]:
        st.checkbox(f"📄 {doc}", key=f"c_{service_select}_{doc}")

# ----------------- TAB 3: Vision Document Checker -----------------
with tab_vision:
    st.subheader("📸 ডকুমেন্ট প্রি-ফ্লাইট ভিশন অডিট (Vision AI)")
    st.write(
        "কাগজপত্র অস্পষ্ট বা স্বাক্ষর বাদ পড়লে আবেদন বাতিল হতে পারে। "
        "সরকারি অফিসে জমা দেওয়ার আগে আপনার স্ক্যান কপিটি এআই দিয়ে পরীক্ষা করে নিন।"
    )

    col_v1, col_v2 = st.columns([1, 1])

    with col_v1:
        doc_category = st.selectbox(
            "ডকুমেন্টের ধরন:",
            [
                ("nid", "জাতীয় পরিচয়পত্র (NID Slip বা কার্ড)"),
                ("passport_slip", "পাসপোর্ট অ্যাপ্লিকেশন সামারি স্লিপ"),
                ("land_deed", "জমির রেজিস্ট্রি দলিল / খতিয়ান"),
                ("certificate", "শিক্ষাগত সনদপত্র (SSC/HSC)")
            ],
            format_func=lambda x: x[1]
        )

        expected_name = st.text_input("আবেদনকারীর পূর্ণ নাম (ঐচ্ছিক):", placeholder="যেমন: MD RAHIM UDDIN")
        uploaded_doc = st.file_uploader("ডকুমেন্টের ছবি বা স্ক্যান আপলোড করুন (JPG, PNG):", type=["jpg", "jpeg", "png"])

        if uploaded_doc:
            st.image(uploaded_doc, caption="আপলোডকৃত ডকুমেন্ট", use_container_width=True)

    with col_v2:
        st.markdown("#### 🔍 অডিট রিপোর্ট")
        if uploaded_doc:
            if st.button("🚀 ডকুমেন্ট অডিট করুন", type="primary"):
                temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scratch")
                os.makedirs(temp_dir, exist_ok=True)
                temp_path = os.path.join(temp_dir, uploaded_doc.name)
                with open(temp_path, "wb") as f:
                    f.write(uploaded_doc.getbuffer())

                with st.spinner("ডকুমেন্ট নিরীক্ষা করা হচ্ছে..."):
                    result = DocumentVisionChecker.inspect_document(
                        image_path=temp_path,
                        doc_type=doc_category[0],
                        expected_name=expected_name,
                        api_key=GEMINI_KEY
                    )

                if "error" in result:
                    st.error(result["error"])
                else:
                    st.success("✅ নিরীক্ষা সম্পন্ন হয়েছে!")
                    st.markdown(result["report_bn"])
        else:
            st.info("👈 একটি ছবি আপলোড করে 'ডকুমেন্ট অডিট করুন' বাটনে ক্লিক করুন।")

# ----------------- TAB 4: Roadmap & Vision -----------------
with tab_roadmap:
    st.subheader("🚀 NagorikAI: ফিউচার রোডম্যাপ")
    st.markdown("""
    **NagorikAI**-এর লক্ষ্য সমগ্র বাংলাদেশকে একটি দালাল-মুক্ত, হয়রানিমুক্ত ও সহজ নাগরিক সেবার ডিজিটাল প্ল্যাটফর্মে রূপান্তর করা।
    """)

    col_r1, col_r2 = st.columns(2)

    with col_r1:
        st.markdown("""
        ### 🗺️ পরবর্তী ধাপসমূহ:
        1. **ফর্ম অটো প্রি-ফিল:** NID ছবি থেকে স্বয়ংক্রিয়ভাবে সরকারি ফর্ম পূরণ।
        2. **অপেক্ষার সময় প্রাক্কলন:** বিভিন্ন অফিসে আবেদনের রিয়েল-টাইম সময় প্রাক্কলন।
        3. **আইভিআর (IVR) কল সেন্টার:** বাটন ফোন থেকেও বাংলায় কল করে সেবা তথ্য জানা।
        4. **আরো ১০+ সেবা সম্প্রসারণ:** বিআরটিএ ড্রাইভিং লাইসেন্স ও পুলিশ ক্লিয়ারেন্স অন্তর্ভুক্তি।
        """)

    with col_r2:
        st.markdown("""
        ### 💡 সামাজিক প্রভাব:
        - **নাগরিকদের আর্থিক সাশ্রয়:** গড়ে প্রতি সেবায় ৮,০০০ থেকে ২০,০০০ টাকা অপচয় রোধ।
        - **বাতিলের হার হ্রাস:** ভুল কাগজপত্রের কারণে আবেদন বাতিল হওয়ার হার ৬০% কমানো।
        - **ডিজিটাল সমতা:** গ্রামীণ ও সুবিধাবঞ্চিত নাগরিকদের জন্য মুখের ভাষায় সহজ সেবা।
        """)

    st.divider()
    st.markdown("""
    <div style="text-align: center; color: #64748b; font-size: 13px;">
        NagorikAI &bull; AI Copilot for Bangladesh Citizens &bull; Grounded in Official Open Data
    </div>
    """, unsafe_allow_html=True)
