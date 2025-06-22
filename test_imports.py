#!/usr/bin/env python3
"""
Test script to verify all imports work correctly
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test all critical imports."""
    print("🧪 Testing imports...")
    
    try:
        # Test basic imports
        import asyncio
        import json
        import requests
        print("✅ Basic imports successful")
        
        # Test Streamlit
        import streamlit as st
        print("✅ Streamlit imported successfully")
        
        # Test web scraper
        from src.scrapers.web_scraper import scrape_website
        print("✅ Web scraper imported successfully")
        
        # Test AI agents
        from src.ai_agents.writer_agent import WriterAgent
        print("✅ Writer agent imported successfully")
        
        # Test configuration
        from src.utils.config import config
        print("✅ Configuration imported successfully")
        
        # Test storage
        from src.storage.chroma_manager import get_storage_manager
        print("✅ Storage manager imported successfully")
        
        print("\n🎉 All imports successful!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_config():
    """Test configuration."""
    print("\n🔧 Testing configuration...")
    
    try:
        from src.utils.config import config
        
        # Check if API key is set
        api_key = config.get_api_key()
        if api_key and api_key != "your_google_api_key_here":
            print("✅ API key configured")
        else:
            print("⚠️  API key not configured - please edit .env file")
        
        # Check directories
        from pathlib import Path
        data_path = Path(config.data_path)
        if data_path.exists():
            print("✅ Data directory exists")
        else:
            print("⚠️  Data directory missing")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 ContentFabric AI - Import Test")
    print("=" * 40)
    
    imports_ok = test_imports()
    config_ok = test_config()
    
    if imports_ok and config_ok:
        print("\n✅ System ready to run!")
        print("💡 Run: python run_streamlit.py")
    else:
        print("\n❌ System not ready. Please fix the issues above.") 