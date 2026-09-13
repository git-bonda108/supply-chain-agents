"""
Logistics Optimization Tools for Logistics Optimization Agent
"""

from typing import Dict, List, Optional
from tools.data_loader import get_data_loader
from tools.calculators.risk_calculator import assess_geopolitical_risk
import logging

logger = logging.getLogger(__name__)


def optimize_route(
    origin: str,
    destination: str,
    product_category: Optional[str] = None,
    exclude_countries: Optional[List[str]] = None
) -> Dict:
    """
    Optimize transportation route considering geopolitical risks.
    
    Args:
        origin: Origin country/region
        destination: Destination country/region
        product_category: Optional product category
        exclude_countries: Countries to avoid
    
    Returns:
        Dict with route recommendations
    """
    try:
        # Assess risks for origin and destination
        origin_risk = assess_geopolitical_risk(origin, product_category)
        dest_risk = assess_geopolitical_risk(destination, product_category)
        
        # Calculate route risk
        route_risk = (origin_risk.get("risk_score", 0.5) + dest_risk.get("risk_score", 0.5)) / 2
        
        # Mock route options (in real scenario, would use routing API)
        routes = [
            {
                "route_id": "R001",
                "path": f"{origin} → {destination}",
                "transit_time_days": 15,
                "cost": 50000,
                "risk_level": "HIGH" if route_risk > 0.5 else "MEDIUM" if route_risk > 0.3 else "LOW",
                "risk_score": round(route_risk, 3)
            },
            {
                "route_id": "R002",
                "path": f"{origin} → Alternative → {destination}",
                "transit_time_days": 18,
                "cost": 55000,
                "risk_level": "MEDIUM",
                "risk_score": round(route_risk * 0.7, 3)
            }
        ]
        
        # Filter out excluded countries
        if exclude_countries:
            routes = [r for r in routes if not any(country in r["path"] for country in exclude_countries)]
        
        # Sort by risk and cost
        routes.sort(key=lambda x: (x["risk_score"], x["cost"]))
        
        return {
            "origin": origin,
            "destination": destination,
            "product_category": product_category,
            "recommended_route": routes[0] if routes else None,
            "alternative_routes": routes[1:3] if len(routes) > 1 else [],
            "risk_assessment": {
                "origin_risk": origin_risk.get("risk_level", "UNKNOWN"),
                "destination_risk": dest_risk.get("risk_level", "UNKNOWN"),
                "overall_route_risk": "HIGH" if route_risk > 0.5 else "MEDIUM" if route_risk > 0.3 else "LOW"
            },
            "recommendations": _get_route_recommendations(routes[0] if routes else None)
        }
        
    except Exception as e:
        logger.error(f"Route optimization error: {e}")
        return {
            "origin": origin,
            "destination": destination,
            "error": str(e)
        }


def compare_transportation_modes(
    origin: str,
    destination: str,
    product_category: Optional[str] = None
) -> Dict:
    """
    Compare different transportation modes.
    
    Args:
        origin: Origin location
        destination: Destination location
        product_category: Optional product category
    
    Returns:
        Dict with mode comparison
    """
    try:
        modes = [
            {
                "mode": "Air Freight",
                "transit_time_days": 3,
                "cost": 100000,
                "reliability": 0.95,
                "risk_level": "LOW"
            },
            {
                "mode": "Sea Freight",
                "transit_time_days": 25,
                "cost": 30000,
                "reliability": 0.85,
                "risk_level": "MEDIUM"
            },
            {
                "mode": "Rail",
                "transit_time_days": 12,
                "cost": 40000,
                "reliability": 0.90,
                "risk_level": "LOW"
            }
        ]
        
        # Assess risk for route
        route_risk = assess_geopolitical_risk(origin, product_category)
        risk_level = route_risk.get("risk_level", "MEDIUM")
        
        # Adjust modes based on risk
        for mode in modes:
            if risk_level == "HIGH":
                mode["risk_level"] = "HIGH"
                mode["reliability"] *= 0.9
            elif risk_level == "CRITICAL":
                mode["risk_level"] = "CRITICAL"
                mode["reliability"] *= 0.8
        
        # Sort by cost-effectiveness
        modes.sort(key=lambda x: x["cost"] / x["reliability"])
        
        return {
            "origin": origin,
            "destination": destination,
            "product_category": product_category,
            "modes": modes,
            "recommended_mode": modes[0],
            "comparison": {
                "fastest": min(modes, key=lambda x: x["transit_time_days"]),
                "cheapest": min(modes, key=lambda x: x["cost"]),
                "most_reliable": max(modes, key=lambda x: x["reliability"])
            }
        }
        
    except Exception as e:
        logger.error(f"Transportation mode comparison error: {e}")
        return {
            "origin": origin,
            "destination": destination,
            "error": str(e)
        }


def _get_route_recommendations(route: Optional[Dict]) -> List[str]:
    """Get recommendations based on route."""
    if not route:
        return ["Unable to determine optimal route"]
    
    recommendations = []
    
    if route["risk_level"] == "HIGH" or route["risk_level"] == "CRITICAL":
        recommendations.append("Consider alternative routes due to high risk")
        recommendations.append("Increase insurance coverage")
        recommendations.append("Monitor route status closely")
    elif route["risk_level"] == "MEDIUM":
        recommendations.append("Route acceptable but monitor for changes")
        recommendations.append("Have backup route ready")
    else:
        recommendations.append("Route is low risk, proceed as planned")
    
    return recommendations



