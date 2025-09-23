# Security and Monitoring Implementation Guide

## Overview

This document describes the implemented security and monitoring enhancements based on the system architecture implementation plan recommendations.

## Implemented Features

### 🔒 Security Enhancements

#### 1. Input Validation System
- **File**: `app/middleware/validation.py`
- **Features**:
  - Comprehensive request validation schemas
  - File upload validation with size/type restrictions
  - Path traversal protection
  - SQL injection prevention
  - XSS protection through input sanitization

#### 2. Authentication & Authorization
- **File**: `app/middleware/auth.py`
- **Features**:
  - Basic HTTP authentication
  - API key authentication
  - Role-based access control
  - Security event logging
  - Password hashing with secure comparison

#### 3. Security Headers & Middleware
- **Implementation**: Integrated in `app/main.py`
- **Features**:
  - Security headers (HSTS, CSP, X-Frame-Options, etc.)
  - Request size validation
  - Rate limiting checks
  - CORS configuration

### 📊 Monitoring & Observability

#### 1. Metrics Collection System
- **File**: `app/monitoring/metrics.py`
- **Features**:
  - System resource monitoring (CPU, memory, disk)
  - Request timing and error tracking
  - Custom business metrics
  - Health check framework
  - Performance analytics

#### 2. Database Transaction Management
- **File**: `app/database/database.py`
- **Features**:
  - Automatic transaction rollback on errors
  - Connection management with cleanup
  - Transactional project operations
  - Data consistency guarantees

#### 3. Health Check Endpoints
- **Endpoints**:
  - `/health` - Basic health status
  - `/health/detailed` - Comprehensive system health
  - `/metrics` - System metrics and performance data

## Configuration

### Environment Variables

```bash
# Security Configuration
AUTH_ENABLED=false                    # Enable authentication
ADMIN_USERNAME=admin                  # Admin username
ADMIN_PASSWORD=your_secure_password   # Admin password (use strong password)
API_KEY=your_api_key_here            # API key for service authentication

# File Upload Security
MAX_FILE_SIZE=524288000              # Maximum upload size (500MB)
ALLOWED_EXTENSIONS=.zip,.tar,.tar.gz # Allowed file extensions

# Rate Limiting
RATE_LIMIT_ENABLED=false             # Enable rate limiting
RATE_LIMIT_REQUESTS=100              # Requests per window
RATE_LIMIT_WINDOW=60                 # Window size in seconds

# Monitoring
METRICS_ENABLED=true                 # Enable metrics collection
HEALTH_CHECK_INTERVAL=30             # Health check interval

# CORS Security
CORS_ORIGINS=http://localhost:3000   # Allowed CORS origins
TRUSTED_HOSTS=localhost,0.0.0.0      # Trusted host names

# Logging Security
LOG_SENSITIVE_DATA=false             # Don't log sensitive data
LOG_LEVEL=INFO                       # Logging level
```

### Quick Setup

1. **Copy security environment template**:
   ```bash
   cp .env.security .env.local
   # Edit .env.local with your values
   ```

2. **Install additional dependencies**:
   ```bash
   pip install -r requirements-security.txt
   ```

3. **Enable authentication** (optional):
   ```bash
   # Set strong passwords in .env.local
   export AUTH_ENABLED=true
   export ADMIN_PASSWORD="your_very_secure_password"
   export API_KEY="your_api_key_here"
   ```

## Security Features in Detail

### 1. Input Validation

**Project Creation with Validation**:
```python
# Now validates:
# - Project name format and length
# - File type and size restrictions
# - Path traversal attempts
# - Special character filtering

POST /api/v1/projects
{
  "name": "valid-project-name",     # Validated format
  "description": "description"      # Length limited
}
```

**File Upload Security**:
- Maximum file size: 500MB (configurable)
- Allowed extensions: `.zip`, `.tar`, `.tar.gz`, `.tgz`, `.tar.bz2`
- Path traversal protection
- Filename sanitization

### 2. Authentication System

**Basic Authentication**:
```bash
# Access protected endpoints
curl -u admin:password http://localhost:8000/api/v1/projects
```

**API Key Authentication**:
```bash
# Use API key for service-to-service communication
curl -H "X-API-Key: your_api_key" http://localhost:8000/api/v1/projects
```

**Protected Endpoints**:
- Project creation: Requires authentication
- Project deletion: Requires admin privileges
- System administration: Requires admin privileges

### 3. Security Headers

