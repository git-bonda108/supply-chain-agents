"""
Risk Calculation Tools for Risk Intelligence Agent
"""

from typing import Dict, Optional, List
from tools.data_sources import get_tavily_client, get_news_api_client, get_cache_manager
from tools.data_loader import get_data_loader
import logging

logger = logging.getLogger(__name__)


def calculate_risk_score(
    geopolitical_risk: float,
    supplier_reliability: float,
    market_volatility: float,
    export_control_status: str
) -> Dict:
    """
    Calculate overall supply chain risk score.
    
    Args:
        geopolitical_risk: Risk score 0-1
        supplier_reliability: Reliability score 0-1
        market_volatility: Volatility score 0-1
        export_control_status: "RESTRICTED" or "ALLOWED"
    
    Returns:
        Dict with risk_score, risk_level, and breakdown
    """
    # Weighted calculation
    base_score = (
        geopolitical_risk * 0.3 +
        (1 - supplier_reliability) * 0.3 +
        market_volatility * 0.2
    )
    
    # Adjust for export controls
    if export_control_status == "RESTRICTED":
        base_score += 0.2
    
    risk_score = min(base_score, 1.0)
    
    # Determine risk level
    if risk_score >= 0.7:
        risk_level = "CRITICAL"
    elif risk_score >= 0.5:
        risk_level = "HIGH"
    elif risk_score >= 0.3:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"
    
    return {
        "risk_score": round(risk_score, 3),
        "risk_level": risk_level,
        "breakdown": {
            "geopolitical": round(geopolitical_risk, 3),
            "supplier": round(1 - supplier_reliability, 3),
            "market": round(market_volatility, 3),
            "export_controls": export_control_status
        },
        "recommendations": _get_risk_recommendations(risk_level)
    }


def assess_geopolitical_risk(
    country: str,
    product: Optional[str] = None,
    use_cache: bool = True
) -> Dict:
    """
    Assess geopolitical risk for a country/product combination.
    Uses real-time Tavily API for latest information.
    
    Args:
        country: Country to assess
        product: Optional product category
        use_cache: Whether to use cached data
    
    Returns:
        Dict with risk assessment
    """
    cache = get_cache_manager()
    cache_key = f"geopolitical_risk:{country}:{product or 'all'}"
    
    # Check cache first
    if use_cache:
        cached_result = cache.get(cache_key)
        if cached_result:
            logger.info(f"Using cached geopolitical risk for {country}")
            return cached_result
    
    try:
        tavily = get_tavily_client()
        
        # Search for export controls
        export_control_query = f"{country} export controls"
        if product:
            export_control_query += f" {product}"
        
        export_results = tavily.search_export_controls(country, product)
        
        # Search for general geopolitical risks
        risk_query = f"{country} supply chain risk geopolitical"
        risk_results = tavily.search_geopolitical_risks(risk_query, region=country)
        
        # Calculate risk score from results
        risk_score = max(
            export_results.get("risk_score", 0.0),
            risk_results.get("risk_score", 0.0)
        )
        
        # Determine export control status
        export_control_status = "RESTRICTED" if risk_score > 0.5 else "ALLOWED"
        
        result = {
            "country": country,
            "product": product,
            "risk_score": round(risk_score, 3),
            "risk_level": "HIGH" if risk_score > 0.5 else "MEDIUM" if risk_score > 0.3 else "LOW",
            "export_control_status": export_control_status,
            "recent_events": export_results.get("results", [])[:5],
            "news_articles": risk_results.get("results", [])[:5],
            "timestamp": export_results.get("timestamp")
        }
        
        # Cache result
        cache.set(cache_key, result, ttl_seconds=3600)
        
        return result
        
    except Exception as e:
        logger.error(f"Error assessing geopolitical risk: {e}")
        # Fallback to supplier data
        data_loader = get_data_loader()
        suppliers = data_loader.get_supplier_by_country(country)
        
        if len(suppliers) > 0:
            avg_risk = suppliers["geopolitical_risk"].mean()
            return {
                "country": country,
                "product": product,
                "risk_score": round(avg_risk, 3),
                "risk_level": "HIGH" if avg_risk > 0.5 else "MEDIUM" if avg_risk > 0.3 else "LOW",
                "export_control_status": "RESTRICTED" if avg_risk > 0.5 else "ALLOWED",
                "source": "fallback_data",
                "warning": "Using fallback data due to API error"
            }
        
        return {
            "country": country,
            "product": product,
            "risk_score": 0.5,
            "risk_level": "MEDIUM",
            "export_control_status": "UNKNOWN",
            "error": str(e)
        }


def _get_risk_recommendations(risk_level: str) -> List[str]:
    """Get recommendations based on risk level."""
    recommendations = {
        "CRITICAL": [
            "Immediate supplier diversification required",
            "Increase safety stock levels",
            "Identify alternative suppliers",
            "Monitor situation daily"
        ],
        "HIGH": [
            "Consider supplier diversification",
            "Increase inventory buffer",
            "Monitor export control updates",
            "Develop contingency plans"
        ],
        "MEDIUM": [
            "Monitor situation regularly",
            "Maintain current inventory levels",
            "Keep alternative suppliers on standby"
        ],
        "LOW": [
            "Continue monitoring",
            "Maintain standard operations"
        ]
    }
    return recommendations.get(risk_level, [])



