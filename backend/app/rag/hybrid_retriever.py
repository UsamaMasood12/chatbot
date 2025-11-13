"""
Hybrid Search Retriever - Combines semantic and keyword search
"""
from typing import List, Dict, Any
from langchain.schema import Document
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
import logging

logger = logging.getLogger(__name__)


class HybridRetriever:
    """Combines semantic (vector) and keyword (BM25) search for better retrieval"""
    
    def __init__(self, vector_retriever, documents: List[Document], weights: List[float] = None):
        """
        Initialize hybrid retriever
        
        Args:
            vector_retriever: Vector store retriever (semantic search)
            documents: All documents for BM25 indexing
            weights: [semantic_weight, keyword_weight] - defaults to [0.7, 0.3]
        """
        self.vector_retriever = vector_retriever
        self.documents = documents
        self.weights = weights or [0.7, 0.3]
        
        # Create BM25 retriever for keyword search
        self.bm25_retriever = BM25Retriever.from_documents(documents)
        self.bm25_retriever.k = 3  # Number of results
        
        # Combine both retrievers
        self.ensemble_retriever = EnsembleRetriever(
            retrievers=[vector_retriever, self.bm25_retriever],
            weights=self.weights
        )
        
        logger.info(f"Hybrid retriever initialized with weights: {self.weights}")
    
    def get_relevant_documents(self, query: str) -> List[Document]:
        """
        Retrieve documents using hybrid search
        
        Args:
            query: Search query
            
        Returns:
            List of relevant documents
        """
        try:
            results = self.ensemble_retriever.get_relevant_documents(query)
            logger.info(f"Hybrid search returned {len(results)} documents")
            return results
        except Exception as e:
            logger.error(f"Error in hybrid search: {str(e)}")
            # Fallback to vector search only
            return self.vector_retriever.get_relevant_documents(query)
    
    def invoke(self, query: str) -> List[Document]:
        """Invoke method for compatibility with LangChain chains"""
        return self.get_relevant_documents(query)
    
    def update_weights(self, semantic_weight: float, keyword_weight: float):
        """
        Update retriever weights
        
        Args:
            semantic_weight: Weight for semantic search (0-1)
            keyword_weight: Weight for keyword search (0-1)
        """
        self.weights = [semantic_weight, keyword_weight]
        self.ensemble_retriever = EnsembleRetriever(
            retrievers=[self.vector_retriever, self.bm25_retriever],
            weights=self.weights
        )
        logger.info(f"Updated weights to: {self.weights}")


class QueryClassifier:
    """Classify queries to route to appropriate handlers"""
    
    QUERY_TYPES = {
        'skills': ['skill', 'technology', 'programming', 'language', 'framework', 'tool'],
        'projects': ['project', 'built', 'created', 'developed', 'work on', 'github'],
        'experience': ['experience', 'worked', 'job', 'role', 'position', 'internship'],
        'education': ['education', 'degree', 'university', 'studied', 'graduated'],
        'contact': ['contact', 'email', 'phone', 'reach', 'linkedin', 'github'],
        'about': ['about', 'who', 'background', 'summary', 'tell me'],
        'chatbot': ['chatbot', 'how do you work', 'what are you', 'how does this work']
    }
    
    @staticmethod
    def classify(query: str) -> str:
        """
        Classify query into a category
        
        Args:
            query: User query
            
        Returns:
            Query category
        """
        query_lower = query.lower()
        
        # Check each category
        for category, keywords in QueryClassifier.QUERY_TYPES.items():
            if any(keyword in query_lower for keyword in keywords):
                return category
        
        return 'general'
    
    @staticmethod
    def get_section_filter(category: str) -> Dict[str, Any]:
        """
        Get metadata filter for category
        
        Args:
            category: Query category
            
        Returns:
            Metadata filter dict
        """
        filters = {
            'skills': {'section': 'technical_skills'},
            'projects': {'section': 'key_projects'},
            'experience': {'section': 'professional_experience'},
            'education': {'section': 'education'},
            'contact': {'type': 'profile'},
            'about': {'section': 'professional_summary'}
        }
        
        return filters.get(category, {})


