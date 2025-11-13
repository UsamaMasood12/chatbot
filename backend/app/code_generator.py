"""
Code generation from project descriptions
"""
from typing import Dict, Optional
from langchain_openai import ChatOpenAI
import logging

logger = logging.getLogger(__name__)


class CodeGenerator:
    """Generate code snippets and examples from project descriptions"""
    
    def __init__(self):
        """Initialize code generator"""
        self.llm = ChatOpenAI(model="gpt-4", temperature=0.3, max_tokens=2000)
    
    def generate_code(
        self,
        project_description: str,
        language: str = "python",
        task: str = "example"
    ) -> Dict:
        """
        Generate code based on project description
        
        Args:
            project_description: Description of the project
            language: Programming language
            task: Type of code to generate (example, function, class, etc.)
            
        Returns:
            Generated code with explanation
        """
        try:
            prompt = f"""Based on this project description, generate a {task} in {language}.

Project Description:
{project_description}

Generate clean, professional {language} code that demonstrates the key concepts.
Include:
1. Well-commented code
2. Error handling
3. Best practices
4. Brief explanation

Format:
```{language}
[code here]
```

EXPLANATION:
[2-3 sentences explaining the code]
"""

            response = self.llm.predict(prompt)
            
            # Extract code and explanation
            code = ""
            explanation = ""
            
            if "```" in response:
                parts = response.split("```")
                if len(parts) >= 2:
                    # Get code block (remove language identifier)
                    code = parts[1].strip()
                    if code.startswith(language):
                        code = code[len(language):].strip()
                    
                    # Get explanation
                    if len(parts) > 2:
                        explanation = parts[2].replace("EXPLANATION:", "").strip()
            
            if not explanation and "EXPLANATION:" in response:
                explanation = response.split("EXPLANATION:")[1].strip()
            
            logger.info(f"Generated {language} code for {task}")
            
            return {
                "code": code,
                "explanation": explanation,
                "language": language,
                "task": task
            }
            
        except Exception as e:
            logger.error(f"Code generation error: {str(e)}")
            return {
                "code": "# Error generating code",
                "explanation": "Unable to generate code at this time.",
                "language": language,
                "task": task
            }
    
    def explain_code(self, code: str, language: str = "python") -> str:
        """
        Explain existing code
        
        Args:
            code: Code to explain
            language: Programming language
            
        Returns:
            Code explanation
        """
        try:
            prompt = f"""Explain this {language} code in simple terms:

```{language}
{code}
```

Provide:
1. What the code does
2. Key concepts used
3. Potential improvements
"""

            response = self.llm.predict(prompt)
            logger.info("Code explanation generated")
            return response.strip()
            
        except Exception as e:
            logger.error(f"Code explanation error: {str(e)}")
            return "Unable to explain code at this time."
    
    def suggest_improvements(self, code: str, language: str = "python") -> Dict:
        """
        Suggest improvements for code
        
        Args:
            code: Code to improve
            language: Programming language
            
        Returns:
            Improvement suggestions
        """
        try:
            prompt = f"""Review this {language} code and suggest improvements:

```{language}
{code}
```

Provide:
1. Performance improvements
2. Code quality suggestions
3. Best practices to apply
4. Security considerations

Format as JSON:
{{
  "improvements": ["improvement 1", "improvement 2"],
  "refactored_code": "improved code here"
}}
"""

            response = self.llm.predict(prompt)
            logger.info("Code improvements suggested")
            
            # Try to parse JSON response
            import json
            try:
                result = json.loads(response)
                return result
            except:
                return {
                    "improvements": [response],
                    "refactored_code": code
                }
            
        except Exception as e:
            logger.error(f"Code improvement error: {str(e)}")
            return {
                "improvements": ["Unable to suggest improvements"],
                "refactored_code": code
            }


# Global instance
code_generator = CodeGenerator()
