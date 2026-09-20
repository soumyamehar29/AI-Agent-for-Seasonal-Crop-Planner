"""
agent.py
========
AI Crop Planning Agent

This module implements the multi-module decision-support agent that:
  - Module 1: Uses the trained Random Forest ML model
  - Module 2: Applies seasonal suitability analysis
  - Module 3: Performs environmental condition analysis
  - Module 4: Checks water requirement compatibility
  - Module 5: Combines all modules into a ranked decision
  - Module 6: Generates a plain-language advisory

NOTE: This system is an AI-assisted decision-support tool.
      It is NOT a scientifically validated agricultural prescription system.
      Results should be verified with local agricultural experts.
"""

import os
import sys
import json
import urllib.request
import urllib.error
import numpy as np
import joblib

from crop_rules import (
    get_crop_info,
    get_season_info,
    check_seasonal_suitability,
    check_water_compatibility,
    ENV_THRESHOLDS,
    WATER_CATEGORIES,
)
from utils.location_rules import get_location_suitability, normalize_location

# ─────────────────────────────────────────────
# SCORING WEIGHTS (Transparent & Configurable)
# ─────────────────────────────────────────────
ML_WEIGHT        = 0.50   # 50% weight to ML model suitability
LOCATION_WEIGHT  = 0.20   # 20% weight to geographic/agro-climatic suitability
SEASON_WEIGHT    = 0.15   # 15% weight to seasonal compatibility
WATER_WEIGHT     = 0.15   # 15% weight to water availability compatibility

SCORE_WEIGHTS = {
    "ml_score":       ML_WEIGHT,
    "location_score": LOCATION_WEIGHT,
    "season_score":   SEASON_WEIGHT,
    "water_score":    WATER_WEIGHT,
}

MODEL_PATH    = os.path.join("model", "crop_model.pkl")
FEATURE_COLS  = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
TOP_N         = 5


# ─────────────────────────────────────────────
# MODEL LOADER
# ─────────────────────────────────────────────

_model_cache = None

def load_model():
    """Load the trained Random Forest model (cached after first load)."""
    global _model_cache
    if _model_cache is not None:
        return _model_cache

    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"Trained model not found at '{MODEL_PATH}'. "
            "Please run:  python train_model.py  first."
        )

    try:
        _model_cache = joblib.load(MODEL_PATH)
    except Exception as e:
        raise RuntimeError(f"Failed to load model: {e}")

    return _model_cache


# ─────────────────────────────────────────────
# MODULE 1: ML PREDICTION
# ─────────────────────────────────────────────

def ml_predict(data: dict, top_n: int = TOP_N) -> list[dict]:
    """
    Use the trained Random Forest model to predict crop suitability.
    Returns a list of dicts with crop name and model suitability score.
    If top_n is None, returns predictions across ALL model classes.
    """
    model = load_model()
    features = np.array([[float(data[f]) for f in FEATURE_COLS]])

    proba  = model.predict_proba(features)[0]
    classes = model.classes_

    # Pair each class with its probability, sorted descending
    crop_probs = sorted(
        zip(classes, proba),
        key=lambda x: x[1],
        reverse=True
    )

    results = []
    subset = crop_probs if top_n is None else crop_probs[:top_n]
    for crop, prob in subset:
        results.append({
            "crop": crop,
            "model_score": round(float(prob) * 100, 2),  # as percentage
        })

    return results


# ─────────────────────────────────────────────
# MODULE 3: ENVIRONMENTAL ANALYSIS
# ─────────────────────────────────────────────

