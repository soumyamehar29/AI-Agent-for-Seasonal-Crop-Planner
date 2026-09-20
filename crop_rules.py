"""
Crop Knowledge Base and Seasonal Rules
======================================
This module contains the knowledge base for crops including
seasonal suitability, water requirements, growing duration,
temperature preferences, and other agronomic characteristics.

NOTE: Values are approximate and based on general agricultural knowledge.
They should not be treated as exact scientific prescriptions.
"""

# =============================================================================
# SEASONAL KNOWLEDGE BASE
# Maps seasons to generally suitable crops (broad guidelines)
# =============================================================================

SEASONAL_CROPS = {
    "Kharif": {
        "description": "Monsoon season (June–October). Generally warm and wet.",
        "general_conditions": "High rainfall, warm temperatures, high humidity.",
        "crops": [
            "rice", "maize", "cotton", "pigeonpeas", "blackgram",
            "mungbean", "groundnuts", "sugarcane", "watermelon",
            "muskmelon", "papaya", "banana", "coconut"
        ]
    },
    "Rabi": {
        "description": "Winter season (October–March). Cool and dry.",
        "general_conditions": "Low to moderate rainfall, cooler temperatures.",
        "crops": [
            "wheat", "chickpea", "lentil", "mustard", "peas",
            "barley", "potato", "onion", "garlic", "apple", "grapes", "orange"
        ]
    },
    "Zaid": {
        "description": "Summer season (March–June). Hot and dry.",
        "general_conditions": "High temperatures, low rainfall, irrigation dependent.",
        "crops": [
            "watermelon", "muskmelon", "cucumber", "maize", "moong",
            "groundnuts", "sunflower", "mango", "papaya"
        ]
    }
}


# =============================================================================
# CROP KNOWLEDGE BASE
# =============================================================================

