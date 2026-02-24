"""
Q-Classify - Summary Page
AI-generated syllabus summary for quick revision
"""

import streamlit as st
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.config import init_session_state, is_api_configured, render_api_key_sidebar
from services.ai_analyzer import ai_analyzer
from components.header import render_page_header, render_api_warning
from components.footer import render_compact_footer

# Page config
st.set_page_config(
    page_title="Summary | Q-Classify",
    page_icon="📝",
    layout="wide"
)

# Initialize session state
init_session_state()

# Custom CSS
st.markdown("""
<style>
    .summary-card {
        background: linear-gradient(145deg, #2D2D44, #1E1E2E);
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem 0;
        border: 1px solid #4A90D9;
    }
    .summary-section {
        background: rgba(74, 144, 217, 0.1);
        border-left: 4px solid #4A90D9;
        padding: 1rem 1.5rem;
        border-radius: 0 10px 10px 0;
        margin: 1rem 0;
    }
    .topic-tag {
        display: inline-block;
        background: #9B59B6;
        color: white;
        padding: 5px 12px;
        border-radius: 15px;
        margin: 3px;
        font-size: 0.85rem;
    }
    .chapter-card {
        background: #2D2D44;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
    }
    .chapter-card:hover {
        transform: translateX(5px);
        border-left: 4px solid #2ECC71;
    }
    .study-tip {
        background: rgba(46, 204, 113, 0.1);
        border-left: 4px solid #2ECC71;
        padding: 1rem;
        border-radius: 0 10px 10px 0;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Page Header
render_page_header(
    "Syllabus Summary",
    "📝",
    "AI-generated summary for quick and effective revision"
)

# Check prerequisites
if not st.session_state.syllabus_text:
    st.warning("⚠️ Please upload a syllabus first")
    if st.button("📤 Go to Upload Page"):
        st.switch_page("pages/1_📤_Upload_Files.py")
    st.stop()

# API Warning
if not render_api_warning():
    st.stop()

syllabus_text = st.session_state.syllabus_text

# ==================== GENERATE SUMMARY ====================
st.markdown("### 📋 Syllabus Summary")

# Check if summary already exists
if st.session_state.syllabus_summary:
    summary = st.session_state.syllabus_summary
    st.success("✅ Summary generated!")
    
    # Option to regenerate
    if st.button("🔄 Regenerate Summary"):
        st.session_state.syllabus_summary = None
        st.rerun()
else:
    if st.button("✨ Generate AI Summary", type="primary", width="stretch"):
        with st.spinner("🤖 AI is analyzing the syllabus..."):
            try:
                summary = ai_analyzer.generate_syllabus_summary(syllabus_text)
                st.session_state.syllabus_summary = summary
                st.session_state.last_error = None
                st.rerun()
            except Exception as e:
                error_str = str(e)
                # Parse specific error types
                if "429" in error_str or "quota" in error_str.lower() or "rate" in error_str.lower():
                    error_msg = "🚫 **API Quota Exceeded**: Your API usage limit has been reached. Please wait a few minutes or check your Google Cloud quota."
                elif "401" in error_str or "403" in error_str or "authentication" in error_str.lower():
                    error_msg = "🔑 **Authentication Error**: Invalid API key. Please check your GOOGLE_API_KEY in the .env file."
                elif "timeout" in error_str.lower() or "timed out" in error_str.lower():
                    error_msg = "⏱️ **Timeout Error**: The request took too long. Please try again."
                elif "connection" in error_str.lower() or "network" in error_str.lower():
                    error_msg = "🌐 **Connection Error**: Unable to reach the API. Please check your internet connection."
                else:
                    error_msg = f"❌ **Error**: {error_str}"
                
                st.session_state.last_error = error_msg
                st.error(error_msg)
                
                col1, col2, col3 = st.columns([1, 1, 1])
                with col2:
                    if st.button("🔄 Retry", type="primary", width="stretch"):
                        st.session_state.last_error = None
                        st.rerun()
                st.stop()
    else:
        # Show previous error with retry option
        if st.session_state.get('last_error'):
            st.error(st.session_state.last_error)
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("🔄 Retry", type="primary", width="stretch"):
                    st.session_state.last_error = None
                    st.rerun()
        else:
            st.info("👆 Click the button above to generate an AI-powered summary of your syllabus")
        st.stop()

# ==================== DISPLAY SUMMARY ====================
if st.session_state.syllabus_summary:
    summary = st.session_state.syllabus_summary
    
    # Display the summary with nice formatting
    st.markdown(f"""
    <div class="summary-card">
        {summary.replace('**', '<b>').replace('*', '<i>')}
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ==================== ADDITIONAL INSIGHTS ====================
    if st.session_state.questions_data:
        st.markdown("### 🎯 Study Recommendations")
        
        questions_data = st.session_state.questions_data
        
        # Get top concepts
        concept_counts = {}
        for q in questions_data:
            for c in q.get('concepts', []):
                concept_counts[c] = concept_counts.get(c, 0) + 1
        
        top_concepts = sorted(concept_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="study-tip">
                <h4 style="color: #2ECC71; margin-top: 0;">🎯 High-Priority Concepts</h4>
                <p style="color: #E0E0E0;">Based on question frequency, focus on these topics:</p>
            </div>
            """, unsafe_allow_html=True)
            
            for i, (concept, count) in enumerate(top_concepts[:5], 1):
                st.markdown(f"""
                <div class="chapter-card">
                    <span style="color: #4A90D9; font-weight: bold;">{i}.</span>
                    <span style="color: #E0E0E0;">{concept}</span>
                    <span style="color: #888; float: right;">{count} questions</span>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            # Difficulty breakdown
            difficulties = {'Easy': 0, 'Medium': 0, 'Hard': 0}
            for q in questions_data:
                diff = q.get('difficulty', 'Medium')
                difficulties[diff] = difficulties.get(diff, 0) + 1
            
            st.markdown("""
            <div class="study-tip">
                <h4 style="color: #2ECC71; margin-top: 0;">📊 Preparation Strategy</h4>
                <p style="color: #E0E0E0;">Question difficulty distribution:</p>
            </div>
            """, unsafe_allow_html=True)
            
            total = sum(difficulties.values())
            diff_colors = {'Easy': '#2ECC71', 'Medium': '#F39C12', 'Hard': '#E74C3C'}
            
            for diff, count in difficulties.items():
                pct = round(count / total * 100) if total > 0 else 0
                color = diff_colors[diff]
                st.markdown(f"""
                <div style="margin: 10px 0;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                        <span style="color: {color}; font-weight: bold;">{diff}</span>
                        <span style="color: #888;">{count} ({pct}%)</span>
                    </div>
                    <div style="background: #1E1E2E; border-radius: 5px; height: 8px;">
                        <div style="background: {color}; width: {pct}%; height: 100%; border-radius: 5px;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Study recommendation based on difficulty
            hard_pct = round(difficulties.get('Hard', 0) / total * 100) if total > 0 else 0
            
            if hard_pct > 40:
                st.warning("⚠️ High proportion of hard questions. Allocate extra time for complex topics.")
            elif hard_pct > 25:
                st.info("💡 Balanced difficulty. Cover basics thoroughly before tackling hard questions.")
            else:
                st.success("✅ Focus on comprehensive coverage. Most questions test fundamental concepts.")
    
    # ==================== EXPORT OPTIONS ====================
    st.markdown("---")
    st.markdown("### 💾 Export Summary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Download as text
        st.download_button(
            label="📄 Download as Text",
            data=summary,
            file_name="QClassify_Summary.txt",
            mime="text/plain",
            width="stretch"
        )
    
    with col2:
        # Download as Markdown
        md_content = f"""# Q-Classify Syllabus Summary

{summary}

---
*Generated by Q-Classify - AI-Powered Question Analysis*
"""
        st.download_button(
            label="📝 Download as Markdown",
            data=md_content,
            file_name="QClassify_Summary.md",
            mime="text/markdown",
            width="stretch"
        )

# ==================== SYLLABUS PREVIEW ====================
with st.expander("📖 View Original Syllabus Text"):
    st.text_area(
        "Syllabus Content",
        syllabus_text[:5000] + ("..." if len(syllabus_text) > 5000 else ""),
        height=300,
        disabled=True
    )

# Sidebar - API Key Settings
render_api_key_sidebar()

# Sidebar - Info
with st.sidebar:
    st.markdown("### 📊 Syllabus Info")
    st.metric("Characters", f"{len(syllabus_text):,}")
    st.metric("Words", f"{len(syllabus_text.split()):,}")
    
    if st.session_state.questions_data:
        st.markdown("---")
        st.markdown("### 📈 Analysis Status")
        st.markdown(f"✅ {len(st.session_state.questions_data)} questions analyzed")
        
        if st.button("🗺️ View Concept Map", width="stretch"):
            st.switch_page("pages/6_🗺️_Concept_Map.py")

# Footer
render_compact_footer()
