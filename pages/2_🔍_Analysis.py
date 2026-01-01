"""
Q-Classify - Analysis Page
AI-powered question categorization with chapter/concept/difficulty mapping
"""

import streamlit as st
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.config import init_session_state, Config
from utils.helpers import parse_questions_from_text, format_difficulty, clean_text
from services.ai_analyzer import ai_analyzer
from services.pdf_generator import pdf_generator
from components.header import render_page_header, render_api_warning
from components.footer import render_compact_footer

# Page config
st.set_page_config(
    page_title="Analysis | Q-Classify",
    page_icon="🔍",
    layout="wide"
)

# Initialize session state
init_session_state()

# Custom CSS
st.markdown("""
<style>
    .question-card {
        background: linear-gradient(145deg, #2D2D44, #1E1E2E);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid #4A90D9;
    }
    .question-text {
        color: #E0E0E0;
        font-size: 1rem;
        line-height: 1.6;
        margin-bottom: 1rem;
    }
    .meta-row {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 10px;
    }
    .chapter-badge {
        background: #4A90D9;
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        font-size: 0.85rem;
    }
    .concept-tag {
        background: #9B59B6;
        color: white;
        padding: 4px 12px;
        border-radius: 15px;
        font-size: 0.8rem;
    }
    .difficulty-easy {
        background: #2ECC71;
        color: white;
        padding: 4px 12px;
        border-radius: 15px;
        font-size: 0.8rem;
    }
    .difficulty-medium {
        background: #F39C12;
        color: white;
        padding: 4px 12px;
        border-radius: 15px;
        font-size: 0.8rem;
    }
    .difficulty-hard {
        background: #E74C3C;
        color: white;
        padding: 4px 12px;
        border-radius: 15px;
        font-size: 0.8rem;
    }
    .stats-card {
        background: linear-gradient(145deg, #2D2D44, #1E1E2E);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        border: 1px solid #4A90D9;
    }
    .stats-number {
        font-size: 2rem;
        font-weight: bold;
        color: #2ECC71;
    }
    .stats-label {
        color: #888;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# Page Header
render_page_header(
    "Question Analysis",
    "🔍",
    "AI-powered categorization of questions by chapter, concepts, and difficulty"
)

# Check prerequisites
if not st.session_state.syllabus_text:
    st.warning("⚠️ Please upload a syllabus first")
    if st.button("📤 Go to Upload Page"):
        st.switch_page("pages/1_📤_Upload_Files.py")
    st.stop()

if not st.session_state.question_papers:
    st.warning("⚠️ Please upload question papers first")
    if st.button("📤 Go to Upload Page"):
        st.switch_page("pages/1_📤_Upload_Files.py")
    st.stop()

# API Warning
if not render_api_warning():
    st.stop()

# ==================== ANALYSIS SECTION ====================
# Check if analysis already done
if st.session_state.analysis_complete and st.session_state.questions_data:
    st.success(f"✅ Analysis complete! {len(st.session_state.questions_data)} questions analyzed.")
    
    # Option to re-analyze
    if st.button("🔄 Re-analyze Questions"):
        st.session_state.analysis_complete = False
        st.session_state.questions_data = []
        st.rerun()
else:
    # Start analysis
    st.markdown("### 🚀 Ready to Analyze")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Syllabus:** {st.session_state.syllabus_file}")
    with col2:
        st.markdown(f"**Question Papers:** {len(st.session_state.question_papers)} file(s)")
    
    if st.button("🔍 Analyze Questions", type="primary", width="stretch"):
        st.session_state.is_processing = True
        st.session_state.last_error = None
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        error_container = st.empty()
        
        all_questions = []
        all_analyzed = []
        
        # Step 1: Extract questions from all papers
        status_text.text("📝 Extracting questions from papers...")
        
        for i, paper in enumerate(st.session_state.question_papers):
            questions = parse_questions_from_text(paper['text'])
            for q in questions:
                all_questions.append({
                    'text': q,
                    'source': paper['name'],
                    'year': paper['year']
                })
            progress_bar.progress((i + 1) / len(st.session_state.question_papers) * 0.3)
        
        if not all_questions:
            st.error("❌ Could not extract questions from the papers. Please check the PDF format.")
            st.session_state.is_processing = False
            st.stop()
        
        st.info(f"📊 Found {len(all_questions)} questions across all papers")
        
        # Step 2: Analyze questions with AI
        status_text.text("🤖 Analyzing questions with AI...")
        
        # Process in batches for better performance
        batch_size = 10
        question_texts = [q['text'] for q in all_questions]
        analysis_error = None
        
        for batch_start in range(0, len(question_texts), batch_size):
            batch_end = min(batch_start + batch_size, len(question_texts))
            batch = question_texts[batch_start:batch_end]
            
            try:
                with st.spinner(f"🤖 Analyzing batch {batch_start//batch_size + 1}..."):
                    analysis_results = ai_analyzer.analyze_questions(
                        batch,
                        st.session_state.syllabus_text
                    )
                
                # Merge with source info
                for j, result in enumerate(analysis_results):
                    idx = batch_start + j
                    if idx < len(all_questions):
                        result['source'] = all_questions[idx]['source']
                        result['year'] = all_questions[idx]['year']
                        result['question'] = result.get('question_text', all_questions[idx]['text'])
                        all_analyzed.append(result)
                
            except Exception as e:
                error_str = str(e)
                # Parse specific error types
                if "429" in error_str or "quota" in error_str.lower() or "rate" in error_str.lower():
                    analysis_error = "🚫 **API Quota Exceeded**: Your API usage limit has been reached. Please wait a few minutes or check your Google Cloud quota."
                elif "401" in error_str or "403" in error_str or "authentication" in error_str.lower() or "invalid" in error_str.lower():
                    analysis_error = "🔑 **Authentication Error**: Invalid API key. Please check your GOOGLE_API_KEY in the .env file."
                elif "timeout" in error_str.lower() or "timed out" in error_str.lower():
                    analysis_error = "⏱️ **Timeout Error**: The request took too long. Please try again with fewer questions or check your internet connection."
                elif "connection" in error_str.lower() or "network" in error_str.lower():
                    analysis_error = "🌐 **Connection Error**: Unable to reach the API. Please check your internet connection."
                else:
                    analysis_error = f"❌ **Analysis Error**: {error_str}"
                
                st.session_state.last_error = analysis_error
                break
            
            # Update progress
            progress = 0.3 + (batch_end / len(question_texts)) * 0.7
            progress_bar.progress(progress)
            status_text.text(f"🤖 Analyzed {batch_end}/{len(question_texts)} questions...")
        
        # Handle error with retry option
        if analysis_error:
            progress_bar.empty()
            status_text.empty()
            error_container.error(analysis_error)
            st.session_state.is_processing = False
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("🔄 Retry Analysis", type="primary", width="stretch"):
                    st.session_state.last_error = None
                    st.rerun()
            st.stop()
        
        # Complete
        progress_bar.progress(1.0)
        status_text.text("✅ Analysis complete!")
        
        st.session_state.questions_data = all_analyzed
        st.session_state.analysis_complete = True
        st.session_state.is_processing = False
        
        st.rerun()

# Show previous error with retry option
if st.session_state.get('last_error') and not st.session_state.analysis_complete:
    st.error(st.session_state.last_error)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔄 Retry Analysis", type="primary", width="stretch", key="retry_prev"):
            st.session_state.last_error = None
            st.rerun()

# ==================== RESULTS DISPLAY ====================
if st.session_state.analysis_complete and st.session_state.questions_data:
    questions_data = st.session_state.questions_data
    
    # Statistics
    st.markdown("### 📊 Analysis Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Calculate stats
    chapters = list(set(q.get('chapter', 'Unknown') for q in questions_data))
    all_concepts = []
    for q in questions_data:
        all_concepts.extend(q.get('concepts', []))
    unique_concepts = list(set(all_concepts))
    
    difficulties = {'Easy': 0, 'Medium': 0, 'Hard': 0}
    for q in questions_data:
        diff = q.get('difficulty', 'Medium')
        difficulties[diff] = difficulties.get(diff, 0) + 1
    
    with col1:
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-number">{len(questions_data)}</div>
            <div class="stats-label">Questions</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-number">{len(chapters)}</div>
            <div class="stats-label">Chapters</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-number">{len(unique_concepts)}</div>
            <div class="stats-label">Concepts</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        # Most common difficulty
        most_common = max(difficulties, key=difficulties.get)
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-number">{most_common}</div>
            <div class="stats-label">Avg Difficulty</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Filters
    st.markdown("### 🔎 Filter Results")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filter_chapter = st.selectbox(
            "Filter by Chapter",
            ["All"] + sorted(chapters)
        )
    
    with col2:
        filter_difficulty = st.selectbox(
            "Filter by Difficulty",
            ["All", "Easy", "Medium", "Hard"]
        )
    
    with col3:
        filter_source = st.selectbox(
            "Filter by Paper",
            ["All"] + list(set(q.get('source', '') for q in questions_data if q.get('source')))
        )
    
    # Apply filters
    filtered_questions = questions_data
    if filter_chapter != "All":
        filtered_questions = [q for q in filtered_questions if q.get('chapter') == filter_chapter]
    if filter_difficulty != "All":
        filtered_questions = [q for q in filtered_questions if q.get('difficulty') == filter_difficulty]
    if filter_source != "All":
        filtered_questions = [q for q in filtered_questions if q.get('source') == filter_source]
    
    st.markdown(f"Showing **{len(filtered_questions)}** of {len(questions_data)} questions")
    
    # Questions display
    st.markdown("### 📋 Analyzed Questions")
    
    for i, q in enumerate(filtered_questions, 1):
        question_text = q.get('question', q.get('question_text', 'N/A'))
        chapter = q.get('chapter', 'Unknown')
        difficulty = q.get('difficulty', 'Medium')
        concepts = q.get('concepts', [])
        source = q.get('source', '')
        year = q.get('year', '')
        
        # Difficulty class
        diff_class = f"difficulty-{difficulty.lower()}"
        
        # Concepts HTML
        concepts_html = ' '.join([f'<span class="concept-tag">{c}</span>' for c in concepts])
        
        # Source info
        source_info = f"{source}"
        if year:
            source_info += f" ({year})"
        
        st.markdown(f"""
        <div class="question-card">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 10px;">
                <span style="color: #4A90D9; font-weight: bold;">Q{i}</span>
                <span style="color: #888; font-size: 0.8rem;">📄 {source_info}</span>
            </div>
            <p class="question-text">{question_text[:500]}{'...' if len(question_text) > 500 else ''}</p>
            <div class="meta-row">
                <span class="chapter-badge">📚 {chapter}</span>
                <span class="{diff_class}">{difficulty}</span>
            </div>
            <div class="meta-row" style="margin-top: 8px;">
                {concepts_html if concepts_html else '<span style="color: #888;">No concepts identified</span>'}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Download section
    st.markdown("---")
    st.markdown("### 💾 Download Report")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Generate PDF Report", type="primary", width="stretch"):
            with st.spinner("Generating PDF report..."):
                try:
                    pdf_bytes = pdf_generator.generate_report(
                        questions_data,
                        syllabus_summary=st.session_state.syllabus_summary,
                        trend_summary=st.session_state.trend_data
                    )
                    
                    st.download_button(
                        label="⬇️ Download PDF",
                        data=pdf_bytes,
                        file_name="QClassify_Report.pdf",
                        mime="application/pdf",
                        width="stretch"
                    )
                except Exception as e:
                    st.error(f"Error generating PDF: {str(e)}")
    
    with col2:
        # Export as JSON
        import json
        json_data = json.dumps(questions_data, indent=2, default=str)
        st.download_button(
            label="📥 Download JSON Data",
            data=json_data,
            file_name="QClassify_Data.json",
            mime="application/json",
            width="stretch"
        )

# Sidebar
with st.sidebar:
    st.markdown("### 📊 Quick Stats")
    if st.session_state.questions_data:
        st.metric("Total Questions", len(st.session_state.questions_data))
        
        difficulties = {'Easy': 0, 'Medium': 0, 'Hard': 0}
        for q in st.session_state.questions_data:
            diff = q.get('difficulty', 'Medium')
            difficulties[diff] = difficulties.get(diff, 0) + 1
        
        st.markdown("**Difficulty Distribution:**")
        for diff, count in difficulties.items():
            st.progress(count / len(st.session_state.questions_data), text=f"{diff}: {count}")
    
    st.markdown("---")
    st.markdown("### 🔗 Quick Links")
    if st.button("📊 View Trends", width="stretch"):
        st.switch_page("pages/3_📊_Trend_Analysis.py")
    if st.button("🔎 Search Questions", width="stretch"):
        st.switch_page("pages/4_🔎_Custom_Search.py")

# Footer
render_compact_footer()
