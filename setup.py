#!/usr/bin/env python3
"""
Setup script for AI Content Scraping & Writing System
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command: str, description: str) -> bool:
    """Run a command and return success status."""
    print(f"🔄 {description}...")
    try:
        # Use shell=True for Windows compatibility
        result = subprocess.run(
            command, 
            shell=True, 
            check=True, 
            capture_output=True, 
            text=True,
            env=dict(os.environ, PYTHONPATH="")
        )
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Error: {e.stderr}")
        return False


def install_dependencies_windows():
    """Install dependencies with Windows-specific handling."""
    print("🔄 Installing Python dependencies for Windows...")
    
    # First, upgrade pip
    try:
        subprocess.run("python -m pip install --upgrade pip", shell=True, check=True)
        print("✅ Pip upgraded successfully")
    except subprocess.CalledProcessError:
        print("⚠️  Pip upgrade failed, continuing...")
    
    # Install dependencies in smaller batches to avoid long path issues
    dependency_batches = [
        "requests beautifulsoup4 python-dotenv pillow",
        "fastapi uvicorn pydantic",
        "numpy scikit-learn",
        "playwright",
        "google-generativeai streamlit nest-asyncio"
    ]
    
    for i, batch in enumerate(dependency_batches, 1):
        print(f"📦 Installing batch {i}/{len(dependency_batches)}: {batch}")
        try:
            # Use --no-warn-script-location to suppress PATH warnings
            cmd = f"pip install {batch} --no-warn-script-location"
            result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
            print(f"✅ Batch {i} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Batch {i} failed: {e.stderr}")
            print("⚠️  Continuing with next batch...")
    
    return True


def main():
    """Main setup function."""
    print("🚀 Setting up AI Content Scraping & Writing System")
    print("=" * 60)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Check if we're on Windows
    is_windows = os.name == 'nt'
    if is_windows:
        print("🪟 Windows detected - using Windows-specific installation")
        install_dependencies_windows()
    else:
        # Install Python dependencies for non-Windows
        if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
            print("❌ Failed to install dependencies. Please check your internet connection and try again.")
            sys.exit(1)
    
    # Install Playwright browsers
    print("🌐 Installing Playwright browsers...")
    try:
        subprocess.run("playwright install", shell=True, check=True)
        print("✅ Playwright browsers installed successfully")
    except subprocess.CalledProcessError:
        print("⚠️  Playwright browser installation failed. You may need to install them manually later.")
        print("   Try running: playwright install")
    
    # Create necessary directories
    directories = [
        "data",
        "screenshots", 
        "data/chroma_db"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    # Create .env file if it doesn't exist
    env_file = Path(".env")
    if not env_file.exists():
        print("📝 Creating .env file...")
        env_content = """# API Keys
GOOGLE_API_KEY=your_google_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

# Database Configuration
CHROMA_DB_PATH=./data/chroma_db

# Server Configuration
HOST=0.0.0.0
PORT=8000

# Storage Paths
SCREENSHOTS_PATH=./screenshots
DATA_PATH=./data

# AI Configuration
MODEL_NAME=gemini-1.5-flash
MAX_TOKENS=2048
TEMPERATURE=0.7
"""
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✅ Created .env file")
        print("⚠️  Please edit .env file and add your API keys")
    else:
        print("✅ .env file already exists")
    
    # Test imports
    print("🧪 Testing imports...")
    try:
        import asyncio
        import json
        import requests
        print("✅ Basic imports successful")
        
        # Test optional imports
        try:
            import playwright
            print("✅ Playwright imported successfully")
        except ImportError:
            print("⚠️  Playwright not available")
        
        try:
            import google.generativeai
            print("✅ Google Generative AI imported successfully")
        except ImportError:
            print("⚠️  Google Generative AI not available")
        
        try:
            import fastapi
            print("✅ FastAPI imported successfully")
        except ImportError:
            print("⚠️  FastAPI not available")
        
    except ImportError as e:
        print(f"❌ Import test failed: {e}")
        sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit .env file and add your API keys")
    print("2. Run: python main.py")
    print("3. Start the API server: python -m src.api.main")
    print("\n📚 For more information, check the README.md file")
    
    if is_windows:
        print("\n🪟 Windows-specific notes:")
        print("- If you encounter PATH issues, add Python Scripts to your PATH")
        print("- For long path issues, enable Windows Long Path support")
        print("- Some packages may need manual installation if automatic fails")


if __name__ == "__main__":
    main() 