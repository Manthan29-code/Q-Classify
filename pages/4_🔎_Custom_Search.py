"""
Q-Classify - Custom Search Page
Search and filter questions by chapter, concept, or keyword
"""

import streamlit as st
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.config import init_session_state, render_api_key_sidebar
from services.ai_analyzer import ai_analyzer
from components.header import render_page_header
from components.footer import render_compact_footer

# Page config
st.set_page_config(
    page_title="Custom Search | Q-Classify",
    page_icon="🔎",
    layout="wide"
)

# Initialize session state
init_session_state()

# Custom CSS
st.markdown("""
<style>
    .search-box {
        background: linear-gradient(145deg, #2D2D44, #1E1E2E);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid #4A90D9;
    }
    .result-card {
        background: linear-gradient(145deg, #2D2D44, #1E1E2E);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.75rem 0;
        border-left: 4px solid #9B59B6;
        transition: all 0.3s ease;
    }
    .result-card:hover {
        border-left-color: #2ECC71;
        transform: translateX(5px);
    }
    .highlight {
        background: rgba(155, 89, 182, 0.3);
        padding: 2px 5px;
        border-radius: 3px;
    }
    .filter-tag {
        display: inline-block;
        background: #4A90D9;
        color: white;
        padding: 5px 12px;
        border-radius: 15px;
        margin: 3px;
        font-size: 0.85rem;
    }
    .no-results {
        text-align: center;
        padding: 3rem;
        color: #888;
    }
</style>
""", unsafe_allow_html=True)

# Page Header
render_page_header(
    "Custom Search",
    "🔎",
    "Find questions based on chapters, concepts, or keywords"
)

# Check prerequisites
if not st.session_state.questions_data:
    st.warning("⚠️ Please complete the question analysis first")
    if st.button("🔍 Go to Analysis Page"):
        st.switch_page("pages/2_🔍_Analysis.py")
    st.stop()

questions_data = st.session_state.questions_data

# ==================== SEARCH INTERFACE ====================
st.markdown("### 🔍 Search Filters")

# Extract unique values for filters
chapters = sorted(set(q.get('chapter', 'Unknown') for q in questions_data))
all_concepts = []
for q in questions_data:
    all_concepts.extend(q.get('concepts', []))
concepts = sorted(set(all_concepts))
sources = sorted(set(q.get('source', '') for q in questions_data if q.get('source')))
years = sorted(set(q.get('year') for q in questions_data if q.get('year')))

# Search inputs
col1, col2 = st.columns([2, 1])

with col1:
    search_query = st.text_input(
        "🔍 Search Keywords",
        placeholder="Enter keywords to search in questions...",
        help="Search for text in question content, concepts, or chapters"
    )

with col2:
    search_button = st.button("Search", type="primary", width="stretch")

# Filters
st.markdown("#### Filters")

col1, col2, col3, col4 = st.columns(4)

with col1:
    filter_chapter = st.selectbox(
        "📚 Chapter",
        ["All Chapters"] + chapters
    )

with col2:
    filter_concept = st.selectbox(
        "🎯 Concept",
        ["All Concepts"] + concepts
    )

with col3:
    filter_difficulty = st.selectbox(
        "📊 Difficulty",
        ["All Levels", "Easy", "Medium", "Hard"]
    )

with col4:
    if years:
        filter_year = st.selectbox(
            "📅 Year",
            ["All Years"] + [str(y) for y in years]
        )
    else:
        filter_year = "All Years"
        st.selectbox("📅 Year", ["All Years"], disabled=True)

# ==================== SEARCH LOGIC ====================
def search_questions(questions, query, chapter, concept, difficulty, year):
    """Filter questions based on search criteria"""
    results = []
    
    query_lower = query.lower() if query else ""
    
    for q in questions:
        # Chapter filter
        if chapter != "All Chapters" and q.get('chapter') != chapter:
            continue
        
        # Concept filter
        if concept != "All Concepts" and concept not in q.get('concepts', []):
            continue
        
        # Difficulty filter
        if difficulty != "All Levels" and q.get('difficulty') != difficulty:
            continue
        
        # Year filter
        if year != "All Years":
            q_year = q.get('year')
            if str(q_year) != year:
                continue
        
        # Text search
        if query_lower:
            q_text = q.get('question', q.get('question_text', '')).lower()
            q_concepts = ' '.join(q.get('concepts', [])).lower()
            q_chapter = q.get('chapter', '').lower()
            
            if not (query_lower in q_text or 
                   query_lower in q_concepts or 
                   query_lower in q_chapter):
                continue
        
        results.append(q)
    
    return results

# Perform search
results = search_questions(
    questions_data,
    search_query,
    filter_chapter,
    filter_concept,
    filter_difficulty,
    filter_year
)

# ==================== ACTIVE FILTERS DISPLAY ====================
active_filters = []
if filter_chapter != "All Chapters":
    active_filters.append(f"Chapter: {filter_chapter}")
if filter_concept != "All Concepts":
    active_filters.append(f"Concept: {filter_concept}")
if filter_difficulty != "All Levels":
    active_filters.append(f"Difficulty: {filter_difficulty}")
if filter_year != "All Years":
    active_filters.append(f"Year: {filter_year}")
if search_query:
    active_filters.append(f"Search: '{search_query}'")

if active_filters:
    st.markdown("**Active Filters:**")
    filters_html = ' '.join([f'<span class="filter-tag">{f}</span>' for f in active_filters])
    st.markdown(f'<div>{filters_html}</div>', unsafe_allow_html=True)

st.markdown("---")

