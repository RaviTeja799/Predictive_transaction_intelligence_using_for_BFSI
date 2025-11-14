"""Database package for MongoDB operations"""
from .config import get_database, close_database
from .models import TransactionModel, PredictionModel, ModelMetricsModel
from .operations import (
    create_transaction,
    get_transaction,
    get_transactions,
    count_transactions,
    get_fraud_statistics,
    get_channel_statistics,
    create_prediction,
    get_prediction,
    save_model_metrics,
    get_latest_model_metrics
)

__all__ = [
    "get_database",
    "close_database",
    "TransactionModel",
    "PredictionModel",
    "ModelMetricsModel",
    "create_transaction",
    "get_transaction",
    "get_transactions",
    "count_transactions",
    "get_fraud_statistics",
    "get_channel_statistics",
    "create_prediction",
    "get_prediction",
    "save_model_metrics",
    "get_latest_model_metrics"
]