def analyze_environment(data: dict) -> list[dict]:
    """
    Analyze the input environmental conditions and return observations.
    Returns a list of observation dicts with type ('ok' / 'warning' / 'info')
    and a message string.
    """
    T   = ENV_THRESHOLDS
    obs = []

    temp = float(data["temperature"])
    if temp < T["temperature"]["low"]:
        obs.append({"type": "warning",
                    "message": f"Temperature ({temp}°C) is relatively cool. "
                               "Suitable mainly for cold-tolerant crops."})
    elif temp > T["temperature"]["high"]:
        obs.append({"type": "warning",
                    "message": f"Temperature ({temp}°C) is quite high. "
                               "Heat stress may affect sensitive crops."})
    elif T["temperature"]["optimal_low"] <= temp <= T["temperature"]["optimal_high"]:
        obs.append({"type": "ok",
                    "message": f"Temperature ({temp}°C) is within a generally suitable range."})
    else:
        obs.append({"type": "info",
                    "message": f"Temperature ({temp}°C) is moderate."})

    hum = float(data["humidity"])
    if hum < T["humidity"]["low"]:
        obs.append({"type": "warning",
                    "message": f"Humidity ({hum}%) is relatively low. "
                               "Moisture-sensitive crops may be at risk."})
    elif hum > T["humidity"]["high"]:
        obs.append({"type": "warning",
                    "message": f"Humidity ({hum}%) is very high. "
                               "Fungal disease risk may increase."})
    else:
        obs.append({"type": "ok",
                    "message": f"Humidity ({hum}%) is within a generally suitable range."})

    rain = float(data["rainfall"])
    if rain < T["rainfall"]["very_low"]:
        obs.append({"type": "warning",
                    "message": f"Rainfall ({rain} mm) is very low. "
                               "Irrigation will be essential for most crops."})
    elif rain < T["rainfall"]["low"]:
        obs.append({"type": "warning",
                    "message": f"Rainfall ({rain} mm) is relatively low. "
                               "Supplemental irrigation may be needed."})
    elif rain > T["rainfall"]["very_high"]:
        obs.append({"type": "warning",
                    "message": f"Rainfall ({rain} mm) is very high. "
                               "Good drainage is important to prevent waterlogging."})
    else:
        obs.append({"type": "ok",
                    "message": f"Rainfall ({rain} mm) is within a moderate-to-good range."})

    ph = float(data["ph"])
    if ph < T["ph"]["very_acidic"]:
        obs.append({"type": "warning",
                    "message": f"Soil pH ({ph}) is very acidic. "
                               "Lime application may be needed before cropping."})
    elif ph < T["ph"]["acidic"]:
        obs.append({"type": "warning",
                    "message": f"Soil pH ({ph}) is moderately acidic. "
                               "Suitable for acid-tolerant crops."})
    elif T["ph"]["neutral_low"] <= ph <= T["ph"]["neutral_high"]:
        obs.append({"type": "ok",
                    "message": f"Soil pH ({ph}) is within a neutral, generally suitable range."})
    elif ph > T["ph"]["alkaline"]:
        obs.append({"type": "warning",
                    "message": f"Soil pH ({ph}) is strongly alkaline. "
                               "Micronutrient availability may be reduced."})
    else:
        obs.append({"type": "info",
                    "message": f"Soil pH ({ph}) is slightly alkaline."})

    n = float(data["N"])
    if n < T["nitrogen"]["low"]:
        obs.append({"type": "info",
                    "message": f"Nitrogen (N={n} kg/ha) is relatively low. "
                               "Nitrogen-fixing legumes or fertilisation may help."})
    elif n > T["nitrogen"]["high"]:
        obs.append({"type": "info",
                    "message": f"Nitrogen (N={n} kg/ha) is relatively high. "
                               "Good for nitrogen-demanding crops."})
    else:
        obs.append({"type": "ok",
                    "message": f"Nitrogen level (N={n} kg/ha) is in a moderate range."})

    p = float(data["P"])
    if p < T["phosphorus"]["low"]:
        obs.append({"type": "info",
                    "message": f"Phosphorus (P={p} kg/ha) is relatively low."})
    else:
        obs.append({"type": "ok",
                    "message": f"Phosphorus level (P={p} kg/ha) is adequate."})

    k = float(data["K"])
    if k < T["potassium"]["low"]:
        obs.append({"type": "info",
                    "message": f"Potassium (K={k} kg/ha) is relatively low."})
    else:
        obs.append({"type": "ok",
                    "message": f"Potassium level (K={k} kg/ha) is adequate."})

    return obs


