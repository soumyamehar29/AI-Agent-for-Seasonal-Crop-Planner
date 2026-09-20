# AI Agent for Seasonal Crop Planning

> **Academic Project — AI-Assisted Decision Support System**  
> CSE Semester Project · Python Flask · Machine Learning · Random Forest

---

## Problem Statement

Farmers often lack data-driven tools to help them decide which crop to grow for a given season based on their soil conditions, available water resources, and local climate. This project builds an AI-assisted decision-support system to address this gap.

---

## Objective

Build a web-based AI Agent that:
1. Accepts soil nutrient levels, weather parameters, seasonal context, and water availability from the farmer.
2. Uses a trained **Random Forest Classifier** to predict the most suitable crops.
3. Combines the ML prediction with a **seasonal knowledge base**, **water requirement analysis**, and **environmental analysis** to produce a ranked crop recommendation.
4. Presents the reasoning process transparently (explainability).

---

## Features

- 🌱 **ML Crop Prediction** — Random Forest trained on Crop Recommendation Dataset
- 🗓 **Seasonal Analysis** — Kharif / Rabi / Zaid seasonal knowledge base
- 🌡 **Environmental Analysis** — Temperature, humidity, rainfall, pH, NPK evaluation
- 💧 **Water Compatibility Analysis** — Matches crop water needs with farmer availability
- 📊 **Interactive Dashboard** — Bar chart + Radar chart with Chart.js
- 🔬 **Explainability** — Step-by-step agent reasoning
- ⚖️ **Transparent Scoring** — Weighted decision score (ML 60% + Season 20% + Water 20%)
- 📱 **Responsive Design** — Works on laptop and mobile

---

## Technologies Used

| Layer        | Technology                                 |
|--------------|--------------------------------------------|
| Frontend     | HTML5, CSS3, JavaScript                    |
| Backend      | Python, Flask                              |
| ML Model     | Scikit-learn (Random Forest)               |
| GenAI & LLM  | Google Gemini API (AI Agronomist Advisory) |
| Weather API  | OpenWeatherMap API (Real-Time Weather)     |
| Data         | Pandas, NumPy                              |
| Model Save   | joblib                                     |
| Visualisation| Chart.js                                   |

---

## System Architecture

```
Farmer Input
    ↓
Input Validation (utils/preprocessing.py)
    ↓
Environmental Analysis (agent.py → Module 3)
    ↓
ML Crop Prediction (agent.py → Module 1, Random Forest)
    ↓
Seasonal Suitability Analysis (agent.py → Module 5, crop_rules.py)
    ↓
Water Requirement Analysis (agent.py → Module 4, crop_rules.py)
    ↓
Decision Layer / Crop Ranking (agent.py → Module 6)
    ↓
AI Advisory Generator (agent.py)
    ↓
Explainable Crop Recommendation (Dashboard)
```

---

## AI Agent Workflow

The agent (`agent.py`) contains six modules:

| Module | Name | Description |
|--------|------|-------------|
| 1 | ML Prediction | Random Forest predict_proba() returns top-5 crop scores |
| 2 | Seasonal Analysis | Knowledge base for Kharif / Rabi / Zaid season compatibility |
| 3 | Environmental Analysis | Evaluates NPK, temperature, humidity, pH, rainfall |
| 4 | Water Analysis | Checks crop water need vs. farmer availability |
| 5 | Seasonal Suitability | Scores crops by seasonal match |
| 6 | Decision Layer | Weighted combined score → ranked list |

**Scoring Formula (Decision-Support Mechanism):**

```
Final Score = (ML Score × 0.60) + (Season Score × 0.20) + (Water Score × 0.20)
```

> Note: This is a decision-support scoring mechanism, not a scientifically validated agricultural formula. Weights are adjustable in `agent.py`.

---

## Dataset Description

**File:** `data/Crop_recommendation.csv`

