#!/usr/bin/env python
"""
Backend Integration Test
Validates MongoDB connection, Gemini API, and FastAPI startup
"""

import asyncio
import os
from pathlib import Path
import sys

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

async def test_mongodb():
    """Test MongoDB Atlas connection"""
    print("\n=== Testing MongoDB Connection ===")
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        from dotenv import load_dotenv
        
        load_dotenv()
        mongo_uri = os.getenv("MONGO_URI")
        
        if not mongo_uri:
            print("❌ MONGO_URI not found in .env")
            return False
        
        client = AsyncIOMotorClient(mongo_uri)
        # Test connection
        await client.admin.command('ping')
        print("✅ MongoDB Atlas connection successful")
        
        # List databases
        db_list = await client.list_database_names()
        print(f"   Available databases: {db_list}")
        
        return True
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False

def test_gemini():
    """Test Gemini API configuration"""
    print("\n=== Testing Gemini API ===")
    try:
        from dotenv import load_dotenv
        import google.generativeai as genai
        
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        
        if not api_key:
            print("❌ GEMINI_API_KEY not found in .env")
            return False
        
        genai.configure(api_key=api_key)
        
        # List available models
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        print(f"✅ Gemini API configured successfully")
        print(f"   Available models: {models[:3]}...")
        
        return True
    except Exception as e:
        print(f"❌ Gemini API test failed: {e}")
        return False

def test_fastapi():
    """Test FastAPI import and router registration"""
    print("\n=== Testing FastAPI Setup ===")
    try:
        from src.api.main import app
        
        # Check registered routes
        routes = [route.path for route in app.routes if hasattr(route, 'path')]
        print(f"✅ FastAPI app loaded successfully")
        print(f"   Registered {len(routes)} routes")
        
        # Check for key API endpoints
        expected_routes = ['/predict', '/settings', '/cases', '/modeling', '/monitoring', '/simulation']
        missing = [r for r in expected_routes if not any(r in route for route in routes)]
        
        if missing:
            print(f"⚠️  Missing routes: {missing}")
        else:
            print("✅ All expected API routers registered")
        
        return True
    except Exception as e:
        print(f"❌ FastAPI setup test failed: {e}")
        return False

def test_model_loading():
    """Test ML model loading"""
    print("\n=== Testing Model Loading ===")
    try:
        import pickle
        from pathlib import Path
        
        model_path = backend_dir / "fraud_detection_model_xgboost.pkl"
        
        if not model_path.exists():
            print(f"❌ Model file not found: {model_path}")
            return False
        
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        
        print(f"✅ Model loaded successfully")
        print(f"   Model type: {type(model).__name__}")
        
        return True
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        return False

async def main():
    print("=" * 60)
    print("BACKEND INTEGRATION TEST SUITE")
    print("=" * 60)
    
    results = {
        "MongoDB": await test_mongodb(),
        "Gemini API": test_gemini(),
        "FastAPI": test_fastapi(),
        "Model Loading": test_model_loading(),
    }
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:<20} {status}")
    
    all_passed = all(results.values())
    print("\n" + ("=" * 60))
    if all_passed:
        print("🎉 ALL TESTS PASSED - Backend ready for deployment!")
    else:
        print("⚠️  SOME TESTS FAILED - Review errors above")
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
