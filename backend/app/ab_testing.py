"""
A/B testing framework for chatbot responses
"""
from typing import Dict, Optional
import json
import os
import random
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ABTester:
    """A/B testing for chatbot features and responses"""
    
    def __init__(self, test_file: str = "ab_tests.json"):
        """
        Initialize A/B tester
        
        Args:
            test_file: Path to test configuration file
        """
        self.test_file = test_file
        self.tests = self._load_tests()
        self.results = self._load_results()
    
    def _load_tests(self) -> Dict:
        """Load test configurations"""
        if os.path.exists(self.test_file):
            try:
                with open(self.test_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading tests: {str(e)}")
        
        return {
            "active_tests": {},
            "completed_tests": {}
        }
    
    def _load_results(self) -> Dict:
        """Load test results"""
        results_file = "ab_test_results.json"
        if os.path.exists(results_file):
            try:
                with open(results_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading results: {str(e)}")
        
        return {}
    
    def _save_results(self):
        """Save test results"""
        try:
            with open("ab_test_results.json", 'w') as f:
                json.dump(self.results, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving results: {str(e)}")
    
    def create_test(
        self,
        test_name: str,
        variant_a: Dict,
        variant_b: Dict,
        traffic_split: float = 0.5
    ):
        """
        Create new A/B test
        
        Args:
            test_name: Name of the test
            variant_a: Configuration for variant A
            variant_b: Configuration for variant B
            traffic_split: Percentage for variant B (0.0-1.0)
        """
        self.tests["active_tests"][test_name] = {
            "variant_a": variant_a,
            "variant_b": variant_b,
            "traffic_split": traffic_split,
            "created_at": datetime.now().isoformat(),
            "impressions_a": 0,
            "impressions_b": 0,
            "conversions_a": 0,
            "conversions_b": 0
        }
        
        self.results[test_name] = {
            "sessions_a": [],
            "sessions_b": [],
            "metrics_a": {},
            "metrics_b": {}
        }
        
        logger.info(f"Created A/B test: {test_name}")
    
    def get_variant(self, test_name: str, session_id: str) -> str:
        """
        Get variant for a session
        
        Args:
            test_name: Name of the test
            session_id: Session identifier
            
        Returns:
            Variant name ('a' or 'b')
        """
        if test_name not in self.tests["active_tests"]:
            return 'a'  # Default
        
        test = self.tests["active_tests"][test_name]
        
        # Consistent assignment based on session_id
        random.seed(session_id)
        variant = 'b' if random.random() < test["traffic_split"] else 'a'
        
        # Track impression
        if variant == 'a':
            test["impressions_a"] += 1
            self.results[test_name]["sessions_a"].append(session_id)
        else:
            test["impressions_b"] += 1
            self.results[test_name]["sessions_b"].append(session_id)
        
        return variant
    
    def track_conversion(self, test_name: str, session_id: str, metric: str = "success"):
        """
        Track conversion event
        
        Args:
            test_name: Name of the test
            session_id: Session identifier
            metric: Metric name
        """
        if test_name not in self.tests["active_tests"]:
            return
        
        test = self.tests["active_tests"][test_name]
        
        # Determine variant
        if session_id in self.results[test_name]["sessions_a"]:
            test["conversions_a"] += 1
            if metric not in self.results[test_name]["metrics_a"]:
                self.results[test_name]["metrics_a"][metric] = 0
            self.results[test_name]["metrics_a"][metric] += 1
        elif session_id in self.results[test_name]["sessions_b"]:
            test["conversions_b"] += 1
            if metric not in self.results[test_name]["metrics_b"]:
                self.results[test_name]["metrics_b"][metric] = 0
            self.results[test_name]["metrics_b"][metric] += 1
        
        self._save_results()
    
    def get_test_results(self, test_name: str) -> Dict:
        """
        Get results for a test
        
        Args:
            test_name: Name of the test
            
        Returns:
            Test results
        """
        if test_name not in self.tests["active_tests"]:
            return {}
        
        test = self.tests["active_tests"][test_name]
        
        # Calculate conversion rates
        conv_rate_a = (
            test["conversions_a"] / test["impressions_a"]
            if test["impressions_a"] > 0 else 0
        )
        conv_rate_b = (
            test["conversions_b"] / test["impressions_b"]
            if test["impressions_b"] > 0 else 0
        )
        
        # Calculate lift
        lift = ((conv_rate_b - conv_rate_a) / conv_rate_a * 100) if conv_rate_a > 0 else 0
        
        return {
            "test_name": test_name,
            "impressions_a": test["impressions_a"],
            "impressions_b": test["impressions_b"],
            "conversions_a": test["conversions_a"],
            "conversions_b": test["conversions_b"],
            "conversion_rate_a": round(conv_rate_a * 100, 2),
            "conversion_rate_b": round(conv_rate_b * 100, 2),
            "lift": round(lift, 2),
            "winner": "b" if conv_rate_b > conv_rate_a else "a"
        }


# Global instance
ab_tester = ABTester()

# Example: Create default tests
ab_tester.create_test(
    "greeting_style",
    variant_a={"greeting": "Hi! How can I help you today?"},
    variant_b={"greeting": "Hello! What would you like to know about Usama?"},
    traffic_split=0.5
)
