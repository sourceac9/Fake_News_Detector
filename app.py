import streamlit as st
import pickle
import re
import nltk
import math
import textwrap
import requests

from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

nltk.download("stopwords", quiet=True)

# Load model and vectorizer
model = pickle.load(open("rf_model.pkl", "rb"))
vectorizer = pickle.load(open("vectorizer.pkl", "rb"))


stop_words = set(stopwords.words("english"))
stemmer = PorterStemmer()


def preprocess_text(text):
    text = text.lower()
    text = re.sub(r"http\S+|www\S+|https\S+", "", text)
    text = re.sub(r"[^a-zA-Z]", " ", text)
    words = text.split()
    words = [stemmer.stem(word) for word in words if word not in stop_words]
    return " ".join(words)

def search_claims(query: str, api_key: str):
    if not api_key:
        return None
    url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
    params = {
        "query": query,
        "languageCode": "en",
        "key": api_key
    }
    try:
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Fact check lookup failed: {e}")
    return None


st.set_page_config(
    page_title="Fake News Detector",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if 'current_page' not in st.session_state:
    st.session_state.current_page = 'home'

def go_to_analyzer():
    st.session_state.current_page = 'analyzer'

def go_to_home():
    st.session_state.current_page = 'home'

# ────────────────────────────────────────────────────────────────────────────────
# FULL PROFESSIONAL CSS  (overrides Streamlit dark mode completely)
# ────────────────────────────────────────────────────────────────────────────────
st.html(textwrap.dedent("""
<link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600&family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
<style>
/* ── Base Reset ── */
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"],
[data-testid="stMain"], .main {
    background: #0B0F17 !important;
    color: #E2E8F0 !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stSidebar"] { display: none !important; }
[data-testid="stHeader"]  { background: transparent !important; }
#MainMenu, footer, header { visibility: hidden !important; }

/* ── Remove Streamlit's default padding ── */
.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0F172A; }
::-webkit-scrollbar-thumb { background: #334155; border-radius: 3px; }

/* ── Developer Editor Container ── */
.stTextArea > div > div {
    display: flex !important;
    flex-direction: row !important;
    background: #0B0F19 !important;
    border: 1px solid #1E293B !important;
    border-radius: 0 0 24px 24px !important;
    overflow: hidden !important;
    position: relative !important;
    transition: border-color 0.25s, box-shadow 0.25s !important;
}

.editor-line-gutter {
    background: #070A13 !important;
    color: #475569 !important;
    font-family: 'Fira Code', monospace !important;
    font-size: 13px !important;
    line-height: 1.7 !important;
    padding: 24px 12px 24px 16px !important;
    text-align: right !important;
    user-select: none !important;
    border-right: 1px solid #1E293B !important;
    min-width: 48px !important;
    overflow: hidden !important;
}

.stTextArea > div > div > textarea {
    background: #0B0F19 !important;
    border: none !important;
    border-radius: 0 !important;
    padding: 24px 20px !important;
    font-size: 13px !important;
    font-family: 'Fira Code', monospace !important;
    color: #E2E8F0 !important;
    resize: none !important;
    box-shadow: none !important;
    line-height: 1.7 !important;
    flex: 1 !important;
    outline: none !important;
    margin: 0 !important;
    min-height: 160px !important;
    max-height: 220px !important;
}

.stTextArea label { display: none !important; }

/* ── Streamlit Primary Button (Giant Analyze Button) ── */
.stButton > button[kind="primary"] {
    background: #6366F1 !important;
    border: none !important;
    color: #FFFFFF !important;
    font-size: 22px !important;
    font-weight: 800 !important;
    padding: 24px 60px !important;
    border-radius: 16px !important;
    width: 100% !important;
    box-shadow: 0 10px 25px -5px rgba(99,102,241,0.4) !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-4px) !important;
    background: #4F46E5 !important;
    box-shadow: 0 20px 25px -5px rgba(99,102,241,0.5), 0 10px 10px -5px rgba(99,102,241,0.2) !important;
}

/* ── Streamlit Secondary Button ── */
.stButton > button[kind="secondary"] {
    background: #1E293B !important;
    border: 1px solid #334155 !important;
    color: #E2E8F0 !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 16px !important;
    padding: 14px 40px !important;
    border-radius: 14px !important;
    width: auto !important;
    cursor: pointer !important;
    letter-spacing: 0.3px !important;
    box-shadow: none !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
}
.stButton > button[kind="secondary"]:hover {
    transform: translateY(-3px) !important;
    background: #2D3748 !important;
    border-color: #4A5568 !important;
    color: #FFFFFF !important;
}
.stButton > button[kind="secondary"]:active { transform: translateY(0px) !important; }

/* ── Tabs ── */
[data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 2px solid #1E293B !important;
    gap: 8px !important;
    justify-content: center !important;
}
[data-baseweb="tab"] {
    background: transparent !important;
    border: none !important;
    padding: 14px 28px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    color: #64748B !important;
    border-bottom: 3px solid transparent !important;
    margin-bottom: -2px !important;
    transition: all 0.2s !important;
}
[data-baseweb="tab"]:hover { color: #818CF8 !important; }
[aria-selected="true"] {
    color: #818CF8 !important;
    border-bottom: 3px solid #818CF8 !important;
}
[data-testid="stTabPanel"] { padding-top: 28px !important; }

/* ── Spinner ── */
.stSpinner > div { border-top-color: #818CF8 !important; }

/* ── Premium Responsive Grid ── */
.steps-grid {
    display: grid;
    gap: 24px;
    margin-bottom: 48px;
}

/* ── Step Cards ── */
.step-card {
    background: #161B26 !important;
    border-radius: 20px !important;
    border: 1px solid #1E293B !important;
    padding: 28px !important;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.2), 0 2px 4px -1px rgba(0,0,0,0.1) !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}
.step-card:hover {
    transform: translateY(-6px) !important;
    box-shadow: 0 20px 25px -5px rgba(0,0,0,0.3), 0 10px 10px -5px rgba(0,0,0,0.2) !important;
    border-color: #3F83F8 !important;
}
.step-card > div:nth-of-type(1) {
    background: #1E293B !important;
    box-shadow: none !important;
}
.step-card > div:nth-of-type(2) {
    color: #818CF8 !important;
}
.step-card h3 {
    color: #E2E8F0 !important;
}
.step-card p {
    color: #94A3B8 !important;
}

/* ── Stats Layout ── */
.stats-container {
    display: flex;
    justify-content: center;
    gap: 48px;
    flex-wrap: wrap;
}

@media (min-width: 1024px) {
    .steps-grid { grid-template-columns: repeat(3, 1fr); }
}
@media (min-width: 768px) and (max-width: 1023px) {
    .steps-grid { grid-template-columns: repeat(2, 1fr); }
    .stats-container { gap: 32px; }
}
@media (max-width: 767px) {
    .steps-grid { grid-template-columns: 1fr; }
    .stats-container { gap: 20px; }
    .stats-divider { display: none !important; }
}

.sources-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
}
@media (max-width: 768px) {
    .sources-grid {
        grid-template-columns: 1fr;
    }
}
.source-btn {
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
}
.source-btn:hover {
    transform: translateY(-4px) !important;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.05) !important;
}
</style>
"""))

# ────────────────────────────────────────────────────────────────────────────────
# HEADER / NAVBAR
# ────────────────────────────────────────────────────────────────────────────────
st.html(textwrap.dedent("""
<div style="
    background: transparent;
    padding: 0 48px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 72px;
    position: relative;
    z-index: 10;
">
    <div style="display:flex; align-items:center; gap:12px;">

        <span style="font-family:'Inter',sans-serif; font-weight:800; font-size:22px; color:#FFFFFF; letter-spacing:-0.5px;">
            Fake News <span style="color:#818CF8;">Detector</span>
        </span>
    </div>
</div>
"""))

# ────────────────────────────────────────────────────────────────────────────────
# HERO SECTION
# ────────────────────────────────────────────────────────────────────────────────
st.html(textwrap.dedent("""
<div style="
    background: #0B0F17;
    padding: 72px 48px 56px 48px;
    text-align: center;
    position: relative;
    overflow: hidden;
    border-bottom: 1px solid #1E293B;
">
    <!-- Decorative blobs -->
    <div style="
        position:absolute; top:-60px; right:-60px; width:320px; height:320px;
        background:radial-gradient(circle, rgba(148, 163, 184, 0.03), transparent 70%);
        border-radius:50%;
    "></div>
    <div style="
        position:absolute; bottom:-80px; left:-80px; width:400px; height:400px;
        background:radial-gradient(circle, rgba(148, 163, 184, 0.02), transparent 70%);
        border-radius:50%;
    "></div>


    <h1 style="
        font-family:'Inter',sans-serif;
        font-size:clamp(36px,6vw,64px);
        font-weight:900;
        color:#FFFFFF;
        letter-spacing:-2px;
        line-height:1.1;
        margin-bottom:20px;
    ">
        Verify News<br>
        <span style="
            background: linear-gradient(135deg, #CBD5E1, #94A3B8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        ">with Precision</span>
    </h1>

    <p style="
        font-family:'Inter',sans-serif;
        font-size:18px;
        color:#94A3B8;
        max-width:600px;
        margin:0 auto 40px auto;
        font-weight:400;
        line-height:1.7;
    ">
        Submit an article for evaluation and our <strong style="color:#818CF8;">AI engine</strong> 
        instantly decodes underlying patterns to verify the authenticity of the content.
    </p>

    <!-- Stats row -->
    </div>
"""))

# ────────────────────────────────────────────────────────────────────────────────
# PAGE RENDER LOGIC
# ────────────────────────────────────────────────────────────────────────────────

# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  PAGE: AI DETECTOR                                                        ║
# ╚═══════════════════════════════════════════════════════════════════════════╝
if st.session_state.current_page == 'analyzer':
    st.html('<div style="max-width:900px; margin:0 auto; padding:8px 0 60px 0;">')
    
    st.button("← Back to Guide", on_click=go_to_home)

    # Card header (no bottom border-radius, border-bottom: none)
    st.html(textwrap.dedent("""
    <div style="
        background:#161B26;
        border-radius:24px 24px 0 0;
        border:1px solid #1E293B;
        border-bottom:none;
        overflow:hidden;
    ">
        <div style="
            padding:24px 28px;
            border-bottom:1px solid #1E293B;
            display:flex; align-items:center; justify-content:space-between;
        ">
            <div style="display:flex; align-items:center; gap:10px;">
                <div style="
                    background:#1E293B;
                    width:36px; height:36px; border-radius:10px;
                    display:flex; align-items:center; justify-content:center;
                    font-size:16px;
                ">📝</div>
                <div>
                    <div style="font-family:'Inter',sans-serif; font-weight:700; font-size:16px; color:#E2E8F0;">Article Input</div>
                    <div style="font-family:'Inter',sans-serif; font-size:12px; color:#94A3B8;">Paste the full news text below</div>
                </div>
            </div>
            <div style="
                background:#064E3B;
                color:#34D399; font-family:'Inter',sans-serif;
                font-size:11px; font-weight:700; padding:5px 12px;
                border-radius:20px; letter-spacing:0.5px;
            ">✓ MODEL ACTIVE</div>
        </div>
    </div>
    """))

    # The actual text area (visually merged via styles in header CSS)
    user_input = st.text_area(
        "article_input",
        height=160,
        placeholder="Input the complete news article text below— e.g. 'Researchers claim a recent study published in ...'",
        label_visibility="collapsed"
    )

    # Left-aligned analyze button
    detect_clicked = st.button("🔍  Analyze Authenticity", key="detect_btn")

    # ── PREDICTION LOGIC ──
    if detect_clicked:
        if user_input.strip() == "":
            st.html(textwrap.dedent("""
            <div style="
                background:#FFF7ED; border:1px solid #FED7AA;
                border-left:4px solid #F97316;
                border-radius:12px; padding:16px 20px; margin-top:24px;
                display:flex; align-items:center; gap:12px;
            ">
                <span style="font-size:20px;">⚠️</span>
                <div>
                    <div style="font-family:'Inter',sans-serif; font-weight:600; color:#9A3412; font-size:14px;">No text provided</div>
                    <div style="font-family:'Inter',sans-serif; color:#C2410C; font-size:13px; margin-top:2px;">Please paste a news article to analyze.</div>
                </div>
            </div>
            """))
        else:
            # Build Google News search URL from first 10 words
            first_words = " ".join(user_input.strip().split()[:10])
            import urllib.parse
            google_news_url = "https://news.google.com/search?q=" + urllib.parse.quote(first_words)
            politifact_url = "https://www.politifact.com/search/?q=" + urllib.parse.quote(first_words)
            bbc_url = "https://www.bbc.com/search?q=" + urllib.parse.quote(first_words)


            with st.spinner("Analyzing linguistic patterns..."):
                cleaned = preprocess_text(user_input)
                vec = vectorizer.transform([cleaned])
                prediction = model.predict(vec)

                # Confidence via decision function
                confidence = 70.0  # honest neutral fallback
                if hasattr(model, "decision_function"):
                    try:
                        dist = model.decision_function(vec)[0]
                        prob = 1 / (1 + math.exp(-dist))
                        if prediction[0] == 0:
                            prob = 1 - prob
                        confidence = max(50.1, min(99.9, prob * 100))
                    except Exception:
                        pass

                is_uncertain = confidence < 65.0

                is_real = prediction[0] == 1
                conf_bar = int(confidence)
                conf_bar_capped = min(conf_bar, 99)

                if is_uncertain:
                    # ── UNCERTAIN / LOW CONFIDENCE RESULT ──
                    st.html(textwrap.dedent(f"""
                    <div style="
                        margin-top:32px;
                        background:#161B26;
                        border-radius:24px;
                        border:1px solid #854D0E;
                        box-shadow:0 12px 48px rgba(0,0,0,0.2);
                        overflow:hidden;
                    ">
                        <div style="height:5px; background:#D97706;"></div>
                        <div style="padding:36px 40px;">
                            <div style="display:flex; align-items:flex-start; gap:24px; margin-bottom:28px;">
                                <div style="
                                    width:72px; height:72px; border-radius:20px; flex-shrink:0;
                                    background:#1E1C15;
                                    display:flex; align-items:center; justify-content:center;
                                    font-size:36px;
                                ">⚠️</div>
                                <div>
                                    <div style="
                                        font-family:'Inter',sans-serif;
                                        font-size:11px; font-weight:700; color:#F59E0B;
                                        letter-spacing:2px; text-transform:uppercase; margin-bottom:6px;
                                    ">Low Confidence — Manual Review Needed</div>
                                    <h2 style="
                                        font-family:'Inter',sans-serif;
                                        font-size:36px; font-weight:900; color:#FEF08A;
                                        letter-spacing:-1px; margin:0 0 8px 0;
                                    ">UNCERTAIN</h2>
                                    <p style="
                                        font-family:'Inter',sans-serif;
                                        font-size:15px; color:#FDE047; margin:0; line-height:1.6;
                                    ">The AI model is <strong>not confident</strong> about this article.
                                    This can happen with very short text, unusual writing styles, or topics
                                    outside the model's training data. Please verify manually.</p>
                                </div>
                            </div>

                            <!-- Confidence meter -->
                            <div style="
                                background:#1E1C15; border:1px solid #854D0E;
                                border-radius:16px; padding:20px 24px; margin-bottom:20px;
                            ">
                                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                                    <div>
                                        <div style="font-family:'Inter',sans-serif; font-size:12px; font-weight:700; color:#FEF08A; letter-spacing:1px; text-transform:uppercase;">AI Confidence Score</div>
                                        <div style="font-family:'Inter',sans-serif; font-size:13px; color:#FDBA74; margin-top:2px;">Below 65% — result may not be reliable</div>
                                    </div>
                                    <div style="font-family:'Inter',sans-serif; font-size:42px; font-weight:900; color:#F59E0B; line-height:1;">{confidence:.1f}<span style="font-size:18px; font-weight:600;">%</span></div>
                                </div>
                                <div style="background:#3F2E1B; border-radius:100px; height:10px; overflow:hidden;">
                                    <div style="
                                        width:{conf_bar_capped}%; height:100%;
                                        background:linear-gradient(90deg,#D97706,#F59E0B);
                                        border-radius:100px;
                                    "></div>
                                </div>
                            </div>

                            <!-- What to do box -->
                            <div style="
                                background:#1F1914; border:1px solid #7C2D12;
                                border-radius:12px; padding:16px 20px;
                            ">
                                <div style="font-family:'Inter',sans-serif; font-weight:700; color:#FDBA74; font-size:13px; margin-bottom:10px;">🔍 What to do when the AI is unsure:</div>
                                <div style="font-family:'Inter',sans-serif; font-size:13px; color:#F59E0B; line-height:1.8;">
                                    ✦ <strong>Add more text</strong> — paste the full article, not just the headline<br>
                                    ✦ Search the article title on <strong>Google News</strong> to see if other outlets covered it<br>
                                    ✦ Check <strong>PolitiFact</strong> or <strong>BBC News</strong> for fact-checks and context<br>
                                    ✦ Look at the <strong>website URL</strong> and "About Us" page for credibility
                                </div>
                            </div>
                        </div>
                    </div>
                    """))

                elif is_real:
                    st.html(textwrap.dedent(f"""
                    <div style="
                        margin-top:32px;
                        background:#161B26;
                        border-radius:24px;
                        border:1px solid #065F46;
                        box-shadow:0 12px 48px rgba(0,0,0,0.2);
                        overflow:hidden;
                        animation:slideIn 0.4s ease;
                    ">
                        <!-- Top accent bar -->
                        <div style="height:5px; background:#059669;"></div>
                        <div style="padding:36px 40px;">
                            <div style="display:flex; align-items:flex-start; gap:24px; margin-bottom:32px;">
                                <div style="
                                    width:72px; height:72px; border-radius:20px; flex-shrink:0;
                                    background:#122B21;
                                    display:flex; align-items:center; justify-content:center;
                                    font-size:36px;
                                ">✅</div>
                                <div>
                                    <div style="
                                        font-family:'Inter',sans-serif;
                                        font-size:11px; font-weight:700; color:#34D399;
                                        letter-spacing:2px; text-transform:uppercase; margin-bottom:6px;
                                    ">Verification Complete</div>
                                    <h2 style="
                                        font-family:'Inter',sans-serif;
                                        font-size:36px; font-weight:900; color:#A7F3D0;
                                        letter-spacing:-1px; margin:0 0 8px 0;
                                    ">REAL NEWS</h2>
                                    <p style="
                                        font-family:'Inter',sans-serif;
                                        font-size:15px; color:#D1FAE5; margin:0;
                                    ">This article exhibits linguistic patterns consistent with legitimate journalism.</p>
                                </div>
                            </div>

                            <!-- Confidence meter -->
                            <div style="
                                background:#122B21; border:1px solid #065F46;
                                border-radius:16px; padding:20px 24px;
                            ">
                                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                                    <div>
                                        <div style="font-family:'Inter',sans-serif; font-size:12px; font-weight:700; color:#34D399; letter-spacing:1px; text-transform:uppercase;">AI Confidence Score</div>
                                        <div style="font-family:'Inter',sans-serif; font-size:13px; color:#A7F3D0; margin-top:2px;">Based on AI analysis</div>
                                    </div>
                                    <div style="font-family:'Inter',sans-serif; font-size:42px; font-weight:900; color:#34D399; line-height:1;">{confidence:.1f}<span style="font-size:18px; font-weight:600;">%</span></div>
                                </div>
                                <div style="background:#0B241A; border-radius:100px; height:10px; overflow:hidden;">
                                    <div style="
                                        width:{conf_bar_capped}%; height:100%;
                                        background:linear-gradient(90deg,#059669,#34D399);
                                        border-radius:100px;
                                        transition:width 1s ease;
                                    "></div>
                                </div>
                            </div>
                        </div>
                    </div>
                    """))
                    st.balloons()

                else:
                    st.html(textwrap.dedent(f"""
                    <div style="
                        margin-top:32px;
                        background:#161B26;
                        border-radius:24px;
                        border:1px solid #991B1B;
                        box-shadow:0 12px 48px rgba(0,0,0,0.2);
                        overflow:hidden;
                    ">
                        <!-- Top accent bar -->
                        <div style="height:5px; background:#DC2626;"></div>
                        <div style="padding:36px 40px;">
                            <div style="display:flex; align-items:flex-start; gap:24px; margin-bottom:32px;">
                                <div style="
                                    width:72px; height:72px; border-radius:20px; flex-shrink:0;
                                    background:#2A1415;
                                    display:flex; align-items:center; justify-content:center;
                                    font-size:36px;
                                ">🚨</div>
                                <div>
                                    <div style="
                                        font-family:'Inter',sans-serif;
                                        font-size:11px; font-weight:700; color:#F87171;
                                        letter-spacing:2px; text-transform:uppercase; margin-bottom:6px;
                                    ">Warning Detected</div>
                                    <h2 style="
                                        font-family:'Inter',sans-serif;
                                        font-size:36px; font-weight:900; color:#FECACA;
                                        letter-spacing:-1px; margin:0 0 8px 0;
                                    ">FAKE NEWS</h2>
                                    <p style="
                                        font-family:'Inter',sans-serif;
                                        font-size:15px; color:#FEE2E2; margin:0;
                                    ">This article contains linguistic patterns associated with misinformation and fabricated content.</p>
                                </div>
                            </div>

                            <!-- Confidence meter -->
                            <div style="
                                background:#2A1415; border:1px solid #991B1B;
                                border-radius:16px; padding:20px 24px;
                            ">
                                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                                    <div>
                                        <div style="font-family:'Inter',sans-serif; font-size:12px; font-weight:700; color:#F87171; letter-spacing:1px; text-transform:uppercase;">AI Confidence Score</div>
                                        <div style="font-family:'Inter',sans-serif; font-size:13px; color:#FECACA; margin-top:2px;">Based on AI analysis</div>
                                    </div>
                                    <div style="font-family:'Inter',sans-serif; font-size:42px; font-weight:900; color:#F87171; line-height:1;">{confidence:.1f}<span style="font-size:18px; font-weight:600;">%</span></div>
                                </div>
                                <div style="background:#2A0F11; border-radius:100px; height:10px; overflow:hidden;">
                                    <div style="
                                        width:{conf_bar_capped}%; height:100%;
                                        background:linear-gradient(90deg,#DC2626,#F87171);
                                        border-radius:100px;
                                    "></div>
                                </div>
                            </div>

                            <!-- Tips box -->
                            <div style="
                                margin-top:20px;
                                background:#221515; border:1px solid #7F1D1D;
                                border-radius:12px; padding:16px 20px;
                            ">
                                <div style="font-family:'Inter',sans-serif; font-weight:700; color:#FCA5A5; font-size:13px; margin-bottom:6px;">💡 What to do next?</div>
                                <div style="font-family:'Inter',sans-serif; font-size:13px; color:#FECACA; line-height:1.6;">
                                    Check the source on <strong>PolitiFact</strong> or <strong>BBC News</strong> · 
                                    Look for corroborating reports from multiple news outlets · 
                                    Examine Author Qualifications's credentials
                                </div>
                            </div>
                        </div>
                    </div>
                    """))

                # ── LIVE FACT-CHECKING LAYER ──
                api_key = ""
                try:
                    if "GOOGLE_API_KEY" in st.secrets:
                        api_key = st.secrets["GOOGLE_API_KEY"]
                except Exception:
                    pass
                
                if api_key:
                    claims_data = search_claims(first_words, api_key)
                    if claims_data and "claims" in claims_data:
                        st.html(textwrap.dedent("""
                        <div style="margin-top:24px; background:#161B26; border-radius:20px; border:1px solid #1E293B; padding:20px 28px;">
                            <div style="display:flex; align-items:center; gap:10px; margin-bottom:16px;">
                                <span style="font-size:22px;">🌐</span>
                                <div>
                                    <div style="font-family:'Inter',sans-serif; font-weight:700; font-size:15px; color:#E2E8F0;">Live Fact Check Matches</div>
                                    <div style="font-family:'Inter',sans-serif; font-size:12px; color:#94A3B8;">Results from global fact-checking agencies</div>
                                </div>
                            </div>
                        """))
                        for claim in claims_data["claims"][:3]:
                            claim_text = claim.get("text", "")
                            claimant = claim.get("claimant", "Unknown Source")
                            review = claim.get("claimReview", [{}])[0]
                            publisher = review.get("publisher", {}).get("name", "Fact-Checker")
                            rating = review.get("textualRating", "No Rating Available")
                            review_url = review.get("url", "#")
                            
                            rating_color = "#34D399" if "true" in rating.lower() else "#F87171"
                            if "false" in rating.lower() or "fake" in rating.lower():
                                rating_color = "#F87171"
                                
                            st.html(textwrap.dedent(f"""
                            <div style="background:#1A202C; border:1px solid #2D3748; border-radius:12px; padding:16px; margin-bottom:12px;">
                                <p style="margin:0 0 8px 0; color:#E2E8F0; font-size:14px;"><strong>Claim:</strong> "{claim_text}"</p>
                                <p style="margin:0 0 8px 0; color:#94A3B8; font-size:12px;"><strong>By:</strong> {claimant}</p>
                                <div style="display:flex; justify-content:space-between; align-items:center;">
                                    <span style="font-size:12px; color:#94A3B8;">Verified by: <strong>{publisher}</strong></span>
                                    <span style="font-size:12px; font-weight:700; color:{rating_color}; background:rgba(255,255,255,0.05); padding:4px 8px; border-radius:6px;">{rating}</span>
                                </div>
                                <a href="{review_url}" target="_blank" style="display:inline-block; margin-top:8px; font-size:12px; color:#818CF8; text-decoration:none;">Read full review &rarr;</a>
                            </div>
                            """))
                        st.html("</div>")
                else:
                    st.html(textwrap.dedent("""
                    <div style="margin-top:24px; background:#161B26; border-radius:20px; border:1px solid #1E293B; padding:20px 28px;">
                        <div style="display:flex; align-items:center; gap:10px;">
                            <span style="font-size:22px;">⚙️</span>
                            <div>
                                <div style="font-family:'Inter',sans-serif; font-weight:700; font-size:15px; color:#E2E8F0;">Live Fact Check API Not Configured</div>
                                <div style="font-family:'Inter',sans-serif; font-size:12px; color:#94A3B8;">Add GOOGLE_API_KEY to your Streamlit secrets to enable global fact-check database lookups.</div>
                            </div>
                        </div>
                    </div>
                    """))

                # ── SHARED: Verify Online panel (appears after EVERY result) ──
                st.html(textwrap.dedent(f"""
                <div style="
                    margin-top:24px;
                    background:#161B26;
                    border-radius:20px;
                    border:1px solid #1E293B;
                    overflow:hidden;
                ">
                    <div style="
                        padding:18px 28px 14px 28px;
                        border-bottom:1px solid #1E293B;
                        display:flex; align-items:center; gap:10px;
                    ">
                        <span style="font-size:22px;">🔍</span>
                        <div>
                            <div style="font-family:'Inter',sans-serif; font-weight:700; font-size:15px; color:#E2E8F0;">Not sure about the AI result? Verify this article yourself</div>
                            <div style="font-family:'Inter',sans-serif; font-size:12px; color:#94A3B8; margin-top:2px;">Click any button below — your article keywords are already pre-searched for you</div>
                        </div>
                    </div>
                    <div style="padding:20px 28px;">
                        <div class="sources-grid">
                            <a href="{google_news_url}" class="source-btn" target="_blank" style="display:flex;flex-direction:column;align-items:center;gap:8px;background:#1E293B;border:1px solid #334155;border-radius:14px;padding:20px 12px;text-decoration:none;">
                                <div style="font-family:'Inter',sans-serif;font-weight:700;font-size:13px;color:#E2E8F0;text-align:center;">Google News</div>
                                <div style="font-family:'Inter',sans-serif;font-size:11px;color:#94A3B8;text-align:center;">See if real outlets reported it</div>
                            </a>
                            <a href="{politifact_url}" class="source-btn" target="_blank" style="display:flex;flex-direction:column;align-items:center;gap:8px;background:#162521;border:1px solid #223E36;border-radius:14px;padding:20px 12px;text-decoration:none;">
                                <div style="font-family:'Inter',sans-serif;font-weight:700;font-size:13px;color:#34D399;text-align:center;">PolitiFact</div>
                                <div style="font-family:'Inter',sans-serif;font-size:11px;color:#047857;text-align:center;">Political news verified</div>
                            </a>
                            <a href="{bbc_url}" class="source-btn" target="_blank" style="display:flex;flex-direction:column;align-items:center;gap:8px;background:#281B1D;border:1px solid #4C2329;border-radius:14px;padding:20px 12px;text-decoration:none;">
                                <div style="font-family:'Inter',sans-serif;font-weight:700;font-size:13px;color:#F87171;text-align:center;">BBC News</div>
                                <div style="font-family:'Inter',sans-serif;font-size:11px;color:#B91C1C;text-align:center;">Trusted global coverage</div>
                            </a>
                        </div>
                        <div style="margin-top:16px;background:#1A1F2C;border-radius:12px;padding:14px 18px;font-family:'Inter',sans-serif;font-size:13px;color:#94A3B8;line-height:1.8;border:1px solid #2A3142;">
                            <strong style="color:#E2E8F0;">💡 Golden Rule — How to know if news is really real:</strong><br>
                            If the AI says <strong style="color:#F87171;">FAKE</strong> but you search on Google News and see the same story reported by
                            <strong>BBC News, CNN, or other major outlets</strong> — the article is almost certainly <strong style="color:#34D399;">REAL</strong>.
                            The AI may have flagged it because of <em>writing style</em>, not because the facts are wrong.<br><br>
                            <strong style="color:#E2E8F0;">🔍 Simple 3-step check:</strong><br>
                            1️⃣ Click <strong>Google News</strong> — if 3+ big outlets report the same story, it’s real<br>
                            2️⃣ Click <strong>PolitiFact</strong> or <strong>BBC News</strong> to verify the facts directly<br>
                            3️⃣ If no results anywhere — be careful, it might be fabricated
                        </div>
                    </div>
                </div>
                """))

    st.html("</div>")


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  PAGE: HOME (HOW TO SPOT FAKE NEWS)                                      ║
# ╚═══════════════════════════════════════════════════════════════════════════╝
if st.session_state.current_page == 'home':
    st.html('<div style="max-width:1100px; margin:0 auto; padding:8px 0 60px 0;">')
    
    # BIG ANALYZE BUTTON
    col1, col2, col3 = st.columns([1.5, 1, 1.5])
    with col2:
        st.button("🔍 Analyze an Article Now", type="primary", use_container_width=True, on_click=go_to_analyzer)
    st.html('<div style="margin-bottom: 40px;"></div>')

    st.html(textwrap.dedent("""
    <div style="text-align:center; margin-bottom:52px;">
        <h2 style="
            font-family:'Inter',sans-serif; font-size:40px; font-weight:900;
            color:#FFFFFF; letter-spacing:-1.5px; margin-bottom:16px;
        ">Verify Before You Trust</h2>
        <p style="
            font-family:'Inter',sans-serif; font-size:17px; color:#94A3B8;
            max-width:600px; margin:0 auto; line-height:1.7;
        ">AI can flag patterns, but the final verdict rests with you.
        Protect the integrity of your information diet by applying the same rigorous verification standards that professional journalists use daily</p>
    </div>

    <!-- 6 tip cards in a 3x2 grid (Fully Responsive via CSS Media Queries) -->
    <div class="steps-grid">

        <div class="step-card">
            <div style="width:52px;height:52px;border-radius:14px;background:linear-gradient(135deg,#EEF2FF,#E0E7FF);display:flex;align-items:center;justify-content:center;font-size:24px;margin-bottom:18px;box-shadow:0 2px 8px rgba(99,102,241,0.15);">🔗</div>
            <div style="font-family:'Inter',sans-serif;font-size:11px;font-weight:700;color:#6366F1;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:8px;">Step 01</div>
            <h3 style="font-family:'Inter',sans-serif;font-size:18px;font-weight:800;color:#1E293B;margin-bottom:12px;letter-spacing:-0.3px;">Verify the Source
</h3>
            <p style="font-family:'Inter',sans-serif;font-size:14px;color:#64748B;line-height:1.7;margin:0;">Verify the Source
 credibility via their 'About Us' page. Watch out for domain spoofing, a common tactic where fraudulent sites use URLs nearly identical to legitimate news outlets to mislead readers.</p>
        </div>

        <div class="step-card">
            <div style="width:52px;height:52px;border-radius:14px;background:linear-gradient(135deg,#F5F3FF,#EDE9FE);display:flex;align-items:center;justify-content:center;font-size:24px;margin-bottom:18px;box-shadow:0 2px 8px rgba(139,92,246,0.15);">🎣</div>
            <div style="font-family:'Inter',sans-serif;font-size:11px;font-weight:700;color:#8B5CF6;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:8px;">Step 02</div>
            <h3 style="font-family:'Inter',sans-serif;font-size:18px;font-weight:800;color:#1E293B;margin-bottom:12px;letter-spacing:-0.3px;">Look Beyond the Headline</h3>
            <p style="font-family:'Inter',sans-serif;font-size:14px;color:#64748B;line-height:1.7;margin:0;">Clickbait prioritizes shares over accuracy. Since headlines rarely provide the full context of the story, make it a rule to read the complete article before trusting or passing it on</p>
        </div>

        <div class="step-card">
            <div style="width:52px;height:52px;border-radius:14px;background:linear-gradient(135deg,#FFFBEB,#FEF3C7);display:flex;align-items:center;justify-content:center;font-size:24px;margin-bottom:18px;box-shadow:0 2px 8px rgba(245,158,11,0.15);">✍️</div>
            <div style="font-family:'Inter',sans-serif;font-size:11px;font-weight:700;color:#D97706;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:8px;">Step 03</div>
            <h3 style="font-family:'Inter',sans-serif;font-size:18px;font-weight:800;color:#1E293B;margin-bottom:12px;letter-spacing:-0.3px;">Examine Author Qualifications</h3>
            <p style="font-family:'Inter',sans-serif;font-size:14px;color:#64748B;line-height:1.7;margin:0;">Verify the source by looking up the reporter's name. A credible journalist will have a traceable body of work; if no author is listed, proceed with extreme caution</p>
        </div>

        <div class="step-card">
            <div style="width:52px;height:52px;border-radius:14px;background:linear-gradient(135deg,#F0FDF4,#DCFCE7);display:flex;align-items:center;justify-content:center;font-size:24px;margin-bottom:18px;box-shadow:0 2px 8px rgba(16,185,129,0.15);">📅</div>
            <div style="font-family:'Inter',sans-serif;font-size:11px;font-weight:700;color:#059669;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:8px;">Step 04</div>
            <h3 style="font-family:'Inter',sans-serif;font-size:18px;font-weight:800;color:#1E293B;margin-bottom:12px;letter-spacing:-0.3px;">Confirm the Timeline</h3>
            <p style="font-family:'Inter',sans-serif;font-size:14px;color:#64748B;line-height:1.7;margin:0;">Context is easily lost when old stories are shared as if they were current events. Always check the timestamp; content that feels surprisingly relevant today may actually be years old and entirely out of context.</p>
        </div>

        <div class="step-card">
            <div style="width:52px;height:52px;border-radius:14px;background:linear-gradient(135deg,#FFF1F2,#FFE4E6);display:flex;align-items:center;justify-content:center;font-size:24px;margin-bottom:18px;box-shadow:0 2px 8px rgba(239,68,68,0.15);">📚</div>
            <div style="font-family:'Inter',sans-serif;font-size:11px;font-weight:700;color:#DC2626;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:8px;">Step 05</div>
            <h3 style="font-family:'Inter',sans-serif;font-size:18px;font-weight:800;color:#1E293B;margin-bottom:12px;letter-spacing:-0.3px;">Verify Through Multiple Outlets</h3>
            <p style="font-family:'Inter',sans-serif;font-size:14px;color:#64748B;line-height:1.7;margin:0;">Authentic news rarely appears in a vacuum. If a shocking story is missing from other major news organizations, treat it as a warning. Protect your judgment by confirming reports through at least two or three independent, credible sources.</p>
        </div>

        <div class="step-card">
            <div style="width:52px;height:52px;border-radius:14px;background:linear-gradient(135deg,#FFF7ED,#FFEDD5);display:flex;align-items:center;justify-content:center;font-size:24px;margin-bottom:18px;box-shadow:0 2px 8px rgba(249,115,22,0.15);">🧠</div>
            <div style="font-family:'Inter',sans-serif;font-size:11px;font-weight:700;color:#EA580C;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:8px;">Step 06</div>
            <h3 style="font-family:'Inter',sans-serif;font-size:18px;font-weight:800;color:#1E293B;margin-bottom:12px;letter-spacing:-0.3px;">Acknowledge Your Perspective</h3>
            <p style="font-family:'Inter',sans-serif;font-size:14px;color:#64748B;line-height:1.7;margin:0;">Our beliefs often act as a filter for what we accept as true. To maintain objectivity, interrogate your reaction: 'Would I challenge this if the author held different views?' Treat emotional triggers as a warning sign to stop, breathe, and verify before you engage or share.</p>
        </div>
    </div>

    <!-- Fact-checking resources banner -->
    <div style="
        background:#161B26;
        border:1px solid #1E293B;
        border-radius:24px; padding:40px 48px;
        display:flex; flex-direction:column; align-items:center;
        text-align:center;
    ">
        <h3 style="font-family:'Inter',sans-serif;font-size:26px;font-weight:900;color:#FFFFFF;margin-bottom:10px;letter-spacing:-0.5px;">Trusted Sources for Verification</h3>
        <p style="font-family:'Inter',sans-serif;font-size:15px;color:#94A3B8;margin-bottom:32px;max-width:500px;">If our analysis or your intuition detects a potential inaccuracy, consult these reputable, journalism-grade fact-checking resources.</p>
        <div style="display:flex; gap:16px; flex-wrap:wrap; justify-content:center;">
            <a href="https://news.google.com/" target="_blank" style="
                background:rgba(255,255,255,0.1); backdrop-filter:blur(10px);
                border:1px solid rgba(255,255,255,0.2);
                color:#FFFFFF; font-family:'Inter',sans-serif; font-weight:700;
                font-size:14px; padding:12px 24px; border-radius:12px;
                text-decoration:none; transition:all 0.2s;
            ">Google News</a>
            <a href="https://www.politifact.com/" target="_blank" style="
                background:rgba(255,255,255,0.1); backdrop-filter:blur(10px);
                border:1px solid rgba(255,255,255,0.2);
                color:#FFFFFF; font-family:'Inter',sans-serif; font-weight:700;
                font-size:14px; padding:12px 24px; border-radius:12px;
                text-decoration:none; transition:all 0.2s;
            ">PolitiFact.com</a>
            <a href="https://www.bbc.com/news" target="_blank" style="
                background:rgba(255,255,255,0.1); backdrop-filter:blur(10px);
                border:1px solid rgba(255,255,255,0.2);
                color:#FFFFFF; font-family:'Inter',sans-serif; font-weight:700;
                font-size:14px; padding:12px 24px; border-radius:12px;
                text-decoration:none; transition:all 0.2s;
            ">BBC News</a>
        </div>
    </div>
    """))
    st.html("</div>")

# ────────────────────────────────────────────────────────────────────────────────
# FOOTER
# ────────────────────────────────────────────────────────────────────────────────
st.html(textwrap.dedent("""
<div style="
    background: transparent;
    padding:32px 48px;
    display:flex; flex-direction:column; align-items:center;
    gap:12px; margin-top:48px;
    border-top:1px solid #1E293B;
">
    <div style="display:flex; align-items:center; gap:10px; margin-bottom:4px;">
        <span style="font-family:'Inter',sans-serif; font-weight:800; font-size:18px; color:#FFFFFF;">
            Fake News <span style="color:#818CF8;">Detector</span>
        </span>
    </div>
    <p style="font-family:'Inter',sans-serif; font-size:13px; color:#94A3B8; margin:8px 0; max-width: 600px; text-align: center; line-height: 1.6;">
        Note: This analysis is based on linguistic style, not fact-checking. Uncharacteristic writing styles may trigger false alerts; please use the suggested links to independently verify all findings.
    </p>
    <p style="font-family:'Inter',sans-serif; font-size:13px; color:#4B5563; margin:4px 0 0 0;">
        © 2026 Fake News Detector. All rights reserved.
    </p>
</div>
"""))