"""
auxiliary_service.py

Auxiliary Service for PWP_Supra (aligned with available main API):
  - Foods List               : GET  /api/foods       (returns cached foods)
  - Nutrition Info Cache     : GET  /api/nutrition   (returns cached nutritional-info items)
  - Consumption Statistics   : POST /api/consume    &    GET /api/stats
  - Natural-Language Summary : GET  /api/summary    (via Mistral AI)
  - Health Check             : GET  /api/health
"""
import os
import json
import logging
from datetime import datetime
from typing import Any, Dict, List

import requests
from flask import Flask, jsonify, request, Response
from apscheduler.schedulers.background import BackgroundScheduler

# === App Initialization ===
app = Flask(__name__)
# allow trailing slash flexibility globally
app.url_map.strict_slashes = False

# === Configuration ===
MAIN_FOODS_URL     = os.getenv("SUPRA_API_URL", "http://127.0.0.1:5000/api/foods/")
NUTRITION_URL      = os.getenv("SUPRA_NUTRITION_URL", "http://127.0.0.1:5000/api/nutritional-info/")
MISTRAL_BASE_URL   = os.getenv("MISTRAL_BASE_URL",   "http://86.50.252.67:11434/v1")
MISTRAL_API_KEY    = os.getenv("MISTRAL_API_KEY",    "")
MISTRAL_MODEL      = os.getenv("MISTRAL_MODEL",      "mistral-large")
MISTRAL_ENDPOINT   = f"{MISTRAL_BASE_URL}/chat/completions"
HEADERS            = {"Accept": "application/vnd.mason+json"}
PORT               = int(os.getenv("PORT", "5002"))
CACHE_INTERVAL_MIN = int(os.getenv("CHECK_INTERVAL_MINUTES", "10"))

# === Logging ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AuxService")

# === In-Memory Stores ===
foods_cache: List[Dict[str, Any]] = []
nutrition_cache: List[Dict[str, Any]] = []
consumption_records: List[Dict[str, Any]] = []

# === Helper Functions ===
def fetch_items(url: str) -> List[Dict[str, Any]]:
    """Fetches a Mason collection endpoint and returns its 'items' list."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=5)
        resp.raise_for_status()
        return resp.json().get("items", [])
    except Exception as e:
        logger.error(f"Failed to fetch from {url}: {e}")
        return []


def call_mistral(prompt: str) -> str:
    """Call Mistral AI for a natural language summary."""
    headers = {
        "Authorization": f"ApiKey {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MISTRAL_MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful food inventory assistant."},
            {"role": "user", "content": prompt}
        ]
    }
    try:
        r = requests.post(MISTRAL_ENDPOINT, headers=headers, json=payload, timeout=10)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"Mistral API error: {e}")
        return "[Error generating summary]"

# === Cache Update Jobs ===
def update_foods_cache():
    global foods_cache
    foods_cache = fetch_items(MAIN_FOODS_URL)
    logger.info(f"Cached {len(foods_cache)} foods items")


def update_nutrition_cache():
    global nutrition_cache
    nutrition_cache = fetch_items(NUTRITION_URL)
    logger.info(f"Cached {len(nutrition_cache)} nutrition-info items")

scheduler = BackgroundScheduler()
scheduler.add_job(update_foods_cache, 'interval', minutes=CACHE_INTERVAL_MIN)
scheduler.add_job(update_nutrition_cache, 'interval', minutes=CACHE_INTERVAL_MIN)
scheduler.start()
# Initial load
update_foods_cache()
update_nutrition_cache()

# === Flask Routes ===
@app.route('/api/health')
def health_check() -> Response:
    """Health check endpoint."""
    return jsonify({"status": "up"}), 200

@app.route('/api/foods')
def get_foods() -> Response:
    """Return cached list of foods."""
    return jsonify({"foods": foods_cache}), 200

@app.route('/api/nutrition')
def get_nutrition() -> Response:
    """Return cached nutrition-info entries."""
    return jsonify({"nutrition_info": nutrition_cache}), 200

@app.route('/api/consume', methods=['POST'])
def record_consumption() -> Response:
    """Log a consumption event."""
    data = request.get_json(force=True)
    rec = {
        "item":      data.get("item"),
        "quantity":  data.get("quantity", 1),
        "timestamp": datetime.utcnow().isoformat()
    }
    consumption_records.append(rec)
    return jsonify({"status": "recorded", "record": rec}), 201

@app.route('/api/stats')
def get_stats() -> Response:
    """Return aggregated consumption statistics."""
    stats: Dict[str, int] = {}
    for r in consumption_records:
        name = r.get("item")
        stats[name] = stats.get(name, 0) + r.get("quantity", 0)
    return jsonify({"consumption_stats": stats}), 200

@app.route('/api/summary')
def get_summary() -> Response:
    """Return a natural-language summary via Mistral AI."""
    prompt = (
        f"Foods (sample): {json.dumps(foods_cache[:3], indent=2)}\n"
        f"Nutrition-info (sample): {json.dumps(nutrition_cache[:3], indent=2)}\n"
        "Please summarize the inventory status."  
    )
    summary = call_mistral(prompt)
    return jsonify({"summary": summary}), 200

# === Main Entry Point ===
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)
