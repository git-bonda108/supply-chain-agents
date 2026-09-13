"""
NewsAPI Client for Supply Chain News Aggregation
"""

import os
from typing import List, Dict, Optional
from newsapi import NewsApiClient
from ratelimit import limits, sleep_and_retry
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class NewsAPIClientWrapper:
    """
    Wrapper for NewsAPI with rate limiting and error handling.
    
    NewsAPI provides news articles for:
    - Supply chain disruptions
    - Industry news
    - Market updates
    - Company announcements
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize NewsAPI client.
        
        Args:
            api_key: NewsAPI key (defaults to NEWSAPI_KEY env var)
        """
        self.api_key = api_key or os.getenv("NEWSAPI_KEY")
        if not self.api_key:
            raise ValueError("NEWSAPI_KEY not found in environment variables")
        
        self.client = NewsApiClient(api_key=self.api_key)
        self.rate_limit = int(os.getenv("NEWSAPI_RATE_LIMIT", "100"))
    
    @sleep_and_retry
    @limits(calls=100, period=60)  # 100 calls per minute
    def get_supply_chain_news(
        self,
        query: str,
        days_back: int = 7,
        language: str = "en"
    ) -> Dict:
        """
        Get supply chain related news.
        
        Args:
            query: Search query
            days_back: Number of days to look back
            language: Language code (default: "en")
        
        Returns:
            Dict with news articles
        """
        try:
            from_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
            to_date = datetime.now().strftime("%Y-%m-%d")
            
            # Search for articles
            response = self.client.get_everything(
                q=query,
                language=language,
                from_param=from_date,
                to=to_date,
                sort_by="relevancy",
                page_size=20
            )
            
            articles = []
            for article in response.get("articles", []):
                articles.append({
                    "title": article.get("title", ""),
                    "description": article.get("description", ""),
                    "url": article.get("url", ""),
                    "published_at": article.get("publishedAt", ""),
                    "source": article.get("source", {}).get("name", ""),
                    "author": article.get("author", "")
                })
            
            return {
                "query": query,
                "articles": articles,
                "total_results": response.get("totalResults", 0),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"NewsAPI error: {e}")
            return {
                "query": query,
                "articles": [],
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    @sleep_and_retry
    @limits(calls=100, period=60)
    def get_headlines(
        self,
        category: Optional[str] = None,
        country: Optional[str] = None
    ) -> Dict:
        """
        Get top headlines.
        
        Args:
            category: News category (business, technology, etc.)
            country: Country code (us, gb, etc.)
        
        Returns:
            Dict with headlines
        """
        try:
            response = self.client.get_top_headlines(
                category=category,
                country=country,
                page_size=20
            )
            
            articles = []
            for article in response.get("articles", []):
                articles.append({
                    "title": article.get("title", ""),
                    "description": article.get("description", ""),
                    "url": article.get("url", ""),
                    "published_at": article.get("publishedAt", ""),
                    "source": article.get("source", {}).get("name", "")
                })
            
            return {
                "category": category,
                "country": country,
                "articles": articles,
                "total_results": len(articles),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"NewsAPI headlines error: {e}")
            return {
                "category": category,
                "country": country,
                "articles": [],
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }


# Create singleton instance
def get_news_api_client() -> NewsAPIClientWrapper:
    """Get NewsAPI client instance."""
    return NewsAPIClientWrapper()



