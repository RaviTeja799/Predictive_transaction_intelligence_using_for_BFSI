"""
Script to import transactions_clean.csv into MongoDB Atlas
Run this script to populate the database with historical transaction data
"""
import pandas as pd
import numpy as np
from pymongo import MongoClient, ASCENDING, DESCENDING
from datetime import datetime, timedelta
from pathlib import Path
import logging
import sys
import os

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# MongoDB Configuration
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "fraud_detection_db")

def create_indexes(db):
    """Create database indexes for better query performance"""
    logger.info("Creating indexes...")
    
    # Transactions collection indexes
    db.transactions.create_index([("transaction_id", ASCENDING)], unique=True)
    db.transactions.create_index([("customer_id", ASCENDING)])
    db.transactions.create_index([("timestamp", DESCENDING)])
    db.transactions.create_index([("is_fraud", ASCENDING)])
    db.transactions.create_index([("channel", ASCENDING)])
    db.transactions.create_index([("kyc_verified", ASCENDING)])
    db.transactions.create_index([("hour", ASCENDING)])
    db.transactions.create_index([("weekday", ASCENDING)])
    
    # Compound indexes for common queries
    db.transactions.create_index([("is_fraud", ASCENDING), ("channel", ASCENDING)])
    db.transactions.create_index([("customer_id", ASCENDING), ("timestamp", DESCENDING)])
    
    # Predictions collection indexes
    db.predictions.create_index([("transaction_id", ASCENDING)], unique=True)
    db.predictions.create_index([("predicted_at", DESCENDING)])
    db.predictions.create_index([("risk_level", ASCENDING)])
    
    # Model metrics collection indexes
    db.model_metrics.create_index([("model_version", ASCENDING)])
    db.model_metrics.create_index([("created_at", DESCENDING)])
    
    logger.info("✅ Indexes created successfully")

def generate_transaction_id(index, prefix="TXN"):
    """Generate unique transaction ID"""
    return f"{prefix}{str(index).zfill(8)}"

def generate_customer_id(index, prefix="C"):
    """Generate customer ID"""
    return f"{prefix}{str(index).zfill(6)}"

def parse_timestamp(row, base_date=None):
    """Parse or generate timestamp from row data"""
    if base_date is None:
        base_date = datetime(2024, 1, 1)
    
    # If timestamp column exists
    if 'timestamp' in row and pd.notna(row['timestamp']):
        try:
            return pd.to_datetime(row['timestamp'])
        except:
            pass
    
    # Generate from hour, weekday, month if available
    hour = int(row.get('hour', 0))
    weekday = int(row.get('weekday', 0))
    month = int(row.get('month', 1))
    
    # Calculate days offset based on weekday and month
    days_offset = weekday + (month - 1) * 30
    timestamp = base_date + timedelta(days=days_offset, hours=hour)
    
    return timestamp

