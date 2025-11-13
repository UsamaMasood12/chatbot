"""
Streaming support for real-time word-by-word responses
"""
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.models import ChatRequest
import json
import logging
import asyncio

logger = logging.getLogger(__name__)

streaming_router = APIRouter()


async def generate_stream(message: str, conversation_history: list, session_id: str):
    """
    Generate streaming response
    
    Args:
        message: User message
        conversation_history: Previous messages
        session_id: Session identifier
    """
    from app.main import rag_chain
    
    if not rag_chain:
        yield json.dumps({"error": "RAG chain not initialized"}) + "\n"
        return
    
    try:
        # Convert history
        history = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in conversation_history
        ]
        
        # Get response
        result = rag_chain.query(
            question=message,
            conversation_history=history
        )
        
        # Stream the response word by word
        words = result["answer"].split()
        
        for i, word in enumerate(words):
            chunk_data = {
                "type": "content",
                "content": word + " ",
                "done": False
            }
            yield json.dumps(chunk_data) + "\n"
            await asyncio.sleep(0.05)  # Small delay for streaming effect
        
        # Send sources at the end
        sources_data = {
            "type": "sources",
            "sources": result["sources"],
            "processing_time": result["processing_time"],
            "model_used": result["model_used"],
            "done": True
        }
        yield json.dumps(sources_data) + "\n"
        
    except Exception as e:
        logger.error(f"Error in streaming: {str(e)}")
        error_data = {
            "type": "error",
            "error": str(e),
            "done": True
        }
        yield json.dumps(error_data) + "\n"


@streaming_router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Streaming chat endpoint - returns Server-Sent Events
    
    Args:
        request: Chat request
        
    Returns:
        StreamingResponse with word-by-word content
    """
    return StreamingResponse(
        generate_stream(
            request.message,
            [msg.dict() for msg in request.conversation_history],
            request.session_id or ""
        ),
        media_type="text/event-stream"
    )
