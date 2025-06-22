#!/usr/bin/env python3
"""
Test script to check if Google API key is responding
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    import google.generativeai as genai
    print("✅ Google Generative AI library imported successfully")
except ImportError:
    print("❌ Google Generative AI library not found")
    print("Run: pip install google-generativeai")
    sys.exit(1)

def test_api_key():
    """Test if the API key is working."""
    print("🔑 Testing Google API Key")
    print("=" * 40)
    
    # Get API key
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ No API key found!")
        print("Please set GOOGLE_API_KEY or GEMINI_API_KEY in your .env file")
        return False
    
    print(f"✅ API key found: {api_key[:10]}...{api_key[-4:]}")
    
    # Configure the API
    try:
        genai.configure(api_key=api_key)
        print("✅ API configured successfully")
    except Exception as e:
        print(f"❌ Failed to configure API: {e}")
        return False
    
    # List available models
    try:
        print("🔄 Checking available models...")
        models = genai.list_models()
        available_models = [model.name for model in models if 'generateContent' in model.supported_generation_methods]
        
        # Filter out deprecated models
        deprecated_models = ['models/gemini-1.0-pro-vision-latest', 'models/gemini-pro-vision']
        available_models = [model for model in available_models if model not in deprecated_models]
        
        print(f"✅ Available models: {available_models}")
        
        if not available_models:
            print("❌ No models available for content generation")
            return False
            
        # Use a specific working model instead of the first available
        model_name = 'models/gemini-1.5-flash'
        if model_name not in available_models:
            # Fallback to first available if our preferred model isn't available
            model_name = available_models[0]
        print(f"🔄 Using model: {model_name}")
        
    except Exception as e:
        print(f"❌ Failed to list models: {e}")
        # Use a specific working model as fallback
        model_name = 'models/gemini-1.5-flash'
        print(f"🔄 Trying with model: {model_name}")
    
    # Test with the model
    try:
        model = genai.GenerativeModel(model_name)
        print("✅ Model created successfully")
    except Exception as e:
        print(f"❌ Failed to create model: {e}")
        return False
    
    # Test a simple generation
    try:
        print("🔄 Testing content generation...")
        response = model.generate_content("Say 'Hello, API is working!' in one sentence.")
        
        if response and response.text:
            print("✅ Content generation successful!")
            print(f"Response: {response.text}")
            return True
        else:
            print("❌ No response received")
            return False
            
    except Exception as e:
        print(f"❌ Content generation failed: {e}")
        return False

def test_different_models():
    """Test different available models."""
    print("\n🤖 Testing Different Models")
    print("=" * 30)
    
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ No API key found")
        return
    
    genai.configure(api_key=api_key)
    
    models_to_test = [
        'models/gemini-1.5-flash',
        'models/gemini-1.5-pro',
        'models/gemini-pro'
    ]
    
    for model_name in models_to_test:
        try:
            print(f"🔄 Testing {model_name}...")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Test message")
            if response and response.text:
                print(f"✅ {model_name} - Working")
            else:
                print(f"⚠️  {model_name} - No response")
        except Exception as e:
            print(f"❌ {model_name} - Failed: {str(e)[:50]}...")

if __name__ == "__main__":
    success = test_api_key()
    
    if success:
        print("\n🎉 API key is working perfectly!")
        test_different_models()
    else:
        print("\n❌ API key test failed. Please check your configuration.") 