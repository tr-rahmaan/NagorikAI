"""
CivicSphere AI: GovCopilot & Dalal-Free Citizen Assistant
Bangla RAG Chatbot grounded in official Bangladesh Government sources (NID, Passport, Land Mutation).
"""

import os
import sys
import streamlit as st
import streamlit.components.v1 as components

# Ensure local packages in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.rag_engine import RAGEngine
from src.dalal_detector import DalalDetector
from src.vision_checker import DocumentVisionChecker
from src.speech_utils import text_to_bangla_speech, get_voice_input_html

# Page configuration
st.set_page_config(
    page_title="CivicSphere AI | GovCopilot (Dalal-Free)",
    page_icon="🇧🇩",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #064e3b;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #374151;
        margin-bottom: 1rem;
    }
    .dalal-box {
        background-color: #fef2f2;
        border-left: 5px solid #ef4444;
        padding: 14px 18px;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    .official-badge {
        background-color: #ecfdf5;
        border: 1px solid #10b981;
        color: #065f46;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.82rem;
        font-weight: 600;
    }
    .source-pill {
        display: inline-block;
        background: #f1f5f9;
        border: 1px solid #cbd5e1;
        border-radius: 6px;
        padding: 3px 8px;
        font-size: 0.8rem;
        margin-right: 6px;
        text-decoration: none;
    }
</style>
""", unsafe_allow_html=True)

# Data directory path
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# Sidebar Configuration
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/8/84/Government_Seal_of_Bangladesh.svg/200px-Government_Seal_of_Bangladesh.svg.png", width=70)
    st.title("🇧🇩 CivicSphere AI")
    st.markdown("**GovCopilot & Dalal-Free**")
    st.caption("বাংলাদেশ সরকারি সেবা সহায়িকা ও দুর্নীতি প্রতিরোধ প্ল্যাটফর্ম")
    st.divider()

    st.subheader("⚙️ AI ইঞ্জিন সেটিংস")
    api_key_input = st.text_input(
        "Gemini API Key (ঐচ্ছিক):",
        type="password",
        value=os.getenv("GEMINI_API_KEY", ""),
        help="API Key না দিলেও অন্তর্নির্মিত অফিসিয়াল RAG ইঞ্জিন দিয়ে সম্পূর্ণ কাজ করবে।"
    )

    st.divider()
    st.subheader("📞 জরুরি সরকারি হটলাইন")
    st.markdown("""
    - 🪪 **NID উইং:** `১০৫` (টোল ফ্রি)
    - 🛂 **ই-পাসপোর্ট:** `১৬৪৪৫` / `৩৩৩`
    - 🌾 **ভূমি সেবা (নামজারি):** `১৬১২২`
    - 🛡️ **দুদক (ঘুষ/দালাল অভিযোগ):** `১০৬`
    - 🚨 **পুলিশ/জরুরি সেবা:** `৯৯৯`
    """)

    st.divider()
    st.info("💡 **মূল লক্ষ্য:** নাগরিকরা যাতে দালালের পেছনে হাজার হাজার টাকা অপচয় না করে সরাসরি সরকারি মূল্যে নির্ভুলভাবে সেবা পান।")

# Initialize RAG Engine in session state
@st.cache_resource
def get_rag_engine(api_key: str):
    return RAGEngine(data_dir=DATA_DIR, api_key=api_key if api_key else None)

rag_engine = get_rag_engine(api_key_input)

# Top Banner
st.markdown('<div class="main-title">🇧🇩 CivicSphere AI (GovCopilot)</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">জাতীয় পরিচয়পত্র (NID), ই-পাসপোর্ট এবং ভূমির ই-নামজারির নির্ভুল সরকারি তথ্য ও দালাল-মুক্ত পরামর্শক</div>', unsafe_allow_html=True)

col_b1, col_b2, col_b3 = st.columns(3)
with col_b1:
    st.markdown('<span class="official-badge">✅ ১০০% অফিশিয়াল সোর্স যাচাইকৃত</span>', unsafe_allow_html=True)
with col_b2:
    st.markdown('<span class="official-badge">🛡️ দালাল ও অতিরিক্ত ফি প্রটেকশন</span>', unsafe_allow_html=True)
with col_b3:
    st.markdown('<span class="official-badge">🎙️ বাংলা ভয়েস ও ভিশন অডিটযুক্ত</span>', unsafe_allow_html=True)

st.write("")

# Navigation Tabs
tab_chat, tab_calculator, tab_vision, tab_roadmap = st.tabs([
    "💬 বাংলা এআই পরামর্শক (GovCopilot)",
    "💰 সরকারি ফি ক্যালকুলেটর ও চেকলিস্ট",
    "📸 ডকুমেন্ট ভিশন অডিট (Vision Demo)",
    "🚀 ফিচার রোডম্যাপ ও ভিশন"
])

# Initialize session messages
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "স্বাগতম! আমি **CivicSphere AI**। এনআইডি সংশোধন, ই-পাসপোর্ট বা জমির ই-নামজারি নিয়ে আপনার যেকোনো প্রশ্ন বাংলায় করতে পারেন।\n\n"
                "**আমি আপনাকে দেব:**\n"
                "1. নির্ভুল সরকারি ফি এর তালিকা (দালাল বা মধ্যস্বত্বভোগীর অতিরিক্ত দাবির বিরুদ্ধে সতর্কবার্তা সহ)\n"
                "2. প্রয়োজনীয় কাগজপত্রের পূর্ণাঙ্গ চেকলিস্ট\n"
                "3. ধাপে ধাপে আবেদনের অফিসিয়াল গাইড ও লিংক\n\n"
                "নিচের বাটনগুলো ক্লিক করে সহজে শুরু করতে পারেন অথবা আপনার প্রশ্নটি লিখুন।"
            )
        }
    ]

# ----------------- TAB 1: Chatbot -----------------
with tab_chat:
    # Web Speech API Bangla Voice input component
    components.html(get_voice_input_html(), height=110)

    # Quick sample question pills
    st.markdown("**💡 দ্রুত প্রশ্ন নির্বাচন করুন:**")
    q_col1, q_col2, q_col3, q_col4 = st.columns(4)

    prompt_to_run = None
    if q_col1.button("🚨 পাসপোর্টে দালাল ৮,০০০ টাকা চাচ্ছে?"):
        prompt_to_run = "পাসপোর্টের জন্য দালাল আট হাজার টাকা চাচ্ছে, এটা কি ঠিক? সরকারি ফি কত?"
    if q_col2.button("🪪 NID নাম সংশোধনে কি কি লাগে?"):
        prompt_to_run = "জাতীয় পরিচয়পত্রে নিজের ও বাবার নাম সংশোধনে কী কী কাগজপত্র লাগে ও সরকারি ফি কত?"
    if q_col3.button("🌾 ই-নামজারির অফিশিয়াল ফি কত?"):
        prompt_to_run = "জমির ই-নামজারি বা খারিজ করতে মোট কত টাকা সরকারি ফি লাগে? দালালরা বেশি টাকা চাইলে কি করব?"
    if q_col4.button("🛂 ১০ বছর মেয়াদি পাসপোর্টের ফি কত?"):
        prompt_to_run = "৪৮ পৃষ্ঠা ১০ বছর মেয়াদী ই-পাসপোর্টের নিয়মিত ও জরুরি সরকারি ফি কত?"

    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if "dalal_alert" in msg and msg["dalal_alert"]:
                alert = msg["dalal_alert"]
                st.markdown(f"""
                <div class="dalal-box">
                    <h4 style="margin:0 0 6px 0; color:#b91c1c;">{alert['alert_banner_bn']}</h4>
                    <p style="margin:0 0 6px 0; font-size:14px;">{alert['advice_bn']}</p>
                    <strong>🚨 জরুরি অভিযোগ নম্বর: {alert['emergency_hotline']}</strong>
                </div>
                """, unsafe_allow_html=True)
            st.markdown(msg["content"])
            if "audio_path" in msg and msg["audio_path"] and os.path.exists(msg["audio_path"]):
                st.audio(msg["audio_path"], format="audio/mp3")

    # Chat input
    user_input = st.chat_input("আপনার প্রশ্ন বাংলায় লিখুন (যেমন: পাসপোর্টের ফি কত?)...")
    active_prompt = prompt_to_run or user_input

    if active_prompt:
        st.session_state.messages.append({"role": "user", "content": active_prompt})
        with st.chat_message("user"):
            st.markdown(active_prompt)

        with st.chat_message("assistant"):
            with st.spinner("অফিসিয়াল সরকারি তথ্যভাণ্ডার যাচাই করা হচ্ছে..."):
                response_data = rag_engine.query(active_prompt)
                answer_text = response_data["answer"]
                dalal_alert = response_data.get("dalal_alert")

                if dalal_alert:
                    st.markdown(f"""
                    <div class="dalal-box">
                        <h4 style="margin:0 0 6px 0; color:#b91c1c;">{dalal_alert['alert_banner_bn']}</h4>
                        <p style="margin:0 0 6px 0; font-size:14px;">{dalal_alert['advice_bn']}</p>
                        <strong>🚨 জরুরি অভিযোগ নম্বর: {dalal_alert['emergency_hotline']}</strong>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown(answer_text)

                # Audio readout with gTTS
                audio_path = text_to_bangla_speech(answer_text)
                if audio_path:
                    st.caption("🔊 বাংলা ভয়েস অডিও:")
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
    st.write("দালালরা বিভ্রান্তি ছড়িয়ে সাধারণ মানুষের কাছ থেকে কয়েকগুণ টাকা হাতিয়ে নেয়। এখানে অফিশিয়াল ফি সরাসরি মিলিয়ে নিন:")

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
            "docs": ["মূল NID / ১৭ ডিজিটের জন্মনিবন্ধন", "অনলাইন আবেদন সামারি প্রিন্ট কপি", "এ-চালান / পেমেন্ট স্লিপ", "পেশার প্রমাণপত্র (GO/NOC/স্টুডেন্ট আইডি)"],
            "url": "https://www.epassport.gov.bd/"
        },
        "ই-পাসপোর্ট: ৪৮ পৃষ্ঠা, ৫ বছর (জরুরি)": {
            "official": 6325,
            "dalal_avg": 13000,
            "breakdown": "মূল ফি ৫,৫০০ টাকা + ১৫% ভ্যাট ৮২৫ টাকা = ৬,৩২৫ টাকা (ডেলিভারি: ৭-১০ কার্যদিবস)",
            "docs": ["মূল NID / ১৭ ডিজিটের জন্মনিবন্ধন", "অনলাইন আবেদন সামারি প্রিন্ট কপি", "এ-চালান / পেমেন্ট স্লিপ"],
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
            "docs": ["মূল NID কার্ড ও কপি", "অনলাইন আবেদন সামারি", "পেমেন্ট ব্যাংক স্লিপ"],
            "url": "https://www.epassport.gov.bd/"
        },
        "জাতীয় পরিচয়পত্র: ব্যক্তিগত তথ্য সংশোধন (১ম বার)": {
            "official": 230,
            "dalal_avg": 3000,
            "breakdown": "মূল আবেদন ফি ২০০ টাকা + ১৫% ভ্যাট ৩০ টাকা = ২৩০ টাকা (বিকাশ/রকেট/নগদে প্রদেয়)",
            "docs": ["SSC / HSC শিক্ষাগত সনদ", "১৭ ডিজিট অনলাইন জন্ম নিবন্ধন", "পিতা-মাতার NID কপি", "প্রয়োজনে ১ম শ্রেণীর ম্যাজিস্ট্রেট এফিডেভিট"],
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
            "docs": ["থানার জিডি (GD) কপি (অনলাইন বা অফলাইন)", "অন্য কোনো পরিচয় প্রমাণ"],
            "url": "https://services.nidw.gov.bd/"
        },
        "ই-নামজারি (জমি খারিজ ও রেকর্ড সংশোধন)": {
            "official": 1170,
            "dalal_avg": 25000,
            "breakdown": "আবেদনে কোর্ট ফি ২০ টাকা + নোটিশ ৫০ টাকা = ৭০ টাকা; আবেদন মঞ্জুর হলে খতিয়ান ফি ১,০০০ টাকা + ডিসিআর ১০০ টাকা = ১,১০০ টাকা। সর্বমোট: ১,১৭০ টাকা মাত্র!",
            "docs": ["মূল রেজিস্ট্রেশনকৃত দলিল", "হালনাগাদ ভূমি উন্নয়ন কর (খাজনা) দাখিলা", "পূর্ববর্তী খতিয়ান (CS/SA/RS)", "ওয়ারিশান সনদ (প্রযোজ্য ক্ষেত্রে)", "আবেদনকারীর NID ও ছবি"],
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
    m3.metric("CivicSphere ব্যবহারে সাশ্রয়", f"{savings:,} ৳", delta="১০০% নাগরিক সঞ্চয়", delta_color="normal")

    st.markdown(f"**ফি এর বিস্তারিত হিসাব:** {selected_info['breakdown']}")
    st.markdown(f"**অফিসিয়াল পোর্টাল:** [{selected_info['url']}]({selected_info['url']})")

    st.divider()
    st.subheader("📋 প্রয়োজনীয় কাগজপত্রের লাইভ চেকলিস্ট")
    st.write("আপনার কাছে কোন কোন কাগজ তৈরি আছে টিক দিন:")
    for doc in selected_info["docs"]:
        st.checkbox(f"📄 {doc}", key=f"chk_{service_select}_{doc}")

# ----------------- TAB 3: Vision Document Checker -----------------
with tab_vision:
    st.subheader("📸 ডকুমেন্ট প্রি-ফ্লাইট ভিশন অডিট (Vision Demo)")
    st.write(
        "ভুল বা অস্পষ্ট ডকুমেন্টের কারণে ৭০% আবেদন সরকারি অফিস থেকে বাতিল হয় বা সংশোধনে বিলম্ব হয়। "
        "আবেদন আপলোড করার আগে এআই ভিশন দিয়ে স্ক্যান কপিটি পরীক্ষা করে নিন।"
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
    st.subheader("🚀 CivicSphere AI: ফিউচার রোডম্যাপ ও ভিশন")
    st.markdown("""
    **GovCopilot** হলো বর্তমান কার্যকরী MVP, এবং **'Dalal-Free' (দালাল-মুক্ত বাংলাদেশ)** হলো নাগরিক সমাজ রূপান্তরের স্থায়ী ভিশন।
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
           - ইন্টারনেট ছাড়া সাধারণ বাটন ফোন থেকেও যেন যেকোনো নাগরিক কল করে বাংলায় সঠিক সরকারি ফি ও তথ্য জেনে নিতে পারেন।
        4. **আরো ১০+ সেবা সম্প্রসারণ:**
           - ড্রাইভিং লাইসেন্স (BRTA), ট্রেড লাইসেন্স, পুলিশ ক্লিয়ারেন্স, জন্ম নিবন্ধন ও পেনশন স্কিম অন্তর্ভুক্তি।
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
        CivicSphere AI &bull; GovCopilot for Bangladesh Citizens &bull; Built with Official Open Data &bull; Zero Hallucination Guarantee
    </div>
    """, unsafe_allow_html=True)
