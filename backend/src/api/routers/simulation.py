"""Batch Simulation API Router"""
from collections import deque
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime
import asyncio
import random

router = APIRouter(prefix="/api/simulation", tags=["Simulation"])

SIMULATION_BUFFER_LIMIT = 500
SIMULATION_BUFFER: deque[Dict[str, Any]] = deque(maxlen=SIMULATION_BUFFER_LIMIT)

INDIAN_CITIES = [
    "Mumbai",
    "Delhi",
    "Bangalore",
    "Hyderabad",
    "Chennai",
    "Kolkata",
    "Pune",
    "Ahmedabad",
    "Jaipur",
    "Surat",
]

class SimulationRequest(BaseModel):
    batch_size: int
    concurrency: int
    transactions: List[Dict[str, Any]]


@router.get("/overlay")
async def get_simulation_overlay(limit: int = SIMULATION_BUFFER_LIMIT):
    """Return the latest simulation results for dashboard overlays."""
    if limit <= 0 or limit > SIMULATION_BUFFER_LIMIT:
        limit = SIMULATION_BUFFER_LIMIT

    snapshot = list(SIMULATION_BUFFER)[-limit:]
    total = len(snapshot)
    fraud_count = sum(1 for entry in snapshot if entry.get("is_fraud"))
    fraud_rate = round((fraud_count / total) * 100, 2) if total else 0.0
    last_updated = snapshot[-1]["timestamp"] if snapshot else None

    return {
        "total": total,
        "fraud_count": fraud_count,
        "fraud_rate": fraud_rate,
        "last_updated": last_updated,
        "transactions": snapshot,
        "channel_summary": _build_channel_summary(snapshot),
    }

@router.post("/batch")
async def run_batch_simulation(request: SimulationRequest):
    """Run batch simulation with controlled concurrency"""
    results = []
    start_time = datetime.utcnow()
    
    # Process in chunks
    for i in range(0, len(request.transactions), request.concurrency):
        chunk = request.transactions[i:i + request.concurrency]
        
        # Process chunk concurrently
        chunk_results = await asyncio.gather(*[
            process_single_transaction(txn) for txn in chunk
        ])
        
        results.extend(chunk_results)

    _enforce_target_fraud_ratio(results)
    _update_simulation_overlay(results)
    
    end_time = datetime.utcnow()
    processing_time = (end_time - start_time).total_seconds()
    
    fraud_count = sum(1 for r in results if r["prediction"] == "Fraud")
    avg_probability = sum(r["fraud_probability"] for r in results) / len(results) if results else 0
    
    return {
        "simulation_id": f"SIM-{int(start_time.timestamp())}",
        "total_processed": len(results),
        "fraudulent_count": fraud_count,
        "fraud_rate": (fraud_count / len(results) * 100) if results else 0,
        "avg_fraud_probability": round(avg_probability * 100, 2),
        "processing_time_seconds": round(processing_time, 2),
        "throughput_per_second": round(len(results) / processing_time, 2) if processing_time > 0 else 0,
        "results": results
    }

