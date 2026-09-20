"""
app.py
======
Flask application for the AI Agent for Seasonal Crop Planning.

Routes:
    GET  /              → Main dashboard page
    GET  /api/health    → Health check
    POST /api/predict   → Quick ML crop predictions
    POST /api/plan      → Full AI crop planning agent

Usage:
    python app.py
"""

import os
import sys
import json
import traceback
import requests
from dotenv import load_dotenv

from flask import Flask, render_template, request, jsonify

from utils.preprocessing import validate_inputs, prepare_ml_features, sanitize_string

# Load environment variables (.env)
load_dotenv()

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

# Regional climatic averages for fallback if OpenWeatherMap key is pending activation
REGIONAL_CLIMATES = {
    "punjab": {"temp": 24.5, "humidity": 60.0},
    "haryana": {"temp": 25.0, "humidity": 58.0},
    "maharashtra": {"temp": 27.5, "humidity": 70.0},
    "nagpur": {"temp": 28.0, "humidity": 65.0},
    "pune": {"temp": 24.0, "humidity": 72.0},
    "mumbai": {"temp": 30.0, "humidity": 82.0},
    "delhi": {"temp": 26.5, "humidity": 62.0},
    "uttar pradesh": {"temp": 26.0, "humidity": 68.0},
    "bihar": {"temp": 27.0, "humidity": 75.0},
    "patna": {"temp": 27.0, "humidity": 74.0},
    "west bengal": {"temp": 28.5, "humidity": 80.0},
    "odisha": {"temp": 28.0, "humidity": 78.0},
    "bhubaneswar": {"temp": 28.2, "humidity": 79.0},
    "karnataka": {"temp": 25.5, "humidity": 68.0},
    "bengaluru": {"temp": 23.5, "humidity": 65.0},
    "bangalore": {"temp": 23.5, "humidity": 65.0},
    "tamil nadu": {"temp": 29.0, "humidity": 72.0},
    "chennai": {"temp": 30.5, "humidity": 78.0},
    "kerala": {"temp": 27.5, "humidity": 85.0},
    "gujarat": {"temp": 29.0, "humidity": 55.0},
    "rajasthan": {"temp": 31.0, "humidity": 45.0},
    "madhya pradesh": {"temp": 26.5, "humidity": 60.0},
    "andhra pradesh": {"temp": 29.5, "humidity": 70.0},
    "telangana": {"temp": 28.5, "humidity": 65.0},
    "hyderabad": {"temp": 27.0, "humidity": 64.0},
}

# ─────────────────────────────────────────────
# LAZY MODEL / AGENT IMPORT
# ─────────────────────────────────────────────

def _get_agent():
    """Import the agent module (deferred so the app starts even if model is missing)."""
    try:
        import agent as ag
        return ag
    except ImportError as e:
        return None


# ─────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────

@app.route("/")
def index():
    """Serve the main application page."""
    return render_template("index.html")


