from typing import Dict

def calculate_project_cost(project_type: str, include_domain: bool = False, include_database: bool = False) -> float:
    """
    Calculate the total cost for a project based on requirements
    
    Args:
        project_type: "basic" or "standard"
        include_domain: Whether to include domain setup
        include_database: Whether to include database setup
    
    Returns:
        Total estimated cost
    """
    # Base pricing
    base_prices = {
        "basic": 49.99,      # Up to 3 pages
        "standard": 69.99    # 3+ pages
    }
    
    # Add-on pricing
    domain_cost = 19.99      # Domain registration and setup
    database_cost = 29.99    # Database setup and integration
    
    # Calculate total cost
    total_cost = base_prices.get(project_type, base_prices["basic"])
    
    if include_domain:
        total_cost += domain_cost
    
    if include_database:
        total_cost += database_cost
    
    return round(total_cost, 2)

def validate_project_type(project_type: str) -> bool:
    """Validate if project type is supported"""
    return project_type in ["basic", "standard"]

def get_project_features(project_type: str) -> Dict[str, list]:
    """Get features included in each project type"""
    features = {
        "basic": [
            "Up to 3 pages",
            "Responsive design",
            "Basic contact form",
            "SEO optimization",
            "Mobile-friendly",
            "2-week delivery",
            "Basic support"
        ],
        "standard": [
            "3+ pages (unlimited)",
            "Advanced responsive design",
            "Multiple contact forms",
            "Advanced SEO optimization",
            "Performance optimization",
            "Social media integration",
            "2-week delivery",
            "Priority support"
        ]
    }
    
    return features.get(project_type, features["basic"])

def get_addon_features() -> Dict[str, Dict]:
    """Get add-on features and pricing"""
    return {
        "domain": {
            "name": "Domain Setup",
            "price": 19.99,
            "features": [
                "Domain registration",
                "DNS configuration",
                "SSL certificate setup",
                "Email forwarding setup"
            ]
        },
        "database": {
            "name": "Database Setup",
            "price": 29.99,
            "features": [
                "User registration system",
                "Email & name storage",
                "Basic user profiles",
                "Data backup included"
            ]
        }
    }

def generate_project_summary(project_type: str, include_domain: bool, include_database: bool) -> Dict:
    """Generate a comprehensive project summary"""
    base_features = get_project_features(project_type)
    addon_features = get_addon_features()
    total_cost = calculate_project_cost(project_type, include_domain, include_database)
    
    summary = {
        "project_type": project_type.title(),
        "base_cost": 49.99 if project_type == "basic" else 69.99,
        "total_cost": total_cost,
        "features": base_features.copy(),
        "addons": [],
        "estimated_timeline": "14 days",
        "support_level": "Basic" if project_type == "basic" else "Priority"
    }
    
    if include_domain:
        summary["addons"].append({
            "name": addon_features["domain"]["name"],
            "cost": addon_features["domain"]["price"],
            "features": addon_features["domain"]["features"]
        })
        summary["features"].extend([f"✓ {feature}" for feature in addon_features["domain"]["features"]])
    
    if include_database:
        summary["addons"].append({
            "name": addon_features["database"]["name"],
            "cost": addon_features["database"]["price"],
            "features": addon_features["database"]["features"]
        })
        summary["features"].extend([f"✓ {feature}" for feature in addon_features["database"]["features"]])
    
    return summary