async def process_single_transaction(txn_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process a single transaction"""
    from ..main import (
        _prepare_enhanced_features,
        _run_model_prediction,
        _derive_risk_factors,
        _apply_demo_boost,
        EnhancedPredictionInput,
    )
    
    try:
        transaction = EnhancedPredictionInput(**txn_data)
        engineered = _prepare_enhanced_features(transaction)
        prediction = _run_model_prediction(engineered)
        risk_factors = _derive_risk_factors(
            transaction.transaction_amount,
            transaction.account_age_days,
            transaction.hour,
            transaction.kyc_verified,
            transaction.channel,
        )
        raw_prediction = prediction["prediction"]
        raw_probability = prediction["fraud_probability"]
        prediction = _apply_demo_boost(prediction, risk_factors)
        demo_boosted = prediction["prediction"] == 1 and raw_prediction == 0
        
        location = txn_data.get("location") or random.choice(INDIAN_CITIES)
        timestamp = txn_data.get("timestamp") or datetime.utcnow().isoformat()
        return {
            "transaction_id": transaction.customer_id,
            "customer_id": transaction.customer_id,
            "prediction": "Fraud" if prediction["prediction"] == 1 else "Legitimate",
            "is_fraud": 1 if prediction["prediction"] == 1 else 0,
            "fraud_probability": prediction["fraud_probability"],
            "risk_level": prediction["risk_level"],
            "confidence": prediction["confidence"],
            "risk_factors": risk_factors,
            "risk_factor_count": len(risk_factors),
            "raw_model_prediction": "Fraud" if raw_prediction == 1 else "Legitimate",
            "raw_model_probability": raw_probability,
            "demo_boosted": demo_boosted,
            "simulation_override": False,
            "transaction_amount": transaction.transaction_amount,
            "channel": transaction.channel,
            "hour": transaction.hour,
            "account_age_days": transaction.account_age_days,
            "kyc_verified": transaction.kyc_verified,
            "location": location,
            "timestamp": timestamp,
        }
    except Exception as e:
        return {
            "transaction_id": txn_data.get("customer_id", "unknown"),
            "error": str(e),
            "prediction": "Error",
            "fraud_probability": 0,
            "risk_level": "Unknown",
            "confidence": 0
        }


def _enforce_target_fraud_ratio(results: List[Dict[str, Any]]) -> None:
    """Ensure batches surface roughly 9-15% fraud by overriding low-signal entries."""
    if not results:
        return

    total = len(results)
    if total == 0:
        return

    lower_bound = max(1, int(round(total * 0.09)))
    upper_bound = max(lower_bound, int(round(total * 0.15)))
    lower_bound = min(lower_bound, total)
    upper_bound = min(max(upper_bound, lower_bound), total)

    if upper_bound == 0:
        return

    target_fraud = random.randint(lower_bound, upper_bound)
    current_fraud = sum(1 for r in results if r.get("prediction") == "Fraud")

    if current_fraud < target_fraud:
        deficit = target_fraud - current_fraud
        candidates = [r for r in results if r.get("prediction") == "Legitimate"]
        candidates.sort(
            key=lambda r: (
                r.get("risk_factor_count", 0),
                r.get("raw_model_probability", 0.0)
            ),
            reverse=True,
        )
        for entry in candidates[:deficit]:
            entry["prediction"] = "Fraud"
            entry["fraud_probability"] = min(
                0.97,
                max(entry.get("fraud_probability", 0.5), entry.get("raw_model_probability", 0.2) + 0.2),
            )
            entry["risk_level"] = _label_from_probability(entry["fraud_probability"])
            entry["confidence"] = round(entry["fraud_probability"] * 100, 2)
            entry.setdefault("risk_factors", []).append("Simulation anomaly injection")
            entry["simulation_override"] = True
            entry["is_fraud"] = 1
    elif current_fraud > target_fraud:
        surplus = current_fraud - target_fraud
        candidates = [r for r in results if r.get("prediction") == "Fraud"]
        candidates.sort(
            key=lambda r: (
                0 if r.get("simulation_override") else 1,
                r.get("raw_model_probability", 0.0)
            )
        )
        for entry in candidates[:surplus]:
            entry["prediction"] = "Legitimate"
            entry["fraud_probability"] = min(entry.get("raw_model_probability", 0.1), 0.35)
            entry["risk_level"] = _label_from_probability(entry["fraud_probability"])
            entry["confidence"] = round(entry["fraud_probability"] * 100, 2)
            entry.setdefault("risk_factors", []).append("Simulation normalization")
            entry["simulation_override"] = True
            entry["is_fraud"] = 0


def _label_from_probability(probability: float) -> str:
    if probability > 0.7:
        return "High"
    if probability > 0.4:
        return "Medium"
    return "Low"


def _update_simulation_overlay(results: List[Dict[str, Any]]) -> None:
    """Store the latest batch results in a rolling buffer for dashboard overlays."""
    if not results:
        return

    for entry in results:
        overlay_entry = {
            "transaction_id": entry.get("transaction_id"),
            "customer_id": entry.get("customer_id") or entry.get("transaction_id"),
            "transaction_amount": entry.get("transaction_amount", 0.0),
            "channel": entry.get("channel", "Mobile"),
            "location": entry.get("location") or random.choice(INDIAN_CITIES),
            "hour": entry.get("hour", datetime.utcnow().hour),
            "timestamp": entry.get("timestamp") or datetime.utcnow().isoformat(),
            "kyc_verified": entry.get("kyc_verified", "No"),
            "account_age_days": entry.get("account_age_days", 0),
            "prediction": entry.get("prediction", "Legitimate"),
            "is_fraud": entry.get("is_fraud", 0),
            "fraud_probability": entry.get("fraud_probability", 0.0),
            "risk_level": entry.get("risk_level", "Low"),
            "simulation_override": entry.get("simulation_override", False),
            "demo_boosted": entry.get("demo_boosted", False),
        }
        SIMULATION_BUFFER.append(overlay_entry)


def _build_channel_summary(entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not entries:
        return []

    summary: Dict[str, Dict[str, Any]] = {}
    for entry in entries:
        channel = entry.get("channel", "Unknown")
        stats = summary.setdefault(channel, {
            "channel": channel,
            "total": 0,
            "fraud_count": 0,
            "amount_sum": 0.0,
        })
        stats["total"] += 1
        stats["amount_sum"] += entry.get("transaction_amount", 0.0)
        if entry.get("is_fraud"):
            stats["fraud_count"] += 1

    response = []
    for stats in summary.values():
        total = stats["total"]
        fraud_count = stats["fraud_count"]
        avg_amount = stats["amount_sum"] / total if total else 0.0
        response.append({
            "channel": stats["channel"],
            "total": total,
            "fraud_count": fraud_count,
            "fraud_rate": round((fraud_count / total) * 100, 2) if total else 0.0,
            "avg_amount": round(avg_amount, 2),
        })

    response.sort(key=lambda item: item["fraud_rate"], reverse=True)
    return response
