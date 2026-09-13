"""
Helper Utilities
"""

import os
import logging
from typing import Optional, Dict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def setup_logging(level: Optional[str] = None):
    """
    Setup logging configuration.
    
    Args:
        level: Log level (defaults to LOG_LEVEL env var or INFO)
    """
    log_level = level or os.getenv("LOG_LEVEL", "INFO")
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )


def get_env_var(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Get environment variable with optional default.
    
    Args:
        key: Environment variable key
        default: Default value if not found
    
    Returns:
        Environment variable value or default
    """
    return os.getenv(key, default)


def validate_api_keys() -> Dict[str, bool]:
    """
    Validate required API keys are present.
    
    Returns:
        Dict with validation results
    """
    required_keys = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "TAVILY_API_KEY": os.getenv("TAVILY_API_KEY"),
        "NEWSAPI_KEY": os.getenv("NEWSAPI_KEY")
    }
    
    # Optional keys
    optional_keys = {
        "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
        "DEEPSEEK_API_KEY": os.getenv("DEEPSEEK_API_KEY"),
        "GROQ_API_KEY": os.getenv("GROQ_API_KEY"),
        "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
        "SERPER_API_KEY": os.getenv("SERPER_API_KEY")
    }
    
    results = {}
    for key, value in required_keys.items():
        results[key] = value is not None and value != ""
    
    # Add optional keys status
    for key, value in optional_keys.items():
        results[key] = value is not None and value != ""
    
    return results

