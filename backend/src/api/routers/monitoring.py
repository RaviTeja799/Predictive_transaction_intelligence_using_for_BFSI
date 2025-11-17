"""Real-time Monitoring API Router"""
from fastapi import APIRouter, Query
from typing import List, Optional
from datetime import datetime, timedelta
import random

router = APIRouter(prefix="/api/monitoring", tags=["Monitoring"])

@router.get("/alerts/stream")
async def get_alert_stream(limit: int = Query(20, le=100)):
    """Get real-time alert stream"""
    # Simulate real-time alerts
    alerts = []
    now = datetime.utcnow()
    
    for i in range(limit):
        alert_time = now - timedelta(minutes=random.randint(0, 120))
        alerts.append({
            "alert_id": f"ALT-{random.randint(10000, 99999)}",
            "transaction_id": f"TXN-{random.randint(100000, 999999)}",
            "type": random.choice(["High Risk", "Velocity", "Pattern Anomaly", "Amount Threshold"]),
            "severity": random.choice(["critical", "high", "medium", "low"]),
            "fraud_probability": round(random.uniform(0.6, 0.99), 2),
            "amount": round(random.uniform(5000, 150000), 2),
            "channel": random.choice(["Mobile", "Web", "ATM", "POS"]),
            "timestamp": alert_time.isoformat(),
            "status": random.choice(["new", "investigating", "resolved"]),
            "assigned_to": random.choice([None, "analyst_1", "analyst_2"])
        })
    
    return {
        "alerts": sorted(alerts, key=lambda x: x["timestamp"], reverse=True),
        "total": len(alerts),
        "updated_at": now.isoformat()
    }

@router.get("/system/health")
async def get_system_health():
    """Get system health metrics"""
    return {
        "status": "healthy",
        "services": {
            "api": {"status": "up", "latency_ms": 45},
            "database": {"status": "up", "latency_ms": 12},
            "model": {"status": "up", "latency_ms": 89},
            "cache": {"status": "up", "latency_ms": 3}
        },
        "resources": {
            "cpu_usage": round(random.uniform(20, 60), 1),
            "memory_usage": round(random.uniform(40, 70), 1),
            "disk_usage": round(random.uniform(30, 50), 1)
        },
        "throughput": {
            "requests_per_minute": random.randint(100, 500),
            "predictions_per_minute": random.randint(50, 200),
            "avg_response_time_ms": random.randint(80, 150)
        },
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/transactions/live")
async def get_live_transactions(limit: int = Query(15, le=50)):
    """Get live transaction feed"""
    transactions = []
    now = datetime.utcnow()
    
    for i in range(limit):
        tx_time = now - timedelta(seconds=random.randint(0, 300))
        is_fraud = random.random() < 0.15
        
        transactions.append({
            "transaction_id": f"TXN-{random.randint(100000, 999999)}",
            "customer_id": f"CUST-{random.randint(1000, 9999)}",
            "amount": round(random.uniform(100, 80000), 2),
            "channel": random.choice(["Mobile", "Web", "ATM", "POS"]),
            "fraud_score": round(random.uniform(0.7, 0.99), 2) if is_fraud else round(random.uniform(0.01, 0.3), 2),
            "risk_level": "High" if is_fraud else random.choice(["Low", "Medium"]),
            "status": "flagged" if is_fraud else "approved",
            "timestamp": tx_time.isoformat()
        })
    
    return {
        "transactions": sorted(transactions, key=lambda x: x["timestamp"], reverse=True),
        "total": len(transactions),
        "fraud_count": sum(1 for t in transactions if t["status"] == "flagged")
    }