# ==================== RESULTS DISPLAY ====================
st.markdown(f"### 📋 Results ({len(results)} questions found)")

if results:
    # Sort options
    col1, col2 = st.columns([3, 1])
    with col2:
        sort_by = st.selectbox(
            "Sort by",
            ["Default", "Difficulty (Easy first)", "Difficulty (Hard first)", "Chapter"]
        )
    
    # Apply sorting
    if sort_by == "Difficulty (Easy first)":
        diff_order = {'Easy': 1, 'Medium': 2, 'Hard': 3}
        results = sorted(results, key=lambda x: diff_order.get(x.get('difficulty', 'Medium'), 2))
    elif sort_by == "Difficulty (Hard first)":
        diff_order = {'Easy': 3, 'Medium': 2, 'Hard': 1}
        results = sorted(results, key=lambda x: diff_order.get(x.get('difficulty', 'Medium'), 2))
    elif sort_by == "Chapter":
        results = sorted(results, key=lambda x: x.get('chapter', 'Unknown'))
    
    # Display results
    for i, q in enumerate(results, 1):
        question_text = q.get('question', q.get('question_text', 'N/A'))
        chapter = q.get('chapter', 'Unknown')
        difficulty = q.get('difficulty', 'Medium')
        concepts = q.get('concepts', [])
        source = q.get('source', '')
        year = q.get('year', '')
        
        # Highlight search term
        display_text = question_text
        if search_query:
            import re
            pattern = re.compile(re.escape(search_query), re.IGNORECASE)
            display_text = pattern.sub(f'<span class="highlight">{search_query}</span>', display_text)
        
        # Difficulty color
        diff_colors = {'Easy': '#2ECC71', 'Medium': '#F39C12', 'Hard': '#E74C3C'}
        diff_color = diff_colors.get(difficulty, '#888')
        
        # Concepts HTML
        concepts_html = ' '.join([
            f'<span style="background: #9B59B6; color: white; padding: 2px 8px; border-radius: 10px; font-size: 0.75rem; margin: 2px;">{c}</span>'
            for c in concepts
        ])
        
        # Source info
        source_info = source
        if year:
            source_info = f"{source} ({year})"
        
        with st.expander(f"**Q{i}** | {chapter} | {difficulty}", expanded=False):
            st.markdown(f"""
            <div class="result-card">
                <p style="color: #E0E0E0; font-size: 1rem; line-height: 1.6;">
                    {display_text[:800]}{'...' if len(question_text) > 800 else ''}
                </p>
                <div style="margin-top: 15px; display: flex; flex-wrap: wrap; gap: 10px; align-items: center;">
                    <span style="background: #4A90D9; color: white; padding: 4px 12px; border-radius: 15px; font-size: 0.85rem;">
                        📚 {chapter}
                    </span>
                    <span style="background: {diff_color}; color: white; padding: 4px 12px; border-radius: 15px; font-size: 0.85rem;">
                        {difficulty}
                    </span>
                    {f'<span style="color: #888; font-size: 0.85rem;">📄 {source_info}</span>' if source_info else ''}
                </div>
                <div style="margin-top: 10px;">
                    {concepts_html if concepts_html else '<span style="color: #666; font-size: 0.8rem;">No concepts identified</span>'}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Export results
    st.markdown("---")
    if st.button("📥 Export Search Results", width="content"):
        import json
        json_data = json.dumps(results, indent=2, default=str)
        st.download_button(
            label="⬇️ Download JSON",
            data=json_data,
            file_name="QClassify_SearchResults.json",
            mime="application/json"
        )

else:
    st.markdown("""
    <div class="no-results">
        <h3 style="color: #888;">🔍 No Results Found</h3>
        <p>Try adjusting your search filters or keywords</p>
    </div>
    """, unsafe_allow_html=True)

# ==================== QUICK SEARCH SUGGESTIONS ====================
st.markdown("---")
st.markdown("### 💡 Quick Searches")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**🔴 Hard Questions**")
    hard_count = len([q for q in questions_data if q.get('difficulty') == 'Hard'])
    if st.button(f"View {hard_count} Hard Questions"):
        st.session_state['quick_filter'] = 'Hard'
        st.rerun()

with col2:
    if concepts:
        st.markdown("**🎯 Top Concept**")
        concept_counts = {}
        for q in questions_data:
            for c in q.get('concepts', []):
                concept_counts[c] = concept_counts.get(c, 0) + 1
        if concept_counts:
            top_concept = max(concept_counts, key=concept_counts.get)
            if st.button(f"View '{top_concept[:20]}...' Questions"):
                st.session_state['quick_filter'] = top_concept
                st.rerun()

with col3:
    if years:
        st.markdown("**📅 Latest Year**")
        latest_year = max(years)
        year_count = len([q for q in questions_data if q.get('year') == latest_year])
        if st.button(f"View {latest_year} Papers ({year_count} Q)"):
            st.session_state['quick_filter'] = str(latest_year)
            st.rerun()

# Sidebar - API Key Settings
render_api_key_sidebar()

# Sidebar - Stats
with st.sidebar:
    st.markdown("### 📊 Search Stats")
    st.metric("Total Questions", len(questions_data))
    st.metric("Results Found", len(results))
    
    st.markdown("---")
    st.markdown("### 📚 Chapters")
    for ch in chapters[:5]:
        count = len([q for q in questions_data if q.get('chapter') == ch])
        st.markdown(f"- {ch[:25]}... ({count})")
    if len(chapters) > 5:
        st.markdown(f"*...and {len(chapters) - 5} more*")

# Footer
render_compact_footer()
