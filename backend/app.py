import sys
import os
import json
import time
import joblib
import numpy as np
import pandas as pd
import pickle

from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS


sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

class RenameUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if module == "preprocessor":
            module = "preprocessing"
        return super().find_class(module, name)

def load_pickle_with_rename(path):
    with open(path, "rb") as f:
        return RenameUnpickler(f).load()


MODEL_PATH = "outputs/all_models/random_forest_model.pkl"
PREPROCESSOR_PATH = "src/preprocessing/preprocessor.pkl"
API_KEY = "super_secret_bfsi_key_123"
SUPPORTED_CHANNELS = ["Web", "Mobile", "Pos", "Atm", "online", "atm", "pos", "mobile"]

# In-memory storage for results (will be replaced with MongoDB in Task 2)
prediction_results = {}


print("🔄 Loading model & preprocessor...")

model = joblib.load(MODEL_PATH)
preprocessor = load_pickle_with_rename(PREPROCESSOR_PATH)

print("✅ Model Loaded:", type(model))
print("✅ Preprocessor Loaded:", type(preprocessor))
print("Model expects:", model.feature_names_in_)

MODEL_FEATURE_ORDER = list(model.feature_names_in_)
N_FEATURES = len(MODEL_FEATURE_ORDER)


# -------------------------------
# RULE-BASED FRAUD DETECTION
# -------------------------------
def apply_fraud_rules(data, ml_risk_score):
    """
    Apply business rules for fraud detection.
    Combines ML model with rule-based logic.
    Returns: (final_prediction, rule_flags, reason)
    """
    amount = float(data.get("amount", 0))
    account_age = float(data.get("account_age_days", 365))
    channel = data.get("channel", "Web").lower()
    kyc_verified = data.get("kyc_verified", "Yes")
    
    # Parse timestamp to get hour
    timestamp_str = data.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    try:
        dt = pd.to_datetime(timestamp_str)
        hour = dt.hour
    except:
        hour = datetime.now().hour
    
    rule_flags = []
    reasons = []
    
    # RULE 1: High-value transaction from new account
    if amount > 10000 and account_age < 30:
        rule_flags.append("HIGH_VALUE_NEW_ACCOUNT")
        reasons.append(f"High transaction amount (₹{amount:,.0f}) from new account ({account_age} days old)")
    
    # RULE 2: KYC not verified with significant amount
    if kyc_verified.lower() == "no" and amount > 5000:
        rule_flags.append("UNVERIFIED_KYC_HIGH_AMOUNT")
        reasons.append(f"KYC not verified with amount ₹{amount:,.0f}")
    
    # RULE 3: Unusual hour transactions (late night/early morning)
    if hour >= 2 and hour <= 5 and amount > 3000:
        rule_flags.append("UNUSUAL_HOUR")
        reasons.append(f"Transaction at unusual hour ({hour}:00) with amount ₹{amount:,.0f}")
    
    # RULE 4: Very high amount (automatic flag)
    if amount > 50000:
        rule_flags.append("VERY_HIGH_AMOUNT")
        reasons.append(f"Extremely high transaction amount (₹{amount:,.0f})")
    
    # RULE 5: New account + unverified KYC
    if account_age < 7 and kyc_verified.lower() == "no":
        rule_flags.append("NEW_ACCOUNT_UNVERIFIED")
        reasons.append(f"Very new account ({account_age} days) without KYC verification")
    
    # RULE 6: ATM withdrawals above threshold
    if channel in ["atm", "pos"] and amount > 20000:
        rule_flags.append("HIGH_ATM_WITHDRAWAL")
        reasons.append(f"Unusually high ATM/POS transaction (₹{amount:,.0f})")
    
    # Combine ML + Rules
    rule_triggered = len(rule_flags) > 0
    
    # Final decision logic
    if rule_triggered and ml_risk_score > 0.3:
        # Both rules and ML suggest fraud
        final_prediction = "Fraud"
        reason = "Rules triggered: " + "; ".join(reasons)
    elif ml_risk_score >= 0.7:
        # High ML confidence
        final_prediction = "Fraud"
        if rule_triggered:
            reason = "High ML risk score (" + str(round(ml_risk_score, 2)) + "). " + "; ".join(reasons)
        else:
            reason = f"High ML fraud risk score ({round(ml_risk_score, 2)})"
    elif rule_triggered:
        # Rules triggered but ML not confident
        final_prediction = "Fraud"
        reason = "Rules triggered: " + "; ".join(reasons)
    elif ml_risk_score >= 0.5:
        # Moderate ML risk
        final_prediction = "Fraud"
        reason = f"Moderate ML fraud risk score ({round(ml_risk_score, 2)})"
    else:
        # Low risk
        final_prediction = "Legitimate"
        reason = f"Low fraud risk. Normal transaction pattern for amount ₹{amount:,.0f}"
    
    return final_prediction, rule_flags, reason


# -------------------------------
# HELPER — Build Feature Row
# -------------------------------
def build_feature_row(data):
    """
    Convert incoming JSON into model-ready features.
    Uses preprocessor to transform raw input.
    """
    # Prepare input for preprocessor
    preprocessor_input = {
        "transaction_amount": float(data.get("amount", 0)),
        "account_age_days": float(data.get("account_age_days", 365)),
        "timestamp": data.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        "channel": data.get("channel", "Web").capitalize(),
        "kyc_verified": data.get("kyc_verified", "Yes")
    }
    
    # Transform using preprocessor
    df_processed = preprocessor.transform(preprocessor_input)
    
    # Convert to numpy array
    if hasattr(df_processed, 'values'):
        return df_processed.values
    else:
        return np.array(df_processed)

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "allow_headers": ["Content-Type", "X-API-Key"]
    }
})


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "OK",
        "message": "Fraud Detection API - Milestone 3",
        "version": "1.0",
        "endpoints": {
            "predict": "POST /api/predict",
            "get_result": "GET /api/result/<transaction_id>",
            "all_results": "GET /api/results"
        },
        "features": [
            "ML Model (Random Forest)",
            "Rule-Based Detection",
            "Risk Scoring",
            "Reason Generation"
        ]
    }), 200


