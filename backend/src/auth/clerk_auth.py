"""
Clerk Authentication Middleware for FastAPI

This module provides JWT verification for Clerk authentication.
It validates tokens from the frontend and extracts user information.
"""

import os
import jwt
import httpx
from functools import lru_cache
from typing import Optional, Dict, Any
from fastapi import HTTPException, Depends, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Clerk Configuration
CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY", "")
CLERK_PUBLISHABLE_KEY = os.getenv("CLERK_PUBLISHABLE_KEY", "")
CLERK_JWKS_URL = os.getenv("CLERK_JWKS_URL", "")

# Security scheme
security = HTTPBearer(auto_error=False)


class ClerkUser(BaseModel):
    """Represents an authenticated Clerk user"""
    user_id: str
    email: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    image_url: Optional[str] = None
    role: str = "User"
    metadata: Dict[str, Any] = {}
    
    @property
    def is_admin(self) -> bool:
        return self.role in ["Admin", "Administrator"]
    
    @property
    def is_analyst(self) -> bool:
        return self.role in ["Analyst", "Admin", "Administrator"]


class ClerkJWKSClient:
    """Client for fetching and caching Clerk's JWKS"""
    
    def __init__(self, jwks_url: str):
        self.jwks_url = jwks_url
        self._jwks_cache: Optional[Dict] = None
        self._cache_time: Optional[datetime] = None
        self._cache_duration = 3600  # 1 hour
    
    async def get_signing_key(self, kid: str) -> Optional[str]:
        """Get the signing key for a given key ID"""
        jwks = await self._get_jwks()
        if not jwks:
            return None
        
        for key in jwks.get("keys", []):
            if key.get("kid") == kid:
                return key
        return None
    
    async def _get_jwks(self) -> Optional[Dict]:
        """Fetch JWKS from Clerk, with caching"""
        now = datetime.now()
        
        # Check cache
        if self._jwks_cache and self._cache_time:
            if (now - self._cache_time).seconds < self._cache_duration:
                return self._jwks_cache
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.jwks_url)
                if response.status_code == 200:
                    self._jwks_cache = response.json()
                    self._cache_time = now
                    return self._jwks_cache
        except Exception as e:
            print(f"Error fetching JWKS: {e}")
        
        return self._jwks_cache  # Return cached version if fetch fails


# Initialize JWKS client
jwks_client = ClerkJWKSClient(CLERK_JWKS_URL) if CLERK_JWKS_URL else None


async def verify_clerk_token(token: str) -> Optional[ClerkUser]:
    """
    Verify a Clerk JWT token and return user info.
    
    For development, we also support a simplified verification
    that trusts the token without full JWKS validation.
    """
    if not token:
        return None
    
    try:
        # First, decode without verification to get claims
        unverified_claims = jwt.decode(token, options={"verify_signature": False})
        
        # In development mode, we can trust the token
        # In production, you should always verify with JWKS
        if os.getenv("ENVIRONMENT", "development") == "development":
            return ClerkUser(
                user_id=unverified_claims.get("sub", ""),
                email=unverified_claims.get("email"),
                username=unverified_claims.get("username"),
                first_name=unverified_claims.get("first_name"),
                last_name=unverified_claims.get("last_name"),
                full_name=unverified_claims.get("name"),
                image_url=unverified_claims.get("image_url"),
                role=unverified_claims.get("public_metadata", {}).get("role", "User"),
                metadata=unverified_claims.get("public_metadata", {}),
            )
        
        # Production: Verify with JWKS
        if not jwks_client:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="JWKS client not configured"
            )
        
        # Get key ID from token header
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
        
        if not kid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing key ID"
            )
        
        # Fetch signing key
        signing_key = await jwks_client.get_signing_key(kid)
        if not signing_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: unknown signing key"
            )
        
        # Verify and decode token
        public_key = jwt.algorithms.RSAAlgorithm.from_jwk(signing_key)
        claims = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            options={"verify_aud": False}  # Clerk doesn't always set aud
        )
        
        return ClerkUser(
            user_id=claims.get("sub", ""),
            email=claims.get("email"),
            username=claims.get("username"),
            first_name=claims.get("first_name"),
            last_name=claims.get("last_name"),
            full_name=claims.get("name"),
            image_url=claims.get("image_url"),
            role=claims.get("public_metadata", {}).get("role", "User"),
            metadata=claims.get("public_metadata", {}),
        )
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )
    except Exception as e:
        print(f"Token verification error: {e}")
        return None


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[ClerkUser]:
    """
    Dependency to get the current authenticated user.
    Returns None if not authenticated (allows anonymous access).
    """
    if not credentials:
        return None
    
    token = credentials.credentials
    return await verify_clerk_token(token)


async def require_auth(
    user: Optional[ClerkUser] = Depends(get_current_user)
) -> ClerkUser:
    """
    Dependency that requires authentication.
    Raises 401 if not authenticated.
    """
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def require_admin(
    user: ClerkUser = Depends(require_auth)
) -> ClerkUser:
    """
    Dependency that requires admin role.
    Raises 403 if not an admin.
    """
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return user


async def require_analyst(
    user: ClerkUser = Depends(require_auth)
) -> ClerkUser:
    """
    Dependency that requires analyst or higher role.
    """
    if not user.is_analyst:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Analyst access required"
        )
    return user