# ─────────────────────────────────────────────
# MODULE 5 + 6: DECISION LAYER & RANKING
# ─────────────────────────────────────────────

def compute_final_ranking(all_ml_results: list[dict], season: str,
                          water_availability: str, location: str = "") -> list[dict]:
    """
    Combine ML score, location suitability, seasonal suitability, and water compatibility
    into a final ranked list.

    Workflow:
      1. Calculate ML suitability (0–100)
      2. Calculate Location suitability (0–100) via location_rules
      3. Calculate Season suitability (0–100)
      4. Calculate Water availability compatibility (0–100)
      5. Calculate combined final score:
         final_score = (ml_score * ML_WEIGHT)
                     + (location_score * LOCATION_WEIGHT)
                     + (season_score * SEASON_WEIGHT)
                     + (water_score * WATER_WEIGHT)
      6. Remove crops with 'Unsuitable' location status (location_score < 25)
      7. Sort by final score descending
    """
    all_evaluated = []

    for item in all_ml_results:
        crop = item["crop"]
        ml_s = item["model_score"]  # 0–100

        # Location / Agro-climatic suitability
        loc_result = get_location_suitability(crop, location)
        loc_score = float(loc_result["score"])
        loc_status = loc_result["status"]
        loc_display = loc_result["status_display"]
        loc_reason = loc_result["reason"]
        exclude_crop = loc_result.get("exclude_from_ranking", False)

        # Seasonal suitability
        season_result = check_seasonal_suitability(crop, season)
        season_val = season_result["score"]   # 0.3–1.0
        season_score = round(season_val * 100, 1)

        # Water compatibility
        water_result = check_water_compatibility(crop, water_availability)
        water_val = water_result["score"]    # 0.3–1.0
        water_score = round(water_val * 100, 1)

        final_score = (
            (ml_s * ML_WEIGHT)
            + (loc_score * LOCATION_WEIGHT)
            + (season_score * SEASON_WEIGHT)
            + (water_score * WATER_WEIGHT)
        )

        crop_info = get_crop_info(crop)

        all_evaluated.append({
            "crop":                  crop,
            "model_score":           ml_s,
            "location_score":        loc_score,
            "location_status":       loc_status,
            "location_display":      loc_display,
            "location_reason":       loc_reason,
            "location_compatible":   loc_status == "Compatible",
            "exclude_from_ranking":  exclude_crop,
            "season_score":          season_score,
            "season_compatible":     season_result["suitable"],
            "season_description":    season_result["description"],
            "water_score":           water_score,
            "water_compatible":      water_result["compatible"],
            "water_warning":         water_result.get("warning", False),
            "water_description":     water_result["description"],
            "final_score":           round(final_score, 2),
            "water_requirement":     crop_info.get("water_requirement", "Medium"),
            "growing_duration":      crop_info.get("growing_duration_days", "N/A"),
            "key_consideration":     crop_info.get("key_consideration", "N/A"),
            "suitable_seasons":      crop_info.get("suitable_seasons", []),
        })

    # Hard exclusion: remove crops with 'Unsuitable' location status (score < 25)
    eligible = [c for c in all_evaluated if not c["exclude_from_ranking"]]
    if not eligible:
        # Failsafe: if all crops are excluded, keep all to avoid empty state
        eligible = all_evaluated

    # Sort by final score descending
    eligible.sort(key=lambda x: x["final_score"], reverse=True)
    return eligible


# ─────────────────────────────────────────────
# ADVISORY GENERATOR
# ─────────────────────────────────────────────

