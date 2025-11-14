"""Database CRUD operations"""
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Global collection references (will be set after database initialization)
transactions_collection = None
predictions_collection = None
metrics_collection = None

def init_collections(db):
    """Initialize collection references"""
    global transactions_collection, predictions_collection, metrics_collection
    transactions_collection = db["transactions"]
    predictions_collection = db["predictions"]
    metrics_collection = db["model_metrics"]

# ==================== Transaction Operations ====================

async def create_transaction(transaction_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Insert a new transaction"""
    from .config import get_database
    db = await get_database()
    collection = db["transactions"]
    
    result = await collection.insert_one(transaction_dict)
    transaction_dict["_id"] = str(result.inserted_id)
    logger.info(f"Created transaction: {transaction_dict.get('transaction_id')}")
    return transaction_dict

async def get_transaction(transaction_id: str) -> Optional[Dict[str, Any]]:
    """Get transaction by ID"""
    from .config import get_database
    db = await get_database()
    collection = db["transactions"]
    
    transaction = await collection.find_one({"transaction_id": transaction_id})
    if transaction:
        transaction["_id"] = str(transaction["_id"])
    return transaction

async def get_transactions(
    skip: int = 0, 
    limit: int = 100, 
    filters: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """Get list of transactions with pagination and filters"""
    from .config import get_database
    db = await get_database()
    collection = db["transactions"]
    
    query = filters or {}
    cursor = collection.find(query).skip(skip).limit(limit).sort("timestamp", -1)
    transactions = await cursor.to_list(length=limit)
    
    for transaction in transactions:
        transaction["_id"] = str(transaction["_id"])
        # Convert datetime to ISO string for JSON serialization
        if isinstance(transaction.get("timestamp"), datetime):
            transaction["timestamp"] = transaction["timestamp"].isoformat()
        if isinstance(transaction.get("created_at"), datetime):
            transaction["created_at"] = transaction["created_at"].isoformat()
        if isinstance(transaction.get("updated_at"), datetime):
            transaction["updated_at"] = transaction["updated_at"].isoformat()
    
    return transactions

async def count_transactions(filters: Optional[Dict[str, Any]] = None) -> int:
    """Count transactions matching filters"""
    from .config import get_database
    db = await get_database()
    collection = db["transactions"]
    
    query = filters or {}
    return await collection.count_documents(query)

async def get_fraud_statistics() -> Dict[str, Any]:
    """Get fraud statistics from database"""
    from .config import get_database
    db = await get_database()
    collection = db["transactions"]
    
    pipeline = [
        {
            "$group": {
                "_id": "$is_fraud",
                "count": {"$sum": 1},
                "avg_amount": {"$avg": "$transaction_amount"}
            }
        }
    ]
    
    result = await collection.aggregate(pipeline).to_list(length=10)
    
    stats = {
        "total": 0,
        "fraud_count": 0,
        "legitimate_count": 0,
        "fraud_rate": 0.0,
        "avg_fraud_amount": 0.0,
        "avg_legitimate_amount": 0.0
    }
    
    for item in result:
        count = item["count"]
        stats["total"] += count
        
        if item["_id"] == 1:
            stats["fraud_count"] = count
            stats["avg_fraud_amount"] = round(item["avg_amount"], 2)
        else:
            stats["legitimate_count"] = count
            stats["avg_legitimate_amount"] = round(item["avg_amount"], 2)
    
    if stats["total"] > 0:
        stats["fraud_rate"] = round((stats["fraud_count"] / stats["total"]) * 100, 2)
    
    return stats

async def get_channel_statistics() -> List[Dict[str, Any]]:
    """Get fraud statistics by channel"""
    from .config import get_database
    db = await get_database()
    collection = db["transactions"]
    
    pipeline = [
        {
            "$group": {
                "_id": "$channel",
                "total": {"$sum": 1},
                "fraud_count": {
                    "$sum": {"$cond": [{"$eq": ["$is_fraud", 1]}, 1, 0]}
                },
                "avg_amount": {"$avg": "$transaction_amount"}
            }
        },
        {
            "$project": {
                "channel": "$_id",
                "total": 1,
                "fraud_count": 1,
                "fraud_rate": {
                    "$multiply": [
                        {"$divide": ["$fraud_count", "$total"]},
                        100
                    ]
                },
                "avg_amount": 1,
                "_id": 0
            }
        },
        {
            "$sort": {"fraud_rate": -1}
        }
    ]
    
    result = await collection.aggregate(pipeline).to_list(length=10)
    
    # Round numeric values
    for item in result:
        item["fraud_rate"] = round(item["fraud_rate"], 2)
        item["avg_amount"] = round(item["avg_amount"], 2)
    
    return result

async def get_hourly_statistics() -> List[Dict[str, Any]]:
    """Get fraud statistics by hour"""
    from .config import get_database
    db = await get_database()
    collection = db["transactions"]
    
    pipeline = [
        {
            "$group": {
                "_id": "$hour",
                "total": {"$sum": 1},
                "fraud_count": {
                    "$sum": {"$cond": [{"$eq": ["$is_fraud", 1]}, 1, 0]}
                }
            }
        },
        {
            "$project": {
                "hour": "$_id",
                "total": 1,
                "fraud_count": 1,
                "fraud_rate": {
                    "$multiply": [
                        {"$divide": ["$fraud_count", "$total"]},
                        100
                    ]
                },
                "_id": 0
            }
        },
        {
            "$sort": {"hour": 1}
        }
    ]
    
    result = await collection.aggregate(pipeline).to_list(length=24)
    
    for item in result:
        item["fraud_rate"] = round(item["fraud_rate"], 2)
    
    return result

# ==================== Prediction Operations ====================

async def create_prediction(prediction_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Store prediction result"""
    from .config import get_database
    db = await get_database()
    collection = db["predictions"]
    
    result = await collection.insert_one(prediction_dict)
    prediction_dict["_id"] = str(result.inserted_id)
    logger.info(f"Stored prediction for transaction: {prediction_dict.get('transaction_id')}")
    return prediction_dict

async def get_prediction(transaction_id: str) -> Optional[Dict[str, Any]]:
    """Get prediction for a transaction"""
    from .config import get_database
    db = await get_database()
    collection = db["predictions"]
    
    prediction = await collection.find_one({"transaction_id": transaction_id})
    if prediction:
        prediction["_id"] = str(prediction["_id"])
        if isinstance(prediction.get("predicted_at"), datetime):
            prediction["predicted_at"] = prediction["predicted_at"].isoformat()
    return prediction

async def get_recent_predictions(limit: int = 10) -> List[Dict[str, Any]]:
    """Get recent predictions"""
    from .config import get_database
    db = await get_database()
    collection = db["predictions"]
    
    cursor = collection.find().sort("predicted_at", -1).limit(limit)
    predictions = await cursor.to_list(length=limit)
    
    for prediction in predictions:
        prediction["_id"] = str(prediction["_id"])
        if isinstance(prediction.get("predicted_at"), datetime):
            prediction["predicted_at"] = prediction["predicted_at"].isoformat()
    
    return predictions

# ==================== Model Metrics Operations ====================

async def save_model_metrics(metrics_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Save model performance metrics"""
    from .config import get_database
    db = await get_database()
    collection = db["model_metrics"]
    
    result = await collection.insert_one(metrics_dict)
    metrics_dict["_id"] = str(result.inserted_id)
    logger.info(f"Saved metrics for model version: {metrics_dict.get('model_version')}")
    return metrics_dict

async def get_latest_model_metrics() -> Optional[Dict[str, Any]]:
    """Get latest model metrics"""
    from .config import get_database
    db = await get_database()
    collection = db["model_metrics"]
    
    metrics = await collection.find_one(sort=[("created_at", -1)])
    if metrics:
        metrics["_id"] = str(metrics["_id"])
        if isinstance(metrics.get("created_at"), datetime):
            metrics["created_at"] = metrics["created_at"].isoformat()
    return metrics

async def get_all_model_metrics() -> List[Dict[str, Any]]:
    """Get all model metrics history"""
    from .config import get_database
    db = await get_database()
    collection = db["model_metrics"]
    
    cursor = collection.find().sort("created_at", -1)
    metrics_list = await cursor.to_list(length=100)
    
    for metrics in metrics_list:
        metrics["_id"] = str(metrics["_id"])
        if isinstance(metrics.get("created_at"), datetime):
            metrics["created_at"] = metrics["created_at"].isoformat()
    
    return metrics_list
