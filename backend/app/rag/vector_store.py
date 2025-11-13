"""
Vector store management for document embeddings and retrieval.
"""
from typing import List, Optional
from langchain.schema import Document
from langchain_community.vectorstores import Chroma, FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings
import logging
import os

logger = logging.getLogger(__name__)


class VectorStoreManager:
    """Manage vector store operations for document retrieval."""
    
    def __init__(
        self,
        store_type: str = "chromadb",
        persist_directory: str = "./vector_store",
        embedding_model: str = "all-MiniLM-L6-v2",
        use_openai_embeddings: bool = False
    ):
        """
        Initialize vector store manager.
        
        Args:
            store_type: Type of vector store ('chromadb' or 'faiss')
            persist_directory: Directory to persist vector store
            embedding_model: Name of the embedding model
            use_openai_embeddings: Whether to use OpenAI embeddings
        """
        self.store_type = store_type
        self.persist_directory = persist_directory
        self.vector_store = None
        
        # Initialize embeddings
        if use_openai_embeddings:
            logger.info("Using OpenAI embeddings")
            self.embeddings = OpenAIEmbeddings()
        else:
            logger.info(f"Using HuggingFace embeddings: {embedding_model}")
            self.embeddings = HuggingFaceEmbeddings(
                model_name=embedding_model,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
        
        # Create persist directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)
    
    def create_vector_store(self, documents: List[Document]) -> None:
        """
        Create a new vector store from documents.
        
        Args:
            documents: List of documents to index
        """
        if not documents:
            raise ValueError("No documents provided to create vector store")
        
        logger.info(f"Creating {self.store_type} vector store with {len(documents)} documents")
        
        try:
            if self.store_type == "chromadb":
                self.vector_store = Chroma.from_documents(
                    documents=documents,
                    embedding=self.embeddings,
                    persist_directory=self.persist_directory
                )
                self.vector_store.persist()
                
            elif self.store_type == "faiss":
                self.vector_store = FAISS.from_documents(
                    documents=documents,
                    embedding=self.embeddings
                )
                self.vector_store.save_local(self.persist_directory)
            
            else:
                raise ValueError(f"Unsupported vector store type: {self.store_type}")
            
            logger.info(f"Vector store created successfully with {len(documents)} documents")
            
        except Exception as e:
            logger.error(f"Error creating vector store: {str(e)}")
            raise
    
    def load_vector_store(self) -> bool:
        """
        Load existing vector store from disk.
        
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            if self.store_type == "chromadb":
                if os.path.exists(self.persist_directory):
                    self.vector_store = Chroma(
                        persist_directory=self.persist_directory,
                        embedding_function=self.embeddings
                    )
                    logger.info("ChromaDB vector store loaded successfully")
                    return True
                    
            elif self.store_type == "faiss":
                index_path = os.path.join(self.persist_directory, "index.faiss")
                if os.path.exists(index_path):
                    self.vector_store = FAISS.load_local(
                        self.persist_directory,
                        self.embeddings,
                        allow_dangerous_deserialization=True
                    )
                    logger.info("FAISS vector store loaded successfully")
                    return True
            
            logger.warning("No existing vector store found")
            return False
            
        except Exception as e:
            logger.error(f"Error loading vector store: {str(e)}")
            return False
    
    def add_documents(self, documents: List[Document]) -> None:
        """
        Add new documents to existing vector store.
        
        Args:
            documents: List of documents to add
        """
        if not self.vector_store:
            raise ValueError("Vector store not initialized. Create or load first.")
        
        if not documents:
            logger.warning("No documents provided to add")
            return
        
        try:
            if self.store_type == "chromadb":
                self.vector_store.add_documents(documents)
                self.vector_store.persist()
                
            elif self.store_type == "faiss":
                self.vector_store.add_documents(documents)
                self.vector_store.save_local(self.persist_directory)
            
            logger.info(f"Added {len(documents)} documents to vector store")
            
        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}")
            raise
    
    def similarity_search(
        self,
        query: str,
        k: int = 3,
        filter_metadata: Optional[dict] = None
    ) -> List[Document]:
        """
        Perform similarity search on vector store.
        
        Args:
            query: Search query
            k: Number of results to return
            filter_metadata: Optional metadata filter
            
        Returns:
            List of most similar documents
        """
        if not self.vector_store:
            raise ValueError("Vector store not initialized")
        
        try:
            if filter_metadata:
                results = self.vector_store.similarity_search(
                    query,
                    k=k,
                    filter=filter_metadata
                )
            else:
                results = self.vector_store.similarity_search(query, k=k)
            
            logger.info(f"Found {len(results)} results for query: {query[:50]}...")
            return results
            
        except Exception as e:
            logger.error(f"Error performing similarity search: {str(e)}")
            return []
    
    def similarity_search_with_score(
        self,
        query: str,
        k: int = 3
    ) -> List[tuple]:
        """
        Perform similarity search with relevance scores.
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            List of (document, score) tuples
        """
        if not self.vector_store:
            raise ValueError("Vector store not initialized")
        
        try:
            results = self.vector_store.similarity_search_with_score(query, k=k)
            logger.info(f"Found {len(results)} results with scores")
            return results
            
        except Exception as e:
            logger.error(f"Error performing similarity search with scores: {str(e)}")
            return []
    
    def get_retriever(self, search_kwargs: Optional[dict] = None):
        """
        Get a retriever object for the vector store.
        
        Args:
            search_kwargs: Search parameters
            
        Returns:
            Retriever object
        """
        if not self.vector_store:
            raise ValueError("Vector store not initialized")
        
        if search_kwargs is None:
            search_kwargs = {"k": 3}
        
        return self.vector_store.as_retriever(search_kwargs=search_kwargs)
    
    def get_document_count(self) -> int:
        """
        Get the number of documents in the vector store.
        
        Returns:
            Number of documents
        """
        if not self.vector_store:
            return 0
        
        try:
            if self.store_type == "chromadb":
                return self.vector_store._collection.count()
            elif self.store_type == "faiss":
                return self.vector_store.index.ntotal
        except Exception as e:
            logger.error(f"Error getting document count: {str(e)}")
            return 0