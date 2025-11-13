"""
Calendar scheduling integration for meeting requests
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class CalendarScheduler:
    """Handle meeting scheduling requests"""
    
    AVAILABLE_SLOTS = [
        "Monday 10:00 AM - 5:00 PM GMT",
        "Tuesday 10:00 AM - 5:00 PM GMT",
        "Wednesday 10:00 AM - 5:00 PM GMT",
        "Thursday 10:00 AM - 5:00 PM GMT",
        "Friday 10:00 AM - 3:00 PM GMT"
    ]
    
    MEETING_TYPES = {
        "technical_interview": {
            "duration": 60,
            "description": "Technical discussion about skills and projects"
        },
        "intro_call": {
            "duration": 30,
            "description": "Initial introduction and role overview"
        },
        "portfolio_review": {
            "duration": 45,
            "description": "Detailed portfolio and project walkthrough"
        }
    }
    
    @staticmethod
    def get_available_slots() -> List[str]:
        """Get available time slots"""
        return CalendarScheduler.AVAILABLE_SLOTS
    
    @staticmethod
    def generate_calendly_link(meeting_type: str = "intro_call") -> str:
        """
        Generate Calendly scheduling link
        
        Args:
            meeting_type: Type of meeting
            
        Returns:
            Calendly link (placeholder)
        """
        # In production, integrate with actual Calendly API
        base_url = "https://calendly.com/usama-masood"
        
        if meeting_type in CalendarScheduler.MEETING_TYPES:
            duration = CalendarScheduler.MEETING_TYPES[meeting_type]["duration"]
            return f"{base_url}/{duration}min"
        
        return base_url
    
    @staticmethod
    def format_scheduling_response(meeting_type: str = "intro_call") -> str:
        """
        Format scheduling response for user
        
        Args:
            meeting_type: Type of meeting
            
        Returns:
            Formatted response with scheduling info
        """
        meeting_info = CalendarScheduler.MEETING_TYPES.get(
            meeting_type,
            CalendarScheduler.MEETING_TYPES["intro_call"]
        )
        
        calendly_link = CalendarScheduler.generate_calendly_link(meeting_type)
        
        response = f"""**Schedule a Meeting with Usama**

📅 **Meeting Type:** {meeting_info['description']}
⏰ **Duration:** {meeting_info['duration']} minutes

**Available Times:**
{chr(10).join(f"• {slot}" for slot in CalendarScheduler.AVAILABLE_SLOTS)}

**How to Schedule:**
1. Click here to book: {calendly_link}
2. Select your preferred time
3. Receive instant confirmation

**Alternative:**
Email: usama.masood@example.com
Subject: Meeting Request - [Your Company/Purpose]

I'll respond within 24 hours to confirm the meeting!

Looking forward to connecting! 🚀
"""
        
        return response
    
    @staticmethod
    def detect_scheduling_intent(query: str) -> Dict:
        """
        Detect if user wants to schedule a meeting
        
        Args:
            query: User query
            
        Returns:
            Detection result with meeting type
        """
        query_lower = query.lower()
        
        scheduling_keywords = [
            'schedule', 'meeting', 'call', 'interview', 'chat',
            'discuss', 'talk', 'connect', 'available', 'book',
            'calendly', 'appointment', 'time', 'meet'
        ]
        
        has_intent = any(keyword in query_lower for keyword in scheduling_keywords)
        
        # Detect meeting type
        meeting_type = "intro_call"
        if 'technical' in query_lower or 'interview' in query_lower:
            meeting_type = "technical_interview"
        elif 'portfolio' in query_lower or 'project' in query_lower:
            meeting_type = "portfolio_review"
        
        logger.info(f"Scheduling intent: {has_intent}, Type: {meeting_type}")
        
        return {
            "has_intent": has_intent,
            "meeting_type": meeting_type,
            "confidence": 0.8 if has_intent else 0.0
        }


# Global instance
calendar_scheduler = CalendarScheduler()
