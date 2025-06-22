import json
import asyncio
from typing import Dict, Any, List, Optional
try:
    import google.generativeai as genai  # type: ignore
except ImportError:
    print("Google Generative AI not installed. Run: pip install google-generativeai")
    genai = None

from .base_agent import BaseAgent, agent_registry
from src.utils.config import config


class ReviewerAgent(BaseAgent):
    """AI agent for content review and feedback."""
    
    def __init__(self, name: str = "reviewer", model_name: Optional[str] = None):
        if model_name is None:
            model_name = config.model_name
        super().__init__(name, model_name)
        self._model: Optional[Any] = None
    
    @property
    def model(self):
        """Get model lazily."""
        if self._model is None and genai:
            genai.configure(api_key=self.api_key)
            self._model = genai.GenerativeModel(self.model_name)
        return self._model
    
    async def process(self, content: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Review content and provide feedback."""
        try:
            if not self.model:
                raise Exception("AI model not initialized")
                
            # Extract content to review
            content_to_review = content.get('result', content.get('content', ''))
            original_content = content.get('original_content', '')
            
            # Get review criteria
            criteria = kwargs.get('criteria', ['grammar', 'style', 'clarity', 'engagement'])
            
            # Create review prompt
            prompt = self._create_review_prompt(content_to_review, original_content, criteria)
            
            # Generate review
            response = await self._generate_review(prompt)
            
            # Parse and validate response
            result = self._parse_response(response)
            result = self._add_metadata(result)
            
            return result
            
        except Exception as e:
            return {
                "status": "error",
                "result": "",
                "feedback": f"Error in reviewer agent: {str(e)}",
                "confidence": 0.0,
                "timestamp": self._get_timestamp(),
                "agent_name": self.name,
                "model_name": self.model_name,
                "processed_at": self._get_timestamp()
            }
    
    def _create_review_prompt(self, content: str, original: str, criteria: List[str]) -> str:
        """Create a review prompt based on criteria."""
        criteria_descriptions = {
            'grammar': "Check for grammatical errors, punctuation, and sentence structure.",
            'style': "Evaluate writing style, tone, and consistency.",
            'clarity': "Assess clarity, readability, and logical flow.",
            'engagement': "Evaluate how engaging and compelling the content is.",
            'accuracy': "Check factual accuracy and consistency with the original.",
            'creativity': "Assess originality and creative elements.",
            'completeness': "Check if all important information is included."
        }
        
        criteria_text = "\n".join([f"- {criteria_descriptions.get(c, c)}" for c in criteria])
        
        instructions = f"""
You are an expert content reviewer. Your task is to review the following content.

Review criteria:
{criteria_text}

Content to review:
{content}

Original content (for comparison):
{original}

Please provide a comprehensive review covering all specified criteria.

Provide your response in the following JSON format:
{{
    "status": "success",
    "result": {{
        "overall_score": 0.0-1.0,
        "criteria_scores": {{
            "grammar": 0.0-1.0,
            "style": 0.0-1.0,
            "clarity": 0.0-1.0,
            "engagement": 0.0-1.0
        }},
        "strengths": ["list of strengths"],
        "weaknesses": ["list of areas for improvement"],
        "suggestions": ["specific suggestions for improvement"]
    }},
    "feedback": "overall assessment",
    "confidence": 0.0-1.0,
    "timestamp": "ISO timestamp"
}}
"""
        return instructions
    
    async def _generate_review(self, prompt: str) -> str:
        """Generate review using the AI model."""
        try:
            if not self.model:
                raise Exception("AI model not initialized")
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            raise Exception(f"Failed to generate review: {str(e)}")
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse the AI response."""
        try:
            # Try to extract JSON from response
            if '{' in response and '}' in response:
                start = response.find('{')
                end = response.rfind('}') + 1
                json_str = response[start:end]
                result = json.loads(json_str)
                
                if self._validate_response(result):
                    return result
            
            # If JSON parsing fails, create a structured response
            return {
                "status": "success",
                "result": {
                    "overall_score": 0.7,
                    "criteria_scores": {
                        "grammar": 0.7,
                        "style": 0.7,
                        "clarity": 0.7,
                        "engagement": 0.7
                    },
                    "strengths": ["Content reviewed successfully"],
                    "weaknesses": ["Unable to parse detailed feedback"],
                    "suggestions": ["Review completed"]
                },
                "feedback": "Content reviewed (JSON parsing failed)",
                "confidence": 0.6,
                "timestamp": self._get_timestamp()
            }
            
        except json.JSONDecodeError:
            return {
                "status": "success",
                "result": {
                    "overall_score": 0.6,
                    "criteria_scores": {
                        "grammar": 0.6,
                        "style": 0.6,
                        "clarity": 0.6,
                        "engagement": 0.6
                    },
                    "strengths": ["Review completed"],
                    "weaknesses": ["JSON parsing failed"],
                    "suggestions": ["Manual review recommended"]
                },
                "feedback": "Content reviewed (JSON parsing failed)",
                "confidence": 0.5,
                "timestamp": self._get_timestamp()
            }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    async def compare_versions(self, version1: Dict[str, Any], version2: Dict[str, Any]) -> Dict[str, Any]:
        """Compare two versions of content."""
        try:
            content1 = version1.get('result', version1.get('content', ''))
            content2 = version2.get('result', version2.get('content', ''))
            
            prompt = f"""
You are an expert content reviewer. Compare these two versions of content and provide feedback.

Version 1:
{content1}

Version 2:
{content2}

Please compare them and provide your assessment in the following JSON format:
{{
    "status": "success",
    "result": {{
        "better_version": "1 or 2",
        "improvements": ["list of improvements in the better version"],
        "regressions": ["list of things that got worse"],
        "overall_assessment": "brief summary"
    }},
    "feedback": "detailed comparison",
    "confidence": 0.0-1.0,
    "timestamp": "ISO timestamp"
}}
"""
            
            response = await self._generate_review(prompt)
            result = self._parse_response(response)
            result = self._add_metadata(result)
            
            return result
            
        except Exception as e:
            return {
                "status": "error",
                "result": "",
                "feedback": f"Error comparing versions: {str(e)}",
                "confidence": 0.0,
                "timestamp": self._get_timestamp(),
                "agent_name": self.name,
                "model_name": self.model_name,
                "processed_at": self._get_timestamp()
            }


# Register the reviewer agent
reviewer_agent = ReviewerAgent()
agent_registry.register(reviewer_agent) 