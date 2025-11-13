"""
Image processing for CV/document uploads
"""
from typing import Dict, Optional
import base64
from io import BytesIO
from PIL import Image
import pytesseract
from langchain_openai import ChatOpenAI
import logging

logger = logging.getLogger(__name__)


class ImageProcessor:
    """Process uploaded images (CV, documents)"""
    
    def __init__(self):
        """Initialize image processor"""
        self.llm = ChatOpenAI(model="gpt-4-vision-preview", temperature=0.3, max_tokens=1000)
    
    def extract_text_ocr(self, image_data: bytes) -> str:
        """
        Extract text from image using OCR
        
        Args:
            image_data: Image bytes
            
        Returns:
            Extracted text
        """
        try:
            image = Image.open(BytesIO(image_data))
            text = pytesseract.image_to_string(image)
            logger.info("Text extracted from image using OCR")
            return text.strip()
        except Exception as e:
            logger.error(f"OCR error: {str(e)}")
            return ""
    
    def analyze_cv_image(self, image_data: bytes) -> Dict:
        """
        Analyze CV image using GPT-4 Vision
        
        Args:
            image_data: Image bytes
            
        Returns:
            CV analysis
        """
        try:
            # Convert to base64
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
            # Use GPT-4 Vision
            prompt = """Analyze this CV/resume image and extract:
1. Name
2. Contact information
3. Skills
4. Experience
5. Education

Format as structured data."""

            # Note: This is a simplified example
            # Full implementation would use vision API
            
            # Fallback to OCR
            text = self.extract_text_ocr(image_data)
            
            if text:
                return {
                    "success": True,
                    "text": text,
                    "message": "CV text extracted successfully"
                }
            else:
                return {
                    "success": False,
                    "text": "",
                    "message": "Unable to extract text from image"
                }
                
        except Exception as e:
            logger.error(f"CV analysis error: {str(e)}")
            return {
                "success": False,
                "text": "",
                "message": f"Error: {str(e)}"
            }
    
    def compare_with_usama_cv(self, extracted_cv: str) -> Dict:
        """
        Compare uploaded CV with Usama's profile
        
        Args:
            extracted_cv: Extracted CV text
            
        Returns:
            Comparison results
        """
        try:
            llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3)
            
            prompt = f"""Compare this CV with Usama Masood's profile:

Usama's Profile:
- MSc Data Science (Distinction)
- Skills: Python, ML, DL, NLP, CV, RAG, LangChain
- Experience: Data Scientist, ML Engineer
- Projects: Enterprise AI, RAG systems, predictive models

Uploaded CV:
{extracted_cv[:1000]}

Provide:
1. Skill overlap (%)
2. Experience similarity
3. Recommendations

Format:
OVERLAP: [percentage]
SIMILARITY: [description]
RECOMMENDATIONS: [suggestions]
"""

            response = llm.predict(prompt)
            
            # Parse response
            result = {
                "overlap": 0,
                "similarity": "",
                "recommendations": []
            }
            
            for line in response.split('\n'):
                if line.startswith('OVERLAP:'):
                    try:
                        result['overlap'] = int(line.split(':')[1].strip().replace('%', ''))
                    except:
                        pass
                elif line.startswith('SIMILARITY:'):
                    result['similarity'] = line.split(':')[1].strip()
                elif line.startswith('RECOMMENDATIONS:'):
                    result['recommendations'] = [line.split(':')[1].strip()]
            
            logger.info("CV comparison completed")
            return result
            
        except Exception as e:
            logger.error(f"CV comparison error: {str(e)}")
            return {
                "overlap": 0,
                "similarity": "Unable to compare",
                "recommendations": []
            }


# Global instance
image_processor = ImageProcessor()
