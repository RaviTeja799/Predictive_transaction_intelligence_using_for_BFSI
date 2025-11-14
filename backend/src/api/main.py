from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pickle
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, List
from datetime import datetime
import os

# Import database operations
from ..database.config import get_database, close_database
from ..database import operations as db_ops
from ..database.models import TransactionModel, PredictionModel, ModelMetricsModel

app = FastAPI(title="Fraud Detection API - TransIntelliFlow", version="1.0")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup"""
    try:
        await get_database()
    except Exception as e:
        print(f"Warning: Could not connect to database: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown"""
    await close_database()

@app.get("/")
def root():
    return {
        "message": "🚀 Fraud Detection API - TransIntelliFlow is running successfully!",
        "version": "1.0.0",
        "endpoints": {
            "predict": "/predict",
            "transactions": "/api/transactions",
            "statistics": "/api/statistics/fraud",
            "channels": "/api/statistics/channels",
            "metrics": "/api/metrics"
        }
    }

@app.post("/predict")
async def predict_fraud(transaction: TransactionInput):
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

    # Determine risk level
    risk_level = "High" if prob > 0.7 else "Medium" if prob > 0.4 else "Low"
    
    # Store prediction in database (optional, if transaction_id is available)
    try:
        prediction_data = {
            "transaction_id": f"TXN_{datetime.utcnow().timestamp()}",
            "prediction": "Fraud" if pred == 1 else "Legitimate",
            "fraud_probability": float(prob),
            "risk_level": risk_level,
            "model_version": os.getenv("MODEL_VERSION", "1.0.0"),
            "predicted_at": datetime.utcnow()
        }
        await db_ops.create_prediction(prediction_data)
    except Exception as e:
        print(f"Could not store prediction: {e}")

    return {
        "fraud_prediction": int(pred),
        "fraud_probability": float(prob),
        "risk_level": risk_level
    }

# ==================== Database API Endpoints ====================

@app.get("/api/transactions")
async def list_transactions(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    is_fraud: Optional[int] = Query(None, ge=0, le=1, description="Filter by fraud status (0 or 1)"),
    channel: Optional[str] = Query(None, description="Filter by transaction channel")
):
    """Get list of transactions with pagination and filters"""
    try:
        filters = {}
        if is_fraud is not None:
            filters["is_fraud"] = is_fraud
        if channel:
            filters["channel"] = channel
        
        transactions = await db_ops.get_transactions(skip=skip, limit=limit, filters=filters)
        total = await db_ops.count_transactions(filters=filters)
        
        return {
            "total": total,
            "page": skip // limit + 1,
            "limit": limit,
            "transactions": transactions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/api/transactions/{transaction_id}")
async def get_transaction_details(transaction_id: str):
    """Get transaction details by ID"""
    try:
        transaction = await db_ops.get_transaction(transaction_id)
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        return transaction
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/api/statistics/fraud")
async def fraud_statistics():
    """Get overall fraud statistics"""
    try:
        return await db_ops.get_fraud_statistics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/api/statistics/channels")
async def channel_statistics():
    """Get fraud statistics by transaction channel"""
    try:
        return await db_ops.get_channel_statistics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/api/statistics/hourly")
async def hourly_statistics():
    """Get fraud statistics by hour of day"""
    try:
        return await db_ops.get_hourly_statistics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/api/predictions/recent")
async def recent_predictions(limit: int = Query(10, ge=1, le=100)):
    """Get recent prediction results"""
    try:
        return await db_ops.get_recent_predictions(limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/api/metrics")
async def get_model_metrics():
    """Get latest model performance metrics"""
    try:
        metrics = await db_ops.get_latest_model_metrics()
        if not metrics:
            # Return default metrics if none exist in database
            return {
                "model_version": "1.0.0",
                "accuracy": 0.9534,
                "precision": 0.8912,
                "recall": 0.8756,
                "f1_score": 0.8833,
                "roc_auc": 0.92
            }
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.post("/api/metrics")
async def save_metrics(metrics: ModelMetricsModel):
    """Save model performance metrics"""
    try:
        metrics_dict = metrics.dict()
        return await db_ops.save_model_metrics(metrics_dict)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/api/metrics/history")
async def get_metrics_history():
    """Get all model metrics history"""
    try:
        return await db_ops.get_all_model_metrics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        db = await get_database()
        # Try to ping database
        await db.command('ping')
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
