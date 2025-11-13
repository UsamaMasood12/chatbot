"""
RAG Chain implementation for conversational question answering.
"""
from typing import List, Dict, Any, Optional
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import Document
import logging
import time
import os

logger = logging.getLogger(__name__)


class RAGChain:
    """Retrieval-Augmented Generation chain for portfolio chatbot."""
    
    def __init__(
        self,
        retriever,
        model_name: str = "gpt-4",
        temperature: float = 0.2,
        max_tokens: int = 500,
        fallback_models: List[str] = None,
        use_free_model: bool = False,
        free_model_type: str = "huggingface"
    ):
        """
        Initialize RAG chain.

        Args:
            retriever: Document retriever
            model_name: LLM model name (ignored if use_free_model=True)
            temperature: Model temperature
            max_tokens: Maximum tokens in response
            fallback_models: List of fallback models if primary fails
            use_free_model: If True, use free HuggingFace models (no API cost)
            free_model_type: "huggingface" or "groq"
        """
        self.retriever = retriever
        self.model_name = model_name
        self.fallback_models = fallback_models or ["gpt-3.5-turbo", "gpt-3.5-turbo-16k"]
        self.use_free_model = use_free_model

        # Initialize LLM based on configuration
        if use_free_model:
            logger.info("Using FREE model (no API costs!)")
            try:
                from app.rag.free_llm import get_free_llm
                groq_key = os.getenv("GROQ_API_KEY", "")
                self.llm = get_free_llm(
                    model_type=free_model_type,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    groq_api_key=groq_key
                )
                logger.info(f"✅ FREE model initialized: {free_model_type}")
            except Exception as e:
                logger.error(f"Failed to initialize free model: {str(e)}")
                logger.info("Falling back to OpenAI (will fail if no quota)")
                use_free_model = False

        if not use_free_model:
            # Use OpenAI (requires API key and quota)
            try:
                self.llm = ChatOpenAI(
                    model=model_name,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                logger.info(f"Primary LLM initialized: {model_name}")
            except Exception as e:
                logger.error(f"Failed to initialize primary LLM: {str(e)}")
                # Use first fallback
                self.llm = ChatOpenAI(
                    model=self.fallback_models[0],
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                logger.info(f"Using fallback LLM: {self.fallback_models[0]}")
        
        # Create custom prompt
        self.prompt = self._create_prompt()
        
        # Initialize memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"
        )
        
        # Get base retriever - SmartRetriever wraps HybridRetriever
        if hasattr(self.retriever, 'hybrid_retriever'):
            # SmartRetriever case - get vector_retriever from HybridRetriever
            base_retriever = self.retriever.hybrid_retriever.vector_retriever
        else:
            # Direct retriever case
            base_retriever = self.retriever
        
        # Create conversational chain
        self.chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=base_retriever,
            memory=self.memory,
            return_source_documents=True,
            combine_docs_chain_kwargs={"prompt": self.prompt},
            verbose=True
        )
        
        logger.info(f"RAG Chain initialized with model: {model_name}")
    
    def _create_prompt(self) -> PromptTemplate:
        """
        Create custom prompt template for the chatbot.
        
        Returns:
            PromptTemplate object
        """
        template = """You are an intelligent AI assistant representing Usama Masood, a Data Scientist and AI/ML Engineer.

⚠️ CRITICAL CONSISTENCY RULE ⚠️
For IDENTICAL questions asked multiple times, you MUST provide the EXACT SAME answer every time.
DO NOT vary your responses for factual questions. Consistency is mandatory.

CRITICAL: Follow this STRICT 3-TIER PRIORITY ORDER:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TIER 1: EXACT MATCH (HIGHEST PRIORITY)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
If context has EXACT answer, use it DIRECTLY without modification.

Examples:
✓ "Email?" → Use exact email from context: usamamasood531@gmail.com
✓ "Phone?" → Use exact phone: +44 7724 030958
✓ "Age?" → Use EXACT age from context (calculate from birthdate if needed)
✓ "University?" → Exact name: "Teesside University" and "NUST"
✓ "Accuracy in predictive maintenance?" → Exact: 99.80%

RULE: Never paraphrase factual data (emails, phones, numbers, dates, names, universities)
RULE: Always extract and use the EXACT values from context

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TIER 2: SIMILAR/RELATED (MEDIUM PRIORITY)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
If no exact match, SYNTHESIZE from related information in context.

Examples:
✓ "ML skills?" → Combine from ALL ML projects:
  - Predictive Maintenance: SVM, Random Forest, XGBoost (9 algorithms)
  - Car Price: Random Forest, XGBoost, regression
  - IBM Course: Supervised/Unsupervised learning
  
✓ "RAG work?" → Mention ALL 3 RAG projects:
  - Enterprise AI Assistant (ChromaDB, LangChain)
  - Donor Chatbot (FAISS, 90% accuracy)
  - Portfolio Chatbot (production system)

✓ "Deep Learning?" → Look for evidence:
  - TensorFlow, PyTorch in skills
  - Neural Networks in projects
  - CNN, RNN, Transformers mentioned

RULE: Only synthesize from information PRESENT in context

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TIER 3: INTELLIGENT INFERENCE (LAST RESORT)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ONLY if Tiers 1 & 2 have NO information, make reasonable inference.

MUST clearly indicate inference:
✓ "Based on Usama's role as Data Scientist, he likely has..."
✓ "Given his MSc in Data Science, he would be familiar with..."
✓ "As an AI/ML Engineer, typical skills would include..."

NEVER infer:
✗ Specific project names not in context
✗ Exact numbers, dates, or metrics
✗ Technologies not mentioned anywhere
✗ Company names or clients

If truly no information: "I don't have that specific information, but I can tell you about [related topic]"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CONTEXT FROM KNOWLEDGE BASE:
{context}

QUESTION: {question}

ANSWER (Follow Tier 1 → Tier 2 → Tier 3 priority):"""

        return PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
    
    def query(
        self,
        question: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Query the RAG chain with a question.
        
        Args:
            question: User's question
            conversation_history: Previous conversation history
            
        Returns:
            Dictionary containing answer and metadata
        """
        start_time = time.time()
        
        try:
            # If conversation history is provided, update memory
            if conversation_history:
                self._update_memory(conversation_history)
            
            # Query the chain
            result = self.chain({"question": question})
            
            processing_time = time.time() - start_time
            
            # Extract source documents
            sources = []
            if "source_documents" in result:
                for doc in result["source_documents"]:
                    sources.append({
                        "content": doc.page_content,
                        "metadata": doc.metadata,
                        "relevance_score": None  # Add scoring in future
                    })
            
            response = {
                "answer": result["answer"],
                "sources": sources,
                "processing_time": processing_time,
                "model_used": self.model_name
            }
            
            logger.info(f"Query processed in {processing_time:.2f}s")
            return response
            
        except Exception as e:
            logger.error(f"Error processing query with primary model: {str(e)}")
            
            # Try fallback models
            for fallback_model in self.fallback_models:
                try:
                    logger.info(f"Trying fallback model: {fallback_model}")
                    
                    # Create new LLM with fallback model
                    fallback_llm = ChatOpenAI(
                        model=fallback_model,
                        temperature=0.2,
                        max_tokens=500
                    )
                    
                    # Create new chain with fallback LLM
                    fallback_chain = ConversationalRetrievalChain.from_llm(
                        llm=fallback_llm,
                        retriever=self.retriever,
                        memory=self.memory,
                        return_source_documents=True,
                        combine_docs_chain_kwargs={"prompt": self.prompt},
                        verbose=False
                    )
                    
                    result = fallback_chain({"question": question})
                    processing_time = time.time() - start_time
                    
                    # Extract sources
                    sources = []
                    if "source_documents" in result:
                        for doc in result["source_documents"]:
                            sources.append({
                                "content": doc.page_content,
                                "metadata": doc.metadata,
                                "relevance_score": None
                            })
                    
                    logger.info(f"Fallback model {fallback_model} succeeded")
                    
                    return {
                        "answer": result["answer"],
                        "sources": sources,
                        "processing_time": processing_time,
                        "model_used": fallback_model
                    }
                    
                except Exception as fallback_error:
                    logger.error(f"Fallback model {fallback_model} failed: {str(fallback_error)}")
                    continue
            
            # All models failed
            logger.error("All models failed")
            raise
    
    def _update_memory(self, conversation_history: List[Dict[str, str]]) -> None:
        """
        Update conversation memory with history.
        
        Args:
            conversation_history: List of conversation messages
        """
        # Clear existing memory
        self.memory.clear()
        
        # Add conversation history
        for message in conversation_history:
            if message["role"] == "user":
                self.memory.chat_memory.add_user_message(message["content"])
            elif message["role"] == "assistant":
                self.memory.chat_memory.add_ai_message(message["content"])
    
    def clear_memory(self) -> None:
        """Clear conversation memory."""
        self.memory.clear()
        logger.info("Conversation memory cleared")
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """
        Get current conversation history.
        
        Returns:
            List of conversation messages
        """
        history = []
        messages = self.memory.chat_memory.messages
        
        for message in messages:
            if message.type == "human":
                history.append({"role": "user", "content": message.content})
            elif message.type == "ai":
                history.append({"role": "assistant", "content": message.content})
        
        return history


class FallbackHandler:
    """Handle fallback responses when queries fail."""
    
    @staticmethod
    def get_fallback_response(question: str) -> str:
        """
        Get a fallback response for failed queries.
        
        Args:
            question: Original question
            
        Returns:
            Fallback response string
        """
        return (
            "I apologize, but I'm having trouble processing your question at the moment. "
            "Here are some things I can help you with:\n\n"
            "- Information about Usama's technical skills and experience\n"
            "- Details about his AI/ML projects\n"
            "- His educational background\n"
            "- Contact information\n\n"
            "Please try rephrasing your question, or ask about any of these topics!"
        )
    
    @staticmethod
    def get_intent_suggestions() -> List[str]:
        """
        Get suggested questions for users.
        
        Returns:
            List of suggested questions
        """
        return [
            "What are Usama's main technical skills?",
            "Tell me about the Enterprise AI Knowledge Assistant project",
            "What is Usama's educational background?",
            "How can I contact Usama?",
            "What experience does Usama have with RAG systems?",
            "Describe Usama's machine learning expertise"
        ]