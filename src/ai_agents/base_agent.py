from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
import json
import os
from datetime import datetime
from src.utils.config import config


class BaseAgent(ABC):
    """Base class for all AI agents."""
    
    def __init__(self, name: str, model_name: Optional[str] = None):
        self.name = name
        if model_name is None:
            model_name = config.model_name
        self.model_name = model_name
        self._api_key = None
    
    @property
    def api_key(self):
        """Get API key lazily."""
        if self._api_key is None:
            self._api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
            if not self._api_key:
                raise ValueError(f"API key not found for {self.name} agent")
        return self._api_key
        
    @abstractmethod
    async def process(self, content: Union[str, Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """Process content and return results."""
        pass
    
    def _create_prompt(self, content: str, instructions: str) -> str:
        """Create a prompt for the AI model."""
        return f"""
{instructions}

Content to process:
{content}

Please provide your response in the following JSON format:
{{
    "status": "success|error",
    "result": "processed content",
    "feedback": "any feedback or suggestions",
    "confidence": 0.0-1.0,
    "timestamp": "ISO timestamp"
}}
"""
    
    def _validate_response(self, response: Dict[str, Any]) -> bool:
        """Validate AI response format."""
        required_fields = ["status", "result", "feedback", "confidence", "timestamp"]
        return all(field in response for field in required_fields)
    
    def _add_metadata(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Add metadata to the result."""
        result.update({
            "agent_name": self.name,
            "model_name": self.model_name,
            "processed_at": datetime.now().isoformat()
        })
        return result


class AgentRegistry:
    """Registry for managing AI agents."""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
    
    def register(self, agent: BaseAgent):
        """Register an agent."""
        self.agents[agent.name] = agent
    
    def get_agent(self, name: str) -> Optional[BaseAgent]:
        """Get an agent by name."""
        return self.agents.get(name)
    
    def list_agents(self) -> List[str]:
        """List all registered agents."""
        return list(self.agents.keys())
    
    async def process_with_agent(self, agent_name: str, content: Union[str, Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """Process content with a specific agent."""
        agent = self.get_agent(agent_name)
        if not agent:
            raise ValueError(f"Agent '{agent_name}' not found")
        
        return await agent.process(content, **kwargs)


# Global agent registry
agent_registry = AgentRegistry() 