"""
Pydantic models for API request and response validation.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class ChatMessage(BaseModel):
    """Single chat message model."""
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    timestamp: Optional[datetime] = Field(default_factory=datetime.now)


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str = Field(..., min_length=1, max_length=1000, description="User message")
    conversation_history: List[ChatMessage] = Field(
        default_factory=list,
        description="Previous conversation history"
    )
    session_id: Optional[str] = Field(None, description="Session identifier")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "What are Usama's main technical skills?",
                "conversation_history": [
                    {
                        "role": "user",
                        "content": "Tell me about Usama's experience",
                        "timestamp": "2024-01-01T10:00:00"
                    },
                    {
                        "role": "assistant",
                        "content": "Usama is an MSc Data Science graduate...",
                        "timestamp": "2024-01-01T10:00:05"
                    }
                ],
                "session_id": "abc123"
            }
        }


class Source(BaseModel):
    """Source document information."""
    content: str = Field(..., description="Source content snippet")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Source metadata")
    relevance_score: Optional[float] = Field(None, description="Relevance score")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str = Field(..., description="Assistant's response")
    sources: List[Source] = Field(default_factory=list, description="Retrieved sources")
    conversation_id: str = Field(..., description="Conversation identifier")
    timestamp: datetime = Field(default_factory=datetime.now)
    model_used: str = Field(..., description="LLM model used")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "response": "Usama has expertise in Python, machine learning, and AI...",
                "sources": [
                    {
                        "content": "Programming Languages: Python, R, SQL...",
                        "metadata": {"source": "cv", "section": "technical_skills"},
                        "relevance_score": 0.95
                    }
                ],
                "conversation_id": "conv_123",
                "timestamp": "2024-01-01T10:00:00",
                "model_used": "gpt-4",
                "processing_time": 1.23
            }
        }


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    timestamp: datetime = Field(default_factory=datetime.now)
    vector_store_status: str = Field(..., description="Vector store status")
    documents_loaded: int = Field(..., description="Number of documents in vector store")


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    timestamp: datetime = Field(default_factory=datetime.now)
