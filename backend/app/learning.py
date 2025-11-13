"""
Learning mode - Improve responses based on feedback
"""
from typing import Dict, List
import json
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class LearningSystem:
    """Learn from user feedback to improve responses"""
    
    def __init__(self, learning_file: str = "learning_data.json"):
        """
        Initialize learning system
        
        Args:
            learning_file: Path to learning data file
        """
        self.learning_file = learning_file
        self.learning_data = self._load_data()
    
    def _load_data(self) -> Dict:
        """Load learning data"""
        if os.path.exists(self.learning_file):
            try:
                with open(self.learning_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading learning data: {str(e)}")
        
        return {
            "successful_responses": [],  # Positively rated
            "failed_responses": [],  # Negatively rated
            "query_patterns": {},  # Common query patterns
            "improvement_suggestions": []
        }
    
    def _save_data(self):
        """Save learning data"""
        try:
            with open(self.learning_file, 'w') as f:
                json.dump(self.learning_data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving learning data: {str(e)}")
    
    def record_feedback(
        self,
        query: str,
        response: str,
        rating: str,
        category: str = "general"
    ):
        """
        Record user feedback for learning
        
        Args:
            query: User query
            response: Bot response
            rating: positive/negative
            category: Query category
        """
        feedback_data = {
            "timestamp": datetime.now().isoformat(),
            "query": query[:200],
            "response": response[:500],
            "category": category
        }
        
        if rating == "positive":
            self.learning_data["successful_responses"].append(feedback_data)
            
            # Extract query pattern
            pattern = self._extract_pattern(query)
            if pattern not in self.learning_data["query_patterns"]:
                self.learning_data["query_patterns"][pattern] = {
                    "count": 0,
                    "success_rate": 0.0,
                    "example_response": response[:200]
                }
            self.learning_data["query_patterns"][pattern]["count"] += 1
            
        else:  # negative
            self.learning_data["failed_responses"].append(feedback_data)
        
        # Keep only last 500 of each
        if len(self.learning_data["successful_responses"]) > 500:
            self.learning_data["successful_responses"] = self.learning_data["successful_responses"][-500:]
        
        if len(self.learning_data["failed_responses"]) > 500:
            self.learning_data["failed_responses"] = self.learning_data["failed_responses"][-500:]
        
        self._save_data()
        logger.info(f"Recorded {rating} feedback for learning")
    
    def _extract_pattern(self, query: str) -> str:
        """
        Extract pattern from query
        
        Args:
            query: User query
            
        Returns:
            Query pattern
        """
        # Simple pattern extraction
        query_lower = query.lower()
        
        if "skill" in query_lower:
            return "skills_question"
        elif "project" in query_lower:
            return "projects_question"
        elif "experience" in query_lower:
            return "experience_question"
        elif "education" in query_lower:
            return "education_question"
        elif "available" in query_lower or "hire" in query_lower:
            return "availability_question"
        else:
            return "general_question"
    
    def get_similar_successful_response(self, query: str) -> Dict:
        """
        Get similar successful response for reference
        
        Args:
            query: Current query
            
        Returns:
            Similar successful response if found
        """
        pattern = self._extract_pattern(query)
        
        if pattern in self.learning_data["query_patterns"]:
            return {
                "found": True,
                "pattern": pattern,
                "example_response": self.learning_data["query_patterns"][pattern]["example_response"],
                "success_count": self.learning_data["query_patterns"][pattern]["count"]
            }
        
        return {"found": False}
    
    def analyze_failures(self) -> Dict:
        """
        Analyze failed responses to identify improvement areas
        
        Returns:
            Failure analysis
        """
        if not self.learning_data["failed_responses"]:
            return {
                "total_failures": 0,
                "common_categories": [],
                "recommendations": []
            }
        
        # Count by category
        category_counts = {}
        for failure in self.learning_data["failed_responses"]:
            cat = failure.get("category", "general")
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        # Sort by frequency
        common_categories = sorted(
            category_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        # Generate recommendations
        recommendations = []
        for category, count in common_categories:
            recommendations.append(
                f"Improve responses for '{category}' queries (failed {count} times)"
            )
        
        return {
            "total_failures": len(self.learning_data["failed_responses"]),
            "common_categories": [
                {"category": cat, "count": count}
                for cat, count in common_categories
            ],
            "recommendations": recommendations
        }
    
    def get_learning_stats(self) -> Dict:
        """Get learning statistics"""
        total_feedback = (
            len(self.learning_data["successful_responses"]) +
            len(self.learning_data["failed_responses"])
        )
        
        success_rate = (
            len(self.learning_data["successful_responses"]) / total_feedback * 100
            if total_feedback > 0 else 0
        )
        
        return {
            "total_feedback": total_feedback,
            "successful_responses": len(self.learning_data["successful_responses"]),
            "failed_responses": len(self.learning_data["failed_responses"]),
            "success_rate": round(success_rate, 2),
            "learned_patterns": len(self.learning_data["query_patterns"]),
            "top_patterns": sorted(
                [
                    {"pattern": p, "count": d["count"]}
                    for p, d in self.learning_data["query_patterns"].items()
                ],
                key=lambda x: x["count"],
                reverse=True
            )[:5]
        }
    
    def suggest_improvements(self) -> List[str]:
        """
        Generate improvement suggestions based on learning data
        
        Returns:
            List of suggestions
        """
        suggestions = []
        
        # Analyze failure analysis
        failure_analysis = self.analyze_failures()
        
        if failure_analysis["total_failures"] > 20:
            suggestions.append(
                "High number of negative ratings - consider reviewing response quality"
            )
        
        # Check success rate
        stats = self.get_learning_stats()
        if stats["success_rate"] < 70:
            suggestions.append(
                f"Success rate is {stats['success_rate']}% - aim for >80%"
            )
        
        # Add category-specific suggestions
        for rec in failure_analysis["recommendations"][:3]:
            suggestions.append(rec)
        
        return suggestions


# Global instance
learning_system = LearningSystem()
