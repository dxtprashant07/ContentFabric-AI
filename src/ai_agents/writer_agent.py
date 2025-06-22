import json
import asyncio
from typing import Dict, Any, List, Optional, Union
try:
    import google.generativeai as genai  # type: ignore
except ImportError:
    print("Google Generative AI not installed. Run: pip install google-generativeai")
    genai = None

from .base_agent import BaseAgent, agent_registry
from src.utils.config import config


class WriterAgent(BaseAgent):
    """AI agent for content writing and spinning."""
    
    def __init__(self, name: str = "writer", model_name: Optional[str] = None):
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
    
    async def process(self, content: Union[str, Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """Process content for writing and spinning."""
        try:
            if not self.model:
                raise Exception("AI model not initialized")
                
            # Handle different input formats
            if isinstance(content, str):
                # If content is a string, treat it as the content to process
                original_content = content
                instructions = kwargs.get('instructions', 'Process this content.')
            elif isinstance(content, dict):
                # Extract content to process
                original_content = content.get('content', '')
                chapter_content = content.get('chapter_content', original_content)
                original_content = chapter_content if chapter_content else original_content
                instructions = kwargs.get('instructions', 'Process this content.')
            else:
                raise ValueError("Content must be a string or dictionary")
            
            # Get writing style and instructions
            style = kwargs.get('style', 'creative')
            target_length = kwargs.get('target_length', 'similar')
            
            # Create writing prompt
            prompt = self._create_writing_prompt(original_content, style, target_length, instructions)
            
            # Generate content
            response = await self._generate_content_async(prompt)
            
            # Parse and validate response
            result = self._parse_response(response)
            result = self._add_metadata(result)
            
            return result
            
        except Exception as e:
            return {
                "status": "error",
                "result": "",
                "feedback": f"Error in writer agent: {str(e)}",
                "confidence": 0.0,
                "timestamp": self._get_timestamp(),
                "agent_name": self.name,
                "model_name": self.model_name,
                "processed_at": self._get_timestamp()
            }
    
    def _create_writing_prompt(self, content: str, style: str, target_length: str, instructions: str) -> str:
        """Create a writing prompt based on style and requirements."""
        style_instructions = {
            'creative': "Rewrite this content in a creative and engaging style, adding vivid descriptions and emotional depth.",
            'academic': "Rewrite this content in an academic style with formal language and analytical approach.",
            'casual': "Rewrite this content in a casual, conversational style that's easy to read and understand.",
            'poetic': "Rewrite this content in a poetic style with rhythmic language and metaphorical expressions.",
            'technical': "Rewrite this content in a technical style with precise language and detailed explanations."
        }
        
        length_instructions = {
            'shorter': "Make the content more concise while preserving key information.",
            'longer': "Expand the content with additional details and examples.",
            'similar': "Maintain similar length while improving quality and style."
        }
        
        prompt = f"""
You are an expert content writer. Your task is to process the following content.

{instructions}

Style: {style_instructions.get(style, style_instructions['creative'])}
Length: {length_instructions.get(target_length, length_instructions['similar'])}

Original content:
{content}

Please process this content according to the specified instructions, style, and length requirements. 
Maintain the core meaning and key information while improving the writing quality.

Provide your response in the following JSON format:
{{
    "status": "success",
    "result": "processed content",
    "feedback": "brief explanation of changes made",
    "confidence": 0.0-1.0,
    "timestamp": "ISO timestamp"
}}
"""
        return prompt
    
    def _generate_content(self, prompt: str) -> str:
        """Generate content using the AI model."""
        try:
            if not self.model:
                raise Exception("AI model not initialized")
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            raise Exception(f"Failed to generate content: {str(e)}")
    
    async def _generate_content_async(self, prompt: str) -> str:
        """Async wrapper for content generation."""
        # Run the synchronous method in a thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._generate_content, prompt)
    
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
                "result": response.strip(),
                "feedback": "Content generated successfully",
                "confidence": 0.8,
                "timestamp": self._get_timestamp()
            }
            
        except json.JSONDecodeError:
            return {
                "status": "success",
                "result": response.strip(),
                "feedback": "Content generated (JSON parsing failed)",
                "confidence": 0.7,
                "timestamp": self._get_timestamp()
            }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    async def spin_content(self, content: str, variations: int = 3) -> List[Dict[str, Any]]:
        """Generate multiple variations of content."""
        results = []
        
        for i in range(variations):
            # Vary the style for each iteration
            styles = ['creative', 'casual', 'poetic']
            style = styles[i % len(styles)]
            
            result = await self.process({'content': content}, style=style)
            result['variation'] = i + 1
            results.append(result)
        
        return results


# Register the writer agent
writer_agent = WriterAgent()
agent_registry.register(writer_agent) 