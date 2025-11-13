"""
API routes for the Portfolio Chatbot.
"""
from fastapi import APIRouter, HTTPException, status, Request
from fastapi.responses import JSONResponse
from typing import Dict, Any, List
import uuid
import logging

from app.models import (
    ChatRequest,
    ChatResponse,
    HealthResponse,
    ErrorResponse,
    Source
)
from app.rag.chain import FallbackHandler
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, req: Request) -> ChatResponse:
    """
    Main chat endpoint for conversational AI.
    
    Args:
        request: Chat request with message and conversation history
        req: FastAPI request object for rate limiting
        
    Returns:
        ChatResponse with assistant's reply and sources
    """
    from app.main import rag_chain
    from app.analytics import analytics
    from app.cache import response_cache
    from app.rag.hybrid_retriever import QueryClassifier
    from app.rate_limiter import rate_limiter, get_client_ip
    from app.content_safety import sentiment_analyzer, content_filter, context_manager
    
    # Rate limiting
    client_ip = get_client_ip(req)
    rate_check = rate_limiter.check_rate_limit(client_ip, "/chat")
    
    if not rate_check['allowed']:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "Rate limit exceeded",
                "reason": rate_check['reason'],
                "retry_after": rate_check.get('retry_after', 60)
            }
        )
    
    if not rag_chain:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="RAG chain not initialized"
        )
    
    try:
        # Sanitize input
        sanitized_message = content_filter.sanitize(request.message)
        
        # Content filtering
        safety_check = content_filter.is_safe(sanitized_message)
        if not safety_check['is_safe']:
            logger.warning(f"Unsafe content detected from {client_ip}")
            return ChatResponse(
                response="I'm sorry, but I can't process that request. Please ask about Usama's professional background, skills, or projects.",
                sources=[],
                conversation_id=request.session_id or str(uuid.uuid4()),
                model_used="content_filter",
                processing_time=0.0
            )
        
        # Sentiment analysis
        sentiment = sentiment_analyzer.analyze(sanitized_message)

        # Convert conversation history to dict format
        conversation_history = [
            {"role": msg.role, "content": msg.content}
            for msg in request.conversation_history
        ]
        
        # Recruiter detection
        from app.recruiter_features import recruiter_detector, job_matcher, availability_manager
        from app.email_notifier import email_notifier
        
        recruiter_check = recruiter_detector.is_recruiter(
            sanitized_message,
            conversation_history
        )
        
        # Handle job description analysis
        job_fit_result = None
        if 'job description' in sanitized_message.lower() or 'does usama fit' in sanitized_message.lower():
            job_fit_result = job_matcher.analyze_fit(sanitized_message)
        
        # Handle availability queries
        if any(word in sanitized_message.lower() for word in ['available', 'availability', 'start date', 'notice period']):
            availability_response = availability_manager.format_availability_response()
            return ChatResponse(
                response=availability_response,
                sources=[],
                conversation_id=request.session_id or str(uuid.uuid4()),
                model_used="availability_manager",
                processing_time=0.1
            )
        
        # Handle scheduling requests
        from app.calendar_scheduler import calendar_scheduler
        scheduling_check = calendar_scheduler.detect_scheduling_intent(sanitized_message)
        
        if scheduling_check['has_intent'] and scheduling_check['confidence'] > 0.6:
            scheduling_response = calendar_scheduler.format_scheduling_response(
                scheduling_check['meeting_type']
            )
            return ChatResponse(
                response=scheduling_response,
                sources=[],
                conversation_id=request.session_id or str(uuid.uuid4()),
                model_used="calendar_scheduler",
                processing_time=0.1
            )
        
        # Check cache first (only for simple queries without history)
        if len(request.conversation_history) == 0:
            cached_response = response_cache.get(sanitized_message)
            if cached_response:
                logger.info("Returning cached response")
                return ChatResponse(**cached_response)
        
        # Classify query for analytics
        query_category = QueryClassifier.classify(sanitized_message)
        
        # Dynamic context adjustment
        context_size = context_manager.adjust_context_size(sanitized_message)
        logger.info(f"Adjusted context size to {context_size} documents")
        
        # Query RAG chain
        result = rag_chain.query(
            question=sanitized_message,
            conversation_history=conversation_history
        )
        
        # Generate conversation ID if not provided
        conversation_id = request.session_id or str(uuid.uuid4())
        
        # Format sources
        sources = [
            Source(
                content=src["content"],
                metadata=src["metadata"],
                relevance_score=src.get("relevance_score")
            )
            for src in result["sources"]
        ]
        
        # Create response
        response = ChatResponse(
            response=result["answer"],
            sources=sources,
            conversation_id=conversation_id,
            model_used=result["model_used"],
            processing_time=result["processing_time"]
        )
        
        # Cache response (only for simple queries)
        if len(request.conversation_history) == 0:
            response_cache.set(sanitized_message, response.dict())
        
        # Track analytics with sentiment
        analytics.track_query(
            query=sanitized_message,
            response=result["answer"],
            session_id=conversation_id,
            processing_time=result["processing_time"],
            category=query_category,
            sources_count=len(sources)
        )
        
        # Send email notification if recruiter detected
        if recruiter_check['is_recruiter'] and recruiter_check['confidence'] > 0.5:
            email_notifier.send_recruiter_notification(
                query=sanitized_message,
                session_id=conversation_id,
                recruiter_confidence=recruiter_check['confidence'],
                job_fit_score=job_fit_result['score'] if job_fit_result else None
            )
        
        logger.info(f"Chat request processed. Session: {conversation_id}, Sentiment: {sentiment['sentiment']}")
        return response
        
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        
        # Track error
        analytics.track_error(
            error=str(e),
            query=request.message,
            session_id=request.session_id or "unknown"
        )
        
        # Return fallback response
        fallback_response = FallbackHandler.get_fallback_response(request.message)
        
        return ChatResponse(
            response=fallback_response,
            sources=[],
            conversation_id=request.session_id or str(uuid.uuid4()),
            model_used="fallback",
            processing_time=0.0
        )


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.
    
    Returns:
        HealthResponse with service status
    """
    from app.main import vector_store_manager, rag_chain, settings
    
    try:
        # Check vector store status
        vector_store_status = "ready" if vector_store_manager and vector_store_manager.vector_store else "not_initialized"
        documents_loaded = vector_store_manager.get_document_count() if vector_store_manager else 0
        
        # Check RAG chain status
        rag_status = "ready" if rag_chain else "not_initialized"
        
        overall_status = "healthy" if vector_store_status == "ready" and rag_status == "ready" else "degraded"
        
        return HealthResponse(
            status=overall_status,
            version=settings.APP_VERSION,
            vector_store_status=vector_store_status,
            documents_loaded=documents_loaded
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unhealthy: {str(e)}"
        )


@router.get("/suggestions")
async def get_suggestions() -> Dict[str, Any]:
    """
    Get suggested questions for users.
    
    Returns:
        Dictionary with suggested questions
    """
    try:
        suggestions = FallbackHandler.get_intent_suggestions()
        
        return {
            "suggestions": suggestions,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting suggestions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get suggestions"
        )


@router.post("/clear-history")
async def clear_conversation_history(session_id: str) -> Dict[str, str]:
    """
    Clear conversation history for a session.
    
    Args:
        session_id: Session identifier
        
    Returns:
        Success message
    """
    from app.main import rag_chain
    
    if not rag_chain:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="RAG chain not initialized"
        )
    
    try:
        rag_chain.clear_memory()
        logger.info(f"Cleared conversation history for session: {session_id}")
        
        return {
            "message": "Conversation history cleared successfully",
            "session_id": session_id
        }
        
    except Exception as e:
        logger.error(f"Error clearing history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear conversation history"
        )


@router.get("/info")
async def get_chatbot_info() -> Dict[str, Any]:
    """
    Get information about the chatbot itself.
    
    Returns:
        Dictionary with chatbot information
    """
    from app.main import settings
    
    return {
        "name": "Portfolio Assistant",
        "version": settings.APP_VERSION,
        "description": "AI-powered chatbot to answer questions about Usama Masood's professional profile",
        "capabilities": [
            "Answer questions about technical skills and expertise",
            "Provide detailed information about projects",
            "Share educational background and certifications",
            "Discuss professional experience",
            "Provide contact information"
        ],
        "technologies": [
            "LangChain",
            "OpenAI GPT-3.5-turbo",
            "FAISS Vector Database",
            "FastAPI",
            "RAG (Retrieval-Augmented Generation)",
            "Hybrid Search (Semantic + Keyword)"
        ],
        "features": [
            "Multi-turn conversations with context retention",
            "Semantic search across knowledge base",
            "Source citations for responses",
            "Professional and friendly tone",
            "Query classification and smart routing"
        ]
    }


@router.get("/analytics")
async def get_analytics() -> Dict[str, Any]:
    """
    Get chatbot usage analytics
    
    Returns:
        Analytics statistics
    """
    from app.analytics import analytics
    
    try:
        stats = analytics.get_stats()
        return {
            "status": "success",
            "data": stats
        }
    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get analytics"
        )


@router.get("/analytics/session/{session_id}")
async def get_session_analytics(session_id: str) -> Dict[str, Any]:
    """
    Get analytics for a specific session
    
    Args:
        session_id: Session identifier
        
    Returns:
        Session analytics
    """
    from app.analytics import analytics
    
    try:
        stats = analytics.get_session_stats(session_id)
        
        if not stats:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        return {
            "status": "success",
            "data": stats
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get session analytics"
        )


@router.get("/cache/stats")
async def get_cache_stats() -> Dict[str, Any]:
    """
    Get cache statistics
    
    Returns:
        Cache statistics
    """
    from app.cache import response_cache
    
    try:
        stats = response_cache.get_stats()
        return {
            "status": "success",
            "data": stats
        }
    except Exception as e:
        logger.error(f"Error getting cache stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get cache stats"
        )


@router.post("/cache/clear")
async def clear_cache() -> Dict[str, str]:
    """
    Clear response cache
    
    Returns:
        Success message
    """
    from app.cache import response_cache
    
    try:
        response_cache.clear()
        return {
            "status": "success",
            "message": "Cache cleared successfully"
        }
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear cache"
        )


@router.get("/languages")
async def get_supported_languages() -> Dict[str, Any]:
    """
    Get list of supported languages
    
    Returns:
        Dictionary of language codes and names
    """
    from app.translation import TranslationService
    
    return {
        "status": "success",
        "languages": TranslationService.get_supported_languages()
    }


@router.post("/translate")
async def translate_text(
    text: str,
    target_language: str,
    source_language: str = "en"
) -> Dict[str, Any]:
    """
    Translate text to target language
    
    Args:
        text: Text to translate
        target_language: Target language code
        source_language: Source language code
        
    Returns:
        Translated text
    """
    from app.translation import translation_service
    
    try:
        translated = translation_service.translate(text, target_language, source_language)
        
        if translated is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Translation failed"
            )
        
        return {
            "status": "success",
            "original": text,
            "translated": translated,
            "source_language": source_language,
            "target_language": target_language
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error translating text: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to translate text"
        )


@router.get("/download/resume")
async def download_resume():
    """
    Download resume/CV
    
    Returns:
        File response with CV
    """
    from fastapi.responses import FileResponse
    import os
    
    cv_path = "./data/cv.txt"
    
    if not os.path.exists(cv_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume file not found"
        )
    
    return FileResponse(
        path=cv_path,
        filename="Usama_Masood_CV.txt",
        media_type="text/plain"
    )


@router.get("/rate-limit/stats")
async def get_rate_limit_stats() -> Dict[str, Any]:
    """
    Get rate limiting statistics
    
    Returns:
        Rate limiter stats
    """
    from app.rate_limiter import rate_limiter
    
    try:
        stats = rate_limiter.get_stats()
        return {
            "status": "success",
            "data": stats
        }
    except Exception as e:
        logger.error(f"Error getting rate limit stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get rate limit stats"
        )


@router.post("/feedback/rating")
async def submit_rating(
    rating: str,
    query: str,
    response: str,
    session_id: str,
    comment: str = None
) -> Dict[str, str]:
    """
    Submit thumbs up/down rating
    
    Args:
        rating: 'positive' or 'negative'
        query: Original query
        response: Bot response
        session_id: Session ID
        comment: Optional comment
        
    Returns:
        Success message
    """
    from app.feedback import feedback_system
    from app.email_notifier import email_notifier
    
    try:
        if rating not in ['positive', 'negative']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rating must be 'positive' or 'negative'"
            )
        
        feedback_system.add_rating(rating, query, response, session_id, comment)
        
        # Send email on negative feedback
        if rating == 'negative':
            email_notifier.send_feedback_notification(rating, query, comment)
        
        return {
            "status": "success",
            "message": "Thank you for your feedback!"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting rating: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit rating"
        )


@router.post("/feedback/comment")
async def submit_comment(
    comment: str,
    session_id: str,
    category: str = "general"
) -> Dict[str, str]:
    """
    Submit text feedback
    
    Args:
        comment: Feedback text
        session_id: Session ID
        category: Feedback category
        
    Returns:
        Success message
    """
    from app.feedback import feedback_system
    
    try:
        feedback_system.add_comment(comment, session_id, category)
        return {
            "status": "success",
            "message": "Thank you for your feedback!"
        }
    except Exception as e:
        logger.error(f"Error submitting comment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit comment"
        )


@router.get("/feedback/stats")
async def get_feedback_stats() -> Dict[str, Any]:
    """
    Get feedback statistics
    
    Returns:
        Feedback stats
    """
    from app.feedback import feedback_system
    
    try:
        stats = feedback_system.get_stats()
        return {
            "status": "success",
            "data": stats
        }
    except Exception as e:
        logger.error(f"Error getting feedback stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get feedback stats"
        )


@router.post("/recruiter/check")
async def check_recruiter(query: str, conversation_history: List[Dict] = None) -> Dict[str, Any]:
    """
    Check if query is from a recruiter
    
    Args:
        query: User query
        conversation_history: Previous conversation
        
    Returns:
        Recruiter detection result
    """
    from app.recruiter_features import recruiter_detector
    
    try:
        result = recruiter_detector.is_recruiter(query, conversation_history or [])
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        logger.error(f"Error checking recruiter: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check recruiter"
        )


@router.post("/recruiter/job-match")
async def analyze_job_match(job_description: str) -> Dict[str, Any]:
    """
    Analyze job fit
    
    Args:
        job_description: Job description text
        
    Returns:
        Job fit analysis
    """
    from app.recruiter_features import job_matcher
    
    try:
        result = job_matcher.analyze_fit(job_description)
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        logger.error(f"Error analyzing job match: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze job match"
        )


@router.get("/availability")
async def get_availability() -> Dict[str, Any]:
    """
    Get current availability
    
    Returns:
        Availability information
    """
    from app.recruiter_features import availability_manager
    
    return {
        "status": "success",
        "data": availability_manager.get_availability()
    }


@router.get("/conversation/export/{session_id}")
async def export_conversation(session_id: str) -> Dict[str, Any]:
    """
    Export conversation history
    
    Args:
        session_id: Session ID
        
    Returns:
        Conversation data
    """
    from app.analytics import analytics
    
    try:
        session_data = analytics.get_session_stats(session_id)
        
        if not session_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        return {
            "status": "success",
            "data": session_data
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting conversation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export conversation"
        )


@router.post("/code/generate")
async def generate_code(
    project_description: str,
    language: str = "python",
    task: str = "example"
) -> Dict[str, Any]:
    """
    Generate code from project description
    
    Args:
        project_description: Project description
        language: Programming language
        task: Type of code to generate
        
    Returns:
        Generated code
    """
    from app.code_generator import code_generator
    
    try:
        result = code_generator.generate_code(project_description, language, task)
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        logger.error(f"Error generating code: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate code"
        )


@router.post("/code/explain")
async def explain_code(code: str, language: str = "python") -> Dict[str, Any]:
    """
    Explain code snippet
    
    Args:
        code: Code to explain
        language: Programming language
        
    Returns:
        Code explanation
    """
    from app.code_generator import code_generator
    
    try:
        explanation = code_generator.explain_code(code, language)
        return {
            "status": "success",
            "explanation": explanation
        }
    except Exception as e:
        logger.error(f"Error explaining code: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to explain code"
        )


@router.post("/schedule/meeting")
async def schedule_meeting(meeting_type: str = "intro_call") -> Dict[str, Any]:
    """
    Get meeting scheduling information
    
    Args:
        meeting_type: Type of meeting
        
    Returns:
        Scheduling information
    """
    from app.calendar_scheduler import calendar_scheduler
    
    try:
        response = calendar_scheduler.format_scheduling_response(meeting_type)
        return {
            "status": "success",
            "message": response,
            "calendly_link": calendar_scheduler.generate_calendly_link(meeting_type)
        }
    except Exception as e:
        logger.error(f"Error scheduling meeting: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get scheduling information"
        )


@router.get("/ab-test/{test_name}/results")
async def get_ab_test_results(test_name: str) -> Dict[str, Any]:
    """
    Get A/B test results
    
    Args:
        test_name: Name of the test
        
    Returns:
        Test results
    """
    from app.ab_testing import ab_tester
    
    try:
        results = ab_tester.get_test_results(test_name)
        return {
            "status": "success",
            "data": results
        }
    except Exception as e:
        logger.error(f"Error getting A/B test results: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get test results"
        )