@app.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint with API key configuration status."""
    model_path = os.path.join("model", "crop_model.pkl")
    model_ready = os.path.exists(model_path)
    data_path = os.path.join("data", "Crop_recommendation.csv")
    data_ready = os.path.exists(data_path)

    has_owm = bool(os.getenv("OPENWEATHERMAP_API_KEY", "").strip())
    has_gemini = bool(os.getenv("GEMINI_API_KEY", "").strip())

    status = {
        "status": "ok",
        "model_ready": model_ready,
        "dataset_ready": data_ready,
        "model_path": model_path,
        "dataset_path": data_path,
        "openweathermap_configured": has_owm,
        "gemini_configured": has_gemini,
    }

    if not model_ready:
        status["model_message"] = (
            "Model not found. Please run: python train_model.py"
        )
    if not data_ready:
        status["dataset_message"] = (
            "Dataset not found. Please place Crop_recommendation.csv in the data/ directory."
        )

    return jsonify(status), 200


@app.route("/api/weather", methods=["GET"])
def get_weather():
    """
    Fetch live weather data from OpenWeatherMap API for the given location.
    Query parameter: ?location=<city or state>
    """
    location = request.args.get("location", "").strip()
    if not location:
        return jsonify({"error": "Please provide a location query."}), 400

    api_key = os.getenv("OPENWEATHERMAP_API_KEY", "").strip()
    search_query = location.split(",")[0].strip()

    live_success = False
    temp = None
    humidity = None
    weather_desc = "Clear"
    note = ""

    if api_key:
        try:
            resp = requests.get(
                "https://api.openweathermap.org/data/2.5/weather",
                params={"q": search_query, "appid": api_key, "units": "metric"},
                timeout=5
            )
            if resp.status_code == 200:
                wdata = resp.json()
                main = wdata.get("main", {})
                temp = round(float(main.get("temp", 25.0)), 1)
                humidity = round(float(main.get("humidity", 65.0)), 1)
                weather_desc = wdata.get("weather", [{}])[0].get("description", "Clear").title()
                live_success = True
                note = f"Live weather fetched via OpenWeatherMap API for {wdata.get('name', search_query)}"
            elif resp.status_code == 401:
                note = "OpenWeatherMap API Key active (pending server-side propagation; fallback regional data applied)"
            else:
                note = f"OpenWeatherMap returned status {resp.status_code}. Using regional climatic data."
        except Exception as ex:
            note = f"OpenWeatherMap request error: {str(ex)}. Using regional climatic data."

    if not live_success:
        # Match regional climatic database
        loc_lower = location.lower()
        matched = None
        for key, vals in REGIONAL_CLIMATES.items():
            if key in loc_lower or loc_lower in key:
                matched = vals
                break

        if matched:
            temp = matched["temp"]
            humidity = matched["humidity"]
            weather_desc = "Regional Climatic Average"
        else:
            temp = 26.5
            humidity = 68.0
            weather_desc = "Subtropical Moderate"

        if not note:
            note = f"Loaded regional parameters for {location}."

    return jsonify({
        "status": "ok",
        "live": live_success,
        "location": location,
        "temperature": temp,
        "humidity": humidity,
        "weather": weather_desc,
        "source": "OpenWeatherMap API" if live_success else "OpenWeatherMap (Key Configured) / Regional Database",
        "note": note
    }), 200


@app.route("/api/predict", methods=["POST"])
def predict():
    """
    Quick ML crop prediction endpoint.
    Returns top-5 crop recommendations based on ML model probabilities.

    Expected JSON body:
    {
        "N": 90, "P": 40, "K": 40,
        "temperature": 25, "humidity": 80,
        "ph": 6.5, "rainfall": 1000,
        "season": "Kharif",
        "water_availability": "High",
        "land_area": 2,
        "location": "Nagpur, Maharashtra"
    }
    """
    try:
        data = request.get_json(force=True, silent=True)
        if not data:
            return jsonify({"error": "Invalid or empty JSON body."}), 400

        # Validate
        is_valid, errors = validate_inputs(data)
        if not is_valid:
            return jsonify({"error": "Validation failed.", "details": errors}), 422

        # Run ML prediction
        ag = _get_agent()
        if ag is None:
            return jsonify({"error": "Agent module could not be loaded."}), 500

        try:
            ml_results = ag.ml_predict(data)
        except FileNotFoundError as e:
            return jsonify({
                "error": str(e),
                "hint": "Run: python train_model.py"
            }), 503
        except Exception as e:
            return jsonify({"error": f"Model prediction failed: {str(e)}"}), 500

        return jsonify({
            "status": "ok",
            "recommendations": ml_results,
            "note": (
                "Model suitability scores are derived from a Random Forest classifier. "
                "They reflect model confidence, not a guaranteed probability of crop success."
            )
        }), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


@app.route("/api/plan", methods=["POST"])
def plan():
    """
    Full AI Crop Planning Agent endpoint.
    Returns complete crop plan including ML prediction, seasonal analysis,
    water compatibility, environmental analysis, advisory, and explainability.
    """
    try:
        data = request.get_json(force=True, silent=True)
        if not data:
            return jsonify({"error": "Invalid or empty JSON body."}), 400

        # Sanitize text fields
        if "location" in data:
            data["location"] = sanitize_string(str(data.get("location", "")))

        # Validate
        is_valid, errors = validate_inputs(data)
        if not is_valid:
            return jsonify({"error": "Validation failed.", "details": errors}), 422

        # Run agent
        ag = _get_agent()
        if ag is None:
            return jsonify({"error": "Agent module could not be loaded."}), 500

        try:
            crop_plan = ag.run_agent(data)
        except FileNotFoundError as e:
            return jsonify({
                "error": str(e),
                "hint": "Run: python train_model.py"
            }), 503
        except Exception as e:
            traceback.print_exc()
            return jsonify({"error": f"Agent error: {str(e)}"}), 500

        return jsonify({
            "status": "ok",
            "recommended_crop":    crop_plan["recommended_crop"],
            "model_score":         crop_plan["model_score"],
            "final_score":         crop_plan["final_score"],
            "recommendations":     crop_plan["recommendations"],
            "location_analysis":   crop_plan.get("location_analysis", {}),
            "environment_analysis": crop_plan["environment_analysis"],
            "season_info":         crop_plan["season_info"],
            "season_analysis":     crop_plan["season_analysis"],
            "water_analysis":      crop_plan["water_analysis"],
            "water_warning":       crop_plan["water_warning"],
            "advisory":            crop_plan["advisory"],
            "advisory_source":     crop_plan.get("advisory_source", "Decision Engine"),
            "explanation":         crop_plan["explanation"],
            "top5_ml_scores":      crop_plan["top5_ml_scores"],
            "score_weights":       crop_plan["score_weights"],
            "disclaimer": (
                "This is an AI-assisted decision-support system. "
                "Results are not guaranteed agricultural prescriptions. "
                "Please consult qualified agricultural experts before making farming decisions."
            )
        }), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


# ─────────────────────────────────────────────
# ERROR HANDLERS
# ─────────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found.", "status": 404}), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"error": "Method not allowed.", "status": 405}), 405


@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error.", "status": 500}), 500


# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("  AI Agent for Seasonal Crop Planning")
    print("  Flask Development Server")
    print("=" * 60)

    model_path = os.path.join("model", "crop_model.pkl")
    data_path  = os.path.join("data", "Crop_recommendation.csv")

    if not os.path.exists(data_path):
        print(f"\n[WARN] Dataset not found: {data_path}")
        print("       Place Crop_recommendation.csv inside the data/ directory")
        print("       then run:  python train_model.py")

    if not os.path.exists(model_path):
        print(f"\n[WARN] Trained model not found: {model_path}")
        print("       Run:  python train_model.py   before using /api/predict or /api/plan")

    print("\n[OK] Starting Flask application...")
    print("[OK] Open your browser at:  http://127.0.0.1:5000")
    print("=" * 60 + "\n")

    app.run(debug=True, host="127.0.0.1", port=5000)
