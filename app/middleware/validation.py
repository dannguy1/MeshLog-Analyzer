"""
Input validation middleware for API security and data integrity
"""
import re
import uuid
from typing import Any, Dict, Optional
from fastapi import HTTPException, Request
from pydantic import BaseModel, Field, validator
import logging

logger = logging.getLogger(__name__)

class ValidationError(HTTPException):
    """Custom validation error with detailed logging"""
    def __init__(self, detail: str, field: str = None):
        super().__init__(status_code=422, detail=detail)
        logger.warning(f"Validation error: {detail} (field: {field})")

class ProjectCreateRequest(BaseModel):
    """Validation schema for project creation"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    
    @validator('name')
    def validate_name(cls, v):
        if not re.match(r'^[a-zA-Z0-9\s\-_\.]+$', v):
            raise ValueError('Project name contains invalid characters')
        if v.strip() != v:
            raise ValueError('Project name cannot start or end with whitespace')
        return v.strip()
    
    @validator('description')
    def validate_description(cls, v):
        if v is not None:
            return v.strip()
        return v

class AnalysisRequest(BaseModel):
    """Validation schema for analysis requests"""
    analysis_type: str = Field(..., pattern=r'^[a-zA-Z0-9_-]+$')
    target_application: Optional[str] = Field(None, pattern=r'^[a-zA-Z0-9\-_]+$')
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    @validator('parameters')
    def validate_parameters(cls, v):
        if v is None:
            return {}
        
        # Validate parameter keys and basic values
        for key, value in v.items():
            if not re.match(r'^[a-zA-Z0-9_-]+$', key):
                raise ValueError(f'Invalid parameter key: {key}')
            if isinstance(value, str) and len(value) > 10000:
                raise ValueError(f'Parameter value too long: {key}')
        
        return v

class FileUploadValidator:
    """Validator for file uploads"""
    
    ALLOWED_EXTENSIONS = {'.zip', '.tar', '.tar.gz', '.tgz', '.tar.bz2'}
    MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB
    
    @classmethod
    def validate_file(cls, filename: str, file_size: int):
        """Validate uploaded file"""
        if not filename:
            raise ValidationError("Filename is required", "filename")
        
        # Check file extension
        if not any(filename.lower().endswith(ext) for ext in cls.ALLOWED_EXTENSIONS):
            raise ValidationError(
                f"Invalid file type. Allowed types: {', '.join(cls.ALLOWED_EXTENSIONS)}", 
                "filename"
            )
        
        # Check file size
        if file_size > cls.MAX_FILE_SIZE:
            raise ValidationError(
                f"File too large. Maximum size: {cls.MAX_FILE_SIZE // (1024*1024)}MB", 
                "file_size"
            )
        
        # Check for path traversal attempts
        if '..' in filename or '/' in filename or '\\' in filename:
            raise ValidationError("Invalid filename: path traversal detected", "filename")

class RequestValidator:
    """General request validation utilities"""
    
    @staticmethod
    def validate_project_id(project_id: str):
        """Validate project ID format"""
        try:
            uuid.UUID(project_id)
        except ValueError:
            raise ValidationError("Invalid project ID format", "project_id")
    
    @staticmethod
    def validate_analysis_id(analysis_id: str):
        """Validate analysis ID format"""
        if not re.match(r'^[a-zA-Z0-9\-_]+$', analysis_id):
            raise ValidationError("Invalid analysis ID format", "analysis_id")
    
    @staticmethod
    def validate_application_name(app_name: str):
        """Validate application name"""
        if not re.match(r'^[a-zA-Z0-9\-_]+$', app_name):
            raise ValidationError("Invalid application name format", "application_name")
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 1000) -> str:
        """Sanitize string input"""
        if not isinstance(value, str):
            raise ValidationError("Expected string value")
        
        # Remove null bytes and control characters
        sanitized = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', value)
        
        # Limit length
        if len(sanitized) > max_length:
            raise ValidationError(f"String too long (max {max_length} characters)")
        
        return sanitized.strip()

async def validate_request_size(request: Request):
    """Middleware to validate request size"""
    content_length = request.headers.get('content-length')
    if content_length:
        content_length = int(content_length)
        if content_length > 100 * 1024 * 1024:  # 100MB
            raise HTTPException(status_code=413, detail="Request too large")

def validate_rate_limit_headers(request: Request):
    """Basic rate limiting validation"""
    # Check for common bot/scanner patterns
    user_agent = request.headers.get('user-agent', '').lower()
    suspicious_patterns = ['bot', 'crawler', 'scanner', 'spider']
    
    if any(pattern in user_agent for pattern in suspicious_patterns):
        logger.warning(f"Suspicious user agent detected: {user_agent}")
        # Could implement actual rate limiting here
    
    return True
