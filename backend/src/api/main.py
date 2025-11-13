from fastapi import FastAPI
from pydantic import BaseModel
import pickle
import pandas as pd
import numpy as np
from pathlib import Path

app = FastAPI(title="Fraud Detection API", version="1.0")

# Load model,scaler,features
MODEL_DIR = Path("final_fraud_model")
model_path = MODEL_DIR / "best_model.pkl"
scaler_path = MODEL_DIR / "scaler.pkl"
features_path = MODEL_DIR / "features.pkl"

with open(model_path, "rb") as f:
    model = pickle.load(f)
with open(scaler_path, "rb") as f:
    scaler = pickle.load(f)
with open(features_path, "rb") as f:
    features = pickle.load(f)

#Input schema
class TransactionInput(BaseModel):
    step: int
    type: int
    amount: float
    oldbalanceOrg: float
    newbalanceOrig: float
    oldbalanceDest: float
    newbalanceDest: float
    errorBalanceOrig: float
    errorBalanceDest: float
    transactionType_CASH_OUT: int
    transactionType_TRANSFER: int
    transactionType_PAYMENT: int
    channel_Atm: int = 0
    channel_Mobile: int = 0
    channel_Pos: int = 0
    channel_Web: int = 0
    kyc_verified_No: int = 0
    kyc_verified_Yes: int = 0

@app.get("/")
def root():
    return {"message": "🚀 Fraud Detection API is running successfully!"}

@app.post("/predict")
def predict_fraud(transaction: TransactionInput):
    input_dict = transaction.dict()

    #Feature engineering
    engineered = {
        "account_age_days": 0,
        "transaction_amount": input_dict["amount"],
        "hour": input_dict["step"] % 24,
        "weekday": (input_dict["step"] // 24) % 7,
        "month": (input_dict["step"] // (24*30)) % 12,
        "is_high_value": int(input_dict["amount"] > 5000),
        "transaction_amount_log": 0 if input_dict["amount"] <= 0 else np.log1p(input_dict["amount"]),
        "channel_Atm": input_dict.get("channel_Atm", 0),
        "channel_Mobile": input_dict.get("channel_Mobile", 0),
        "channel_Pos": input_dict.get("channel_Pos", 0),
        "channel_Web": input_dict.get("channel_Web", 0),
        "kyc_verified_No": input_dict.get("kyc_verified_No", 0),
        "kyc_verified_Yes": input_dict.get("kyc_verified_Yes", 0)
    }

    #Build DataFrame aligned to features.pkl
    df = pd.DataFrame([{f: engineered.get(f, 0) for f in features}])

    X_scaled = scaler.transform(df)

    pred = model.predict(X_scaled)[0]
    prob = model.predict_proba(X_scaled)[0][1]

    return {"fraud_prediction": int(pred), "fraud_probability": float(prob)}
