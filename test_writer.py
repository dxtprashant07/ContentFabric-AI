#!/usr/bin/env python3
"""
Test script for the writer agent
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.ai_agents.writer_agent import WriterAgent
from src.utils.config import config

def test_writer_agent():
    """Test the writer agent with a simple example."""
    print("🧪 Testing Writer Agent")
    print("=" * 40)
    
    # Check configuration
    print(f"API Key available: {bool(config.get_api_key())}")
    print(f"Model name: {config.model_name}")
    
    if not config.get_api_key():
        print("❌ No API key found. Please create a .env file with GOOGLE_API_KEY or GEMINI_API_KEY")
        return
    
    # Create writer agent
    try:
        writer = WriterAgent()
        print("✅ Writer agent created successfully")
    except Exception as e:
        print(f"❌ Failed to create writer agent: {e}")
        return
    
    # Test content
    test_content = {
        'content': 'The sun rises in the east and sets in the west. This is a fundamental truth of nature.',
        'title': 'Test Content'
    }
    
    print("\n📝 Testing with content:")
    print(test_content['content'])
    
    # Test processing
    try:
        import asyncio
        result = asyncio.run(writer.process(test_content, style='creative'))
        print("\n✅ Processing completed!")
        print(f"Status: {result.get('status')}")
        print(f"Result: {result.get('result', '')[:200]}...")
        print(f"Feedback: {result.get('feedback')}")
    except Exception as e:
        print(f"❌ Processing failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_writer_agent() 