def import_transactions_from_csv(csv_path: str, batch_size: int = 1000):
    """Import transactions from CSV to MongoDB"""
    logger.info(f"📂 Loading CSV from {csv_path}")
    
    # Check if file exists
    if not Path(csv_path).exists():
        logger.error(f"❌ CSV file not found: {csv_path}")
        return False
    
    # Connect to MongoDB
    logger.info(f"🔌 Connecting to MongoDB Atlas...")
    try:
        client = MongoClient(MONGODB_URL, serverSelectionTimeoutMS=5000)
        # Test connection
        client.admin.command('ping')
        logger.info("✅ Successfully connected to MongoDB Atlas")
    except Exception as e:
        logger.error(f"❌ Failed to connect to MongoDB: {e}")
        return False
    
    db = client[DATABASE_NAME]
    
    # Load CSV
    try:
        df = pd.read_csv(csv_path)
        logger.info(f"📊 Loaded {len(df)} transactions from CSV")
        logger.info(f"📋 Columns: {list(df.columns)}")
    except Exception as e:
        logger.error(f"❌ Failed to load CSV: {e}")
        return False
    
    # Display sample data
    logger.info(f"\n📝 Sample data:\n{df.head(3)}")
    
    # Clean and prepare data
    transactions = []
    base_date = datetime(2024, 1, 1)
    
    for idx, row in df.iterrows():
        try:
            # Generate IDs if not present
            transaction_id = str(row.get('transaction_id', generate_transaction_id(idx)))
            customer_id = str(row.get('customer_id', generate_customer_id(idx % 10000)))
            
            # Parse timestamp
            timestamp = parse_timestamp(row, base_date)
            
            # Build transaction document
            transaction = {
                "transaction_id": transaction_id,
                "customer_id": customer_id,
                "timestamp": timestamp,
                "account_age_days": int(row.get('account_age_days', 0)),
                "transaction_amount": float(row.get('transaction_amount', 0.0)),
                "channel": str(row.get('channel', 'Unknown')),
                "kyc_verified": str(row.get('kyc_verified', 'No')),
                "is_fraud": int(row.get('is_fraud', 0)),
                "hour": int(row.get('hour', 0)),
                "weekday": int(row.get('weekday', 0)),
                "month": int(row.get('month', 1)),
                "is_high_value": int(row.get('is_high_value', 0)),
                "transaction_amount_log": float(row.get('transaction_amount_log', 0.0)),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            transactions.append(transaction)
            
        except Exception as e:
            logger.warning(f"⚠️  Skipping row {idx} due to error: {e}")
            continue
    
    if not transactions:
        logger.error("❌ No valid transactions to import")
        return False
    
    logger.info(f"✅ Prepared {len(transactions)} transactions for import")
    
    # Clear existing data
    logger.info("🗑️  Clearing existing transactions...")
    db.transactions.delete_many({})
    
    # Insert in batches
    logger.info(f"💾 Inserting transactions in batches of {batch_size}...")
    
    total_inserted = 0
    for i in range(0, len(transactions), batch_size):
        batch = transactions[i:i + batch_size]
        try:
            result = db.transactions.insert_many(batch, ordered=False)
            total_inserted += len(result.inserted_ids)
            logger.info(f"   Batch {i//batch_size + 1}: Inserted {len(batch)} transactions")
        except Exception as e:
            logger.error(f"⚠️  Error in batch {i//batch_size + 1}: {e}")
            # Continue with next batch
    
    logger.info(f"✅ Successfully imported {total_inserted} transactions")
    
    # Create indexes
    create_indexes(db)
    
    # Print statistics
    stats = {
        "total": db.transactions.count_documents({}),
        "fraud": db.transactions.count_documents({"is_fraud": 1}),
        "legitimate": db.transactions.count_documents({"is_fraud": 0})
    }
    
    logger.info(f"\n📊 Database Statistics:")
    logger.info(f"   Total transactions: {stats['total']}")
    logger.info(f"   Fraud transactions: {stats['fraud']}")
    logger.info(f"   Legitimate transactions: {stats['legitimate']}")
    
    if stats['total'] > 0:
        fraud_rate = (stats['fraud'] / stats['total'] * 100)
        logger.info(f"   Fraud rate: {fraud_rate:.2f}%")
    
    # Channel statistics
    logger.info(f"\n📱 Channel Statistics:")
    channels = db.transactions.aggregate([
        {"$group": {"_id": "$channel", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ])
    
    for channel in channels:
        logger.info(f"   {channel['_id']}: {channel['count']} transactions")
    
    client.close()
    logger.info("\n✅ Import completed successfully!")
    return True

def insert_sample_model_metrics(db):
    """Insert sample model metrics"""
    logger.info("📊 Inserting sample model metrics...")
    
    metrics = {
        "model_version": "1.0.0",
        "accuracy": 0.9534,
        "precision": 0.8912,
        "recall": 0.8756,
        "f1_score": 0.8833,
        "roc_auc": 0.92,
        "created_at": datetime.utcnow()
    }
    
    db.model_metrics.insert_one(metrics)
    logger.info("✅ Sample model metrics inserted")

if __name__ == "__main__":
    # CSV file paths to try
    csv_paths = [
        "backend/data/raw/transactions_clean.csv",
        "backend/data/processed/transactions_clean.csv",
        "data/raw/transactions_clean.csv",
        "data/processed/transactions_clean.csv",
    ]
    
    csv_path = None
    for path in csv_paths:
        if Path(path).exists():
            csv_path = path
            break
    
    if csv_path is None:
        logger.error("❌ Could not find transactions_clean.csv in any of the expected locations:")
        for path in csv_paths:
            logger.error(f"   - {path}")
        sys.exit(1)
    
    # Import data
    success = import_transactions_from_csv(csv_path)
    
    if success:
        # Insert sample model metrics
        client = MongoClient(MONGODB_URL)
        db = client[DATABASE_NAME]
        insert_sample_model_metrics(db)
        client.close()
        
        logger.info("\n🎉 Database setup completed successfully!")
        logger.info(f"🔗 Database: {DATABASE_NAME}")
        logger.info(f"🌐 You can now start the API server with: uvicorn src.api.main:app --reload")
    else:
        logger.error("\n❌ Database setup failed!")
        sys.exit(1)
