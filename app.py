"""
Q-Classify - AI-Powered PDF Analyzer
Main Streamlit Application - Landing Page
"""

import streamlit as st
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="Q-Classify | AI PDF Analyzer",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
def load_css():
    css_file = Path(__file__).parent / "assets" / "styles.css"
    if css_file.exists():
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Initialize session state
from utils.config import init_session_state
init_session_state()

# Custom CSS for landing page (inline for reliability)
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary: #4A90D9;
        --secondary: #2ECC71;
        --accent: #9B59B6;
    }
    
    .hero-section {
        background: linear-gradient(135deg, #4A90D9 0%, #9B59B6 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(74, 144, 217, 0.3);
    }
    
    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        color: white;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .hero-subtitle {
        font-size: 1.3rem;
        color: rgba(255,255,255,0.95);
        max-width: 700px;
        margin: 0 auto 1.5rem auto;
        line-height: 1.6;
    }
    
    .feature-box {
        background: linear-gradient(145deg, #1E1E2E, #2D2D44);
        border: 1px solid #4A90D9;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
        min-height: 120px;
    }
    
    .feature-box:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(74, 144, 217, 0.2);
        border-color: #2ECC71;
    }
    
    .feature-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }
    
    .feature-text {
        color: #E0E0E0;
        font-size: 1rem;
    }
    
    .step-item {
        background: #2D2D44;
        border-left: 4px solid #9B59B6;
        padding: 1rem 1.5rem;
        margin: 0.75rem 0;
        border-radius: 0 12px 12px 0;
        transition: all 0.3s ease;
    }
    
    .step-item:hover {
        border-left-color: #2ECC71;
        background: #363650;
    }
    
    .step-text {
        color: #E0E0E0;
        font-size: 1.1rem;
    }
    
    .section-title {
        color: #4A90D9;
        font-size: 1.8rem;
        font-weight: 700;
        margin: 2.5rem 0 1.5rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #9B59B6;
    }
    
    .footer-section {
        background: linear-gradient(135deg, #1E1E2E 0%, #2D2D44 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-top: 3rem;
        border-top: 3px solid #4A90D9;
    }
    
    .footer-text {
        color: #B0B0C0;
        font-size: 1.1rem;
        margin: 0;
    }
    
    .cta-container {
        text-align: center;
        margin: 2rem 0;
    }
    
    /* Stats cards */
    .stat-card {
        background: linear-gradient(145deg, #2D2D44, #1E1E2E);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        border: 1px solid #4A90D9;
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: 800;
        color: #2ECC71;
    }
    
    .stat-label {
        color: #B0B0C0;
        font-size: 0.95rem;
    }
</style>
""", unsafe_allow_html=True)

# ==================== HERO SECTION ====================
st.markdown("""
<div class="hero-section">
    <div class="hero-title">🎓 Q-Classify</div>
    <div class="hero-subtitle">
        Analyze Your Exam Papers with AI-Powered Insights!<br>
        Upload your syllabus and question papers, and let AI map each question to its corresponding chapter and concepts.
    </div>
</div>
""", unsafe_allow_html=True)

# CTA Button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🚀 Get Started", width="stretch", type="primary"):
        st.switch_page("pages/1_📤_Upload_Files.py")

st.markdown("<br>", unsafe_allow_html=True)

# ==================== FEATURES SECTION ====================
st.markdown('<div class="section-title">✨ Features</div>', unsafe_allow_html=True)

features = [
    ("🔍", "AI-driven Question Categorization", "Automatically maps questions to syllabus chapters"),
    ("📂", "Multiple Question Papers", "Upload and analyze papers from different years"),
    ("📑", "Structured PDF Reports", "Download comprehensive categorized reports"),
    ("📊", "Question Trend Analysis", "Identify recurring concepts and patterns"),
    ("🎯", "Key Concept Identification", "Discover important topics for focused study"),
]

# Display features in columns
col1, col2, col3 = st.columns(3)
columns = [col1, col2, col3]

for idx, (icon, title, desc) in enumerate(features):
    with columns[idx % 3]:
        st.markdown(f"""
        <div class="feature-box">
            <div class="feature-icon">{icon}</div>
            <strong style="color: #2ECC71; font-size: 1.1rem;">{title}</strong>
            <p class="feature-text">{desc}</p>
        </div>
        """, unsafe_allow_html=True)

# Additional features row
col1, col2 = st.columns(2)
with col1:
    st.markdown("""
    <div class="feature-box">
        <div class="feature-icon">🗺️</div>
        <strong style="color: #2ECC71; font-size: 1.1rem;">Concept Mapping</strong>
        <p class="feature-text">Visual representation of concepts and their relationships</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-box">
        <div class="feature-icon">📝</div>
        <strong style="color: #2ECC71; font-size: 1.1rem;">Summary Generator</strong>
        <p class="feature-text">Quick syllabus summary for efficient revision</p>
    </div>
    """, unsafe_allow_html=True)

# ==================== HOW IT WORKS SECTION ====================
st.markdown('<div class="section-title">📋 How It Works</div>', unsafe_allow_html=True)

steps = [
    "1️⃣ Upload your syllabus PDF",
    "2️⃣ Upload one or more question paper PDFs",
    "3️⃣ AI processes the files and maps questions to syllabus concepts",
    "4️⃣ Download a categorized report with insights"
]

for step in steps:
    st.markdown(f"""
    <div class="step-item">
        <span class="step-text">{step}</span>
    </div>
    """, unsafe_allow_html=True)

# ==================== STATS SECTION ====================
st.markdown("<br>", unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="stat-card">
        <div class="stat-number">AI</div>
        <div class="stat-label">Powered Analysis</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="stat-card">
        <div class="stat-number">∞</div>
        <div class="stat-label">Questions Analyzed</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="stat-card">
        <div class="stat-number">PDF</div>
        <div class="stat-label">Report Generation</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="stat-card">
        <div class="stat-number">🎯</div>
        <div class="stat-label">Accurate Mapping</div>
    </div>
    """, unsafe_allow_html=True)

# ==================== FOOTER SECTION ====================
st.markdown("""
<div class="footer-section">
    <p class="footer-text">🎓 Empowering students with AI-driven learning insights.</p>
    <p style="color: #6c757d; font-size: 0.9rem; margin-top: 1rem;">
        Built with Streamlit • Powered by Google Gemini AI
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 🎓 Q-Classify")
    st.markdown("---")
    st.markdown("""
    **Quick Navigation:**
    - 📤 Upload Files
    - 🔍 Analysis
    - 📊 Trend Analysis
    - 🔎 Custom Search
    - 📝 Summary
    - 🗺️ Concept Map
    """)
    st.markdown("---")
    st.markdown("**Need Help?**")
    st.markdown("Check the [README](README.md) for setup instructions.")
