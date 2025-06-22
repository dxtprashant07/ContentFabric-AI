#!/usr/bin/env python3
"""
Streamlit runner script to avoid Windows file watcher issues
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Run Streamlit with file watcher disabled."""
    print("🚀 Starting ContentFabric AI Streamlit App...")
    print("📝 File watcher disabled to prevent Windows issues")
    
    # Set environment variable to disable file watcher
    env = os.environ.copy()
    env["STREAMLIT_SERVER_FILE_WATCHER_TYPE"] = "none"
    
    # Run streamlit
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ], env=env, check=True)
    except KeyboardInterrupt:
        print("\n👋 Streamlit app stopped by user")
    except Exception as e:
        print(f"❌ Error running Streamlit: {e}")
        print("💡 Try running: streamlit run app.py --server.fileWatcherType none")

if __name__ == "__main__":
    main() 