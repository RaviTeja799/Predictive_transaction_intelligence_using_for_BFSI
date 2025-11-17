"""Database CRUD operations"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging
import random
import os

logger = logging.getLogger(__name__)

# Global collection references (will be set after database initialization)
transactions_collection = None
predictions_collection = None
metrics_collection = None

# ==================== Mock Data Cache ====================
# Cache mock data to ensure consistency across API calls
_MOCK_DATA_CACHE = {
    "transactions": None,
    "fraud_stats": None,
    "channel_stats": None,
    "hourly_stats": None,
}

# Toggle for forcing mock data (default True for demo consistency)
USE_MOCK_DATA = os.getenv("USE_MOCK_DATA", "true").strip().lower() == "true"

# ==================== Mock Data Generators ====================

INDIAN_CITIES = ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Kolkata", "Pune", "Ahmedabad", "Jaipur", "Surat"]
CHANNELS = ["Mobile", "ATM", "Web", "POS"]
TRANSACTION_TYPES = ["Transfer", "Payment", "Withdrawal", "Purchase", "Deposit", "Bill Payment"]
MERCHANTS = [
    "Amazon India", "Flipkart", "BigBasket", "Swiggy", "Zomato", 
    "BookMyShow", "MakeMyTrip", "Uber India", "Ola", "PayTM Mall",
    "Reliance Digital", "DMart", "Pantaloons", "Shoppers Stop", "Westside"
]

def generate_mock_transactions(count: int = 100) -> List[Dict[str, Any]]:
    """Generate realistic mock transactions for Indian banking with dates Oct 30 - Nov 15"""
    transactions = []
    start_date = datetime(2024, 10, 30)
    end_date = datetime(2024, 11, 15)
    date_range = (end_date - start_date).days
    
    # Generate 8-12% fraud transactions
    fraud_count = random.randint(8, 12)
    fraud_indices = set(random.sample(range(count), fraud_count))
    
    for i in range(count):
        # Random date between Oct 30 and Nov 15
        days_offset = random.randint(0, date_range)
        hours_offset = random.randint(0, 23)
        minutes_offset = random.randint(0, 59)
        transaction_date = start_date + timedelta(days=days_offset, hours=hours_offset, minutes=minutes_offset)
        
        is_fraud = 1 if i in fraud_indices else 0
        
        # Fraud transactions tend to have higher amounts
        if is_fraud:
            amount = round(random.uniform(15000, 95000), 2)
        else:
            amount = round(random.uniform(100, 12000), 2)
        
        transaction = {
            "transaction_id": f"TXN{1000 + i}",
            "customer_id": f"CUST{random.randint(1000, 9999)}",
            "transaction_amount": amount,
            "channel": random.choice(CHANNELS),
            "location": random.choice(INDIAN_CITIES),
            "transaction_type": random.choice(TRANSACTION_TYPES),
            "merchant_name": random.choice(MERCHANTS),
            "timestamp": transaction_date.isoformat(),
            "is_fraud": is_fraud,
            "hour": transaction_date.hour,
            "created_at": transaction_date.isoformat(),
            "updated_at": transaction_date.isoformat()
        }
        transactions.append(transaction)
    
    # Sort by timestamp descending (most recent first)
    transactions.sort(key=lambda x: x["timestamp"], reverse=True)
    return transactions

def _get_mock_transactions(filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    if _MOCK_DATA_CACHE["transactions"] is None:
        logger.info("Generating and caching mock transaction data")
        _MOCK_DATA_CACHE["transactions"] = generate_mock_transactions(200)

    mock_data = _MOCK_DATA_CACHE["transactions"]

    if not filters:
        return mock_data

    filtered = mock_data
    if "is_fraud" in filters:
        filtered = [t for t in filtered if t["is_fraud"] == filters["is_fraud"]]
    if "channel" in filters:
        filtered = [t for t in filtered if t["channel"].lower() == filters["channel"].strip().lower()]
    return filtered

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
    # Always use mock data when enabled or when DB is empty
    if USE_MOCK_DATA:
        filtered = _get_mock_transactions(filters)
        return filtered[skip:skip + limit]

    from .config import get_database
    db = await get_database()
    collection = db["transactions"]
    
    # Check if database has transactions
    count = await collection.count_documents({})
    
    if count == 0:
        filtered = _get_mock_transactions(filters)
        return filtered[skip:skip + limit]
    
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
    if USE_MOCK_DATA:
        return len(_get_mock_transactions(filters))

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
    
    # Check if database has transactions
    count = await collection.count_documents({})
    
    # If no data in database or mock mode enabled, return cached mock statistics
    if USE_MOCK_DATA or count == 0:
        # Use cached statistics if available
        if _MOCK_DATA_CACHE["fraud_stats"] is None:
            # Use cached transactions if available, otherwise generate
            if _MOCK_DATA_CACHE["transactions"] is None:
                logger.info("Generating mock data for fraud statistics")
                _MOCK_DATA_CACHE["transactions"] = generate_mock_transactions(200)
            
            mock_transactions = _MOCK_DATA_CACHE["transactions"]
            fraud_count = sum(1 for t in mock_transactions if t["is_fraud"] == 1)
            legitimate_count = len(mock_transactions) - fraud_count
            
            fraud_amounts = [t["transaction_amount"] for t in mock_transactions if t["is_fraud"] == 1]
            legit_amounts = [t["transaction_amount"] for t in mock_transactions if t["is_fraud"] == 0]
            
            _MOCK_DATA_CACHE["fraud_stats"] = {
                "total": len(mock_transactions),
                "fraud_count": fraud_count,
                "legitimate_count": legitimate_count,
                "fraud_rate": round((fraud_count / len(mock_transactions)) * 100, 2),
                "avg_fraud_amount": round(sum(fraud_amounts) / len(fraud_amounts), 2) if fraud_amounts else 0.0,
                "avg_legitimate_amount": round(sum(legit_amounts) / len(legit_amounts), 2) if legit_amounts else 0.0
            }
            logger.info("Cached fraud statistics")
        else:
            logger.info("Returning cached fraud statistics")
        
        return _MOCK_DATA_CACHE["fraud_stats"]
    
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
    
    # Check if database has transactions
    count = await collection.count_documents({})
    
    # If no data in database or mock mode enabled, return cached mock channel statistics
    if USE_MOCK_DATA or count == 0:
        # Use cached statistics if available
        if _MOCK_DATA_CACHE["channel_stats"] is None:
            # Use cached transactions if available, otherwise generate
            if _MOCK_DATA_CACHE["transactions"] is None:
                logger.info("Generating mock data for channel statistics")
                _MOCK_DATA_CACHE["transactions"] = generate_mock_transactions(200)
            
            mock_transactions = _MOCK_DATA_CACHE["transactions"]
            
            # Group by channel
            channel_data = {}
            for t in mock_transactions:
                channel = t["channel"]
                if channel not in channel_data:
                    channel_data[channel] = {"total": 0, "fraud_count": 0, "amounts": []}
                
                channel_data[channel]["total"] += 1
                channel_data[channel]["amounts"].append(t["transaction_amount"])
                if t["is_fraud"] == 1:
                    channel_data[channel]["fraud_count"] += 1
            
            # Convert to list format
            result = []
            for channel, data in channel_data.items():
                result.append({
                    "channel": channel,
                    "total": data["total"],
                    "fraud_count": data["fraud_count"],
                    "fraud_rate": round((data["fraud_count"] / data["total"]) * 100, 2),
                    "avg_amount": round(sum(data["amounts"]) / len(data["amounts"]), 2)
                })
            
            # Sort by fraud_rate descending
            result.sort(key=lambda x: x["fraud_rate"], reverse=True)
            _MOCK_DATA_CACHE["channel_stats"] = result
            logger.info("Cached channel statistics")
        else:
            logger.info("Returning cached channel statistics")
        
        return _MOCK_DATA_CACHE["channel_stats"]
        result = []
        for channel, data in channel_data.items():
            result.append({
                "channel": channel,
                "total": data["total"],
                "fraud_count": data["fraud_count"],
                "fraud_rate": round((data["fraud_count"] / data["total"]) * 100, 2),
                "avg_amount": round(sum(data["amounts"]) / len(data["amounts"]), 2)
            })
        
        # Sort by fraud_rate descending
        result.sort(key=lambda x: x["fraud_rate"], reverse=True)
        return result
    
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
    if USE_MOCK_DATA:
        mock_transactions = _get_mock_transactions()
        hourly = {}
        for txn in mock_transactions:
            bucket = txn["hour"]
            if bucket not in hourly:
                hourly[bucket] = {"total": 0, "fraud": 0}
            hourly[bucket]["total"] += 1
            if txn["is_fraud"] == 1:
                hourly[bucket]["fraud"] += 1
        result = []
        for hour in range(24):
            bucket = hourly.get(hour, {"total": 0, "fraud": 0})
            total = bucket["total"] or 1  # avoid division by zero
            fraud_rate = round((bucket["fraud"] / total) * 100, 2) if bucket["total"] else 0
            result.append({
                "hour": hour,
                "total": bucket["total"],
                "fraud_count": bucket["fraud"],
                "fraud_rate": fraud_rate,
            })
        return result

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
