# prplOS LCM Log Analysis System - Configuration Management

import os
from typing import Optional, Dict, Any
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application settings
    APP_NAME: str = Field(default="prplOS LCM Log Analysis System", env="APP_NAME")
    APP_VERSION: str = Field(default="1.0.0", env="APP_VERSION")
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    # Data storage configuration - Use standard LCM-Logs-Data directory
    DATA_DIR: str = Field(default="/data/WNC/LCM-Logs-Data", env="DATA_DIR")
    UPLOAD_DIR: str = Field(default="uploads", env="UPLOAD_DIR")
    ANALYSIS_DIR: str = Field(default="analysis", env="ANALYSIS_DIR")
    TEMP_DIR: str = Field(default="temp", env="TEMP_DIR")
    BACKUP_DIR: str = Field(default="backups", env="BACKUP_DIR")
    
    # Database configuration
    DATABASE_URL: str = Field(
        default="sqlite:////data/WNC/LCM-Logs-Data/prplos_analysis.db",
        env="DATABASE_URL"
    )
    # Additional database paths for compatibility
    DATABASE_PATH: str = Field(
        default="/data/WNC/LCM-Logs-Data/meshlog.db",
        env="DATABASE_PATH"
    )
    DATA_FILE: str = Field(
        default="/data/WNC/LCM-Logs-Data/projects.json",
        env="DATA_FILE"
    )
    POSTGRES_DB: str = Field(default="prplos_logs", env="POSTGRES_DB")
    POSTGRES_USER: str = Field(default="prplos_user", env="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field(default="prplos_password", env="POSTGRES_PASSWORD")
    
    # Redis configuration
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        env="REDIS_URL"
    )
    REDIS_HOST: str = Field(default="localhost", env="REDIS_HOST")
    REDIS_PORT: int = Field(default=6379, env="REDIS_PORT")
    REDIS_DB: int = Field(default=0, env="REDIS_DB")
    
    # Security settings
    SECRET_KEY: str = Field(default="your-secret-key-change-in-production", env="SECRET_KEY")
    JWT_SECRET_KEY: str = Field(default="your-jwt-secret-key-change-in-production", env="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = Field(default="HS256", env="JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # CORS settings
    CORS_ORIGINS: list = Field(default=["http://localhost:3000", "http://127.0.0.1:3000", "http://0.0.0.0:3000"], env="CORS_ORIGINS")
    
    # Logging settings
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FILE: str = Field(default="./logs/app.log", env="LOG_FILE")
    LOG_MAX_SIZE: int = Field(default=10485760, env="LOG_MAX_SIZE")  # 10MB
    LOG_BACKUP_COUNT: int = Field(default=5, env="LOG_BACKUP_COUNT")
    LOG_FORMAT: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s", env="LOG_FORMAT")
    
    # Analysis configuration
    ANALYSIS_TIMEOUT: int = Field(default=3600, env="ANALYSIS_TIMEOUT")  # 1 hour
    MAX_CONCURRENT_ANALYSES: int = Field(default=5, env="MAX_CONCURRENT_ANALYSES")
    ANOMALY_DETECTION_ENABLED: bool = Field(default=True, env="ANOMALY_DETECTION_ENABLED")
    PREDICTIVE_ANALYTICS_ENABLED: bool = Field(default=True, env="PREDICTIVE_ANALYTICS_ENABLED")
    DEFAULT_ANALYSIS_CONFIG: Dict[str, Any] = Field(
        default={
            "include_raw_logs": False,
            "extract_structured_data": True,
            "perform_correlation": True,
            "detect_anomalies": True,
            "generate_summary": True,
            "create_visualizations": True,
            "embed_analysis": True
        },
        env="DEFAULT_ANALYSIS_CONFIG"
    )
    
    # Processing configuration
    MAX_WORKERS: int = Field(default=4, env="MAX_WORKERS")
    WORKER_PROCESSES: int = Field(default=4, env="WORKER_PROCESSES")
    WORKER_CONNECTIONS: int = Field(default=1000, env="WORKER_CONNECTIONS")
    MAX_REQUESTS: int = Field(default=1000, env="MAX_REQUESTS")
    MAX_REQUESTS_JITTER: int = Field(default=50, env="MAX_REQUESTS_JITTER")
    CHUNK_SIZE: int = Field(default=8192, env="CHUNK_SIZE")
    TIMEOUT_SECONDS: int = Field(default=300, env="TIMEOUT_SECONDS")
    
    # Monitoring configuration
    ENABLE_METRICS: bool = Field(default=True, env="ENABLE_METRICS")
    METRICS_PORT: int = Field(default=9090, env="METRICS_PORT")
    ENABLE_MONITORING: bool = Field(default=True, env="ENABLE_MONITORING")
    ALERT_THRESHOLD_ERROR_RATE: float = Field(default=0.1, env="ALERT_THRESHOLD_ERROR_RATE")
    ALERT_THRESHOLD_RESPONSE_TIME: int = Field(default=1000, env="ALERT_THRESHOLD_RESPONSE_TIME")
    ALERT_THRESHOLD_MEMORY_USAGE: int = Field(default=80, env="ALERT_THRESHOLD_MEMORY_USAGE")
    
    # WebSocket configuration
    WEBSOCKET_ENABLED: bool = Field(default=True, env="WEBSOCKET_ENABLED")
    WEBSOCKET_HEARTBEAT_INTERVAL: int = Field(default=30, env="WEBSOCKET_HEARTBEAT_INTERVAL")
    WEBSOCKET_PING_INTERVAL: int = Field(default=25, env="WEBSOCKET_PING_INTERVAL")
    WEBSOCKET_PING_TIMEOUT: int = Field(default=10, env="WEBSOCKET_PING_TIMEOUT")
    
    # Email configuration
    SMTP_HOST: str = Field(default="", env="SMTP_HOST")
    SMTP_PORT: int = Field(default=587, env="SMTP_PORT")
    SMTP_USER: str = Field(default="", env="SMTP_USER")
    SMTP_PASSWORD: str = Field(default="", env="SMTP_PASSWORD")
    SMTP_TLS: bool = Field(default=True, env="SMTP_TLS")
    
    # Application specific settings
    SUPPORTED_APPLICATIONS: list = Field(default=["wnc-steer", "wnc-acs", "wnc-tpyopt", "otbr-agent"], env="SUPPORTED_APPLICATIONS")
    
    # Search configuration
    ELASTICSEARCH_URL: str = Field(default="", env="ELASTICSEARCH_URL")
    SEARCH_INDEX_PREFIX: str = Field(default="prplos", env="SEARCH_INDEX_PREFIX")
    
    # Collaboration settings
    ENABLE_COLLABORATION: bool = Field(default=True, env="ENABLE_COLLABORATION")
    MAX_COLLABORATORS_PER_PROJECT: int = Field(default=10, env="MAX_COLLABORATORS_PER_PROJECT")
    
    # Error handling
    MAX_RETRY_ATTEMPTS: int = Field(default=3, env="MAX_RETRY_ATTEMPTS")
    RETRY_DELAY_SECONDS: int = Field(default=5, env="RETRY_DELAY_SECONDS")
    
    # External services
    LLM_API_KEY: str = Field(default="", env="LLM_API_KEY")
    LLM_API_URL: str = Field(default="https://api.openai.com/v1", env="LLM_API_URL")
    
    # Celery configuration
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/0", env="CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/0", env="CELERY_RESULT_BACKEND")
    CELERY_TASK_SERIALIZER: str = Field(default="json", env="CELERY_TASK_SERIALIZER")
    CELERY_RESULT_SERIALIZER: str = Field(default="json", env="CELERY_RESULT_SERIALIZER")
    CELERY_ACCEPT_CONTENT: str = Field(default="json", env="CELERY_ACCEPT_CONTENT")
    CELERY_TIMEZONE: str = Field(default="UTC", env="CELERY_TIMEZONE")
    CELERY_ENABLE_UTC: bool = Field(default=True, env="CELERY_ENABLE_UTC")
    
    # File upload settings
    MAX_FILE_SIZE: int = Field(default=1073741824, env="MAX_FILE_SIZE")  # 1GB
    ALLOWED_EXTENSIONS: list = Field(default=[".tar.gz", ".tgz", ".tar"], env="ALLOWED_EXTENSIONS")
    
    # API settings
    API_PREFIX: str = Field(default="/api/v1", env="API_PREFIX")
    
    # Alert settings
    ALERT_ENABLED: bool = Field(default=True, env="ALERT_ENABLED")
    ALERT_CHECK_INTERVAL: int = Field(default=60, env="ALERT_CHECK_INTERVAL")
    ALERT_RETENTION_DAYS: int = Field(default=30, env="ALERT_RETENTION_DAYS")
    
    # Visualization settings
    CHART_DEFAULT_WIDTH: int = Field(default=800, env="CHART_DEFAULT_WIDTH")
    CHART_DEFAULT_HEIGHT: int = Field(default=600, env="CHART_DEFAULT_HEIGHT")
    CHART_THEME: str = Field(default="plotly", env="CHART_THEME")
    
    # Agent Services Integration
    WNC_LOG_AGENTS_ENABLED: bool = Field(default=False, env="WNC_LOG_AGENTS_ENABLED")
    WNC_LOG_AGENTS_URL: str = Field(default="http://localhost:8001", env="WNC_LOG_AGENTS_URL")
    WNC_LOG_AGENTS_TIMEOUT: int = Field(default=300, env="WNC_LOG_AGENTS_TIMEOUT")  # 5 minutes
    SHARED_DATA_PATH: str = Field(default="/shared-data", env="SHARED_DATA_PATH")
    AGENT_ANALYSIS_ENABLED: bool = Field(default=True, env="AGENT_ANALYSIS_ENABLED")
    AGENT_RESULT_CACHE_TTL: int = Field(default=3600, env="AGENT_RESULT_CACHE_TTL")  # 1 hour
    
    # Integrated Agent System Configuration
    INTEGRATED_AGENTS_ENABLED: bool = Field(default=True, env="INTEGRATED_AGENTS_ENABLED")
    INTEGRATED_AGENTS_PATH: str = Field(default="app.agents", env="INTEGRATED_AGENTS_PATH")
    HYBRID_AGENT_MODE: bool = Field(default=True, env="HYBRID_AGENT_MODE")  # Support both integrated and service agents
    INTEGRATED_AGENT_TIMEOUT: int = Field(default=600, env="INTEGRATED_AGENT_TIMEOUT")  # 10 minutes for heavy processing
    AGENT_EXECUTION_PRIORITY: str = Field(default="integrated", env="AGENT_EXECUTION_PRIORITY")  # "integrated" or "service"
    AGENT_DISCOVERY_AUTO_REFRESH: bool = Field(default=True, env="AGENT_DISCOVERY_AUTO_REFRESH")
    
    # Agent-specific settings
    AGENT_DETECTION_CONFIDENCE_THRESHOLD: float = Field(default=0.7, env="AGENT_DETECTION_CONFIDENCE_THRESHOLD")
    AGENT_AUTO_TRIGGER: bool = Field(default=True, env="AGENT_AUTO_TRIGGER")
    AGENT_RESULT_FORMATS: list = Field(default=["html", "json"], env="AGENT_RESULT_FORMATS")
    
    # Development settings
    AUTO_RELOAD: bool = Field(default=False, env="AUTO_RELOAD")
    HOT_RELOAD: bool = Field(default=False, env="HOT_RELOAD")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Allow extra fields from .env file

# Global settings instance
_settings: Optional[Settings] = None

def get_settings() -> Settings:
    """Get global settings instance"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

def get_database_url() -> str:
    """Get database URL from settings, ensuring it uses DATA_DIR for SQLite"""
    settings = get_settings()
    database_url = settings.DATABASE_URL
    
    # If it's a SQLite URL with relative path, convert to use DATA_DIR
    if database_url.startswith('sqlite:///./'):
        # Replace relative path with DATA_DIR
        db_filename = database_url.replace('sqlite:///./', '')
        database_url = f"sqlite:///{os.path.join(settings.DATA_DIR, db_filename)}"
    
    return database_url

def get_redis_url() -> str:
    """Get Redis URL from settings"""
    settings = get_settings()
    return settings.REDIS_URL

def get_upload_dir() -> str:
    """Get upload directory from settings"""
    settings = get_settings()
    return settings.UPLOAD_DIR

def get_data_dir() -> str:
    """Get data directory from settings"""
    settings = get_settings()
    return settings.DATA_DIR

def get_temp_dir() -> str:
    """Get temp directory from settings"""
    settings = get_settings()
    return settings.TEMP_DIR

def get_backup_dir() -> str:
    """Get backup directory from settings"""
    settings = get_settings()
    return settings.BACKUP_DIR

def get_analysis_config() -> Dict[str, Any]:
    """Get analysis configuration from settings"""
    settings = get_settings()
    return settings.DEFAULT_ANALYSIS_CONFIG

def get_cors_origins() -> list:
    """Get CORS origins from settings"""
    settings = get_settings()
    return settings.CORS_ORIGINS

def get_secret_key() -> str:
    """Get secret key from settings"""
    settings = get_settings()
    return settings.SECRET_KEY

def get_llm_config() -> Dict[str, str]:
    """Get LLM configuration from settings"""
    settings = get_settings()
    return {
        "api_url": settings.LLM_API_URL,
        "api_key": settings.LLM_API_KEY
    }

def get_websocket_config() -> Dict[str, Any]:
    """Get WebSocket configuration from settings"""
    settings = get_settings()
    return {
        "enabled": settings.WEBSOCKET_ENABLED,
        "ping_interval": settings.WEBSOCKET_PING_INTERVAL,
        "ping_timeout": settings.WEBSOCKET_PING_TIMEOUT
    }

def get_monitoring_config() -> Dict[str, Any]:
    """Get monitoring configuration from settings"""
    settings = get_settings()
    return {
        "enabled": settings.ENABLE_MONITORING,
        "metrics_port": settings.METRICS_PORT
    }

def get_alert_config() -> Dict[str, Any]:
    """Get alert configuration from settings"""
    settings = get_settings()
    return {
        "enabled": settings.ALERT_ENABLED,
        "check_interval": settings.ALERT_CHECK_INTERVAL,
        "retention_days": settings.ALERT_RETENTION_DAYS
    }

def get_visualization_config() -> Dict[str, Any]:
    """Get visualization configuration from settings"""
    settings = get_settings()
    return {
        "chart_width": settings.CHART_DEFAULT_WIDTH,
        "chart_height": settings.CHART_DEFAULT_HEIGHT,
        "theme": settings.CHART_THEME
    }

def get_performance_config() -> Dict[str, Any]:
    """Get performance configuration from settings"""
    settings = get_settings()
    return {
        "worker_processes": settings.WORKER_PROCESSES,
        "max_workers": settings.MAX_WORKERS
    }

def get_storage_config() -> Dict[str, str]:
    """Get storage configuration from settings"""
    settings = get_settings()
    return {
        "max_file_size": settings.MAX_FILE_SIZE,
        "allowed_extensions": settings.ALLOWED_EXTENSIONS,
        "upload_dir": settings.UPLOAD_DIR,
        "data_dir": settings.DATA_DIR,
        "temp_dir": settings.TEMP_DIR,
        "backup_dir": settings.BACKUP_DIR
    }

def get_api_config() -> Dict[str, Any]:
    """Get API configuration from settings"""
    settings = get_settings()
    return {
        "prefix": settings.API_PREFIX,
        "timeout": settings.ANALYSIS_TIMEOUT,
        "max_concurrent": settings.MAX_CONCURRENT_ANALYSES
    }

def get_logging_config() -> Dict[str, Any]:
    """Get logging configuration from settings"""
    settings = get_settings()
    return {
        "level": settings.LOG_LEVEL,
        "format": settings.LOG_FORMAT
    }

def get_development_config() -> Dict[str, bool]:
    """Get development configuration from settings"""
    settings = get_settings()
    return {
        "debug": settings.DEBUG,
        "auto_reload": settings.AUTO_RELOAD,
        "hot_reload": settings.HOT_RELOAD
    }

# Convenience functions for common settings
def is_debug_mode() -> bool:
    """Check if debug mode is enabled"""
    settings = get_settings()
    return settings.DEBUG

def is_development_mode() -> bool:
    """Check if development mode is enabled"""
    settings = get_settings()
    return settings.DEBUG or settings.AUTO_RELOAD

def get_app_info() -> Dict[str, str]:
    """Get application information"""
    settings = get_settings()
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION
    }

def get_database_info() -> Dict[str, str]:
    """Get database information"""
    settings = get_settings()
    return {
        "url": settings.DATABASE_URL,
        "type": "sqlite" if "sqlite" in settings.DATABASE_URL.lower() else "postgresql"
    }

def get_redis_info() -> Dict[str, str]:
    """Get Redis information"""
    settings = get_settings()
    return {
        "url": settings.REDIS_URL,
        "host": settings.REDIS_URL.split("://")[1].split(":")[0] if "://" in settings.REDIS_URL else "localhost",
        "port": settings.REDIS_URL.split(":")[-1].split("/")[0] if ":" in settings.REDIS_URL else "6379"
    }

def get_all_settings() -> Dict[str, Any]:
    """Get all settings as dictionary"""
    settings = get_settings()
    return settings.dict()