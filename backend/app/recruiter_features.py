"""
Recruiter-specific features and job matching
"""
from typing import Dict, List, Optional
from langchain_openai import ChatOpenAI
import logging

logger = logging.getLogger(__name__)


class RecruiterDetector:
    """Detect if user is a recruiter based on query patterns"""
    
    RECRUITER_INDICATORS = [
        'hire', 'hiring', 'position', 'role', 'job opening',
        'candidate', 'recruitment', 'vacancy', 'opportunity',
        'interview', 'salary', 'compensation', 'available',
        'start date', 'notice period', 'job description'
    ]
    
    @staticmethod
    def is_recruiter(query: str, conversation_history: List[Dict] = None) -> Dict:
        """
        Detect if user is likely a recruiter
        
        Args:
            query: Current query
            conversation_history: Previous conversation
            
        Returns:
            Detection result with confidence
        """
        query_lower = query.lower()
        
        # Check for recruiter indicators
        matches = sum(1 for indicator in RecruiterDetector.RECRUITER_INDICATORS 
                     if indicator in query_lower)
        
        confidence = min(matches * 0.2, 1.0)
        
        # Check conversation history
        if conversation_history:
            history_text = ' '.join([msg.get('content', '') for msg in conversation_history])
            history_matches = sum(1 for indicator in RecruiterDetector.RECRUITER_INDICATORS 
                                 if indicator in history_text.lower())
            confidence = min(confidence + (history_matches * 0.1), 1.0)
        
        is_recruiter = confidence >= 0.3
        
        if is_recruiter:
            logger.info(f"Recruiter detected with confidence: {confidence}")
        
        return {
            'is_recruiter': is_recruiter,
            'confidence': confidence,
            'indicators_found': matches
        }


class JobMatcher:
    """Match job descriptions with candidate profile"""
    
    def __init__(self):
        """Initialize job matcher"""
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3, max_tokens=500)
    
    def analyze_fit(self, job_description: str) -> Dict:
        """
        Analyze if Usama fits a job description
        
        Args:
            job_description: Job description text
            
        Returns:
            Fit analysis with score and reasoning
        """
        try:
            prompt = f"""Analyze if Usama Masood is a good fit for this job description.

Usama's Profile:
- MSc Data Science (Distinction) from Teesside University
- Experience: Data Scientist, ML Engineer, AI Developer
- Skills: Python, Machine Learning, Deep Learning, NLP, Computer Vision, RAG, LangChain, TensorFlow, PyTorch
- Projects: Enterprise AI systems, RAG chatbots, predictive models, document processing
- Languages: English (Fluent), Urdu (Native)

Job Description:
{job_description}

Provide:
1. Fit Score (0-100)
2. Matching Skills
3. Missing Skills
4. Overall Assessment

Format as:
SCORE: [number]
MATCHING: [comma-separated skills]
MISSING: [comma-separated skills]
ASSESSMENT: [2-3 sentences]"""

            response = self.llm.predict(prompt)
            
            # Parse response
            lines = response.strip().split('\n')
            result = {
                'score': 0,
                'matching_skills': [],
                'missing_skills': [],
                'assessment': ''
            }
            
            for line in lines:
                if line.startswith('SCORE:'):
                    try:
                        result['score'] = int(line.split(':')[1].strip())
                    except:
                        pass
                elif line.startswith('MATCHING:'):
                    skills = line.split(':')[1].strip()
                    result['matching_skills'] = [s.strip() for s in skills.split(',') if s.strip()]
                elif line.startswith('MISSING:'):
                    skills = line.split(':')[1].strip()
                    result['missing_skills'] = [s.strip() for s in skills.split(',') if s.strip()]
                elif line.startswith('ASSESSMENT:'):
                    result['assessment'] = line.split(':')[1].strip()
            
            logger.info(f"Job fit score: {result['score']}")
            return result
            
        except Exception as e:
            logger.error(f"Job matching error: {str(e)}")
            return {
                'score': 0,
                'matching_skills': [],
                'missing_skills': [],
                'assessment': 'Unable to analyze job fit at this time.'
            }


class AvailabilityManager:
    """Manage availability and preferences"""
    
    AVAILABILITY_INFO = {
        'status': 'Open to opportunities',
        'notice_period': '2-4 weeks',
        'work_type': ['Remote', 'Hybrid', 'On-site'],
        'location_preference': 'UK (Open to relocation)',
        'visa_status': 'Graduate Visa (Valid until 2026)',
        'salary_expectation': 'Competitive (Negotiable)',
        'start_date': 'Flexible'
    }
    
    @staticmethod
    def get_availability() -> Dict:
        """Get current availability information"""
        return AvailabilityManager.AVAILABILITY_INFO
    
    @staticmethod
    def format_availability_response() -> str:
        """Format availability as human-readable text"""
        info = AvailabilityManager.AVAILABILITY_INFO
        
        response = f"""**Current Availability:**

📅 **Status:** {info['status']}
⏰ **Notice Period:** {info['notice_period']}
💼 **Work Type:** {', '.join(info['work_type'])}
📍 **Location:** {info['location_preference']}
🛂 **Visa Status:** {info['visa_status']}
💰 **Salary:** {info['salary_expectation']}
🚀 **Start Date:** {info['start_date']}

I'm actively looking for Data Science, ML Engineering, or AI Developer roles. Feel free to reach out at usama.masood@example.com!"""
        
        return response


# Global instances
recruiter_detector = RecruiterDetector()
job_matcher = JobMatcher()
availability_manager = AvailabilityManager()
