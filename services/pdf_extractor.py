"""
Q-Classify PDF Extractor Service
Extracts text from PDF files using pdfplumber (primary) with PyPDF2 fallback
"""

import io
from typing import Optional, List, Dict, Any
from pathlib import Path


class PDFExtractor:
    """
    PDF text extraction service
    Uses pdfplumber as primary extractor with PyPDF2 as fallback
    """
    
    def __init__(self):
        self.pdfplumber_available = self._check_pdfplumber()
        self.pypdf2_available = self._check_pypdf2()
    
    def _check_pdfplumber(self) -> bool:
        """Check if pdfplumber is available"""
        try:
            import pdfplumber
            return True
        except ImportError:
            return False
    
    def _check_pypdf2(self) -> bool:
        """Check if PyPDF2 is available"""
        try:
            import PyPDF2
            return True
        except ImportError:
            return False
    
    def extract_text(self, file_content: bytes, filename: str = "document.pdf") -> Dict[str, Any]:
        """
        Extract text from PDF file content
        
        Args:
            file_content: PDF file as bytes
            filename: Original filename for reference
            
        Returns:
            Dict with 'success', 'text', 'pages', 'method', 'error'
        """
        result = {
            'success': False,
            'text': '',
            'pages': [],
            'page_count': 0,
            'method': None,
            'error': None,
            'filename': filename
        }
        
        # Try pdfplumber first
        if self.pdfplumber_available:
            try:
                result = self._extract_with_pdfplumber(file_content, filename)
                if result['success'] and result['text'].strip():
                    return result
            except Exception as e:
                result['error'] = f"pdfplumber error: {str(e)}"
        
        # Fallback to PyPDF2
        if self.pypdf2_available:
            try:
                result = self._extract_with_pypdf2(file_content, filename)
                if result['success']:
                    return result
            except Exception as e:
                result['error'] = f"PyPDF2 error: {str(e)}"
        
        # Both failed
        if not result['success']:
            result['error'] = result.get('error', 'No PDF extraction library available')
        
        return result
    
    def _extract_with_pdfplumber(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Extract text using pdfplumber (better for tables and structured content)"""
        import pdfplumber
        
        result = {
            'success': False,
            'text': '',
            'pages': [],
            'page_count': 0,
            'method': 'pdfplumber',
            'error': None,
            'filename': filename
        }
        
        try:
            with pdfplumber.open(io.BytesIO(file_content)) as pdf:
                result['page_count'] = len(pdf.pages)
                
                for i, page in enumerate(pdf.pages):
                    page_text = page.extract_text() or ''
                    result['pages'].append({
                        'page_num': i + 1,
                        'text': page_text
                    })
                
                # Combine all pages
                result['text'] = '\n\n'.join([p['text'] for p in result['pages']])
                result['success'] = True
                
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def _extract_with_pypdf2(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Extract text using PyPDF2 (fallback for simpler PDFs)"""
        import PyPDF2
        
        result = {
            'success': False,
            'text': '',
            'pages': [],
            'page_count': 0,
            'method': 'PyPDF2',
            'error': None,
            'filename': filename
        }
        
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
            result['page_count'] = len(pdf_reader.pages)
            
            for i, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text() or ''
                result['pages'].append({
                    'page_num': i + 1,
                    'text': page_text
                })
            
            # Combine all pages
            result['text'] = '\n\n'.join([p['text'] for p in result['pages']])
            result['success'] = True
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def extract_tables(self, file_content: bytes) -> List[List[List[str]]]:
        """
        Extract tables from PDF (pdfplumber only)
        
        Returns:
            List of tables, where each table is a list of rows
        """
        if not self.pdfplumber_available:
            return []
        
        import pdfplumber
        
        tables = []
        try:
            with pdfplumber.open(io.BytesIO(file_content)) as pdf:
                for page in pdf.pages:
                    page_tables = page.extract_tables()
                    if page_tables:
                        tables.extend(page_tables)
        except Exception:
            pass
        
        return tables
    
    def get_metadata(self, file_content: bytes) -> Dict[str, Any]:
        """Extract PDF metadata"""
        metadata = {
            'title': None,
            'author': None,
            'subject': None,
            'creator': None,
            'creation_date': None
        }
        
        if self.pypdf2_available:
            try:
                import PyPDF2
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
                if pdf_reader.metadata:
                    metadata['title'] = pdf_reader.metadata.get('/Title')
                    metadata['author'] = pdf_reader.metadata.get('/Author')
                    metadata['subject'] = pdf_reader.metadata.get('/Subject')
                    metadata['creator'] = pdf_reader.metadata.get('/Creator')
            except Exception:
                pass
        
        return metadata
    
    def validate_pdf(self, file_content: bytes) -> Dict[str, Any]:
        """
        Validate if the file is a valid PDF
        
        Returns:
            Dict with 'valid', 'page_count', 'error'
        """
        result = {
            'valid': False,
            'page_count': 0,
            'error': None
        }
        
        # Check PDF magic bytes
        if not file_content.startswith(b'%PDF'):
            result['error'] = 'File is not a valid PDF'
            return result
        
        # Try to read the PDF
        if self.pypdf2_available:
            try:
                import PyPDF2
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
                result['page_count'] = len(pdf_reader.pages)
                result['valid'] = True
            except Exception as e:
                result['error'] = f'Invalid PDF: {str(e)}'
        elif self.pdfplumber_available:
            try:
                import pdfplumber
                with pdfplumber.open(io.BytesIO(file_content)) as pdf:
                    result['page_count'] = len(pdf.pages)
                    result['valid'] = True
            except Exception as e:
                result['error'] = f'Invalid PDF: {str(e)}'
        else:
            result['error'] = 'No PDF library available'
        
        return result


# Singleton instance
pdf_extractor = PDFExtractor()
