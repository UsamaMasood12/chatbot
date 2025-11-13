"""
Sentiment analysis and content filtering
"""
import re
from typing import Dict, Optional
from langchain_openai import ChatOpenAI
import logging

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """Analyze sentiment of user queries"""
    
    def __init__(self):
        """Initialize sentiment analyzer"""
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3, max_tokens=50)
    
    def analyze(self, text: str) -> Dict[str, any]:
        """
        Analyze sentiment of text
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with sentiment and score
        """
        try:
            prompt = f"""Analyze the sentiment of the following text. 
Respond with only one word: positive, negative, or neutral.

Text: {text}

Sentiment:"""
            
            response = self.llm.predict(prompt).strip().lower()
            
            sentiment = response if response in ['positive', 'negative', 'neutral'] else 'neutral'
            
            # Simple scoring based on sentiment
            score = {
                'positive': 0.8,
                'neutral': 0.5,
                'negative': 0.2
            }.get(sentiment, 0.5)
            
            logger.info(f"Sentiment: {sentiment} (score: {score})")
            
            return {
                'sentiment': sentiment,
                'score': score
            }
            
        except Exception as e:
            logger.error(f"Sentiment analysis error: {str(e)}")
            return {
                'sentiment': 'neutral',
                'score': 0.5
            }


class ContentFilter:
    """Filter inappropriate or harmful content"""
    
    # Blocked patterns (basic filtering)
    BLOCKED_PATTERNS = [
        r'\b(hack|exploit|breach|attack)\b',
        r'\b(password|credential|secret|key)\s+(steal|hack|get)',
        r'\b(illegal|fraud|scam)\b',
    ]
    
    # Allowed patterns for legitimate queries
    ALLOWED_CONTEXTS = [
        r'how (does|do|to)',
        r'what (is|are)',
        r'explain',
        r'security (measure|practice|best)',
    ]
    
    @staticmethod
    def is_safe(text: str) -> Dict[str, any]:
        """
        Check if content is safe
        
        Args:
            text: Text to check
            
        Returns:
            Dictionary with safety status and reason
        """
        text_lower = text.lower()
        
        # Check for blocked patterns
        for pattern in ContentFilter.BLOCKED_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                # Check if it's in an allowed context
                is_allowed_context = any(
                    re.search(allowed, text_lower, re.IGNORECASE)
                    for allowed in ContentFilter.ALLOWED_CONTEXTS
                )
                
                if not is_allowed_context:
                    logger.warning(f"Content filtered: {text[:50]}...")
                    return {
                        'is_safe': False,
                        'reason': 'potentially_harmful',
                        'confidence': 0.7
                    }
        
        return {
            'is_safe': True,
            'reason': None,
            'confidence': 1.0
        }
    
    @staticmethod
    def sanitize(text: str) -> str:
        """
        Sanitize input text
        
        Args:
            text: Text to sanitize
            
        Returns:
            Sanitized text
        """
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Limit length
        if len(text) > 1000:
            text = text[:1000]
        
        return text.strip()


class DynamicContextManager:
    """Manage dynamic context window based on query complexity"""
    
    @staticmethod
    def adjust_context_size(query: str, base_k: int = 3) -> int:
        """
        Adjust number of retrieved documents based on query complexity
        
        Args:
            query: User query
            base_k: Base number of documents
            
        Returns:
            Adjusted number of documents to retrieve
        """
        query_lower = query.lower()
        
        # Simple queries - fewer documents
        simple_patterns = [
            r'^what is ',
            r'^who is ',
            r'^when ',
            r'^where ',
        ]
        
        if any(re.match(pattern, query_lower) for pattern in simple_patterns):
            return max(base_k - 1, 1)
        
        # Complex queries - more documents
        complex_indicators = [
            'compare', 'analyze', 'explain', 'describe in detail',
            'comprehensive', 'deep dive', 'all', 'every'
        ]
        
        if any(indicator in query_lower for indicator in complex_indicators):
            return min(base_k + 2, 8)
        
        # Multi-part questions
        if query.count('?') > 1 or query.count(' and ') > 1:
            return min(base_k + 1, 6)
        
        return base_k


# Global instances
sentiment_analyzer = SentimentAnalyzer()
content_filter = ContentFilter()
context_manager = DynamicContextManager()
