"""
Real-Time Data Sources Module
"""

from .tavily_client import TavilyClientWrapper, get_tavily_client
from .news_api_client import NewsAPIClientWrapper, get_news_api_client
from .cache_manager import CacheManager, get_cache_manager, cached
from .data_refresher import DataRefresher, get_data_refresher

__all__ = [
    "TavilyClientWrapper",
    "NewsAPIClientWrapper",
    "CacheManager",
    "DataRefresher",
    "get_tavily_client",
    "get_news_api_client",
    "get_cache_manager",
    "get_data_refresher",
    "cached",
]

