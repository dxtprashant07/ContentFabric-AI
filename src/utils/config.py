import os
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv


class Config:
    """Configuration manager for the application."""
    
    def __init__(self, env_file: str = ".env"):
        # Load environment variables
        load_dotenv(env_file)
        
        # API Keys
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        
        # Database Configuration
        self.chroma_db_path = os.getenv("CHROMA_DB_PATH", "./data/chroma_db")
        
        # Server Configuration
        self.host = os.getenv("HOST", "0.0.0.0")
        self.port = int(os.getenv("PORT", "8000"))
        
        # Storage Paths
        self.screenshots_path = os.getenv("SCREENSHOTS_PATH", "./screenshots")
        self.data_path = os.getenv("DATA_PATH", "./data")
        
        # AI Configuration
        self.model_name = os.getenv("MODEL_NAME", "models/gemini-1.5-flash")
        self.max_tokens = int(os.getenv("MAX_TOKENS", "2048"))
        self.temperature = float(os.getenv("TEMPERATURE", "0.7"))
        
        # Create necessary directories
        self._create_directories()
    
    def _create_directories(self):
        """Create necessary directories if they don't exist."""
        directories = [
            self.chroma_db_path,
            self.screenshots_path,
            self.data_path
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def validate(self) -> bool:
        """Validate configuration."""
        errors = []
        
        if not self.google_api_key and not self.gemini_api_key:
            errors.append("Either GOOGLE_API_KEY or GEMINI_API_KEY must be set")
        
        if self.port < 1 or self.port > 65535:
            errors.append("PORT must be between 1 and 65535")
        
        if self.temperature < 0.0 or self.temperature > 2.0:
            errors.append("TEMPERATURE must be between 0.0 and 2.0")
        
        if errors:
            print("Configuration errors:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        return True
    
    def get_api_key(self) -> Optional[str]:
        """Get the available API key."""
        return self.google_api_key or self.gemini_api_key
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "api_keys": {
                "google_api_key": bool(self.google_api_key),
                "gemini_api_key": bool(self.gemini_api_key)
            },
            "database": {
                "chroma_db_path": self.chroma_db_path
            },
            "server": {
                "host": self.host,
                "port": self.port
            },
            "storage": {
                "screenshots_path": self.screenshots_path,
                "data_path": self.data_path
            },
            "ai": {
                "model_name": self.model_name,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature
            }
        }


# Global configuration instance
config = Config() 