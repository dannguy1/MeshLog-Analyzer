"""
Auth middleware - DISABLED for demo project
"""
from fastapi import Request, Response
from typing import Any, Optional

# Placeholder functions to prevent import errors
def log_security_event(*args, **kwargs):
    """Disabled security event logging"""
    pass

async def get_current_user(request: Request = None):
    """Always return mock user - demo mode"""
    return {"id": "demo", "username": "demo_user"}

async def verify_api_key(request: Request = None):
    """Always return True - demo mode"""
    return True

async def require_admin(request: Request = None):
    """Always allow admin access - demo mode"""
    return {"id": "admin", "username": "demo_admin"}

class AuthManager:
    """Disabled auth manager"""
    def __init__(self):
        self.enabled = False
    
    def authenticate(self, *args, **kwargs):
        """Always allow access - demo mode"""
        return True

# Create a disabled auth manager instance
auth_manager = AuthManager()

class SecurityHeaders:
    """Security headers handler - minimal for demo"""
    @staticmethod
    def add_security_headers(response: Response):
        """Add minimal security headers"""
        return response