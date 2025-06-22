#!/usr/bin/env python3
"""
Test suite for AI Content Scraping & Writing System
"""

import asyncio
import sys
import os
from pathlib import Path
import json
from unittest.mock import Mock, patch

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.utils.config import Config
from src.ai_agents.base_agent import BaseAgent, AgentRegistry
from src.storage.chroma_manager import ChromaManager
from src.search.rl_search import RLSearchAgent


class TestConfig:
    """Test configuration management."""
    
    def test_config_validation(self):
        """Test configuration validation."""
        # Test with valid config
        config = Config()
        assert isinstance(config, Config)
        
        # Test API key validation
        config.google_api_key = "test_key"
        assert config.validate() is True
        
        config.google_api_key = None
        config.gemini_api_key = None
        assert config.validate() is False
    
    def test_directory_creation(self):
        """Test directory creation."""
        config = Config()
        assert Path(config.data_path).exists()
        assert Path(config.screenshots_path).exists()


class TestAgentRegistry:
    """Test agent registry functionality."""
    
    def test_agent_registration(self):
        """Test agent registration."""
        registry = AgentRegistry()
        
        # Create mock agent
        mock_agent = Mock(spec=BaseAgent)
        mock_agent.name = "test_agent"
        
        # Register agent
        registry.register(mock_agent)
        
        # Test retrieval
        retrieved_agent = registry.get_agent("test_agent")
        assert retrieved_agent == mock_agent
        
        # Test listing
        agents = registry.list_agents()
        assert "test_agent" in agents
    
    def test_agent_not_found(self):
        """Test handling of non-existent agent."""
        registry = AgentRegistry()
        agent = registry.get_agent("non_existent")
        assert agent is None


class TestChromaManager:
    """Test ChromaDB manager functionality."""
    
    @patch('src.storage.chroma_manager.chromadb')
    def test_chroma_initialization(self, mock_chromadb):
        """Test ChromaDB initialization."""
        # Mock ChromaDB client
        mock_client = Mock()
        mock_chromadb.PersistentClient.return_value = mock_client
        
        # Mock collections
        mock_collection = Mock()
        mock_client.get_or_create_collection.return_value = mock_collection
        
        # Test initialization
        manager = ChromaManager("./test_db")
        assert manager.client == mock_client
    
    def test_content_storage(self):
        """Test content storage functionality."""
        # This would require a real ChromaDB instance
        # For now, we'll test the interface
        pass


class TestRLSearch:
    """Test RL search functionality."""
    
    def test_rl_search_initialization(self):
        """Test RL search agent initialization."""
        agent = RLSearchAgent()
        assert agent.learning_rate == 0.1
        assert agent.exploration_rate == 0.1
        assert len(agent.search_history) == 0
    
    def test_search_functionality(self):
        """Test search functionality."""
        agent = RLSearchAgent()
        
        # Mock content database
        content_db = [
            {
                "version_id": "test1",
                "content": "This is a test content about morning gates",
                "metadata": {"title": "Test 1"}
            },
            {
                "version_id": "test2", 
                "content": "Another test content about chapters",
                "metadata": {"title": "Test 2"}
            }
        ]
        
        # Test search
        results = agent.search("morning gates", content_db, n_results=2)
        assert isinstance(results, list)
        assert len(results) <= 2
    
    def test_feedback_functionality(self):
        """Test feedback functionality."""
        agent = RLSearchAgent()
        
        # Add some search history
        agent.search_history.append({
            "search_id": "test_search",
            "query": "test query",
            "results": [{"version_id": "test1"}]
        })
        
        # Provide feedback
        agent.provide_feedback("test_search", "test1", 0.8)
        
        # Check reward history
        assert len(agent.reward_history) == 1
        assert agent.reward_history[0]["feedback_score"] == 0.8


class TestIntegration:
    """Integration tests."""
    
    async def test_full_workflow(self):
        """Test full workflow integration."""
        # This would test the complete workflow
        # For now, we'll create a mock test
        pass
    
    def test_api_endpoints(self):
        """Test API endpoint functionality."""
        # This would test the FastAPI endpoints
        # For now, we'll create a mock test
        pass


def run_tests():
    """Run all tests."""
    print("🧪 Running AI Content Scraping & Writing System Tests")
    print("=" * 60)
    
    test_classes = [
        TestConfig,
        TestAgentRegistry,
        TestChromaManager,
        TestRLSearch,
        TestIntegration
    ]
    
    total_tests = 0
    passed_tests = 0
    
    for test_class in test_classes:
        print(f"\n📋 Testing {test_class.__name__}...")
        
        test_instance = test_class()
        test_methods = [method for method in dir(test_instance) if method.startswith('test_')]
        
        for method_name in test_methods:
            total_tests += 1
            try:
                method = getattr(test_instance, method_name)
                
                # Handle async methods
                if asyncio.iscoroutinefunction(method):
                    asyncio.run(method())
                else:
                    method()
                
                print(f"  ✅ {method_name}")
                passed_tests += 1
                
            except Exception as e:
                print(f"  ❌ {method_name}: {str(e)}")
    
    print(f"\n📊 Test Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed!")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return False


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1) 