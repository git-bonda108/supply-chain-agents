"""
Report Generation Tools for Executive Reporting Agent
"""

from typing import Dict, List, Any
from datetime import datetime
import json


def aggregate_insights(agent_outputs: List[Dict]) -> Dict:
    """
    Aggregate insights from multiple agent outputs.
    
    Args:
        agent_outputs: List of agent output dictionaries
    
    Returns:
        Dict with aggregated insights
    """
    aggregated = {
        "timestamp": datetime.now().isoformat(),
        "summary": {},
        "key_findings": [],
        "recommendations": [],
        "risk_assessment": {},
        "metrics": {}
    }
    
    # Extract key information from each agent output
    for output in agent_outputs:
        agent_name = output.get("agent", "Unknown")
        data = output.get("data", {})
        
        # Risk information
        if "risk_score" in data or "risk_level" in data:
            aggregated["risk_assessment"][agent_name] = {
                "risk_score": data.get("risk_score"),
                "risk_level": data.get("risk_level")
            }
        
        # Recommendations
        if "recommendations" in data:
            if isinstance(data["recommendations"], list):
                aggregated["recommendations"].extend(data["recommendations"])
            else:
                aggregated["recommendations"].append(data["recommendations"])
        
        # Key findings
        if "summary" in data:
            aggregated["key_findings"].append(f"{agent_name}: {data['summary']}")
    
    # Create executive summary
    aggregated["summary"] = _create_executive_summary(aggregated)
    
    return aggregated


def generate_executive_report(
    insights: Dict,
    format: str = "text"
) -> str:
    """
    Generate executive report from aggregated insights.
    
    Args:
        insights: Aggregated insights dictionary
        format: Output format ("text" or "json")
    
    Returns:
        Formatted report string
    """
    if format == "json":
        return json.dumps(insights, indent=2)
    
    # Text format
    report = []
    report.append("=" * 60)
    report.append("EXECUTIVE SUPPLY CHAIN REPORT")
    report.append("=" * 60)
    report.append(f"Generated: {insights.get('timestamp', 'Unknown')}")
    report.append("")
    
    # Executive Summary
    report.append("EXECUTIVE SUMMARY")
    report.append("-" * 60)
    summary = insights.get("summary", {})
    if isinstance(summary, dict):
        for key, value in summary.items():
            report.append(f"{key}: {value}")
    else:
        report.append(str(summary))
    report.append("")
    
    # Key Findings
    report.append("KEY FINDINGS")
    report.append("-" * 60)
    for finding in insights.get("key_findings", []):
        report.append(f"• {finding}")
    report.append("")
    
    # Risk Assessment
    if insights.get("risk_assessment"):
        report.append("RISK ASSESSMENT")
        report.append("-" * 60)
        for agent, risk in insights["risk_assessment"].items():
            report.append(f"{agent}:")
            report.append(f"  Risk Level: {risk.get('risk_level', 'Unknown')}")
            report.append(f"  Risk Score: {risk.get('risk_score', 'Unknown')}")
        report.append("")
    
    # Recommendations
    report.append("RECOMMENDATIONS")
    report.append("-" * 60)
    recommendations = insights.get("recommendations", [])
    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            report.append(f"{i}. {rec}")
    else:
        report.append("No specific recommendations at this time.")
    report.append("")
    
    report.append("=" * 60)
    
    return "\n".join(report)


def _create_executive_summary(aggregated: Dict) -> Dict:
    """Create executive summary from aggregated data."""
    summary = {
        "overall_status": "ASSESSING",
        "critical_risks": 0,
        "high_priority_actions": 0,
        "key_concerns": []
    }
    
    # Count critical risks
    for agent, risk in aggregated.get("risk_assessment", {}).items():
        risk_level = risk.get("risk_level", "")
        if risk_level in ["CRITICAL", "HIGH"]:
            summary["critical_risks"] += 1
            summary["key_concerns"].append(f"{agent}: {risk_level} risk")
    
    # Count high priority recommendations
    recommendations = aggregated.get("recommendations", [])
    summary["high_priority_actions"] = len([r for r in recommendations if any(word in r.upper() for word in ["IMMEDIATE", "URGENT", "CRITICAL"])])
    
    # Determine overall status
    if summary["critical_risks"] > 0:
        summary["overall_status"] = "ATTENTION_REQUIRED"
    elif summary["high_priority_actions"] > 0:
        summary["overall_status"] = "ACTION_REQUIRED"
    else:
        summary["overall_status"] = "NORMAL"
    
    return summary



