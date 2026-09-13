"""
Data Refresher for Background Data Updates
"""

import asyncio
import logging
from typing import List, Callable
from datetime import datetime
from .cache_manager import CacheManager
from .tavily_client import TavilyClientWrapper
from .news_api_client import NewsAPIClientWrapper

logger = logging.getLogger(__name__)


class DataRefresher:
    """
    Background data refresher for keeping cache updated.
    
    Periodically refreshes:
    - Geopolitical risk data
    - Supply chain news
    - Market updates
    """
    
    def __init__(self):
        """Initialize data refresher."""
        self.cache = CacheManager()
        self.tavily = TavilyClientWrapper()
        self.news_api = NewsAPIClientWrapper()
        self.refresh_tasks: List[Callable] = []
        self.running = False
    
    def register_refresh_task(self, task: Callable, interval_seconds: int = 3600):
        """
        Register a refresh task.
        
        Args:
            task: Async function to run
            interval_seconds: Refresh interval
        """
        self.refresh_tasks.append((task, interval_seconds))
    
    async def refresh_geopolitical_risks(self):
        """Refresh geopolitical risk data."""
        try:
            # Common risk queries
            queries = [
                "China export controls",
                "supply chain disruptions",
                "trade restrictions",
                "component shortages"
            ]
            
            for query in queries:
                result = self.tavily.search_geopolitical_risks(query)
                # Cache result
                cache_key = f"geopolitical:{query}"
                self.cache.set(cache_key, result)
            
            logger.info("Geopolitical risks refreshed")
            
        except Exception as e:
            logger.error(f"Error refreshing geopolitical risks: {e}")
    
    async def refresh_supply_chain_news(self):
        """Refresh supply chain news."""
        try:
            queries = [
                "supply chain disruption",
                "component shortage",
                "export controls"
            ]
            
            for query in queries:
                result = self.news_api.get_supply_chain_news(query, days_back=1)
                # Cache result
                cache_key = f"news:{query}"
                self.cache.set(cache_key, result)
            
            logger.info("Supply chain news refreshed")
            
        except Exception as e:
            logger.error(f"Error refreshing news: {e}")
    
    async def run_refresh_loop(self):
        """Run background refresh loop."""
        self.running = True
        
        while self.running:
            try:
                # Clear expired cache entries
                self.cache.clear_expired()
                
                # Refresh data
                await self.refresh_geopolitical_risks()
                await self.refresh_supply_chain_news()
                
                # Wait before next refresh (1 hour)
                await asyncio.sleep(3600)
                
            except Exception as e:
                logger.error(f"Refresh loop error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    def start(self):
        """Start background refresh."""
        if not self.running:
            asyncio.create_task(self.run_refresh_loop())
    
    def stop(self):
        """Stop background refresh."""
        self.running = False


# Create singleton instance
def get_data_refresher() -> DataRefresher:
    """Get data refresher instance."""
    return DataRefresher()



