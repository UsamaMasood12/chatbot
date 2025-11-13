"""
Analytics tracking for chatbot usage
"""
from datetime import datetime
from typing import Dict, List, Any
import json
import os
from collections import defaultdict, Counter
import logging

logger = logging.getLogger(__name__)


class ChatAnalytics:
    """Track and analyze chatbot usage"""
    
    def __init__(self, analytics_file: str = "analytics.json"):
        """
        Initialize analytics tracker
        
        Args:
            analytics_file: Path to analytics data file
        """
        self.analytics_file = analytics_file
        self.data = self._load_analytics()
    
    def _load_analytics(self) -> Dict:
        """Load analytics from file"""
        if os.path.exists(self.analytics_file):
            try:
                with open(self.analytics_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading analytics: {str(e)}")
        
        return {
            "total_queries": 0,
            "total_sessions": 0,
            "queries": [],
            "sessions": {},
            "query_categories": defaultdict(int),
            "response_times": [],
            "errors": []
        }
    
    def _save_analytics(self):
        """Save analytics to file"""
        try:
            with open(self.analytics_file, 'w') as f:
                json.dump(self.data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving analytics: {str(e)}")
    
    def track_query(
        self,
        query: str,
        response: str,
        session_id: str,
        processing_time: float,
        category: str = "general",
        sources_count: int = 0
    ):
        """
        Track a user query
        
        Args:
            query: User's question
            response: Bot's response
            session_id: Session identifier
            processing_time: Time taken to process
            category: Query category
            sources_count: Number of sources retrieved
        """
        self.data["total_queries"] += 1
        
        query_data = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "response_length": len(response),
            "session_id": session_id,
            "processing_time": processing_time,
            "category": category,
            "sources_count": sources_count
        }
        
        self.data["queries"].append(query_data)
        
        # Track session
        if session_id not in self.data["sessions"]:
            self.data["sessions"][session_id] = {
                "start_time": datetime.now().isoformat(),
                "query_count": 0
            }
            self.data["total_sessions"] += 1
        
        self.data["sessions"][session_id]["query_count"] += 1
        self.data["sessions"][session_id]["last_active"] = datetime.now().isoformat()
        
        # Track category
        self.data["query_categories"][category] = self.data["query_categories"].get(category, 0) + 1
        
        # Track response time
        self.data["response_times"].append(processing_time)
        
        self._save_analytics()
        logger.info(f"Tracked query: {query[:50]}... | Category: {category}")
    
    def track_error(self, error: str, query: str, session_id: str):
        """
        Track an error
        
        Args:
            error: Error message
            query: Query that caused error
            session_id: Session identifier
        """
        error_data = {
            "timestamp": datetime.now().isoformat(),
            "error": error,
            "query": query,
            "session_id": session_id
        }
        
        self.data["errors"].append(error_data)
        self._save_analytics()
        logger.info(f"Tracked error: {error[:50]}...")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get analytics statistics
        
        Returns:
            Dictionary with analytics stats
        """
        queries = self.data.get("queries", [])
        response_times = self.data.get("response_times", [])
        
        # Calculate average response time
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Get most common queries (by first 50 chars)
        query_texts = [q.get("query", "")[:50] for q in queries[-100:]]
        common_queries = Counter(query_texts).most_common(10)
        
        # Get category distribution
        categories = self.data.get("query_categories", {})
        
        # Recent queries
        recent_queries = queries[-10:] if len(queries) >= 10 else queries
        
        return {
            "total_queries": self.data.get("total_queries", 0),
            "total_sessions": self.data.get("total_sessions", 0),
            "average_response_time": round(avg_response_time, 2),
            "total_errors": len(self.data.get("errors", [])),
            "category_distribution": dict(categories),
            "common_queries": [{"query": q, "count": c} for q, c in common_queries],
            "recent_queries": [
                {
                    "query": q.get("query", "")[:100],
                    "timestamp": q.get("timestamp", ""),
                    "category": q.get("category", ""),
                    "processing_time": q.get("processing_time", 0)
                }
                for q in recent_queries
            ]
        }
    
    def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """
        Get statistics for a specific session
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session statistics
        """
        session = self.data.get("sessions", {}).get(session_id, {})
        
        if not session:
            return {}
        
        # Get queries for this session
        session_queries = [
            q for q in self.data.get("queries", [])
            if q.get("session_id") == session_id
        ]
        
        return {
            "session_id": session_id,
            "start_time": session.get("start_time", ""),
            "last_active": session.get("last_active", ""),
            "total_queries": len(session_queries),
            "queries": session_queries[-10:]  # Last 10 queries
        }


# Global analytics instance
analytics = ChatAnalytics()
