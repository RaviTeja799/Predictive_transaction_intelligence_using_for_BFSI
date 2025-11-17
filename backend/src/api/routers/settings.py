"""Settings and Configuration API Router"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime

router = APIRouter(prefix="/api/settings", tags=["Settings"])

# In-memory settings store (replace with database in production)
SETTINGS_STORE: Dict[str, Any] = {
    "model_thresholds": {
        "high_risk_threshold": 0.7,
        "medium_risk_threshold": 0.4,
        "high_value_amount": 50000,
        "new_account_days": 30,
    },
    "notification_rules": {
        "email_enabled": True,
        "sms_enabled": False,
        "high_risk_immediate": True,
        "batch_digest": True,
        "digest_frequency": "daily",
    },
    "system_config": {
        "auto_block_threshold": 0.95,
        "manual_review_threshold": 0.7,
        "monitoring_enabled": True,
        "api_rate_limit": 1000,
    },
    "user_preferences": {
        "theme": "light",
        "notifications_enabled": True,
        "dashboard_refresh_interval": 30,
    }
}

class ModelThresholds(BaseModel):
    high_risk_threshold: float
    medium_risk_threshold: float
    high_value_amount: float
    new_account_days: int

class NotificationRules(BaseModel):
    email_enabled: bool
    sms_enabled: bool
    high_risk_immediate: bool
    batch_digest: bool
    digest_frequency: str

class SystemConfig(BaseModel):
    auto_block_threshold: float
    manual_review_threshold: float
    monitoring_enabled: bool
    api_rate_limit: int

class UserPreferences(BaseModel):
    theme: str
    notifications_enabled: bool
    dashboard_refresh_interval: int

@router.get("/all")
async def get_all_settings():
    """Get all system settings"""
    return {
        "settings": SETTINGS_STORE,
        "last_updated": datetime.utcnow().isoformat()
    }

@router.get("/model-thresholds")
async def get_model_thresholds():
    """Get model threshold settings"""
    return SETTINGS_STORE["model_thresholds"]

@router.put("/model-thresholds")
async def update_model_thresholds(thresholds: ModelThresholds):
    """Update model threshold settings"""
    SETTINGS_STORE["model_thresholds"] = thresholds.dict()
    return {
        "message": "Model thresholds updated successfully",
        "settings": SETTINGS_STORE["model_thresholds"]
    }

@router.get("/notification-rules")
async def get_notification_rules():
    """Get notification rules"""
    return SETTINGS_STORE["notification_rules"]

@router.put("/notification-rules")
async def update_notification_rules(rules: NotificationRules):
    """Update notification rules"""
    SETTINGS_STORE["notification_rules"] = rules.dict()
    return {
        "message": "Notification rules updated successfully",
        "settings": SETTINGS_STORE["notification_rules"]
    }

@router.get("/system-config")
async def get_system_config():
    """Get system configuration"""
    return SETTINGS_STORE["system_config"]

@router.put("/system-config")
async def update_system_config(config: SystemConfig):
    """Update system configuration"""
    SETTINGS_STORE["system_config"] = config.dict()
    return {
        "message": "System config updated successfully",
        "settings": SETTINGS_STORE["system_config"]
    }

@router.get("/user-preferences")
async def get_user_preferences():
    """Get user preferences"""
    return SETTINGS_STORE["user_preferences"]

@router.put("/user-preferences")
async def update_user_preferences(prefs: UserPreferences):
    """Update user preferences"""
    SETTINGS_STORE["user_preferences"] = prefs.dict()
    return {
        "message": "User preferences updated successfully",
        "settings": SETTINGS_STORE["user_preferences"]
    }