All responses include security headers:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000`
- `Referrer-Policy: strict-origin-when-cross-origin`

## Monitoring Features in Detail

### 1. System Health Monitoring

**Basic Health Check**:
```bash
curl http://localhost:8000/health
```

**Detailed Health Check**:
```bash
curl http://localhost:8000/health/detailed
```

**Response Example**:
```json
{
  "status": "healthy",
  "timestamp": "2025-09-16T20:30:00Z",
  "system": {
    "cpu_percent": 25.5,
    "memory_percent": 68.2,
    "disk_percent": 45.0,
    "active_connections": 12,
    "response_time_avg": 0.15,
    "error_rate": 0.5,
    "status": "healthy"
  },
  "checks": {
    "database": {"status": "healthy", "message": "Database connection OK"},
    "disk_space": {"status": "healthy", "message": "Disk usage OK: 45%"}
  }
}
```

### 2. Metrics Collection

**Get System Metrics**:
```bash
curl http://localhost:8000/metrics
```

**Metric Types Collected**:
- Request duration by endpoint
- Error rates and counts
- System resource utilization
- Custom business metrics
- Performance trends

### 3. Database Transaction Management

**Before** (No transaction management):
```python
# If error occurred, partial data could be left in inconsistent state
conn.execute("INSERT INTO projects ...")
conn.execute("INSERT INTO analysis_results ...")  # Error here leaves orphaned project
```

**After** (With transaction management):
```python
# Automatic rollback on any error ensures data consistency
async with db.get_transaction() as conn:
    conn.execute("INSERT INTO projects ...")
    conn.execute("INSERT INTO analysis_results ...")  # Error here rolls back everything
```

## Production Deployment

### 1. Enable Security Features

```bash
# Set production environment variables
export AUTH_ENABLED=true
export ADMIN_PASSWORD="$(openssl rand -base64 32)"
export API_KEY="$(openssl rand -base64 32)"
export RATE_LIMIT_ENABLED=true
```

### 2. Configure Monitoring

```bash
# Enable comprehensive monitoring
export METRICS_ENABLED=true
export HEALTH_CHECK_INTERVAL=30
export LOG_LEVEL=INFO
```

### 3. Security Hardening

```bash
# Restrict CORS origins to production domains
export CORS_ORIGINS="https://your-domain.com,https://www.your-domain.com"

# Set trusted hosts
export TRUSTED_HOSTS="your-domain.com,www.your-domain.com"

# Disable sensitive data logging
export LOG_SENSITIVE_DATA=false
```

### 4. Monitoring Setup

```bash
# Setup log monitoring (example with systemd)
journalctl -u meshlog -f | grep "Security Event"

# Monitor health endpoint
while true; do
  curl -s http://localhost:8000/health/detailed | jq '.status'
  sleep 30
done
```

## Testing Security Features

### 1. Test Authentication

```bash
# Test without credentials (should fail)
curl http://localhost:8000/api/v1/projects
# Response: 401 Unauthorized

# Test with credentials (should succeed)
curl -u admin:password http://localhost:8000/api/v1/projects
# Response: Project list
```

### 2. Test Input Validation

```bash
# Test invalid file upload
curl -X POST -F "file=@test.txt" -F "name=test" http://localhost:8000/api/v1/projects
# Response: 422 Invalid file type

# Test path traversal
curl -X POST -F "file=@../../../etc/passwd" -F "name=test" http://localhost:8000/api/v1/projects
# Response: 422 Invalid filename: path traversal detected
```

### 3. Test Rate Limiting

```bash
# Send many requests quickly (if rate limiting enabled)
for i in {1..150}; do
  curl http://localhost:8000/health &
done
# Some requests should be rate limited
```

## Monitoring Dashboard (Future Enhancement)

The current implementation provides the foundation for advanced monitoring dashboards:

```bash
# Example Grafana queries for future implementation:
# - avg(response_time) by endpoint
# - rate(error_count) by status_code
# - cpu_percent, memory_percent over time
# - request_count by user/endpoint
```

## Security Best Practices

### 1. Password Management
- Use strong, unique passwords
- Store passwords in secure environment variables
- Rotate passwords regularly
- Consider using password managers

### 2. API Key Management
- Generate long, random API keys
- Rotate API keys regularly
- Use different keys for different environments
- Monitor API key usage

### 3. File Upload Security
- Scan uploaded files for malware (future enhancement)
- Limit file types strictly
- Monitor upload patterns
- Implement quota management

### 4. Network Security
- Use HTTPS in production
- Configure firewall rules
- Monitor network traffic
- Use reverse proxy for additional security

## Troubleshooting

### Common Issues

1. **Authentication Not Working**
   ```bash
   # Check if authentication is enabled
   echo $AUTH_ENABLED
   
   # Check password hash generation
   python3 -c "import hashlib; print(hashlib.sha256('your_password'.encode()).hexdigest())"
   ```

2. **Metrics Not Collecting**
   ```bash
   # Check if psutil is installed
   pip show psutil
   
   # Check metrics endpoint
   curl http://localhost:8000/metrics
   ```

3. **Health Checks Failing**
   ```bash
   # Check detailed health status
   curl http://localhost:8000/health/detailed
   
   # Check logs for errors
   tail -f logs/app.log | grep -i error
   ```

## Summary

The implemented security and monitoring enhancements provide:

✅ **Comprehensive Input Validation**  
✅ **Authentication & Authorization**  
✅ **Security Headers & Middleware**  
✅ **System Monitoring & Metrics**  
✅ **Database Transaction Management**  
✅ **Health Check Framework**  
✅ **Security Event Logging**  
✅ **Performance Monitoring**  

The system is now production-ready with enterprise-grade security and monitoring capabilities.