CROP_KNOWLEDGE = {
    "rice": {
        "suitable_seasons": ["Kharif"],
        "water_requirement": "High",
        "growing_duration_days": "90–150",
        "temperature_preference": "Warm (20–35°C)",
        "rainfall_preference": "High (1000–2000 mm)",
        "soil_ph_range": "5.0–7.0",
        "notes": "Requires flooded or well-irrigated fields. Staple crop of India.",
        "key_consideration": "High water demand; ensure adequate irrigation or monsoon rainfall."
    },
    "maize": {
        "suitable_seasons": ["Kharif", "Zaid"],
        "water_requirement": "Medium",
        "growing_duration_days": "60–90",
        "temperature_preference": "Warm (18–32°C)",
        "rainfall_preference": "Moderate (500–900 mm)",
        "soil_ph_range": "5.5–7.0",
        "notes": "Versatile crop grown in multiple seasons. Used for food and fodder.",
        "key_consideration": "Sensitive to waterlogging; ensure good drainage."
    },
    "wheat": {
        "suitable_seasons": ["Rabi"],
        "water_requirement": "Medium",
        "growing_duration_days": "100–150",
        "temperature_preference": "Cool (10–25°C)",
        "rainfall_preference": "Moderate (300–700 mm)",
        "soil_ph_range": "6.0–7.5",
        "notes": "Major cereal crop grown in winter season.",
        "key_consideration": "Frost-sensitive at flowering stage."
    },
    "chickpea": {
        "suitable_seasons": ["Rabi"],
        "water_requirement": "Low",
        "growing_duration_days": "90–120",
        "temperature_preference": "Cool to Warm (15–30°C)",
        "rainfall_preference": "Low to Moderate (200–600 mm)",
        "soil_ph_range": "6.0–8.0",
        "notes": "Drought-tolerant legume. Fixes atmospheric nitrogen.",
        "key_consideration": "Excess moisture can cause root diseases."
    },
    "cotton": {
        "suitable_seasons": ["Kharif"],
        "water_requirement": "Medium",
        "growing_duration_days": "150–180",
        "temperature_preference": "Warm (25–35°C)",
        "rainfall_preference": "Moderate (600–1200 mm)",
        "soil_ph_range": "5.8–8.0",
        "notes": "Major cash crop. Long growing season.",
        "key_consideration": "Requires warm temperatures throughout the season."
    },
    "lentil": {
        "suitable_seasons": ["Rabi"],
        "water_requirement": "Low",
        "growing_duration_days": "80–110",
        "temperature_preference": "Cool (15–25°C)",
        "rainfall_preference": "Low (200–400 mm)",
        "soil_ph_range": "6.0–8.0",
        "notes": "Drought-tolerant. Good source of protein.",
        "key_consideration": "Sensitive to waterlogging and high humidity."
    },
    "pigeonpeas": {
        "suitable_seasons": ["Kharif"],
        "water_requirement": "Low",
        "growing_duration_days": "120–200",
        "temperature_preference": "Warm (20–35°C)",
        "rainfall_preference": "Moderate (600–1000 mm)",
        "soil_ph_range": "5.5–7.0",
        "notes": "Drought-tolerant pulse crop. Long season.",
        "key_consideration": "Sensitive to waterlogging."
    },
    "blackgram": {
        "suitable_seasons": ["Kharif", "Rabi"],
        "water_requirement": "Low",
        "growing_duration_days": "60–90",
        "temperature_preference": "Warm (25–35°C)",
        "rainfall_preference": "Moderate (600–1000 mm)",
        "soil_ph_range": "6.0–7.5",
        "notes": "Short-duration pulse crop.",
        "key_consideration": "Avoid waterlogging conditions."
    },
    "mungbean": {
        "suitable_seasons": ["Kharif", "Zaid"],
        "water_requirement": "Low",
        "growing_duration_days": "60–90",
        "temperature_preference": "Warm (25–35°C)",
        "rainfall_preference": "Low to Moderate (400–700 mm)",
        "soil_ph_range": "6.0–7.5",
        "notes": "Short-duration warm-season pulse.",
        "key_consideration": "Cannot withstand frost or excessive waterlogging."
    },
    "banana": {
        "suitable_seasons": ["Kharif", "Zaid"],
        "water_requirement": "High",
        "growing_duration_days": "270–365",
        "temperature_preference": "Warm (20–35°C)",
        "rainfall_preference": "High (1000–2000 mm)",
        "soil_ph_range": "5.5–7.0",
        "notes": "Perennial fruit crop requiring warm, humid climate.",
        "key_consideration": "Sensitive to drought and cold."
    },
    "mango": {
        "suitable_seasons": ["Zaid"],
        "water_requirement": "Medium",
        "growing_duration_days": "90–120 (fruiting season)",
        "temperature_preference": "Warm (24–30°C)",
        "rainfall_preference": "Moderate (700–1200 mm)",
        "soil_ph_range": "5.5–7.5",
        "notes": "Long-lived fruit tree. Fruiting primarily in summer.",
        "key_consideration": "Requires dry period during flowering."
    },
    "apple": {
        "suitable_seasons": ["Rabi"],
        "water_requirement": "Medium",
        "growing_duration_days": "120–180 (fruiting season)",
        "temperature_preference": "Cool (10–20°C)",
        "rainfall_preference": "Moderate (700–1200 mm)",
        "soil_ph_range": "5.5–6.5",
        "notes": "Requires chilling hours for proper fruit development.",
        "key_consideration": "Not suitable for tropical and hot regions."
    },
    "grapes": {
        "suitable_seasons": ["Rabi", "Zaid"],
        "water_requirement": "Medium",
        "growing_duration_days": "120–150 (fruiting season)",
        "temperature_preference": "Warm to Hot (15–35°C)",
        "rainfall_preference": "Low to Moderate (500–900 mm)",
        "soil_ph_range": "6.0–7.5",
        "notes": "Prefers well-drained soils and dry conditions during ripening.",
        "key_consideration": "High humidity during ripening can cause fungal disease."
    },
    "watermelon": {
        "suitable_seasons": ["Kharif", "Zaid"],
        "water_requirement": "Medium",
        "growing_duration_days": "70–90",
        "temperature_preference": "Hot (25–40°C)",
        "rainfall_preference": "Moderate (400–700 mm)",
        "soil_ph_range": "6.0–7.0",
        "notes": "Grows best in sandy loam soils with full sun.",
        "key_consideration": "Requires warm nights for fruit development."
    },
    "muskmelon": {
        "suitable_seasons": ["Kharif", "Zaid"],
        "water_requirement": "Medium",
        "growing_duration_days": "75–95",
        "temperature_preference": "Hot (25–38°C)",
        "rainfall_preference": "Low to Moderate (400–700 mm)",
        "soil_ph_range": "6.0–7.0",
        "notes": "Similar growing conditions to watermelon.",
        "key_consideration": "Excess moisture at maturity reduces sweetness."
    },
    "orange": {
        "suitable_seasons": ["Rabi"],
        "water_requirement": "Medium",
        "growing_duration_days": "180–240 (fruiting period)",
        "temperature_preference": "Warm (15–30°C)",
        "rainfall_preference": "Moderate (750–1200 mm)",
        "soil_ph_range": "5.5–7.0",
        "notes": "Subtropical fruit requiring mild winters.",
        "key_consideration": "Frost can damage fruit and trees."
    },
    "papaya": {
        "suitable_seasons": ["Kharif", "Zaid"],
        "water_requirement": "Medium",
        "growing_duration_days": "270–360",
        "temperature_preference": "Warm (25–35°C)",
        "rainfall_preference": "Moderate (1000–1700 mm)",
        "soil_ph_range": "6.0–7.0",
        "notes": "Fast-growing tropical fruit. Cannot tolerate frost.",
        "key_consideration": "Susceptible to waterlogging and viral diseases."
    },
    "coconut": {
        "suitable_seasons": ["Kharif"],
        "water_requirement": "High",
        "growing_duration_days": "365+ (perennial tree)",
        "temperature_preference": "Warm (25–35°C)",
        "rainfall_preference": "High (1500–2500 mm)",
        "soil_ph_range": "5.0–8.0",
        "notes": "Coastal and tropical perennial tree crop.",
        "key_consideration": "Grows best in coastal, humid regions."
    },
    "coffee": {
        "suitable_seasons": ["Kharif"],
        "water_requirement": "High",
        "growing_duration_days": "365+ (perennial)",
        "temperature_preference": "Warm (15–28°C)",
        "rainfall_preference": "High (1500–2500 mm)",
        "soil_ph_range": "5.5–6.5",
        "notes": "Grown in hilly, tropical areas.",
        "key_consideration": "Requires shade and high humidity."
    },
    "jute": {
        "suitable_seasons": ["Kharif"],
        "water_requirement": "High",
        "growing_duration_days": "100–120",
        "temperature_preference": "Warm (25–35°C)",
        "rainfall_preference": "High (1500–2000 mm)",
        "soil_ph_range": "6.0–7.5",
        "notes": "Fibre crop requiring warm and humid conditions.",
        "key_consideration": "Requires warm nights and high humidity."
    },
    "kidneybeans": {
        "suitable_seasons": ["Kharif", "Rabi"],
        "water_requirement": "Medium",
        "growing_duration_days": "80–120",
        "temperature_preference": "Warm (18–30°C)",
        "rainfall_preference": "Moderate (500–800 mm)",
        "soil_ph_range": "6.0–7.0",
        "notes": "Versatile pulse crop.",
        "key_consideration": "Sensitive to frost and waterlogging."
    },
    "mothbeans": {
        "suitable_seasons": ["Kharif", "Zaid"],
        "water_requirement": "Low",
        "growing_duration_days": "70–90",
        "temperature_preference": "Warm to Hot (25–40°C)",
        "rainfall_preference": "Low (200–400 mm)",
        "soil_ph_range": "6.0–8.0",
        "notes": "Highly drought-tolerant pulse.",
        "key_consideration": "Best suited for arid and semi-arid regions."
    },
    "pomegranate": {
        "suitable_seasons": ["Rabi", "Zaid"],
        "water_requirement": "Low",
        "growing_duration_days": "180–210 (fruiting period)",
        "temperature_preference": "Warm to Hot (20–38°C)",
        "rainfall_preference": "Low to Moderate (500–800 mm)",
        "soil_ph_range": "5.5–7.5",
        "notes": "Drought-tolerant fruit crop.",
        "key_consideration": "Excess rain during fruiting causes splitting."
    },
}

# Default entry for crops not in the knowledge base
DEFAULT_CROP_INFO = {
    "suitable_seasons": ["Kharif", "Rabi", "Zaid"],
    "water_requirement": "Medium",
    "growing_duration_days": "90–150",
    "temperature_preference": "Warm (20–35°C)",
    "rainfall_preference": "Moderate (500–1000 mm)",
    "soil_ph_range": "6.0–7.5",
    "notes": "Detailed information not available for this crop.",
    "key_consideration": "Consult local agricultural extension for specific guidance."
}

# =============================================================================
# WATER REQUIREMENT CATEGORIES
# =============================================================================

WATER_CATEGORIES = {
    "Low": {
        "description": "Generally < 500 mm/season",
        "compatible_availability": ["Low", "Medium", "High"]
    },
    "Medium": {
        "description": "Generally 500–1000 mm/season",
        "compatible_availability": ["Medium", "High"]
    },
    "High": {
        "description": "Generally > 1000 mm/season",
        "compatible_availability": ["High"]
    }
}

# =============================================================================
# ENVIRONMENTAL THRESHOLDS (broad reference ranges)
# =============================================================================

ENV_THRESHOLDS = {
    "temperature": {
        "low": 15,
        "optimal_low": 20,
        "optimal_high": 35,
        "high": 40
    },
    "humidity": {
        "low": 40,
        "optimal_low": 50,
        "optimal_high": 85,
        "high": 95
    },
    "rainfall": {
        "very_low": 200,
        "low": 500,
        "moderate": 1000,
        "high": 1500,
        "very_high": 2000
    },
    "ph": {
        "very_acidic": 4.5,
        "acidic": 5.5,
        "neutral_low": 6.0,
        "neutral_high": 7.5,
        "alkaline": 8.5
    },
    "nitrogen": {
        "low": 40,
        "medium": 80,
        "high": 120
    },
    "phosphorus": {
        "low": 20,
        "medium": 50,
        "high": 100
    },
    "potassium": {
        "low": 20,
        "medium": 50,
        "high": 100
    }
}


def get_crop_info(crop_name: str) -> dict:
    """
    Return knowledge base entry for a crop.
    Falls back to DEFAULT_CROP_INFO if the crop is not found.
    """
    crop_lower = crop_name.lower().strip()
    if crop_lower in CROP_KNOWLEDGE:
        info = CROP_KNOWLEDGE[crop_lower].copy()
        info["crop"] = crop_lower
        info["found_in_kb"] = True
        return info
    else:
        info = DEFAULT_CROP_INFO.copy()
        info["crop"] = crop_lower
        info["found_in_kb"] = False
        return info


def get_season_info(season: str) -> dict:
    """Return knowledge base entry for a season."""
    return SEASONAL_CROPS.get(season, {
        "description": "Season information not available.",
        "general_conditions": "N/A",
        "crops": []
    })


def check_seasonal_suitability(crop_name: str, season: str) -> dict:
    """
    Check if a crop is generally suitable for the selected season.
    Returns a suitability flag and description.
    """
    crop_info = get_crop_info(crop_name)
    suitable_seasons = crop_info.get("suitable_seasons", [])
    
    if season in suitable_seasons:
        return {
            "suitable": True,
            "score": 1.0,
            "description": f"{crop_name.capitalize()} is generally suitable for the {season} season."
        }
    else:
        return {
            "suitable": False,
            "score": 0.3,
            "description": (
                f"{crop_name.capitalize()} is typically grown in "
                f"{', '.join(suitable_seasons) if suitable_seasons else 'other seasons'}, "
                f"not primarily in {season}. Growing outside its typical season may affect yield."
            )
        }


def check_water_compatibility(crop_name: str, water_availability: str) -> dict:
    """
    Check if the crop's water requirement is compatible with the
    farmer's water availability.
    Returns a compatibility flag and warning if needed.
    """
    crop_info = get_crop_info(crop_name)
    crop_water_req = crop_info.get("water_requirement", "Medium")
    
    compatible_avail = WATER_CATEGORIES.get(crop_water_req, {}).get(
        "compatible_availability", ["Medium", "High"]
    )
    
    if water_availability in compatible_avail:
        if crop_water_req == "High" and water_availability == "High":
            description = (
                f"{crop_name.capitalize()} has high water requirements and your "
                f"water availability is high — this is compatible."
            )
        elif crop_water_req == "Low":
            description = (
                f"{crop_name.capitalize()} has low water requirements and is "
                f"compatible with {water_availability.lower()} water availability."
            )
        else:
            description = (
                f"{crop_name.capitalize()} water requirements are compatible with "
                f"your {water_availability.lower()} water availability."
            )
        return {
            "compatible": True,
            "score": 1.0,
            "warning": False,
            "description": description
        }
    else:
        # Warn if crop needs more water than available
        water_levels = ["Low", "Medium", "High"]
        req_idx = water_levels.index(crop_water_req)
        avail_idx = water_levels.index(water_availability)
        
        if req_idx > avail_idx:
            description = (
                f"⚠ {crop_name.capitalize()} has {crop_water_req.lower()} water requirements, "
                f"but your water availability is {water_availability.lower()}. "
                f"Consider supplemental irrigation or choose a crop with lower water demand."
            )
        else:
            description = (
                f"{crop_name.capitalize()} has {crop_water_req.lower()} water requirements. "
                f"Your water availability ({water_availability.lower()}) is sufficient."
            )
        
        return {
            "compatible": False,
            "score": 0.3,
            "warning": req_idx > avail_idx,
            "description": description
        }
