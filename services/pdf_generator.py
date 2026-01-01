"""
Q-Classify PDF Report Generator
Generates structured PDF reports using ReportLab
"""

import io
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path


class PDFReportGenerator:
    """
    PDF Report Generator for Q-Classify
    Creates structured analysis reports with questions, chapters, concepts, and difficulty
    """
    
    def __init__(self):
        self.reportlab_available = self._check_reportlab()
        
        # Theme colors
        self.PRIMARY_COLOR = (0.29, 0.56, 0.85)    # #4A90D9
        self.SECONDARY_COLOR = (0.18, 0.80, 0.44)  # #2ECC71
        self.ACCENT_COLOR = (0.61, 0.35, 0.71)     # #9B59B6
        self.TEXT_COLOR = (0.2, 0.2, 0.2)
        self.LIGHT_GRAY = (0.95, 0.95, 0.95)
    
    def _check_reportlab(self) -> bool:
        """Check if reportlab is available"""
        try:
            from reportlab.lib.pagesizes import A4
            return True
        except ImportError:
            return False
    
    def generate_report(
        self,
        questions_data: List[Dict[str, Any]],
        syllabus_summary: Optional[str] = None,
        trend_summary: Optional[Dict[str, Any]] = None,
        filename: str = "QClassify_Report.pdf"
    ) -> bytes:
        """
        Generate a comprehensive PDF report
        
        Args:
            questions_data: List of analyzed questions with chapter, concepts, difficulty
            syllabus_summary: Optional summary of the syllabus
            trend_summary: Optional trend analysis data
            filename: Output filename (for metadata)
            
        Returns:
            PDF file as bytes
        """
        if not self.reportlab_available:
            raise ImportError("ReportLab is not installed. Run: pip install reportlab")
        
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch, cm
        from reportlab.lib import colors
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
            PageBreak, ListFlowable, ListItem
        )
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
        
        # Create buffer
        buffer = io.BytesIO()
        
        # Create document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=1.5*cm,
            leftMargin=1.5*cm,
            topMargin=2*cm,
            bottomMargin=2*cm,
            title="Q-Classify Analysis Report",
            author="Q-Classify AI"
        )
        
        # Styles
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=24,
            textColor=colors.HexColor('#4A90D9'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#9B59B6'),
            spaceBefore=20,
            spaceAfter=12
        )
        
        subheading_style = ParagraphStyle(
            'CustomSubheading',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#2ECC71'),
            spaceBefore=10,
            spaceAfter=6
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#333333'),
            alignment=TA_JUSTIFY,
            spaceAfter=8
        )
        
        # Build story
        story = []
        
        # Title Page
        story.append(Spacer(1, 2*inch))
        story.append(Paragraph("🎓 Q-Classify", title_style))
        story.append(Paragraph("AI-Powered Question Analysis Report", ParagraphStyle(
            'Subtitle',
            parent=styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#666666'),
            alignment=TA_CENTER,
            spaceAfter=40
        )))
        
        # Report info
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}", ParagraphStyle(
            'Info',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#888888'),
            alignment=TA_CENTER
        )))
        story.append(Paragraph(f"Total Questions Analyzed: {len(questions_data)}", ParagraphStyle(
            'Info',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#888888'),
            alignment=TA_CENTER,
            spaceBefore=10
        )))
        
        story.append(PageBreak())
        
        # Table of Contents header
        story.append(Paragraph("📋 Report Contents", heading_style))
        toc_items = [
            "1. Executive Summary",
            "2. Question Analysis",
            "3. Chapter Distribution",
            "4. Difficulty Analysis",
        ]
        if syllabus_summary:
            toc_items.append("5. Syllabus Summary")
        if trend_summary:
            toc_items.append("6. Trend Analysis")
        
        for item in toc_items:
            story.append(Paragraph(f"• {item}", body_style))
        
        story.append(Spacer(1, 0.5*inch))
        
        # Executive Summary
        story.append(Paragraph("1. Executive Summary", heading_style))
        
        # Calculate statistics
        total_questions = len(questions_data)
        chapters = set(q.get('chapter', 'Unknown') for q in questions_data)
        difficulties = {'Easy': 0, 'Medium': 0, 'Hard': 0}
        all_concepts = []
        
        for q in questions_data:
            diff = q.get('difficulty', 'Medium')
            difficulties[diff] = difficulties.get(diff, 0) + 1
            all_concepts.extend(q.get('concepts', []))
        
        unique_concepts = len(set(all_concepts))
        
        summary_text = f"""
        This report analyzes <b>{total_questions}</b> questions from the uploaded question papers.
        The questions span <b>{len(chapters)}</b> chapters and cover <b>{unique_concepts}</b> unique concepts.
        <br/><br/>
        <b>Difficulty Distribution:</b><br/>
        • Easy: {difficulties.get('Easy', 0)} questions ({round(difficulties.get('Easy', 0)/max(total_questions,1)*100)}%)<br/>
        • Medium: {difficulties.get('Medium', 0)} questions ({round(difficulties.get('Medium', 0)/max(total_questions,1)*100)}%)<br/>
        • Hard: {difficulties.get('Hard', 0)} questions ({round(difficulties.get('Hard', 0)/max(total_questions,1)*100)}%)
        """
        story.append(Paragraph(summary_text, body_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Question Analysis Section
        story.append(Paragraph("2. Detailed Question Analysis", heading_style))
        
        for i, q in enumerate(questions_data, 1):
            # Question header
            story.append(Paragraph(f"<b>Question {i}</b>", subheading_style))
            
            # Question text (truncated if too long)
            q_text = q.get('question', 'N/A')
            if len(q_text) > 500:
                q_text = q_text[:500] + "..."
            story.append(Paragraph(f"<i>{q_text}</i>", body_style))
            
            # Create info table
            info_data = [
                ['Chapter:', q.get('chapter', 'Unknown')],
                ['Difficulty:', q.get('difficulty', 'Medium')],
                ['Concepts:', ', '.join(q.get('concepts', ['N/A']))],
            ]
            
            if q.get('year'):
                info_data.append(['Year:', str(q.get('year'))])
            
            info_table = Table(info_data, colWidths=[2*cm, 12*cm])
            info_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#4A90D9')),
                ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#333333')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            story.append(info_table)
            story.append(Spacer(1, 0.2*inch))
            
            # Add page break every 5 questions
            if i % 5 == 0 and i < total_questions:
                story.append(PageBreak())
        
        # Chapter Distribution
        story.append(PageBreak())
        story.append(Paragraph("3. Chapter Distribution", heading_style))
        
        chapter_counts = {}
        for q in questions_data:
            ch = q.get('chapter', 'Unknown')
            chapter_counts[ch] = chapter_counts.get(ch, 0) + 1
        
        chapter_data = [['Chapter', 'Questions', 'Percentage']]
        for ch, count in sorted(chapter_counts.items(), key=lambda x: x[1], reverse=True):
            pct = round(count / max(total_questions, 1) * 100)
            chapter_data.append([ch, str(count), f"{pct}%"])
        
        chapter_table = Table(chapter_data, colWidths=[8*cm, 3*cm, 3*cm])
        chapter_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4A90D9')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CCCCCC')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(chapter_table)
        
        # Difficulty Analysis
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph("4. Difficulty Analysis", heading_style))
        
        diff_data = [['Difficulty Level', 'Count', 'Percentage']]
        diff_colors = {'Easy': '#2ECC71', 'Medium': '#F39C12', 'Hard': '#E74C3C'}
        
        for diff in ['Easy', 'Medium', 'Hard']:
            count = difficulties.get(diff, 0)
            pct = round(count / max(total_questions, 1) * 100)
            diff_data.append([diff, str(count), f"{pct}%"])
        
        diff_table = Table(diff_data, colWidths=[6*cm, 4*cm, 4*cm])
        diff_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9B59B6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CCCCCC')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(diff_table)
        
        # Syllabus Summary (if provided)
        if syllabus_summary:
            story.append(PageBreak())
            story.append(Paragraph("5. Syllabus Summary", heading_style))
            story.append(Paragraph(syllabus_summary, body_style))
        
        # Trend Analysis (if provided)
        if trend_summary:
            story.append(PageBreak())
            section_num = "6" if syllabus_summary else "5"
            story.append(Paragraph(f"{section_num}. Trend Analysis", heading_style))
            
            if 'top_concepts' in trend_summary:
                story.append(Paragraph("<b>Most Frequently Tested Concepts:</b>", body_style))
                for concept, count in trend_summary['top_concepts'][:10]:
                    story.append(Paragraph(f"• {concept}: {count} times", body_style))
        
        # Footer
        story.append(Spacer(1, inch))
        story.append(Paragraph(
            "Generated by Q-Classify | AI-Powered Question Analysis",
            ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, 
                         textColor=colors.HexColor('#999999'), alignment=TA_CENTER)
        ))
        
        # Build PDF
        doc.build(story)
        
        # Get PDF bytes
        buffer.seek(0)
        return buffer.getvalue()
    
    def generate_simple_report(
        self,
        questions_data: List[Dict[str, Any]]
    ) -> bytes:
        """Generate a simplified report with just questions and mappings"""
        return self.generate_report(questions_data)


# Singleton instance
pdf_generator = PDFReportGenerator()
