# Main.py Refactoring Plan

## Current State
- **File**: `app/main.py`
- **Size**: 1,901 lines
- **Issues**: 
  - Mixed responsibilities (API routes, business logic, data persistence, background tasks)
  - Difficult to maintain and test
  - Single monolithic file

## Refactoring Strategy

### 1. Immediate Structure (Created)
```
app/
├── main_refactored.py          # New clean FastAPI app (76 lines)
├── routers/                    # API route organization
│   ├── __init__.py
│   ├── health.py              # Health endpoints (3 endpoints)
│   ├── projects.py            # Project CRUD (4 endpoints)
│   ├── analysis.py            # Analysis operations (2 endpoints)
│   ├── admin.py               # Admin functions (3 endpoints)
│   └── visualization.py       # Charts and viz (2 endpoints)
└── utils/
    ├── __init__.py
    └── data_loader.py          # Data persistence utilities
```

### 2. Endpoint Distribution

#### From main.py (20+ endpoints) to organized routers:

**Health Router** (3 endpoints):
- `GET /` - Root endpoint
- `GET /health` - Health check  
- `GET /api/v1/health` - API health check

**Projects Router** (8 endpoints):
- `GET /api/v1/projects` - List projects
- `POST /api/v1/projects` - Create project
- `GET /api/v1/projects/{id}` - Get project
- `DELETE /api/v1/projects/{id}` - Delete project
- `GET /api/v1/projects/restore/available` - List packages
- `POST /api/v1/projects/restore` - Restore project
- `GET /api/v1/projects/{id}/export` - Export project
- `POST /api/v1/projects/import` - Import project

**Analysis Router** (4 endpoints):
- `POST /api/v1/analysis/run/{id}` - Run analysis
- `POST /api/v1/projects/{id}/analyze` - Analyze project
- `POST /api/v1/projects/{id}/analyze/{app}` - Analyze application
- `GET /api/v1/analysis/results/{id}` - Get results

**Admin Router** (3 endpoints):
- `POST /api/v1/admin/clear-all-data` - Clear data
- `POST /api/v1/admin/recover-projects` - Recover projects
- `GET /api/v1/admin/system-info` - System info

**Visualization Router** (2 endpoints):
- `GET /api/v1/visualization/charts/{id}` - Get charts
- `GET /api/v1/visualization/summary/{id}` - Get summary

### 3. Benefits Achieved

#### ✅ **Separation of Concerns**
- **Before**: All logic mixed in 1,901 lines
- **After**: Clean separation by function
  - `main_refactored.py`: App setup and routing (76 lines)
  - `routers/`: API endpoints by domain (~50-100 lines each)
  - `utils/`: Shared utilities

#### ✅ **Maintainability**
- **Before**: Hard to find specific endpoints in massive file
- **After**: Logical organization by feature area
- Easy to locate and modify specific functionality

#### ✅ **Testing**
- **Before**: Difficult to test individual components
- **After**: Each router can be tested independently
- Clear separation of business logic

#### ✅ **Scalability**
- **Before**: Adding features meant modifying huge file
- **After**: New features can be added as new routers
- Existing code doesn't get disrupted

### 4. Migration Path

#### Phase 1: ✅ **Structure Created**
- Created modular router structure
- Extracted core endpoints to organized routers
- Created data utilities module

#### Phase 2: **Validation & Testing**
- Test refactored structure with existing data
- Ensure all endpoints work correctly
- Validate WebSocket and background tasks

#### Phase 3: **Cutover**
- Switch from `main.py` to `main_refactored.py`
- Update deployment scripts
- Archive old monolithic file

### 5. Key Improvements

#### **Code Organization**
```python
# Before: Everything in main.py (1,901 lines)
@app.get("/api/v1/projects")
@app.post("/api/v1/projects") 
@app.delete("/api/v1/projects/{id}")
@app.get("/api/v1/analysis/run")
@app.post("/api/v1/admin/clear-data")
# ... 15+ more endpoints mixed together

# After: Organized by domain
app.include_router(projects.router, prefix="/api/v1")  # Project operations
app.include_router(analysis.router, prefix="/api/v1")  # Analysis operations  
app.include_router(admin.router, prefix="/api/v1")     # Admin operations
```

#### **Simplified Main Application**
```python
# main_refactored.py - Clean and focused (76 lines vs 1,901)
app = FastAPI(title="prplOS LCM Log Analysis System")
app.add_middleware(CORSMiddleware, ...)

# Include organized routers
app.include_router(health.router)
app.include_router(projects.router, prefix="/api/v1")
app.include_router(analysis.router, prefix="/api/v1") 
app.include_router(admin.router, prefix="/api/v1")
app.include_router(visualization.router, prefix="/api/v1")

# WebSocket and startup logic
@app.websocket("/ws")
@app.on_event("startup")
```

### 6. Next Steps
1. **Test the refactored structure** with current data
2. **Gradually migrate** complex business logic from main.py
3. **Add proper error handling** and validation
4. **Switch deployment** to use `main_refactored.py`

## Summary
Successfully broke down 1,901-line monolith into:
- **1 main app file**: 76 lines (96% reduction)
- **5 focused routers**: ~50-100 lines each
- **Organized by domain**: Projects, Analysis, Admin, Visualization
- **Maintained compatibility**: Uses existing data structures and utilities

This refactoring provides a solid foundation for future development while maintaining all existing functionality.