class SmartRetriever:
    """Intelligent retriever that uses query classification and hybrid search"""
    
    def __init__(self, hybrid_retriever: HybridRetriever):
        """
        Initialize smart retriever
        
        Args:
            hybrid_retriever: Hybrid retriever instance
        """
        self.hybrid_retriever = hybrid_retriever
        self.query_classifier = QueryClassifier()
        logger.info("Smart retriever initialized")
    
    def get_relevant_documents(self, query: str, use_filter: bool = True, k: int = 10) -> List[Document]:
        """
        Intelligently retrieve documents with semantic understanding
        
        Args:
            query: Search query
            use_filter: Whether to use query classification for filtering
            k: Number of documents to retrieve (default: 10 for better synthesis)
            
        Returns:
            List of relevant documents
        """
        # Classify query
        category = self.query_classifier.classify(query)
        logger.info(f"Query classified as: {category}")
        
        # Expand query for better semantic matching
        expanded_query = self._expand_query(query, category)
        logger.info(f"Expanded query: {expanded_query[:100]}...")
        
        # Get more documents initially (will re-rank later)
        results = self.hybrid_retriever.get_relevant_documents(expanded_query)
        
        # Re-rank documents by relevance to original query
        results = self._rerank_documents(results, query, k=k)
        
        # Apply post-retrieval filtering if needed
        if use_filter and category != 'general':
            section_filter = self.query_classifier.get_section_filter(category)
            if section_filter:
                # Filter results by metadata
                filtered_results = [
                    doc for doc in results
                    if any(
                        doc.metadata.get(key) == value
                        for key, value in section_filter.items()
                    )
                ]
                
                # Use filtered results if we have any, otherwise use all
                if filtered_results:
                    logger.info(f"Filtered to {len(filtered_results)} relevant documents")
                    return filtered_results[:k]
        
        return results[:k]
    
    def _expand_query(self, query: str, category: str) -> str:
        """
        Expand query with synonyms and related terms
        
        Args:
            query: Original query
            category: Query category
            
        Returns:
            Expanded query
        """
        # Synonym mapping for better semantic search
        expansions = {
            'skills': ['expertise', 'technologies', 'tools', 'proficient', 'experienced'],
            'projects': ['portfolio', 'built', 'developed', 'created', 'work'],
            'experience': ['worked', 'employment', 'job', 'role', 'career'],
            'education': ['degree', 'studied', 'qualification', 'university', 'academic'],
            'contact': ['email', 'phone', 'reach', 'linkedin', 'connect'],
            'about': ['background', 'summary', 'bio', 'profile', 'overview']
        }
        
        # Add 2 most relevant expansion terms
        terms = expansions.get(category, [])
        if terms:
            return f"{query} {terms[0]} {terms[1]}"
        return query
    
    def _rerank_documents(self, documents: List[Document], query: str, k: int = 10) -> List[Document]:
        """
        Re-rank documents by semantic relevance
        
        Args:
            documents: Retrieved documents  
            query: Original query
            k: Number to return
            
        Returns:
            Re-ranked top k documents
        """
        if not documents:
            return documents
        
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        scored = []
        for doc in documents:
            content_lower = doc.page_content.lower()
            content_words = set(content_lower.split())
            
            # Scoring factors
            word_overlap = len(query_words.intersection(content_words))
            exact_match = 5.0 if query_lower in content_lower else 0.0
            partial_matches = sum(1 for qw in query_words if qw in content_lower)
            
            # Prefer focused, relevant content
            relevance_score = (word_overlap * 2.0) + exact_match + (partial_matches * 1.5)
            
            scored.append((relevance_score, doc))
        
        # Sort by score descending
        scored.sort(reverse=True, key=lambda x: x[0])
        
        return [doc for _, doc in scored[:k]]
    
    def invoke(self, query: str) -> List[Document]:
        """Invoke method for compatibility"""
        return self.get_relevant_documents(query)