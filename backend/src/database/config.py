"""MongoDB Database Configuration"""
import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# MongoDB Configuration
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "fraud_detection_db")

# Async client for FastAPI
async_client = None
async_db = None

# Sync client for scripts
sync_client = None
sync_db = None

def get_sync_database():
    """Get synchronous database instance for scripts"""
    global sync_client, sync_db
    
    if sync_client is None:
        logger.info(f"Connecting to MongoDB at {MONGODB_URL}")
        sync_client = MongoClient(MONGODB_URL)
        sync_db = sync_client[DATABASE_NAME]
        logger.info(f"Connected to database: {DATABASE_NAME}")
    
    return sync_db

async def get_database():
    """Get async database instance for FastAPI"""
    global async_client, async_db
    
    if async_client is None:
        logger.info(f"Connecting to MongoDB Atlas at {MONGODB_URL[:50]}...")
        async_client = AsyncIOMotorClient(MONGODB_URL)
        async_db = async_client[DATABASE_NAME]
        
        # Test connection
        try:
            await async_client.admin.command('ping')
            logger.info(f"✅ Successfully connected to MongoDB Atlas database: {DATABASE_NAME}")
        except Exception as e:
            logger.error(f"❌ Failed to connect to MongoDB: {e}")
            raise
    
    return async_db

async def close_database():
    """Close async database connection"""
    global async_client
    
    if async_client:
        async_client.close()
        logger.info("MongoDB connection closed")
        async_client = None

def close_sync_database():
    """Close sync database connection"""
    global sync_client
    
    if sync_client:
        sync_client.close()
        logger.info("MongoDB sync connection closed")
        sync_client = None

# Collection references (accessed after database initialization)
def get_collections():
    """Get collection references"""
    if async_db is None:
        raise Exception("Database not initialized. Call get_database() first.")
    
    return {
        "transactions": async_db["transactions"],
        "predictions": async_db["predictions"],
        "metrics": async_db["model_metrics"]
    }

def get_sync_collections():
    """Get sync collection references"""
    db = get_sync_database()
    
    return {
        "transactions": db["transactions"],
        "predictions": db["predictions"],
        "metrics": db["model_metrics"]
    }
