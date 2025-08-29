"""
AidenAI Tool Cards - Dynamic skill discovery and capability mapping
"""
from __future__ import annotations
import os
import yaml
from typing import List, Dict, Any, Optional
from pathlib import Path

TOOLCARDS_PATH = Path(__file__).parent / "toolcards.yaml"

def load_toolcards() -> Dict[str, Any]:
    """Load tool cards configuration from YAML"""
    try:
        with open(TOOLCARDS_PATH, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Warning: Could not load toolcards.yaml: {e}")
        return {"skills": [], "categories": {}, "risk_levels": {}}

def pick_relevant_cards(query: str, k: int = 6) -> List[str]:
    """Pick relevant skill cards based on query analysis"""
    config = load_toolcards()
    skills = config.get("skills", [])
    
    query_lower = query.lower()
    scored_skills = []
    
    # Score skills based on query relevance
    for skill in skills:
        score = 0
        name = skill.get("name", "")
        title = skill.get("title", "")
        description = skill.get("description", "")
        capabilities = skill.get("capabilities", [])
        category = skill.get("category", "")
        
        # Direct name match
        if name in query_lower:
            score += 10
            
        # Title keyword match  
        for word in title.lower().split():
            if word in query_lower:
                score += 5
                
        # Description keyword match
        for word in description.lower().split():
            if word in query_lower:
                score += 2
                
        # Capability match
        for cap in capabilities:
            if cap.replace("_", " ") in query_lower:
                score += 3
                
        # Category match
        if category in query_lower:
            score += 4
            
        # Specific query patterns
        patterns = {
            "website": ["web_site_builder", "browser", "web_fetch"],
            "deploy": ["cloud_run_deploy", "gcs_upload"],
            "mobile": ["mobile_expo_scaffold", "mobile_expo_build_ios"],
            "data": ["bigquery_query"], 
            "image": ["image_watermark"],
            "browser": ["browser"],
            "bigquery": ["bigquery_query"],
            "storage": ["gcs_upload"],
            "cloud": ["bigquery_query", "gcs_upload", "cloud_run_deploy"]
        }
        
        for pattern, skill_names in patterns.items():
            if pattern in query_lower and name in skill_names:
                score += 8
                
        if score > 0:
            scored_skills.append((name, score))
    
    # Sort by score and return top k
    scored_skills.sort(key=lambda x: x[1], reverse=True)
    return [skill[0] for skill in scored_skills[:k]]

def get_skill_info(skill_name: str) -> Optional[Dict[str, Any]]:
    """Get detailed information about a specific skill"""
    config = load_toolcards()
    skills = config.get("skills", [])
    
    for skill in skills:
        if skill.get("name") == skill_name:
            return skill
    return None

def get_skills_by_category(category: str) -> List[Dict[str, Any]]:
    """Get all skills in a specific category"""
    config = load_toolcards()
    skills = config.get("skills", [])
    
    return [skill for skill in skills if skill.get("category") == category]

def get_high_risk_skills() -> List[str]:
    """Get list of high-risk skills that require PIN authorization"""
    config = load_toolcards()
    skills = config.get("skills", [])
    
    high_risk = []
    for skill in skills:
        if skill.get("risk_level") == "high" or skill.get("requires_pin", False):
            high_risk.append(skill.get("name"))
    
    return high_risk

def build_capability_summary() -> Dict[str, Any]:
    """Build a summary of all available capabilities"""
    config = load_toolcards()
    skills = config.get("skills", [])
    categories = config.get("categories", {})
    
    summary = {
        "total_skills": len(skills),
        "categories": {},
        "risk_distribution": {"low": 0, "medium": 0, "high": 0},
        "pin_required_count": 0
    }
    
    # Count by category and risk level
    for skill in skills:
        category = skill.get("category", "uncategorized")
        risk_level = skill.get("risk_level", "low")
        requires_pin = skill.get("requires_pin", False)
        
        # Category stats
        if category not in summary["categories"]:
            summary["categories"][category] = {
                "count": 0,
                "icon": categories.get(category, {}).get("icon", "❓"),
                "description": categories.get(category, {}).get("description", "")
            }
        summary["categories"][category]["count"] += 1
        
        # Risk level stats
        if risk_level in summary["risk_distribution"]:
            summary["risk_distribution"][risk_level] += 1
            
        # PIN requirement stats
        if requires_pin:
            summary["pin_required_count"] += 1
    
    return summary