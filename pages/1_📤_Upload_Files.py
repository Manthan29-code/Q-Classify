"""
Q-Classify - Upload Files Page
Upload syllabus and question paper PDFs
"""

import streamlit as st
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.config import init_session_state, Config, is_api_configured, restore_files_from_disk, clear_session_state
from utils.helpers import extract_year_from_filename, format_file_size, clean_text
from services.pdf_extractor import pdf_extractor
from components.header import render_page_header, render_api_warning
from components.footer import render_compact_footer

# Page config
st.set_page_config(
    page_title="Upload Files | Q-Classify",
    page_icon="📤",
    layout="wide"
)

# Initialize session state
init_session_state()

# Restore files from disk on page load
restore_files_from_disk()

# Custom CSS
st.markdown("""
<style>
    .upload-box {
        border: 2px dashed #4A90D9;
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        background: rgba(74, 144, 217, 0.1);
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    .upload-box:hover {
        background: rgba(74, 144, 217, 0.15);
        border-color: #2ECC71;
    }
    .file-item {
        background: #2D2D44;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .file-name {
        color: #E0E0E0;
        font-weight: 500;
    }
    .file-info {
        color: #888;
        font-size: 0.85rem;
    }
    .success-badge {
        background: #2ECC71;
        color: white;
        padding: 3px 10px;
        border-radius: 10px;
        font-size: 0.8rem;
    }
    .status-card {
        background: linear-gradient(145deg, #2D2D44, #1E1E2E);
        border-radius: 12px;
        padding: 1.5rem;
        border-left: 4px solid #4A90D9;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Page Header
render_page_header(
    "Upload Files",
    "📤",
    "Upload your syllabus PDF and question paper PDFs for AI-powered analysis"
)

# API Warning
api_ready = render_api_warning()

# Main content
col1, col2 = st.columns(2)

# ==================== SYLLABUS UPLOAD ====================
with col1:
    st.markdown("### 📚 Syllabus PDF")
    st.markdown("Upload your course syllabus (single PDF)")
    
    syllabus_file = st.file_uploader(
        "Upload Syllabus",
        type=['pdf'],
        key="syllabus_uploader",
        help="Upload the course syllabus PDF containing chapters and topics"
    )
    
    if syllabus_file:
        # Validate and extract
        file_content = syllabus_file.read()
        validation = pdf_extractor.validate_pdf(file_content)
        
        if validation['valid']:
            # Extract text
            with st.spinner("Extracting syllabus content..."):
                extraction = pdf_extractor.extract_text(file_content, syllabus_file.name)
            
            if extraction['success']:
                # Save file to disk for persistence
                save_path = Config.UPLOADS_DIR / f"syllabus_{syllabus_file.name}"
                save_path.write_bytes(file_content)
                
                st.session_state.syllabus_file = syllabus_file.name
                st.session_state.syllabus_text = extraction['text']
                st.session_state.syllabus_path = str(save_path)  # Store path for restoration
                
                st.markdown(f"""
                <div class="status-card">
                    <span class="success-badge">✓ Uploaded</span>
                    <h4 style="color: #2ECC71; margin: 10px 0 5px 0;">{syllabus_file.name}</h4>
                    <p class="file-info">
                        📄 {extraction['page_count']} pages • 
                        📝 {len(extraction['text'])} characters •
                        ⚙️ {extraction['method']}
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # Preview
                with st.expander("👀 Preview Syllabus Content"):
                    preview_text = extraction['text'][:2000]
                    st.text_area("Content Preview", preview_text, height=200, disabled=True)
            else:
                st.error(f"❌ Failed to extract text: {extraction['error']}")
        else:
            st.error(f"❌ Invalid PDF: {validation['error']}")
    
    # Show current status
    if st.session_state.syllabus_text and not syllabus_file:
        st.info(f"✓ Syllabus loaded: {st.session_state.syllabus_file}")

# ==================== QUESTION PAPERS UPLOAD ====================
with col2:
    st.markdown("### 📝 Question Papers")
    st.markdown("Upload one or more question paper PDFs")
    
    question_files = st.file_uploader(
        "Upload Question Papers",
        type=['pdf'],
        accept_multiple_files=True,
        key="questions_uploader",
        help="Upload question paper PDFs (you can select multiple files)"
    )
    
    if question_files:
        papers_processed = []
        
        for qf in question_files:
            file_content = qf.read()
            validation = pdf_extractor.validate_pdf(file_content)
            
            if validation['valid']:
                with st.spinner(f"Processing {qf.name}..."):
                    extraction = pdf_extractor.extract_text(file_content, qf.name)
                
                if extraction['success']:
                    year = extract_year_from_filename(qf.name)
                    
                    # Save file to disk for persistence
                    save_path = Config.UPLOADS_DIR / f"paper_{qf.name}"
                    save_path.write_bytes(file_content)
                    
                    papers_processed.append({
                        'name': qf.name,
                        'text': extraction['text'],
                        'year': year,
                        'pages': extraction['page_count'],
                        'method': extraction['method'],
                        'path': str(save_path)  # Store path for restoration
                    })
        
        if papers_processed:
            st.session_state.question_papers = papers_processed
            
            st.markdown(f"""
            <div class="status-card">
                <span class="success-badge">✓ {len(papers_processed)} file(s) uploaded</span>
            </div>
            """, unsafe_allow_html=True)
            
            for paper in papers_processed:
                year_badge = f"📅 {paper['year']}" if paper['year'] else "📅 Year unknown"
                st.markdown(f"""
                <div class="file-item">
                    <div>
                        <span class="file-name">📄 {paper['name']}</span>
                        <p class="file-info">{paper['pages']} pages • {year_badge}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Preview
            with st.expander("👀 Preview Question Paper Content"):
                selected_paper = st.selectbox(
                    "Select paper to preview",
                    [p['name'] for p in papers_processed]
                )
                for p in papers_processed:
                    if p['name'] == selected_paper:
                        preview_text = p['text'][:2000]
                        st.text_area("Content Preview", preview_text, height=200, disabled=True)
    
    # Show current status
    if st.session_state.question_papers and not question_files:
        st.info(f"✓ {len(st.session_state.question_papers)} question paper(s) loaded")

# ==================== STATUS SUMMARY ====================
st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    syllabus_status = "✅ Ready" if st.session_state.syllabus_text else "❌ Not uploaded"
    st.metric("Syllabus", syllabus_status)

with col2:
    papers_count = len(st.session_state.question_papers)
    papers_status = f"✅ {papers_count} file(s)" if papers_count > 0 else "❌ Not uploaded"
    st.metric("Question Papers", papers_status)

with col3:
    if st.session_state.syllabus_text and st.session_state.question_papers and api_ready:
        st.metric("Status", "✅ Ready to Analyze")
    else:
        missing = []
        if not st.session_state.syllabus_text:
            missing.append("syllabus")
        if not st.session_state.question_papers:
            missing.append("papers")
        if not api_ready:
            missing.append("API key")
        st.metric("Status", f"⏳ Need: {', '.join(missing)}")

# ==================== ACTION BUTTONS ====================
st.markdown("<br>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    # Analyze button
    if st.session_state.syllabus_text and st.session_state.question_papers and api_ready:
        if st.button("🚀 Start Analysis", width="stretch", type="primary"):
            st.switch_page("pages/2_🔍_Analysis.py")
    else:
        st.button("🚀 Start Analysis", width="stretch", disabled=True)
        st.caption("Upload syllabus and at least one question paper to proceed")

# Clear data button
with st.sidebar:
    st.markdown("### ⚙️ Options")
    if st.button("🗑️ Clear All Data"):
        clear_session_state()
        st.success("✅ All data and files cleared!")
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 📊 Upload Status")
    st.markdown(f"**Syllabus:** {'✅' if st.session_state.syllabus_text else '❌'}")
    st.markdown(f"**Papers:** {len(st.session_state.question_papers)} file(s)")
    st.markdown(f"**API:** {'✅' if api_ready else '❌'}")

# Footer
render_compact_footer()
