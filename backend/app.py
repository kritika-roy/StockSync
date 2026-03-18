from flask import Flask, request, jsonify
import pandas as pd
import os

from utils.csv_validator import validate_and_clean_csv
from services.demand_forecast import forecast_demand
from services.inventory_service import calculate_inventory
from services.revenue_service import calculate_revenue
from services.expiry_service import detect_expiry

from rag.llm_client import call_llm

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Global variable to store analytics data
analytics_data = None


@app.route("/")
def home():
    return "Business Analytics SaaS Backend Running"


# ---------- CSV UPLOAD ----------
@app.route("/upload", methods=["POST"])
def upload_file():

    global analytics_data

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    # ---------- VALIDATE CSV ----------
    df, message = validate_and_clean_csv(file_path)

    if df is None:
        return jsonify({"error": message}), 400

    # ---------- ANALYTICS ----------
    forecast_results = forecast_demand(df)
    inventory_results = calculate_inventory(df, forecast_results)
    revenue_results = calculate_revenue(df, forecast_results)
    expiry_results = detect_expiry(df, forecast_results)

    response = {
        "Demand Forecast": forecast_results,
        "Inventory Analysis": inventory_results,
        "Revenue Forecast": revenue_results,
        "Expiry Risk": expiry_results
    }

    # Store globally for AI usage
    analytics_data = response

    return jsonify(response)


# ---------- AI INSIGHTS ----------
@app.route("/ai-insights", methods=["POST"])
def ai_insights():

    global analytics_data

    if analytics_data is None:
        return jsonify({"answer": "Please upload dataset first."})

    data = request.json

    question = data.get("question")
    api_key = data.get("api_key")
    base_url = data.get("base_url")
    model_name = data.get("model_name")
    provider = data.get("provider")

    # ---------- CONVERT JSON → READABLE CONTEXT ----------
    context = ""

    # Demand Forecast
    for product, d in analytics_data["Demand Forecast"].items():
        context += f"""
Product: {product}
Predicted Daily Demand: {d['Predicted Daily Demand']}
"""

    # Inventory
    for product, d in analytics_data["Inventory Analysis"].items():
        context += f"""
Product: {product}
Current Stock: {d['Current Stock']}
Inventory Status: {d['Status']}
"""

    # Revenue
    for product, d in analytics_data["Revenue Forecast"].items():
        context += f"""
Product: {product}
Predicted Revenue: {d['Predicted Revenue']}
"""

    # Expiry
    for product, d in analytics_data["Expiry Risk"].items():
        context += f"""
Product: {product}
Potential Expiry Units: {d['Potential Expiry Units']}
Expiry Status: {d['Status']}
"""

    # ---------- PROMPT ----------
    prompt = f"""
You are a business analytics assistant.

Use ONLY the business data below to answer.

Business Data:
{context}

Question:
{question}

Instructions:
- Answer clearly using the data
- Mention product name if relevant
- Do NOT say "information not available" unless truly missing
"""

    # ---------- CALL LLM ----------
    answer = call_llm(
        provider,
        api_key,
        base_url,
        model_name,
        prompt
    )

    return jsonify({"answer": answer})


# ---------- RUN ----------
if __name__ == "__main__":
    print("Backend running on http://127.0.0.1:5000")
    app.run(debug=True)