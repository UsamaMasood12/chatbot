"""
Email notification system for important queries
"""
from typing import Dict, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
import os

logger = logging.getLogger(__name__)


class EmailNotifier:
    """Send email notifications for important queries"""
    
    def __init__(
        self,
        smtp_server: str = "smtp.gmail.com",
        smtp_port: int = 587,
        sender_email: Optional[str] = None,
        sender_password: Optional[str] = None,
        recipient_email: Optional[str] = None
    ):
        """
        Initialize email notifier
        
        Args:
            smtp_server: SMTP server address
            smtp_port: SMTP port
            sender_email: Sender email address
            sender_password: Sender email password/app password
            recipient_email: Recipient email (Usama)
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email or os.getenv("NOTIFICATION_EMAIL")
        self.sender_password = sender_password or os.getenv("NOTIFICATION_PASSWORD")
        self.recipient_email = recipient_email or os.getenv("USAMA_EMAIL", "usama.masood@example.com")
        
        self.enabled = bool(self.sender_email and self.sender_password)
        
        if not self.enabled:
            logger.warning("Email notifications disabled - credentials not configured")
    
    def send_recruiter_notification(
        self,
        query: str,
        session_id: str,
        recruiter_confidence: float,
        job_fit_score: Optional[int] = None
    ):
        """
        Send notification when recruiter is detected
        
        Args:
            query: Recruiter's query
            session_id: Session ID
            recruiter_confidence: Detection confidence
            job_fit_score: Job fit score if available
        """
        if not self.enabled:
            logger.info("Email notification skipped - not configured")
            return
        
        try:
            subject = f"🎯 Recruiter Query Detected - Confidence: {recruiter_confidence:.0%}"
            
            body = f"""
Hello Usama,

A potential recruiter has engaged with your portfolio chatbot!

📊 Detection Confidence: {recruiter_confidence:.0%}
🔗 Session ID: {session_id}
💬 Query: "{query}"
"""
            
            if job_fit_score:
                body += f"\n🎯 Job Fit Score: {job_fit_score}/100\n"
            
            body += f"""
⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

View full conversation in analytics dashboard.

Best regards,
Portfolio Chatbot
"""
            
            self._send_email(subject, body)
            logger.info(f"Recruiter notification sent for session {session_id}")
            
        except Exception as e:
            logger.error(f"Error sending recruiter notification: {str(e)}")
    
    def send_feedback_notification(
        self,
        rating: str,
        query: str,
        comment: Optional[str] = None
    ):
        """
        Send notification for feedback
        
        Args:
            rating: Rating (positive/negative)
            query: User query
            comment: Optional comment
        """
        if not self.enabled or rating == "positive":
            return  # Only notify on negative feedback
        
        try:
            subject = "⚠️ Negative Feedback Received"
            
            body = f"""
Hello Usama,

Negative feedback received on your portfolio chatbot.

👎 Rating: Negative
💬 Query: "{query}"
"""
            
            if comment:
                body += f"\n💭 Comment: \"{comment}\"\n"
            
            body += f"""
⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Please review and improve the response.

Best regards,
Portfolio Chatbot
"""
            
            self._send_email(subject, body)
            logger.info("Negative feedback notification sent")
            
        except Exception as e:
            logger.error(f"Error sending feedback notification: {str(e)}")
    
    def _send_email(self, subject: str, body: str):
        """
        Send email using SMTP
        
        Args:
            subject: Email subject
            body: Email body
        """
        message = MIMEMultipart()
        message["From"] = self.sender_email
        message["To"] = self.recipient_email
        message["Subject"] = subject
        
        message.attach(MIMEText(body, "plain"))
        
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.send_message(message)


# Global email notifier
email_notifier = EmailNotifier()
