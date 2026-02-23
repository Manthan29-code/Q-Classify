"""
Q-Classify Helper Utilities
Common helper functions used throughout the application
"""

import re
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any


def clean_text(text: str) -> str:
    """
    Clean extracted text from PDF
    - Remove excessive whitespace
    - Fix common OCR errors
    - Normalize line breaks
    """
    if not text:
        return ""
    
    # Replace multiple spaces with single space
    text = re.sub(r' +', ' ', text)
    
    # Replace multiple newlines with double newline
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Remove leading/trailing whitespace from each line
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)
    
    # Remove non-printable characters except newlines and tabs
    text = re.sub(r'[^\x20-\x7E\n\t]', '', text)
    
    return text.strip()


def format_difficulty(difficulty: str) -> Dict[str, str]:
    """
    Format difficulty level with color coding
    Returns dict with 'text', 'color', 'emoji'
    """
    difficulty_map = {
        'easy': {
            'text': 'Easy',
            'color': '#2ECC71',
            'emoji': '🟢'
        },
        'medium': {
            'text': 'Medium',
            'color': '#F39C12',
            'emoji': '🟡'
        },
        'hard': {
            'text': 'Hard',
            'color': '#E74C3C',
            'emoji': '🔴'
        }
    }
    
    return difficulty_map.get(difficulty.lower(), difficulty_map['medium'])


def get_download_path(filename: str) -> Path:
    """
    Get the user's default download path
    Falls back to current directory if unable to determine
    """
    # Try to get user's Downloads folder
    if os.name == 'nt':  # Windows
        download_path = Path.home() / "Downloads"
    else:  # macOS/Linux
        download_path = Path.home() / "Downloads"
    
    if not download_path.exists():
        download_path = Path.cwd()
    
    return download_path / filename


def extract_year_from_filename(filename: str) -> Optional[int]:
    """
    Extract year from question paper filename
    Looks for 4-digit year patterns (2000-2099)
    """
    # Look for year patterns
    year_pattern = r'(20[0-9]{2}|19[9][0-9])'
    match = re.search(year_pattern, filename)
    
    if match:
        return int(match.group(1))
    return None


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"


def generate_report_filename() -> str:
    """Generate unique filename for PDF report"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"QClassify_Report_{timestamp}.pdf"


def create_chapter_mapping(syllabus_text: str) -> List[Dict[str, Any]]:
    """
    Extract chapter structure from syllabus text
    Returns list of chapters with their topics
    """
    chapters = []
    
    # Common chapter patterns
    chapter_patterns = [
        r'(?:Chapter|Unit|Module)\s*(\d+)[.:]\s*(.+?)(?=(?:Chapter|Unit|Module)\s*\d+|$)',
        r'(\d+)\.\s*([A-Z][^0-9]+?)(?=\d+\.|$)',
    ]
    
    for pattern in chapter_patterns:
        matches = re.findall(pattern, syllabus_text, re.DOTALL | re.IGNORECASE)
        if matches:
            for num, content in matches:
                # Extract chapter title (first line) and topics
                lines = content.strip().split('\n')
                title = lines[0].strip() if lines else f"Chapter {num}"
                topics = [line.strip() for line in lines[1:] if line.strip()]
                
                chapters.append({
                    'number': int(num),
                    'title': clean_text(title),
                    'topics': topics,
                    'content': clean_text(content)
                })
            break
    
    return chapters


def calculate_concept_frequency(questions_data: List[Dict]) -> Dict[str, int]:
    """
    Calculate frequency of concepts across all questions
    """
    concept_freq = {}
    
    for q in questions_data:
        concepts = q.get('concepts', [])
        for concept in concepts:
            concept_freq[concept] = concept_freq.get(concept, 0) + 1
    
    return dict(sorted(concept_freq.items(), key=lambda x: x[1], reverse=True))


def calculate_chapter_frequency(questions_data: List[Dict]) -> Dict[str, int]:
    """
    Calculate frequency of questions per chapter
    """
    chapter_freq = {}
    
    for q in questions_data:
        chapter = q.get('chapter', 'Unknown')
        chapter_freq[chapter] = chapter_freq.get(chapter, 0) + 1
    
    return dict(sorted(chapter_freq.items(), key=lambda x: x[1], reverse=True))
