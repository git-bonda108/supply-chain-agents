"""
Tavily API Client for Real-Time Geopolitical Risk Monitoring
"""

import os
from typing import List, Dict, Optional
from tavily import TavilyClient
from ratelimit import limits, sleep_and_retry
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class TavilyClientWrapper:
    """
    Wrapper for Tavily API with rate limiting and error handling.
    
    Tavily provides real-time web search for:
    - Geopolitical events
    - Export control announcements
    - Supply chain disruptions
    - Trade policy changes
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Tavily client.
        
        Args:
            api_key: Tavily API key (defaults to TAVILY_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY not found in environment variables")
        
        self.client = TavilyClient(api_key=self.api_key)
        self.rate_limit = int(os.getenv("TAVILY_RATE_LIMIT", "100"))
        
    @sleep_and_retry
    @limits(calls=100, period=60)  # 100 calls per minute
    def search_geopolitical_risks(
        self,
        query: str,
        region: Optional[str] = None,
        max_results: int = 10
    ) -> Dict:
        """
        Search for geopolitical risks affecting supply chains.
        
        Args:
            query: Search query (e.g., "China export controls memory chips")
            region: Optional region filter
            max_results: Maximum number of results
        
        Returns:
            Dict with search results including:
            - results: List of relevant articles/events
            - risk_score: Calculated risk score
            - timestamp: Search timestamp
        """
        try:
            # Enhance query for supply chain context
            enhanced_query = f"{query} supply chain export controls trade restrictions"
            if region:
                enhanced_query += f" {region}"
            
            # Search using Tavily
            response = self.client.search(
                query=enhanced_query,
                search_depth="advanced",
                max_results=max_results,
                include_answer=True,
                include_raw_content=False
            )
            
            # Process results
            results = []
            for result in response.get("results", []):
                results.append({
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "content": result.get("content", ""),
                    "score": result.get("score", 0.0),
                    "published_date": result.get("published_date")
                })
            
            # Calculate risk score based on recency and relevance
            risk_score = self._calculate_risk_score(results)
            
            return {
                "query": query,
                "region": region,
                "results": results,
                "risk_score": risk_score,
                "answer": response.get("answer", ""),
                "timestamp": datetime.now().isoformat(),
                "total_results": len(results)
            }
            
        except Exception as e:
            logger.error(f"Tavily search error: {e}")
            return {
                "query": query,
                "region": region,
                "results": [],
                "risk_score": 0.0,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    @sleep_and_retry
    @limits(calls=100, period=60)
    def search_export_controls(
        self,
        country: str,
        product: Optional[str] = None
    ) -> Dict:
        """
        Search for export control information.
        
        Args:
            country: Country to check (e.g., "China", "Russia")
            product: Optional product category
        
        Returns:
            Dict with export control information
        """
        query = f"{country} export controls restrictions"
        if product:
            query += f" {product}"
        
        return self.search_geopolitical_risks(query, region=country)
    
    @sleep_and_retry
    @limits(calls=100, period=60)
    def search_supply_chain_disruptions(
        self,
        component: Optional[str] = None,
        region: Optional[str] = None
    ) -> Dict:
        """
        Search for supply chain disruption news.
        
        Args:
            component: Component name (e.g., "memory chips", "cobalt")
            region: Optional region filter
        
        Returns:
            Dict with disruption information
        """
        query = "supply chain disruption shortage"
        if component:
            query += f" {component}"
        
        return self.search_geopolitical_risks(query, region=region)
    
    def _calculate_risk_score(self, results: List[Dict]) -> float:
        """
        Calculate risk score from search results.
        
        Args:
            results: List of search results
        
        Returns:
            Risk score between 0.0 and 1.0
        """
        if not results:
            return 0.0
        
        # Weight by relevance score and recency
        total_score = 0.0
        for result in results:
            score = result.get("score", 0.0)
            # Boost recent results
            total_score += score
        
        # Normalize to 0-1 range
        avg_score = total_score / len(results) if results else 0.0
        return min(avg_score, 1.0)


# Create singleton instance
def get_tavily_client() -> TavilyClientWrapper:
    """Get Tavily client instance."""
    return TavilyClientWrapper()