@app.route("/api/predict", methods=["POST"])
def predict():
    """
    POST /api/predict
    Fraud detection with ML model + business rules
    
    Request: {
      "transaction_id": "T1001",
      "customer_id": "C123",
      "amount": 5000,
      "channel": "online",
      "timestamp": "2024-01-15T10:30:00",
      "account_age_days": 365,
      "kyc_verified": "Yes"
    }
    
    Response: {
      "transaction_id": "T1001",
      "prediction": "Fraud" | "Legitimate",
      "risk_score": 0.80,
      "confidence": 0.95,
      "reason": "High transaction amount from new account",
      "rule_flags": ["HIGH_VALUE_NEW_ACCOUNT"],
      "model_version": "RandomForest"
    }
    """
    start = time.time()

    key = request.headers.get("X-API-Key")
    if key != API_KEY:
        return jsonify({"status": "error", "message": "Invalid API Key"}), 401

    try:
        data = request.get_json(force=True)
    except Exception:
        return jsonify({"status": "error", "message": "Malformed JSON"}), 400

    # Required fields
    required = ["transaction_id", "customer_id", "amount", "channel"]
    if not all(r in data for r in required):
        return jsonify({
            "status": "error",
            "message": f"Missing required fields. Required: {required}"
        }), 400

    transaction_id = data["transaction_id"]

    try:
        # Step 1: Get ML model prediction
        X = build_feature_row(data)
        if X.ndim == 1:
            X = X.reshape(1, -1)

        probas = model.predict_proba(X)[0]
        ml_risk_score = float(probas[1])  # Probability of fraud
        confidence = float(max(probas))
        
        # Step 2: Apply rule-based detection
        final_prediction, rule_flags, reason = apply_fraud_rules(data, ml_risk_score)
        
        # Step 3: Build response
        result = {
            "transaction_id": transaction_id,
            "prediction": final_prediction,
            "risk_score": round(ml_risk_score, 4),
            "confidence": round(confidence, 4),
            "reason": reason,
            "rule_flags": rule_flags,
            "model_version": "RandomForest"
        }
        
        # Step 4: Store result (in-memory for now, will be MongoDB in Task 2)
        prediction_results[transaction_id] = {
            **result,
            "customer_id": data["customer_id"],
            "amount": data["amount"],
            "channel": data["channel"],
            "timestamp": data.get("timestamp", datetime.now().isoformat()),
            "account_age_days": data.get("account_age_days", 365),
            "kyc_verified": data.get("kyc_verified", "Yes"),
            "processed_at": datetime.now().isoformat(),
            "latency_ms": round((time.time() - start) * 1000, 2)
        }

        return jsonify(result), 200

    except Exception as e:
        print("❌ Prediction Error:", e)
        import traceback
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": f"Server error during inference: {str(e)}"
        }), 500


@app.route("/api/result/<transaction_id>", methods=["GET"])
def get_result(transaction_id):
    """
    GET /api/result/<transaction_id>
    Retrieves previously stored prediction result
    
    Response: Full prediction details including input data
    """
    key = request.headers.get("X-API-Key")
    if key != API_KEY:
        return jsonify({"status": "error", "message": "Invalid API Key"}), 401

    if transaction_id not in prediction_results:
        return jsonify({
            "status": "error",
            "message": f"No result found for transaction_id: {transaction_id}"
        }), 404

    return jsonify(prediction_results[transaction_id]), 200


@app.route("/api/results", methods=["GET"])
def get_all_results():
    """
    GET /api/results?limit=100&fraud_only=false
    Returns all stored prediction results
    """
    key = request.headers.get("X-API-Key")
    if key != API_KEY:
        return jsonify({"status": "error", "message": "Invalid API Key"}), 401

    limit = request.args.get('limit', type=int, default=100)
    fraud_only = request.args.get('fraud_only', type=str, default='false').lower() == 'true'
    
    results_list = list(prediction_results.values())
    
    # Filter fraud only if requested
    if fraud_only:
        results_list = [r for r in results_list if r.get('prediction') == 'Fraud']
    
    # Apply limit
    results_list = results_list[-limit:]
    
    return jsonify({
        "total": len(prediction_results),
        "returned": len(results_list),
        "fraud_count": sum(1 for r in prediction_results.values() if r.get('prediction') == 'Fraud'),
        "results": results_list
    }), 200


@app.route("/api/stats", methods=["GET"])
def get_stats():
    """
    GET /api/stats
    Returns statistics about predictions
    """
    key = request.headers.get("X-API-Key")
    if key != API_KEY:
        return jsonify({"status": "error", "message": "Invalid API Key"}), 401
    
    if not prediction_results:
        return jsonify({
            "total_predictions": 0,
            "fraud_count": 0,
            "legitimate_count": 0,
            "fraud_rate": 0.0
        }), 200
    
    fraud_count = sum(1 for r in prediction_results.values() if r.get('prediction') == 'Fraud')
    total = len(prediction_results)
    
    return jsonify({
        "total_predictions": total,
        "fraud_count": fraud_count,
        "legitimate_count": total - fraud_count,
        "fraud_rate": round(fraud_count / total, 4) if total > 0 else 0.0,
        "avg_risk_score": round(np.mean([r.get('risk_score', 0) for r in prediction_results.values()]), 4)
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)