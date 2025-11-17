"""Case Management API Router"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from uuid import uuid4

router = APIRouter(prefix="/api/cases", tags=["Cases"])

# In-memory case store
CASES_STORE: List[dict] = []

class CaseCreate(BaseModel):
    title: str
    description: str
    priority: str  # high, medium, low
    transaction_ids: List[str]
    assigned_to: Optional[str] = None

class CaseUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    notes: Optional[str] = None
    assigned_to: Optional[str] = None

@router.get("")
async def list_cases(
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 50
):
    """List all fraud investigation cases"""
    filtered = CASES_STORE
    
    if status:
        filtered = [c for c in filtered if c.get("status") == status]
    if priority:
        filtered = [c for c in filtered if c.get("priority") == priority]
    
    return {
        "total": len(filtered),
        "cases": filtered[skip:skip + limit]
    }

@router.post("")
async def create_case(case: CaseCreate):
    """Create a new fraud investigation case"""
    case_id = f"CASE-{uuid4().hex[:8].upper()}"
    new_case = {
        "case_id": case_id,
        "title": case.title,
        "description": case.description,
        "priority": case.priority,
        "status": "open",
        "transaction_ids": case.transaction_ids,
        "transaction_count": len(case.transaction_ids),
        "total_amount": 0,  # Calculate from transactions
        "assigned_to": case.assigned_to,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "notes": []
    }
    CASES_STORE.append(new_case)
    return new_case

@router.get("/{case_id}")
async def get_case(case_id: str):
    """Get case details"""
    case = next((c for c in CASES_STORE if c["case_id"] == case_id), None)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case

@router.put("/{case_id}")
async def update_case(case_id: str, update: CaseUpdate):
    """Update case status and details"""
    case = next((c for c in CASES_STORE if c["case_id"] == case_id), None)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    if update.status:
        case["status"] = update.status
    if update.priority:
        case["priority"] = update.priority
    if update.assigned_to:
        case["assigned_to"] = update.assigned_to
    if update.notes:
        case["notes"].append({
            "text": update.notes,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    case["updated_at"] = datetime.utcnow().isoformat()
    return case

@router.get("/{case_id}/recommendations")
async def get_case_recommendations(case_id: str):
    """Get AI-powered investigation recommendations"""
    from ...utils.gemini_client import generate_case_recommendations
    
    case = next((c for c in CASES_STORE if c["case_id"] == case_id), None)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    recommendations = await generate_case_recommendations(case)
    return recommendations
