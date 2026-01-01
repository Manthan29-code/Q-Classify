"""
Q-Classify AI Analyzer Service
Uses LangChain + Google Gemini for intelligent question analysis
"""

import os
import json
import re
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()


class AIAnalyzer:
    """
    AI-powered analyzer using LangChain and Google Gemini
    Handles question mapping, difficulty estimation, and concept extraction
    """
    
    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None, temperature: Optional[float] = None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.model_name = model_name or os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
        self.temperature = temperature if temperature is not None else float(os.getenv("GEMINI_TEMPERATURE", "0.3"))
        self._llm = None
    
    def set_model(self, model_name: str):
        """Change the model and reset LLM instance"""
        self.model_name = model_name
        self._llm = None  # Reset to reinitialize with new model
    
    def set_temperature(self, temperature: float):
        """Change temperature and reset LLM instance"""
        self.temperature = temperature
        self._llm = None
    
    def get_current_model(self) -> str:
        """Get the currently configured model name"""
        return self.model_name
    
    @property
    def llm(self):
        """Lazy initialization of LLM"""
        if self._llm is None:
            self._llm = self._initialize_llm()
        return self._llm
    
    def _initialize_llm(self):
        """Initialize the Gemini LLM through LangChain"""
        if not self.api_key:
            raise ValueError("Google API key not found. Please set GOOGLE_API_KEY in .env file")
        
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            
            return ChatGoogleGenerativeAI(
                model=self.model_name,
                google_api_key=self.api_key,
                temperature=self.temperature,
                convert_system_message_to_human=True
            )
        except ImportError:
            raise ImportError(
                "langchain-google-genai is not installed. "
                "Run: pip install langchain-google-genai"
            )
    
    def analyze_questions(
        self,
        questions: List[str],
        syllabus_text: str,
        syllabus_chapters: Optional[List[Dict]] = None
    ) -> List[Dict[str, Any]]:
        """
        Analyze questions and map them to syllabus chapters/concepts
        
        Args:
            questions: List of question texts
            syllabus_text: Full syllabus text
            syllabus_chapters: Optional pre-extracted chapter structure
            
        Returns:
            List of analyzed questions with chapter, concepts, difficulty
        """
        from langchain_core.prompts import PromptTemplate
        from langchain_core.output_parsers import StrOutputParser
        
        # Create analysis prompt
        analysis_prompt = PromptTemplate(
            input_variables=["syllabus", "questions"],
            template="""You are an expert educational content analyzer. Analyze the following exam questions and map them to the provided syllabus.

SYLLABUS:
{syllabus}

QUESTIONS TO ANALYZE:
{questions}

For each question, provide analysis in the following JSON format:
{{
    "questions": [
        {{
            "question_number": 1,
            "question_text": "original question text",
            "chapter": "Chapter name/number from syllabus",
            "concepts": ["concept1", "concept2"],
            "difficulty": "Easy|Medium|Hard",
            "explanation": "Brief explanation of why this maps to this chapter and concepts"
        }}
    ]
}}

IMPORTANT GUIDELINES:
1. Chapter must match exactly or closely to a chapter/unit from the syllabus
2. Concepts should be specific topics from the syllabus needed to solve the question
3. Difficulty estimation:
   - Easy: Direct recall, single concept, straightforward application
   - Medium: Multiple concepts, some analysis required, moderate application
   - Hard: Complex reasoning, multiple concepts integration, deep understanding
4. If a question doesn't clearly match any chapter, use "General" or the closest match
5. List 1-4 most relevant concepts per question

Respond ONLY with the JSON object, no additional text."""
        )
        
        # Format questions for prompt
        formatted_questions = "\n".join([
            f"Q{i+1}: {q}" for i, q in enumerate(questions)
        ])
        
        # Run analysis using LCEL
        try:
            chain = analysis_prompt | self.llm | StrOutputParser()
            response = chain.invoke({"syllabus": syllabus_text, "questions": formatted_questions})
            
            # Parse JSON response
            results = self._parse_json_response(response)
            return results.get('questions', [])
            
        except Exception as e:
            # Return basic structure on error
            return [{
                'question_number': i + 1,
                'question_text': q,
                'chapter': 'Analysis Error',
                'concepts': [],
                'difficulty': 'Medium',
                'explanation': f'Error during analysis: {str(e)}'
            } for i, q in enumerate(questions)]
    
    def estimate_difficulty(self, question: str, syllabus_context: str) -> Dict[str, Any]:
        """
        Estimate difficulty level of a single question
        
        Returns:
            Dict with 'difficulty', 'reasoning', 'factors'
        """
        from langchain_core.prompts import PromptTemplate
        from langchain_core.output_parsers import StrOutputParser
        
        difficulty_prompt = PromptTemplate(
            input_variables=["question", "syllabus"],
            template="""Analyze the difficulty of this exam question based on the syllabus context.

SYLLABUS CONTEXT:
{syllabus}

QUESTION:
{question}

Evaluate based on:
1. Cognitive level (recall, understand, apply, analyze, evaluate, create)
2. Number of concepts required
3. Complexity of reasoning needed
4. Prior knowledge requirements

Respond in JSON format:
{{
    "difficulty": "Easy|Medium|Hard",
    "cognitive_level": "level",
    "concepts_required": ["concept1", "concept2"],
    "reasoning": "brief explanation",
    "confidence": 0.0-1.0
}}

Respond ONLY with JSON."""
        )
        
        try:
            chain = difficulty_prompt | self.llm | StrOutputParser()
            response = chain.invoke({"question": question, "syllabus": syllabus_context})
            return self._parse_json_response(response)
        except Exception as e:
            return {
                'difficulty': 'Medium',
                'reasoning': f'Error: {str(e)}',
                'confidence': 0.0
            }
    
    def generate_syllabus_summary(self, syllabus_text: str) -> str:
        """
        Generate a concise summary of the syllabus for quick revision
        """
        from langchain_core.prompts import PromptTemplate
        from langchain_core.output_parsers import StrOutputParser
        
        summary_prompt = PromptTemplate(
            input_variables=["syllabus"],
            template="""Create a comprehensive yet concise summary of this syllabus for quick student revision.

SYLLABUS:
{syllabus}

Structure your summary as:
1. **Course Overview**: Brief description of the subject (2-3 sentences)
2. **Main Topics**: List the main chapters/units with key points
3. **Key Concepts**: Most important concepts to master
4. **Study Tips**: Brief recommendations for studying this material

Keep the summary clear, well-organized, and helpful for exam preparation.
Use bullet points and clear formatting."""
        )
        
        try:
            chain = summary_prompt | self.llm | StrOutputParser()
            return chain.invoke({"syllabus": syllabus_text})
        except Exception as e:
            return f"Error generating summary: {str(e)}"
    
    def extract_concepts_relationships(
        self,
        syllabus_text: str,
        questions_data: List[Dict]
    ) -> Dict[str, Any]:
        """
        Extract concept relationships for concept mapping visualization
        
        Returns:
            Dict with 'nodes', 'edges' for graph visualization
        """
        from langchain_core.prompts import PromptTemplate
        from langchain_core.output_parsers import StrOutputParser
        
        concept_prompt = PromptTemplate(
            input_variables=["syllabus", "concepts"],
            template="""Analyze the relationships between concepts from this syllabus and question analysis.

SYLLABUS:
{syllabus}

CONCEPTS FROM QUESTIONS:
{concepts}

Create a concept map showing relationships. Respond in JSON:
{{
    "nodes": [
        {{"id": "concept_name", "type": "chapter|concept|topic", "importance": 1-10}}
    ],
    "edges": [
        {{"source": "concept1", "target": "concept2", "relationship": "requires|related|part_of"}}
    ]
}}

Include:
- Main chapters as parent nodes
- Key concepts as child nodes  
- Relationships showing prerequisites and connections
- Importance based on frequency in questions

Respond ONLY with JSON."""
        )
        
        # Extract unique concepts from questions
        all_concepts = []
        for q in questions_data:
            all_concepts.extend(q.get('concepts', []))
            all_concepts.append(q.get('chapter', ''))
        
        unique_concepts = list(set([c for c in all_concepts if c]))
        
        try:
            chain = concept_prompt | self.llm | StrOutputParser()
            response = chain.invoke({
                "syllabus": syllabus_text,
                "concepts": ", ".join(unique_concepts)
            })
            return self._parse_json_response(response)
        except Exception as e:
            # Return basic structure on error
            return {
                'nodes': [{'id': c, 'type': 'concept', 'importance': 5} for c in unique_concepts],
                'edges': [],
                'error': str(e)
            }
    
    def identify_trends(
        self,
        questions_data: List[Dict],
        by_year: bool = True
    ) -> Dict[str, Any]:
        """
        Identify trends in question patterns
        
        Returns:
            Dict with 'top_concepts', 'chapter_frequency', 'difficulty_distribution', 'yearly_trends'
        """
        # Aggregate concept frequency
        concept_freq = {}
        chapter_freq = {}
        difficulty_dist = {'Easy': 0, 'Medium': 0, 'Hard': 0}
        yearly_data = {}
        
        for q in questions_data:
            # Concepts
            for concept in q.get('concepts', []):
                concept_freq[concept] = concept_freq.get(concept, 0) + 1
            
            # Chapters
            chapter = q.get('chapter', 'Unknown')
            chapter_freq[chapter] = chapter_freq.get(chapter, 0) + 1
            
            # Difficulty
            diff = q.get('difficulty', 'Medium')
            difficulty_dist[diff] = difficulty_dist.get(diff, 0) + 1
            
            # Yearly (if available)
            year = q.get('year')
            if year:
                if year not in yearly_data:
                    yearly_data[year] = {'chapters': {}, 'concepts': {}}
                yearly_data[year]['chapters'][chapter] = yearly_data[year]['chapters'].get(chapter, 0) + 1
                for concept in q.get('concepts', []):
                    yearly_data[year]['concepts'][concept] = yearly_data[year]['concepts'].get(concept, 0) + 1
        
        # Sort by frequency
        top_concepts = sorted(concept_freq.items(), key=lambda x: x[1], reverse=True)
        top_chapters = sorted(chapter_freq.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'top_concepts': top_concepts,
            'top_chapters': top_chapters,
            'difficulty_distribution': difficulty_dist,
            'yearly_trends': yearly_data if by_year else {},
            'total_questions': len(questions_data)
        }
    
    def search_questions(
        self,
        questions_data: List[Dict],
        query: str,
        filter_chapter: Optional[str] = None,
        filter_concept: Optional[str] = None,
        filter_difficulty: Optional[str] = None
    ) -> List[Dict]:
        """
        Search and filter questions based on criteria
        """
        results = []
        
        query_lower = query.lower() if query else ""
        
        for q in questions_data:
            # Apply filters
            if filter_chapter and q.get('chapter') != filter_chapter:
                continue
            
            if filter_concept and filter_concept not in q.get('concepts', []):
                continue
            
            if filter_difficulty and q.get('difficulty') != filter_difficulty:
                continue
            
            # Text search
            if query_lower:
                q_text = q.get('question_text', '').lower()
                concepts_text = ' '.join(q.get('concepts', [])).lower()
                chapter_text = q.get('chapter', '').lower()
                
                if not (query_lower in q_text or 
                       query_lower in concepts_text or 
                       query_lower in chapter_text):
                    continue
            
            results.append(q)
        
        return results
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON from LLM response, handling potential formatting issues"""
        # Clean response
        response = response.strip()
        
        # Try to extract JSON from markdown code blocks
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response)
        if json_match:
            response = json_match.group(1)
        
        # Remove any leading/trailing non-JSON content
        start_idx = response.find('{')
        end_idx = response.rfind('}')
        
        if start_idx != -1 and end_idx != -1:
            response = response[start_idx:end_idx + 1]
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to fix common issues
            response = response.replace("'", '"')
            response = re.sub(r',\s*}', '}', response)
            response = re.sub(r',\s*]', ']', response)
            
            try:
                return json.loads(response)
            except json.JSONDecodeError as e:
                return {'error': f'Failed to parse response: {str(e)}', 'raw': response}
    
    def is_configured(self) -> bool:
        """Check if the analyzer is properly configured"""
        return bool(self.api_key and self.api_key != "your_gemini_api_key_here")


# Singleton instance
ai_analyzer = AIAnalyzer()
