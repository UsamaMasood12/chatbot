"""
Free LLM implementation using Hugging Face models (no API costs).
"""
from typing import Optional, List, Any
from langchain.llms.base import LLM
from langchain.callbacks.manager import CallbackManagerForLLMRun
import logging

logger = logging.getLogger(__name__)


class HuggingFaceLLM(LLM):
    """Free Hugging Face LLM wrapper for LangChain."""

    model_name: str = "google/flan-t5-large"  # Free, good for Q&A
    pipeline: Any = None
    max_length: int = 500
    temperature: float = 0.2

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._initialize_model()

    def _initialize_model(self):
        """Initialize the Hugging Face model pipeline."""
        try:
            from transformers import pipeline

            logger.info(f"Loading free model: {self.model_name}")

            # Use text2text-generation for FLAN-T5
            self.pipeline = pipeline(
                "text2text-generation",
                model=self.model_name,
                device=-1  # CPU only (use 0 for GPU)
            )

            logger.info(f"Model {self.model_name} loaded successfully (FREE)")

        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise

    @property
    def _llm_type(self) -> str:
        """Return type of LLM."""
        return "huggingface_free"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Call the model."""
        try:
            # Generate response
            result = self.pipeline(
                prompt,
                max_length=self.max_length,
                temperature=self.temperature,
                do_sample=True if self.temperature > 0 else False,
                top_p=0.95,
                num_return_sequences=1
            )

            response = result[0]['generated_text']

            # Apply stop sequences if provided
            if stop:
                for stop_seq in stop:
                    if stop_seq in response:
                        response = response.split(stop_seq)[0]

            return response.strip()

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return "I apologize, but I'm having trouble generating a response."

    @property
    def _identifying_params(self):
        """Return identifying parameters."""
        return {
            "model_name": self.model_name,
            "max_length": self.max_length,
            "temperature": self.temperature
        }


class GroqFreeLLM(LLM):
    """Free Groq API LLM (much faster than HuggingFace, also free!)"""

    api_key: str = ""  # Read from config/env
    model_name: str = "llama3-8b-8192"
    temperature: float = 0.2
    max_tokens: int = 500

    def __init__(self, api_key: str = "", **kwargs):
        super().__init__(**kwargs)
        if api_key:
            self.api_key = api_key
        else:
            # Try to read from environment
            import os
            self.api_key = os.getenv("GROQ_API_KEY", "")

    @property
    def _llm_type(self) -> str:
        return "groq_free"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Call Groq API (free tier available)."""
        try:
            import requests

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            data = {
                "model": self.model_name,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": self.temperature,
                "max_tokens": self.max_tokens
            }

            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )

            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                logger.error(f"Groq API error: {response.status_code}")
                return "Error contacting free API"

        except Exception as e:
            logger.error(f"Error with Groq: {str(e)}")
            return "Free API temporarily unavailable"

    @property
    def _identifying_params(self):
        return {"model_name": self.model_name}


def get_free_llm(
    model_type: str = "huggingface",
    temperature: float = 0.2,
    max_tokens: int = 500,
    groq_api_key: str = ""
) -> LLM:
    """
    Get a free LLM instance.

    Args:
        model_type: "huggingface" or "groq"
        temperature: Model temperature
        max_tokens: Maximum tokens
        groq_api_key: Groq API key (if using Groq)

    Returns:
        LLM instance
    """
    if model_type == "groq":
        logger.info("Using Groq free API (fast, requires free key)")
        if not groq_api_key:
            # Try to read from environment
            import os
            groq_api_key = os.getenv("GROQ_API_KEY", "")

        if not groq_api_key or groq_api_key == "PASTE_YOUR_KEY_HERE":
            logger.error("❌ GROQ_API_KEY not set! Get free key from console.groq.com")
            logger.info("Falling back to HuggingFace model...")
            model_type = "huggingface"
        else:
            return GroqFreeLLM(
                api_key=groq_api_key,
                temperature=temperature,
                max_tokens=max_tokens
            )

    if model_type == "huggingface":
        logger.info("Using Hugging Face free model (no key needed, slower)")
        return HuggingFaceLLM(
            temperature=temperature,
            max_length=max_tokens
        )