def generate_advisory(top_crop: dict, ranked_crops: list[dict],
                       season: str, water_availability: str,
                       env_analysis: list[dict], location: str) -> str:
    """Generate a plain-language AI advisory paragraph."""
    crop_name   = top_crop["crop"].capitalize()
    model_score = top_crop["model_score"]
    final_score = top_crop["final_score"]
    water_req   = top_crop["water_requirement"]
    water_warn  = top_crop["water_warning"]
    season_ok   = top_crop["season_compatible"]
    loc_str     = f" for {location}" if location else ""
    loc_reason  = top_crop.get("location_reason", "")

    advisory_parts = []

    advisory_parts.append(
        f"Based on the supplied soil, weather, season, and water conditions"
        f"{loc_str}, the AI agent identifies {crop_name} as the highest-ranked crop "
        f"with a model suitability score of {model_score:.1f}% and a combined decision score of "
        f"{final_score:.1f}/100."
    )

    if loc_reason:
        advisory_parts.append(f"Geographic feasibility: {loc_reason}")

    if not season_ok:
        advisory_parts.append(
            f"{crop_name} is not typically associated with the {season} season, "
            "which reduces its seasonal compatibility score. Consider verifying with local experts."
        )

    if water_warn:
        advisory_parts.append(
            f"The system detects that {crop_name} has {water_req.lower()} water requirements "
            f"while your water availability is {water_availability.lower()}. "
            "Supplemental irrigation or an alternative crop with lower water demand is advisable."
        )
    else:
        advisory_parts.append(
            f"Water compatibility appears satisfactory: {crop_name} has {water_req.lower()} "
            f"water requirements, aligned with your {water_availability.lower()} availability."
        )

    # Highlight any warnings from environmental analysis
    warnings = [o["message"] for o in env_analysis if o["type"] == "warning"]
    if warnings:
        advisory_parts.append(
            "Environmental notes to consider: " + " | ".join(warnings[:2])
        )

    # Mention runner-up
    if len(ranked_crops) > 1:
        runner = ranked_crops[1]["crop"].capitalize()
        runner_score = ranked_crops[1]["final_score"]
        advisory_parts.append(
            f"The next-best candidate is {runner} (score: {runner_score:.1f}/100). "
            "Review the comparison table for full details."
        )

    advisory_parts.append(
        "⚠ This is an AI-assisted recommendation and should not replace advice from "
        "qualified agricultural experts familiar with your specific region and conditions."
    )

    return " ".join(advisory_parts)