**Source:** [Kaggle — Crop Recommendation Dataset](https://www.kaggle.com/datasets/atharvaingle/crop-recommendation-dataset)

| Column       | Description                        |
|--------------|------------------------------------|
| N            | Nitrogen content in soil (kg/ha)   |
| P            | Phosphorus content in soil (kg/ha) |
| K            | Potassium content in soil (kg/ha)  |
| temperature  | Temperature in °C                  |
| humidity     | Relative humidity (%)              |
| ph           | Soil pH value                      |
| rainfall     | Rainfall in mm                     |
| label        | Crop name (target variable)        |

The dataset contains approximately 2200 records across 22 crop types.

---

## ML Methodology

- **Algorithm:** Random Forest Classifier
- **Parameters:** `n_estimators=200, random_state=42`
- **Split:** 80% train / 20% test (stratified)
- **Features:** N, P, K, temperature, humidity, ph, rainfall
- **Target:** crop label
- **Output:** `predict_proba()` used to generate ranked suitability scores

**Important:** The model suitability score is the classifier's confidence value. It reflects model prediction strength, NOT a guaranteed probability of successful crop cultivation.

---

## Model Evaluation

After running `python train_model.py`, the terminal will display:
- Accuracy (%)
- Precision (weighted)
- Recall (weighted)
- F1-Score (weighted)
- Classification report (per-class)
- Confusion matrix summary

Typical accuracy on this dataset with Random Forest is > 97%.

---

## Project Folder Structure

```
AI-Agent-Seasonal-Crop-Planning/
├── app.py                      ← Flask application
├── train_model.py              ← Model training script
├── agent.py                    ← AI agent (6 modules)
├── crop_rules.py               ← Crop knowledge base
├── requirements.txt            ← Python dependencies
├── README.md                   ← This file
│
├── data/
│   └── Crop_recommendation.csv ← ⚠ YOU MUST PLACE THIS FILE HERE
│
├── model/
│   └── crop_model.pkl          ← Generated by train_model.py
│
├── templates/
│   └── index.html              ← Main HTML page
│
├── static/
│   ├── css/style.css           ← Stylesheet
│   ├── js/script.js            ← Frontend JavaScript
│   └── images/                 ← (images folder, optional)
│
└── utils/
    └── preprocessing.py        ← Input validation utilities
```

---

## Installation Steps

### 1. Prerequisites
- Python 3.8 or later
- pip

### 2. Create a virtual environment (recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Where to Put the Dataset

⚠ **This step is mandatory before training.**

1. Download the Crop Recommendation Dataset from:  
   https://www.kaggle.com/datasets/atharvaingle/crop-recommendation-dataset

2. Place the downloaded file at:
   ```
   data/Crop_recommendation.csv
   ```

3. Verify the file has these columns: `N, P, K, temperature, humidity, ph, rainfall, label`

---

## How to Train the Model

After placing the dataset:

```bash
python train_model.py
```

This will:
- Load and validate the dataset
- Train the Random Forest model
- Print accuracy, precision, recall, F1, classification report
- Save the model to `model/crop_model.pkl`

---

## How to Run the Application

```bash
python app.py
```

Open your browser at:  
**http://127.0.0.1:5000**

---

## API Endpoints

| Method | Endpoint        | Description                              |
|--------|-----------------|------------------------------------------|
| GET    | `/`             | Main dashboard page                      |
| GET    | `/api/health`   | System health check & API status         |
| GET    | `/api/weather`  | Real-time weather via OpenWeatherMap API |
| POST   | `/api/predict`  | Quick ML crop prediction (top-5)         |
| POST   | `/api/plan`     | Full AI crop planning agent (with Gemini)|

---

## API Configuration (`.env`)

The project uses a `.env` file to manage external API keys securely:

```env
# OpenWeatherMap API Key (for live temperature & humidity)
OPENWEATHERMAP_API_KEY=YOUR_OPENWEATHER_API_KEY

# Google Gemini API Key (for AI Agronomist smart advisory)
GEMINI_API_KEY=YOUR_GCP_API_KEY
```

- **OpenWeatherMap Integration**: Click **"🌦 Fetch Weather"** on the dashboard after typing a location to auto-populate temperature & humidity.
- **Google Gemini Integration**: The backend automatically synthesizes the Random Forest outputs into an AI Agronomist advisory report.
- **Fail-Safe Fallback**: If internet connectivity is interrupted or API propagation is pending, the system gracefully falls back to built-in agricultural knowledge rules without crashing.


### Example: `/api/predict` request

```json
{
  "N": 90, "P": 40, "K": 40,
  "temperature": 25, "humidity": 80,
  "ph": 6.5, "rainfall": 1000,
  "season": "Kharif",
  "water_availability": "High",
  "land_area": 2,
  "location": "Nagpur, Maharashtra"
}
```

### Example: `/api/predict` response

```json
{
  "status": "ok",
  "recommendations": [
    { "crop": "rice",   "model_score": 92.4 },
    { "crop": "maize",  "model_score":  4.2 },
    ...
  ],
  "note": "Model suitability scores are derived from a Random Forest classifier..."
}
```

---

## Example Input (Demo)

| Parameter          | Value               |
|--------------------|---------------------|
| Location           | Nagpur, Maharashtra |
| Season             | Kharif              |
| Nitrogen (N)       | 90 kg/ha            |
| Phosphorus (P)     | 40 kg/ha            |
| Potassium (K)      | 40 kg/ha            |
| Temperature        | 25 °C               |
| Humidity           | 80 %                |
| Soil pH            | 6.5                 |
| Rainfall           | 1000 mm             |
| Water Availability | High                |
| Land Area          | 2 acres             |

---

## Example Output

```
Recommended Crop : Rice
Model Score      : 92.4%
Final Score      : 88.7/100
Season           : Kharif ✓ Compatible
Water            : High ✓ Compatible
Advisory         : "Based on the supplied soil, weather, season and water
                   conditions for Nagpur, Maharashtra, the AI agent identifies
                   Rice as the highest-ranked crop..."
```

---

## Limitations

1. The model is only as good as the training dataset. Regional agricultural variation is not captured.
2. The system does NOT fetch real-time weather data. All inputs must be supplied by the user.
3. The seasonal knowledge base uses broad categories. Local micro-climatic conditions may differ.
4. The crop knowledge base values are approximate. Always verify with local agricultural extension officers.
5. The system covers crops present in the Crop Recommendation Dataset (~22 crops).

---

## Future Scope

- Integrate a real-time weather API (e.g., OpenWeatherMap) for automatic weather data
- Add soil test report parsing (image/PDF upload)
- Expand the crop knowledge base with district-level data
- Add a market price module for economic decision support
- Deploy on a cloud platform (Heroku / Render / AWS)
- Add multi-language support for regional farmers
- Mobile app (React Native / Flutter) wrapping the Flask API

---

## Disclaimer

This system is an AI-assisted decision-support tool developed for academic purposes.  
Results should not replace advice from qualified agricultural experts.  
Model suitability scores reflect classifier confidence, not guaranteed crop success probabilities.

---

*Built with ❤️ as a CSE Semester Project | AI Agent for Seasonal Crop Planning*
