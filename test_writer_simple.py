#!/usr/bin/env python3
"""
Simple test for writer agent with instructions
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.ai_agents.writer_agent import WriterAgent

def test_with_instructions():
    """Test the writer agent with custom instructions."""
    print("🧪 Testing Writer Agent with Instructions")
    print("=" * 50)
    
    # Check for API key
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ No API key found!")
        print("Please create a .env file with your API key:")
        print("GOOGLE_API_KEY=your_actual_api_key_here")
        print("or")
        print("GEMINI_API_KEY=your_actual_api_key_here")
        return
    
    print("✅ API key found")
    
    # Create writer agent
    try:
        writer = WriterAgent()
        print("✅ Writer agent created")
    except Exception as e:
        print(f"❌ Failed to create writer agent: {e}")
        return
    
    # Test content
    test_content = """
    The sun rises in the east and sets in the west. This is a fundamental truth of nature that has been observed by humans for thousands of years. 
    The Earth's rotation on its axis causes this daily cycle, creating day and night. This natural phenomenon affects all life on Earth, 
    from the smallest plants to the largest animals, and has influenced human culture, religion, and science throughout history.
    """
    
    print("\n📝 Original content:")
    print(test_content)
    
    # Test with instructions
    instructions = "Summarize the content above."
    
    print(f"\n🎯 Instructions: {instructions}")
    
    try:
        import asyncio
        result = asyncio.run(writer.process(test_content, instructions=instructions))
        
        print("\n✅ Processing completed!")
        print(f"Status: {result.get('status')}")
        print(f"Result: {result.get('result', '')}")
        print(f"Feedback: {result.get('feedback')}")
        print(f"Confidence: {result.get('confidence')}")
        
    except Exception as e:
        print(f"❌ Processing failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_with_instructions() 