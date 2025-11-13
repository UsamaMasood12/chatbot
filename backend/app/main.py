"""
Main FastAPI application for Portfolio Chatbot.
"""
from dotenv import load_dotenv
load_dotenv()  # Load .env file

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import sys

from app.config import get_settings
from app.api.routes import router
from app.rag.vector_store import VectorStoreManager
from app.rag.chain import RAGChain
from app.knowledge.loader import KnowledgeBaseLoader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Global instances
settings = get_settings()
vector_store_manager = None
rag_chain = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    logger.info("Starting Portfolio Chatbot API...")
    
    global vector_store_manager, rag_chain
    
    try:
        # Initialize vector store
        vector_store_manager = VectorStoreManager(
            store_type=settings.VECTOR_STORE_TYPE,
            persist_directory=settings.VECTOR_STORE_PATH,
            embedding_model=settings.EMBEDDING_MODEL
        )
        
        # Try to load existing vector store
        if not vector_store_manager.load_vector_store():
            logger.info("No existing vector store found. Creating new one...")
            
            # Load knowledge base
            loader = KnowledgeBaseLoader(
                chunk_size=settings.CHUNK_SIZE,
                chunk_overlap=settings.CHUNK_OVERLAP
            )
            
            # Load documents from data directory
            documents = loader.load_from_directory("./data")
            
            if not documents:
                logger.warning("No documents found in data directory!")
            else:
                # Create vector store
                vector_store_manager.create_vector_store(documents)
                logger.info(f"Created vector store with {len(documents)} documents")
        
        # Initialize RAG chain with hybrid retrieval
        from app.rag.hybrid_retriever import HybridRetriever, SmartRetriever
        
        # Get base vector retriever
        vector_retriever = vector_store_manager.get_retriever(
            search_kwargs={"k": settings.TOP_K_RESULTS}
        )
        
        # Create hybrid retriever (semantic + keyword)
        hybrid_retriever = HybridRetriever(
            vector_retriever=vector_retriever,
            documents=documents,
            weights=[0.7, 0.3]  # 70% semantic, 30% keyword
        )
        
        # Wrap in smart retriever for query classification
        smart_retriever = SmartRetriever(hybrid_retriever)
        
        rag_chain = RAGChain(
            retriever=smart_retriever,
            model_name=settings.LLM_MODEL,
            temperature=settings.TEMPERATURE,
            max_tokens=settings.MAX_TOKENS,
            use_free_model=settings.USE_FREE_MODEL,
            free_model_type=settings.FREE_MODEL_TYPE
        )
        
        logger.info("Portfolio Chatbot API started successfully!")
        
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Portfolio Chatbot API...")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI Chatbot for Usama Masood's Portfolio",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1")

# Include streaming routes
from app.api.streaming import streaming_router
app.include_router(streaming_router, prefix="/api/v1")


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An error occurred"
        }
    )


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Portfolio Chatbot API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/api/v1/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )