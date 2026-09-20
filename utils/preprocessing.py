"""
Preprocessing Utilities
========================
Helper functions for input validation, feature scaling,
and data preprocessing for the AI Crop Planning Agent.
"""

import numpy as np

# Feature order expected by the ML model
ML_FEATURES = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]

# Validation ranges
VALIDATION_RANGES = {
    "N":           {"min": 0,   "max": 300,  "label": "Nitrogen (N)"},
    "P":           {"min": 0,   "max": 300,  "label": "Phosphorus (P)"},
    "K":           {"min": 0,   "max": 300,  "label": "Potassium (K)"},
    "temperature": {"min": -10, "max": 55,   "label": "Temperature (°C)"},
    "humidity":    {"min": 0,   "max": 100,  "label": "Humidity (%)"},
    "ph":          {"min": 0,   "max": 14,   "label": "Soil pH"},
    "rainfall":    {"min": 0,   "max": 5000, "label": "Rainfall (mm)"},
    "land_area":   {"min": 0.01,"max": 10000,"label": "Land Area (acres)"},
}


def validate_inputs(data: dict) -> tuple[bool, list[str]]:
    """
    Validate farmer input values.
    Returns (is_valid, list_of_error_messages).
    """
    errors = []

    numeric_fields = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall", "land_area"]
    
    for field in numeric_fields:
        value = data.get(field)
        if value is None or str(value).strip() == "":
            errors.append(f"{VALIDATION_RANGES[field]['label']} is required.")
            continue
        
        try:
            val = float(value)
        except (ValueError, TypeError):
            errors.append(f"{VALIDATION_RANGES[field]['label']} must be a valid number.")
            continue
        
        rng = VALIDATION_RANGES[field]
        if val < rng["min"] or val > rng["max"]:
            errors.append(
                f"{rng['label']} must be between {rng['min']} and {rng['max']}. "
                f"You entered: {val}"
            )

    # Validate season
    valid_seasons = ["Kharif", "Rabi", "Zaid"]
    season = data.get("season", "")
    if season not in valid_seasons:
        errors.append(f"Season must be one of: {', '.join(valid_seasons)}.")

    # Validate water availability
    valid_water = ["Low", "Medium", "High"]
    water = data.get("water_availability", "")
    if water not in valid_water:
        errors.append(f"Water availability must be one of: {', '.join(valid_water)}.")

    # Location is optional but must be a non-empty string if provided
    location = data.get("location", "")
    if location and len(str(location).strip()) > 200:
        errors.append("Location name is too long (max 200 characters).")

    return (len(errors) == 0), errors


def prepare_ml_features(data: dict) -> np.ndarray:
    """
    Extract and order the features required by the ML model.
    Returns a 2D numpy array ready for model.predict().
    """
    features = [float(data[f]) for f in ML_FEATURES]
    return np.array(features).reshape(1, -1)


def sanitize_string(value: str, max_len: int = 100) -> str:
    """Basic string sanitization."""
    if not isinstance(value, str):
        value = str(value)
    return value.strip()[:max_len]
