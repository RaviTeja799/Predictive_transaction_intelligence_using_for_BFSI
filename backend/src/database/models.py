"""Pydantic models for database schemas"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Literal

class TransactionModel(BaseModel):
    """Transaction data model matching transactions_clean.csv structure"""
    transaction_id: str = Field(..., description="Unique transaction identifier")
    customer_id: str = Field(..., description="Customer identifier")
    timestamp: datetime = Field(..., description="Transaction timestamp")
    account_age_days: int = Field(..., ge=0, description="Account age in days")
    transaction_amount: float = Field(..., ge=0, description="Transaction amount")
    channel: Literal["Mobile", "Web", "ATM", "POS"] = Field(..., description="Transaction channel")
    kyc_verified: Literal["Yes", "No"] = Field(..., description="KYC verification status")
    is_fraud: int = Field(..., ge=0, le=1, description="Fraud label (0=legitimate, 1=fraud)")
    hour: int = Field(..., ge=0, le=23, description="Hour of transaction")
    weekday: int = Field(..., ge=0, le=6, description="Day of week (0=Monday)")
    month: int = Field(..., ge=1, le=12, description="Month of transaction")
    is_high_value: int = Field(..., ge=0, le=1, description="High value transaction flag")
    transaction_amount_log: float = Field(..., description="Log transformed amount")
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "transaction_id": "TXN001234",
                "customer_id": "C12345",
                "timestamp": "2024-01-15T10:30:00Z",
                "account_age_days": 365,
                "transaction_amount": 5000.00,
                "channel": "Mobile",
                "kyc_verified": "Yes",
                "is_fraud": 0,
                "hour": 10,
                "weekday": 1,
                "month": 1,
                "is_high_value": 1,
                "transaction_amount_log": 8.517
            }
        }

class PredictionModel(BaseModel):
    """Model prediction result"""
    transaction_id: str = Field(..., description="Transaction ID for the prediction")
    prediction: Literal["Fraud", "Legitimate"] = Field(..., description="Prediction result")
    fraud_probability: float = Field(..., ge=0, le=1, description="Probability of fraud")
    risk_level: Literal["Low", "Medium", "High"] = Field(..., description="Risk assessment level")
    model_version: str = Field(..., description="Model version used for prediction")
    predicted_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "transaction_id": "TXN001234",
                "prediction": "Fraud",
                "fraud_probability": 0.85,
                "risk_level": "High",
                "model_version": "1.0.0"
            }
        }

class ModelMetricsModel(BaseModel):
    """Model performance metrics"""
    model_version: str = Field(..., description="Model version identifier")
    accuracy: float = Field(..., ge=0, le=1, description="Model accuracy")
    precision: float = Field(..., ge=0, le=1, description="Model precision")
    recall: float = Field(..., ge=0, le=1, description="Model recall")
    f1_score: float = Field(..., ge=0, le=1, description="F1 score")
    roc_auc: float = Field(..., ge=0, le=1, description="ROC AUC score")
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "model_version": "1.0.0",
                "accuracy": 0.9534,
                "precision": 0.8912,
                "recall": 0.8756,
                "f1_score": 0.8833,
                "roc_auc": 0.92
            }
        }

class TransactionStats(BaseModel):
    """Transaction statistics response model"""
    total: int
    fraud_count: int
    legitimate_count: int
    fraud_rate: float
    avg_fraud_amount: float
    avg_legitimate_amount: float

class ChannelStats(BaseModel):
    """Channel statistics response model"""
    channel: str
    total: int
    fraud_count: int
    fraud_rate: float
    avg_amount: float
