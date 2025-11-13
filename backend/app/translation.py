"""
Multi-language translation support using LLM
"""
import logging
from typing import Dict, Optional
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)


class TranslationService:
    """Handle translation using OpenAI API"""
    
    SUPPORTED_LANGUAGES = {
        'en': 'English',
        'es': 'Spanish',
        'fr': 'French',
        'de': 'German',
        'it': 'Italian',
        'pt': 'Portuguese',
        'ar': 'Arabic',
        'hi': 'Hindi',
        'zh': 'Chinese',
        'ja': 'Japanese',
        'ko': 'Korean',
        'ru': 'Russian'
    }
    
    def __init__(self, model: str = "gpt-3.5-turbo"):
        """
        Initialize translation service
        
        Args:
            model: OpenAI model to use
        """
        self.llm = ChatOpenAI(model=model, temperature=0.3)
        logger.info("Translation service initialized")
    
    def translate(self, text: str, target_language: str, source_language: str = 'en') -> Optional[str]:
        """
        Translate text to target language
        
        Args:
            text: Text to translate
            target_language: Target language code
            source_language: Source language code (default: English)
            
        Returns:
            Translated text or None if error
        """
        if target_language not in self.SUPPORTED_LANGUAGES:
            logger.error(f"Unsupported language: {target_language}")
            return None
        
        # Skip if same language
        if source_language == target_language:
            return text
        
        try:
            target_lang_name = self.SUPPORTED_LANGUAGES[target_language]
            
            prompt = f"""Translate the following text from {source_language} to {target_lang_name}.
Only provide the translation, no explanations.

Text to translate:
{text}

Translation:"""

            response = self.llm.predict(prompt)
            
            logger.info(f"Translated text to {target_lang_name}")
            return response.strip()
            
        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            return None
    
    def detect_language(self, text: str) -> str:
        """
        Detect language of text
        
        Args:
            text: Text to analyze
            
        Returns:
            Language code
        """
        try:
            prompt = f"""Detect the language of the following text and respond with only the 2-letter ISO 639-1 language code (e.g., 'en', 'es', 'fr').

Text:
{text}

Language code:"""

            response = self.llm.predict(prompt)
            lang_code = response.strip().lower()[:2]
            
            if lang_code in self.SUPPORTED_LANGUAGES:
                logger.info(f"Detected language: {lang_code}")
                return lang_code
            
            return 'en'  # Default to English
            
        except Exception as e:
            logger.error(f"Language detection error: {str(e)}")
            return 'en'
    
    @classmethod
    def get_supported_languages(cls) -> Dict[str, str]:
        """Get dictionary of supported languages"""
        return cls.SUPPORTED_LANGUAGES


# Global translation service
translation_service = TranslationService()
