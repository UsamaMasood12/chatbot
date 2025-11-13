"""
Feedback and rating system for responses
"""
from datetime import datetime
from typing import Dict, List, Optional
import json
import os
import logging

logger = logging.getLogger(__name__)


class FeedbackSystem:
    """Collect and manage user feedback"""
    
    def __init__(self, feedback_file: str = "feedback.json"):
        """
        Initialize feedback system
        
        Args:
            feedback_file: Path to feedback storage file
        """
        self.feedback_file = feedback_file
        self.feedback_data = self._load_feedback()
    
    def _load_feedback(self) -> Dict:
        """Load feedback from file"""
        if os.path.exists(self.feedback_file):
            try:
                with open(self.feedback_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading feedback: {str(e)}")
        
        return {
            "ratings": [],
            "comments": [],
            "total_positive": 0,
            "total_negative": 0,
            "satisfaction_score": 0.0
        }
    
    def _save_feedback(self):
        """Save feedback to file"""
        try:
            with open(self.feedback_file, 'w', encoding='utf-8') as f:
                json.dump(self.feedback_data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving feedback: {str(e)}")
    
    def add_rating(
        self,
        rating: str,
        query: str,
        response: str,
        session_id: str,
        comment: Optional[str] = None
    ):
        """
        Add a rating (thumbs up/down)
        
        Args:
            rating: 'positive' or 'negative'
            query: User's query
            response: Bot's response
            session_id: Session identifier
            comment: Optional comment
        """
        rating_data = {
            "timestamp": datetime.now().isoformat(),
            "rating": rating,
            "query": query[:200],  # Truncate
            "response": response[:200],  # Truncate
            "session_id": session_id,
            "comment": comment
        }
        
        self.feedback_data["ratings"].append(rating_data)
        
        # Update counts
        if rating == "positive":
            self.feedback_data["total_positive"] += 1
        else:
            self.feedback_data["total_negative"] += 1
        
        # Calculate satisfaction score
        total = self.feedback_data["total_positive"] + self.feedback_data["total_negative"]
        if total > 0:
            self.feedback_data["satisfaction_score"] = (
                self.feedback_data["total_positive"] / total
            ) * 100
        
        self._save_feedback()
        logger.info(f"Rating added: {rating}")
    
    def add_comment(
        self,
        comment: str,
        session_id: str,
        category: str = "general"
    ):
        """
        Add a text comment/feedback
        
        Args:
            comment: Feedback text
            session_id: Session identifier
            category: Feedback category
        """
        comment_data = {
            "timestamp": datetime.now().isoformat(),
            "comment": comment,
            "session_id": session_id,
            "category": category
        }
        
        self.feedback_data["comments"].append(comment_data)
        self._save_feedback()
        logger.info(f"Comment added: {comment[:50]}...")
    
    def get_stats(self) -> Dict:
        """
        Get feedback statistics
        
        Returns:
            Feedback stats
        """
        recent_ratings = self.feedback_data["ratings"][-50:]  # Last 50
        
        return {
            "total_ratings": len(self.feedback_data["ratings"]),
            "total_positive": self.feedback_data["total_positive"],
            "total_negative": self.feedback_data["total_negative"],
            "satisfaction_score": round(self.feedback_data["satisfaction_score"], 2),
            "total_comments": len(self.feedback_data["comments"]),
            "recent_ratings": recent_ratings[-10:],  # Last 10
            "recent_comments": self.feedback_data["comments"][-10:]  # Last 10
        }
    
    def get_low_rated_queries(self, limit: int = 10) -> List[Dict]:
        """
        Get queries with negative ratings
        
        Args:
            limit: Max number to return
            
        Returns:
            List of low-rated queries
        """
        negative_ratings = [
            r for r in self.feedback_data["ratings"]
            if r["rating"] == "negative"
        ]
        
        return negative_ratings[-limit:]


# Global feedback system
feedback_system = FeedbackSystem()
