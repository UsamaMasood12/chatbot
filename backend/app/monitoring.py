"""
Error reporting and monitoring system
"""
from typing import Dict, Optional
import json
import os
from datetime import datetime
import logging
import traceback

logger = logging.getLogger(__name__)


class ErrorReporter:
    """Centralized error reporting and tracking"""
    
    def __init__(self, error_file: str = "errors.json"):
        """
        Initialize error reporter
        
        Args:
            error_file: Path to error log file
        """
        self.error_file = error_file
        self.errors = self._load_errors()
    
    def _load_errors(self) -> Dict:
        """Load errors from file"""
        if os.path.exists(self.error_file):
            try:
                with open(self.error_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading error log: {str(e)}")
        
        return {
            "errors": [],
            "error_counts": {},
            "total_errors": 0
        }
    
    def _save_errors(self):
        """Save errors to file"""
        try:
            with open(self.error_file, 'w') as f:
                json.dump(self.errors, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving error log: {str(e)}")
    
    def report_error(
        self,
        error: Exception,
        context: Dict = None,
        severity: str = "error"
    ):
        """
        Report an error
        
        Args:
            error: Exception object
            context: Additional context
            severity: Error severity (info, warning, error, critical)
        """
        error_type = type(error).__name__
        error_message = str(error)
        stack_trace = traceback.format_exc()
        
        error_data = {
            "timestamp": datetime.now().isoformat(),
            "type": error_type,
            "message": error_message,
            "severity": severity,
            "stack_trace": stack_trace,
            "context": context or {}
        }
        
        self.errors["errors"].append(error_data)
        self.errors["total_errors"] += 1
        
        # Count by type
        if error_type not in self.errors["error_counts"]:
            self.errors["error_counts"][error_type] = 0
        self.errors["error_counts"][error_type] += 1
        
        # Keep only last 1000 errors
        if len(self.errors["errors"]) > 1000:
            self.errors["errors"] = self.errors["errors"][-1000:]
        
        self._save_errors()
        
        logger.error(f"{severity.upper()}: {error_type} - {error_message}")
        
        # Send to external service (if configured)
        self._send_to_sentry(error_data)
    
    def _send_to_sentry(self, error_data: Dict):
        """Send error to Sentry (placeholder)"""
        # In production, integrate with Sentry
        # import sentry_sdk
        # sentry_sdk.capture_exception(error_data)
        pass
    
    def get_error_stats(self) -> Dict:
        """Get error statistics"""
        recent_errors = self.errors["errors"][-20:]  # Last 20
        
        return {
            "total_errors": self.errors["total_errors"],
            "error_types": self.errors["error_counts"],
            "recent_errors": [
                {
                    "timestamp": e["timestamp"],
                    "type": e["type"],
                    "message": e["message"][:100],
                    "severity": e["severity"]
                }
                for e in recent_errors
            ]
        }
    
    def get_error_by_type(self, error_type: str, limit: int = 10) -> list:
        """
        Get errors by type
        
        Args:
            error_type: Error type to filter
            limit: Max number to return
            
        Returns:
            List of errors
        """
        filtered = [
            e for e in self.errors["errors"]
            if e["type"] == error_type
        ]
        return filtered[-limit:]


class PerformanceMonitor:
    """Monitor application performance"""
    
    def __init__(self, metrics_file: str = "performance.json"):
        """
        Initialize performance monitor
        
        Args:
            metrics_file: Path to metrics file
        """
        self.metrics_file = metrics_file
        self.metrics = self._load_metrics()
    
    def _load_metrics(self) -> Dict:
        """Load metrics from file"""
        if os.path.exists(self.metrics_file):
            try:
                with open(self.metrics_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading metrics: {str(e)}")
        
        return {
            "response_times": [],
            "endpoint_times": {},
            "memory_usage": [],
            "uptime_start": datetime.now().isoformat()
        }
    
    def _save_metrics(self):
        """Save metrics to file"""
        try:
            with open(self.metrics_file, 'w') as f:
                json.dump(self.metrics, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving metrics: {str(e)}")
    
    def record_response_time(self, endpoint: str, time_ms: float):
        """
        Record response time
        
        Args:
            endpoint: API endpoint
            time_ms: Response time in milliseconds
        """
        self.metrics["response_times"].append({
            "timestamp": datetime.now().isoformat(),
            "endpoint": endpoint,
            "time_ms": time_ms
        })
        
        # Track by endpoint
        if endpoint not in self.metrics["endpoint_times"]:
            self.metrics["endpoint_times"][endpoint] = []
        
        self.metrics["endpoint_times"][endpoint].append(time_ms)
        
        # Keep only last 1000
        if len(self.metrics["response_times"]) > 1000:
            self.metrics["response_times"] = self.metrics["response_times"][-1000:]
        
        # Keep only last 100 per endpoint
        if len(self.metrics["endpoint_times"][endpoint]) > 100:
            self.metrics["endpoint_times"][endpoint] = self.metrics["endpoint_times"][endpoint][-100:]
        
        self._save_metrics()
    
    def get_performance_stats(self) -> Dict:
        """Get performance statistics"""
        if not self.metrics["response_times"]:
            return {
                "average_response_time": 0,
                "p95_response_time": 0,
                "p99_response_time": 0,
                "slowest_endpoints": []
            }
        
        times = [m["time_ms"] for m in self.metrics["response_times"]]
        times.sort()
        
        avg_time = sum(times) / len(times)
        p95_time = times[int(len(times) * 0.95)] if times else 0
        p99_time = times[int(len(times) * 0.99)] if times else 0
        
        # Get slowest endpoints
        endpoint_avgs = {}
        for endpoint, times_list in self.metrics["endpoint_times"].items():
            if times_list:
                endpoint_avgs[endpoint] = sum(times_list) / len(times_list)
        
        slowest = sorted(endpoint_avgs.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "average_response_time": round(avg_time, 2),
            "p95_response_time": round(p95_time, 2),
            "p99_response_time": round(p99_time, 2),
            "slowest_endpoints": [
                {"endpoint": e, "avg_time": round(t, 2)}
                for e, t in slowest
            ]
        }


# Global instances
error_reporter = ErrorReporter()
performance_monitor = PerformanceMonitor()