def generate_gemini_advisory(top_crop: dict, ranked_crops: list[dict],
                             season: str, water_availability: str,
                             env_analysis: list[dict], location: str,
                             data: dict) -> tuple[str, str]:
    """
    Generate an AI Agronomist advisory report using the Google Gemini API.
    Falls back gracefully to the local expert rules if the API key is pending or restricted.
    Returns: (advisory_text, advisory_source)
    """
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    crop_name = top_crop["crop"].capitalize()
    model_score = top_crop["model_score"]
    final_score = top_crop["final_score"]
    loc_reason = top_crop.get("location_reason", "Regionally compatible")

    if gemini_key:
        prompt = (
            f"You are an expert AI Agronomist advising an Indian farmer on seasonal crop planning.\n"
            f"Parameters:\n"
            f"- Recommended Crop: {crop_name} (ML Model Suitability: {model_score}%, Final Decision Score: {final_score}/100)\n"
            f"- Farm Location: {location or 'Agricultural field'}\n"
            f"- Geographic Compatibility: {loc_reason}\n"
            f"- Season: {season}\n"
            f"- Water Availability: {water_availability}\n"
            f"- Soil Nutrients: N={data.get('N')} kg/ha, P={data.get('P')} kg/ha, K={data.get('K')} kg/ha, pH={data.get('ph')}\n"
            f"- Weather: Temp={data.get('temperature')}°C, Humidity={data.get('humidity')}%, Rainfall={data.get('rainfall')} mm\n\n"
            f"Provide a concise, highly practical 3-4 sentence agronomic advisory covering:\n"
            f"1) Why {crop_name} is best suited for these exact soil, weather, and geographic conditions.\n"
            f"2) Fertilizer and irrigation management recommendations.\n"
            f"3) Key precautions for the {season} season."
        )

        candidate_models = [
            "gemini-2.5-flash",
            "gemini-1.5-flash",
            "gemini-flash-latest",
            "gemini-3.6-flash"
        ]

        for mod in candidate_models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{mod}:generateContent?key={gemini_key}"
            try:
                payload = json.dumps({
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": 0.3, "maxOutputTokens": 350}
                }).encode("utf-8")
                req = urllib.request.Request(
                    url,
                    data=payload,
                    headers={"Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req, timeout=5) as resp:
                    res_json = json.loads(resp.read().decode("utf-8"))
                    cand = res_json.get("candidates", [{}])[0]
                    text = cand.get("content", {}).get("parts", [{}])[0].get("text", "").strip()
                    if text:
                        return text, f"Google Gemini ({mod})"
            except Exception:
                continue

    # Graceful fallback to built-in agricultural expert system
    local_text = generate_advisory(
        top_crop, ranked_crops, season, water_availability, env_analysis, location
    )
    return local_text, "Gemini-Ready Decision Engine"


# ─────────────────────────────────────────────
# EXPLAINABILITY
# ─────────────────────────────────────────────

def generate_explanation(data: dict, all_ml_results: list, ranked_crops: list,
                          season: str, water_availability: str,
                          advisory_source: str = "Decision Engine",
                          norm_location: dict = None) -> list[dict]:
    """Generate a step-by-step explanation of the agent's reasoning process."""
    loc_display = norm_location["display"] if norm_location else (data.get("location") or "Not specified")
    top_c = ranked_crops[0]

    steps = [
        {
            "step": 1,
            "title": "Received and Validated Farmer Inputs",
            "detail": (
                f"Location: {data.get('location', 'Not specified')}, Season: {season}, "
                f"N={data['N']}, P={data['P']}, K={data['K']}, "
                f"Temp={data['temperature']}°C, Humidity={data['humidity']}%, "
                f"pH={data['ph']}, Rainfall={data['rainfall']} mm, "
                f"Water availability: {water_availability}, Land: {data.get('land_area', 'N/A')} acres"
            )
        },
        {
            "step": 2,
            "title": "Analysed Environmental Conditions",
            "detail": "Evaluated temperature, humidity, rainfall, soil pH, and nutrient levels "
                      "against general reference ranges to identify conditions needing attention."
        },
        {
            "step": 3,
            "title": "ML Model Predicted Initial Crop Probabilities",
            "detail": (
                f"The Random Forest model (200 estimators) scored all {len(all_ml_results)} "
                f"candidate crops based on soil nutrients and climatic parameters. "
                f"Raw ML #1: {all_ml_results[0]['crop'].capitalize()} ({all_ml_results[0]['model_score']}%). "
                f"ML weight in final score: {int(SCORE_WEIGHTS['ml_score']*100)}%."
            )
        },
        {
            "step": 4,
            "title": "Applied Geographic & Agro-Climatic Suitability Layer",
            "detail": (
                f"Evaluated all candidate crops against regional guidelines for {loc_display}. "
                f"Crops failing regional suitability (e.g. coffee or apples in warm lowland plains) were flagged as Unsuitable and excluded before final ranking. "
                f"Location score weight: {int(SCORE_WEIGHTS['location_score']*100)}%."
            )
        },
        {
            "step": 5,
            "title": "Applied Seasonal Suitability Rules",
            "detail": (
                f"Filtered and scored candidate crops against known {season} season characteristics. "
                f"Seasonal score weight: {int(SCORE_WEIGHTS['season_score']*100)}%."
            )
        },
        {
            "step": 6,
            "title": "Checked Water Requirement Compatibility",
            "detail": (
                f"Matched each crop's water requirement category against the "
                f"farmer's stated water availability ({water_availability}). "
                f"Water score weight: {int(SCORE_WEIGHTS['water_score']*100)}%."
            )
        },
        {
            "step": 7,
            "title": "Computed Final Combined Score & Selected Top 5",
            "detail": (
                f"Final score = ML ({int(SCORE_WEIGHTS['ml_score']*100)}%) + Location ({int(SCORE_WEIGHTS['location_score']*100)}%) "
                f"+ Season ({int(SCORE_WEIGHTS['season_score']*100)}%) + Water ({int(SCORE_WEIGHTS['water_score']*100)}%). "
                f"Top-ranked crop: {top_c['crop'].capitalize()} (Score: {top_c['final_score']}/100, Location: {top_c['location_display']})."
            )
        },
        {
            "step": 8,
            "title": "Generated AI Advisory & Recommendations",
            "detail": (
                f"Synthesized crop prediction, soil health alerts, geographic feasibility, and water risks into an "
                f"actionable agronomist advisory powered by {advisory_source}."
            )
        }
    ]
    return steps


# ─────────────────────────────────────────────
# MAIN AGENT FUNCTION
# ─────────────────────────────────────────────

def run_agent(data: dict) -> dict:
    """
    Main entry point for the AI Crop Planning Agent.
    Accepts validated farmer input and returns the full crop plan.

    Workflow:
      1. ML Model: Generates predictions across all crop classes
      2. Geographic Normalization & Location Suitability Layer
      3. Environmental Analysis (NPK, pH, temperature, humidity, rainfall)
      4. Seasonal Suitability Layer
      5. Water Compatibility Layer
      6. Combined Decision Score & Hard Exclusion of Unsuitable Crops
      7. Selection of Top 5 Recommendations
      8. AI Agronomist Advisory & Step-by-Step Explainability
    """
    season             = data.get("season", "Kharif")
    water_availability = data.get("water_availability", "Medium")
    location           = data.get("location", "")

    # Module 1 — ML Prediction across ALL candidate crops
    all_ml_results = ml_predict(data, top_n=None)

    # Module 2 — Location Normalization
    norm_location = normalize_location(location)

    # Module 3 — Environmental Analysis
    env_analysis = analyze_environment(data)

    # Module 4/5/6 — Decision Layer (Location + Season + Water + ML combined ranking)
    # Automatically excludes crops with 'Unsuitable' location score (<25)
    all_ranked_crops = compute_final_ranking(all_ml_results, season, water_availability, location)

    # Select Top 5 recommendations
    top_5_recommendations = all_ranked_crops[:5]
    top_crop = top_5_recommendations[0]

    # Location Analysis structure for UI and reporting
    location_analysis = {
        "location_input": location or "Not specified",
        "normalized_location": norm_location["display"],
        "region": norm_location["region"],
        "city": norm_location.get("city"),
        "state": norm_location.get("state"),
        "analysis_text": (
            f"The system evaluated crop suitability for {norm_location['display']} using regional agro-climatic rules. "
            f"For {top_crop['crop'].capitalize()}: {top_crop['location_reason']}"
        ),
        "top_crop_status": top_crop["location_display"],
        "top_crop_reason": top_crop["location_reason"],
        "model_limitation_note": (
            "The machine-learning model predicts crops from soil and environmental variables. "
            "Geographic suitability is therefore handled separately through a rule-based regional knowledge layer. "
            "The final recommendation combines both components."
        )
    }

    # Advisory (Google Gemini API with expert fallback)
    advisory, advisory_source = generate_gemini_advisory(
        top_crop, top_5_recommendations, season, water_availability, env_analysis, location, data
    )

    # Explainability
    explanation = generate_explanation(
        data, all_ml_results, top_5_recommendations, season, water_availability,
        advisory_source, norm_location
    )

    # Season info
    season_info = get_season_info(season)

    # Top 5 pure ML scores (for comparison bar chart)
    top5_ml_scores = all_ml_results[:5]

    # Build and return the full plan
    plan = {
        "recommended_crop":     top_crop["crop"],
        "model_score":          top_crop["model_score"],
        "final_score":          top_crop["final_score"],
        "recommendations":      top_5_recommendations,
        "location_analysis":    location_analysis,
        "environment_analysis": env_analysis,
        "season_info":          season_info,
        "season_analysis":      top_crop["season_description"],
        "water_analysis":       top_crop["water_description"],
        "water_warning":        top_crop["water_warning"],
        "advisory":             advisory,
        "advisory_source":      advisory_source,
        "explanation":          explanation,
        "top5_ml_scores":       top5_ml_scores,
        "score_weights":        SCORE_WEIGHTS,
    }

    return plan

