"""
Supplier Evaluation Tools for Supplier Assessment Agent
"""

from typing import Dict, List, Optional
from tools.data_loader import get_data_loader
from tools.calculators.risk_calculator import assess_geopolitical_risk
import pandas as pd
import logging

logger = logging.getLogger(__name__)


def evaluate_supplier(
    supplier_id: str,
    include_risk_assessment: bool = True
) -> Dict:
    """
    Evaluate a supplier's reliability and risk factors.
    
    Args:
        supplier_id: Supplier ID to evaluate
        include_risk_assessment: Whether to include real-time risk assessment
    
    Returns:
        Dict with supplier evaluation
    """
    try:
        data_loader = get_data_loader()
        suppliers = data_loader.load_supplier_data(supplier_id)
        
        if len(suppliers) == 0:
            return {
                "supplier_id": supplier_id,
                "error": "Supplier not found"
            }
        
        supplier = suppliers.iloc[0]
        
        # Calculate overall reliability score
        reliability_score = (
            supplier["reliability_score"] * 0.3 +
            supplier["on_time_delivery"] * 0.3 +
            supplier["quality_score"] * 0.2 +
            supplier["cost_score"] * 0.2
        )
        
        # Get real-time risk assessment if requested
        risk_assessment = None
        if include_risk_assessment:
            try:
                risk_assessment = assess_geopolitical_risk(
                    supplier["country"],
                    supplier["product_category"]
                )
            except Exception as e:
                logger.warning(f"Could not get real-time risk: {e}")
        
        # Determine overall rating
        if reliability_score >= 0.8:
            rating = "EXCELLENT"
        elif reliability_score >= 0.7:
            rating = "GOOD"
        elif reliability_score >= 0.6:
            rating = "FAIR"
        else:
            rating = "POOR"
        
        result = {
            "supplier_id": supplier_id,
            "supplier_name": supplier["supplier_name"],
            "country": supplier["country"],
            "region": supplier["region"],
            "product_category": supplier["product_category"],
            "reliability_score": round(reliability_score, 3),
            "rating": rating,
            "metrics": {
                "reliability": round(supplier["reliability_score"], 3),
                "on_time_delivery": round(supplier["on_time_delivery"], 3),
                "quality": round(supplier["quality_score"], 3),
                "cost": round(supplier["cost_score"], 3)
            },
            "geopolitical_risk": round(supplier["geopolitical_risk"], 3),
            "export_control_status": supplier["export_control_status"]
        }
        
        if risk_assessment:
            result["real_time_risk"] = risk_assessment
        
        return result
        
    except Exception as e:
        logger.error(f"Supplier evaluation error: {e}")
        return {
            "supplier_id": supplier_id,
            "error": str(e)
        }


def find_alternatives(
    current_supplier_id: str,
    product_category: Optional[str] = None,
    exclude_countries: Optional[List[str]] = None,
    min_reliability: float = 0.7
) -> Dict:
    """
    Find alternative suppliers for a given supplier.
    
    Args:
        current_supplier_id: Current supplier ID
        product_category: Optional product category filter
        exclude_countries: Countries to exclude
        min_reliability: Minimum reliability score
    
    Returns:
        Dict with alternative suppliers
    """
    try:
        data_loader = get_data_loader()
        
        # Get current supplier info
        current_supplier = data_loader.load_supplier_data(current_supplier_id)
        if len(current_supplier) == 0:
            return {
                "current_supplier_id": current_supplier_id,
                "error": "Current supplier not found"
            }
        
        current = current_supplier.iloc[0]
        product = product_category or current["product_category"]
        
        # Get all suppliers for same product
        all_suppliers = data_loader.get_supplier_by_product(product)
        
        # Filter out current supplier
        alternatives = all_suppliers[all_suppliers["supplier_id"] != current_supplier_id]
        
        # Filter by reliability
        alternatives = alternatives[alternatives["reliability_score"] >= min_reliability]
        
        # Filter out excluded countries
        if exclude_countries:
            alternatives = alternatives[~alternatives["country"].isin(exclude_countries)]
        
        # Calculate match score (similarity to current supplier)
        alternatives["match_score"] = (
            1 - abs(alternatives["reliability_score"] - current["reliability_score"]) * 0.4 +
            alternatives["on_time_delivery"] * 0.3 +
            alternatives["quality_score"] * 0.3
        )
        
        # Sort by match score
        alternatives = alternatives.sort_values("match_score", ascending=False)
        
        # Format results
        alternative_list = []
        for _, alt in alternatives.head(10).iterrows():
            alternative_list.append({
                "supplier_id": alt["supplier_id"],
                "supplier_name": alt["supplier_name"],
                "country": alt["country"],
                "reliability_score": round(alt["reliability_score"], 3),
                "match_score": round(alt["match_score"], 3),
                "geopolitical_risk": round(alt["geopolitical_risk"], 3),
                "export_control_status": alt["export_control_status"]
            })
        
        return {
            "current_supplier": {
                "supplier_id": current["supplier_id"],
                "supplier_name": current["supplier_name"],
                "country": current["country"]
            },
            "product_category": product,
            "alternatives": alternative_list,
            "total_alternatives": len(alternative_list),
            "recommendations": _get_alternative_recommendations(alternative_list)
        }
        
    except Exception as e:
        logger.error(f"Find alternatives error: {e}")
        return {
            "current_supplier_id": current_supplier_id,
            "error": str(e)
        }


def _get_alternative_recommendations(alternatives: List[Dict]) -> List[str]:
    """Get recommendations based on alternatives."""
    if not alternatives:
        return ["No suitable alternatives found. Consider expanding supplier network."]
    
    recommendations = []
    
    # Check for low-risk alternatives
    low_risk = [a for a in alternatives if a["geopolitical_risk"] < 0.3]
    if low_risk:
        recommendations.append(f"Found {len(low_risk)} low-risk alternatives. Consider diversifying to reduce geopolitical exposure.")
    
    # Check for high-reliability alternatives
    high_reliability = [a for a in alternatives if a["reliability_score"] >= 0.8]
    if high_reliability:
        recommendations.append(f"Found {len(high_reliability)} high-reliability alternatives (score >= 0.8).")
    
    # Geographic diversity
    countries = set(a["country"] for a in alternatives)
    if len(countries) > 1:
        recommendations.append(f"Alternatives available in {len(countries)} different countries for geographic diversification.")
    
    if not recommendations:
        recommendations.append("Review alternatives and select based on your risk tolerance and requirements.")
    
    return recommendations



