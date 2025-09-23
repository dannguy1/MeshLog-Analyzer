-- SQLite Database Schema for prplOS LCM Log Analysis System
-- This schema is optimized for SQLite and removes PostgreSQL-specific features

-- Enable foreign key support
PRAGMA foreign_keys = ON;

-- Enable WAL mode for better concurrency
PRAGMA journal_mode = WAL;

-- Set synchronous mode for better performance
PRAGMA synchronous = NORMAL;

-- Set cache size for better performance
PRAGMA cache_size = 10000;

-- Create projects table
CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    file_path TEXT NOT NULL,
    file_size INTEGER,
    status TEXT DEFAULT 'uploading',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create analyses table
CREATE TABLE IF NOT EXISTS analyses (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    status TEXT DEFAULT 'queued',
    progress_percentage INTEGER DEFAULT 0,
    current_stage TEXT,
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_timestamp TIMESTAMP,
    completed_timestamp TIMESTAMP,
    error_message TEXT,
    result_data TEXT,  -- JSON stored as TEXT
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Create applications table
CREATE TABLE IF NOT EXISTS applications (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    name TEXT NOT NULL,
    log_file_path TEXT,
    total_entries INTEGER DEFAULT 0,
    time_range_start TIMESTAMP,
    time_range_end TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Create log_entries table
CREATE TABLE IF NOT EXISTS log_entries (
    id TEXT PRIMARY KEY,
    application_id TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    level TEXT,
    message TEXT NOT NULL,
    source TEXT,
    raw_data TEXT,  -- JSON stored as TEXT
    FOREIGN KEY (application_id) REFERENCES applications(id) ON DELETE CASCADE
);

-- Create time_series_data table
CREATE TABLE IF NOT EXISTS time_series_data (
    id TEXT PRIMARY KEY,
    analysis_id TEXT NOT NULL,
    application_name TEXT,
    timestamp TIMESTAMP NOT NULL,
    metric_name TEXT NOT NULL,
    metric_value REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (analysis_id) REFERENCES analyses(id) ON DELETE CASCADE
);

-- Create anomalies table
CREATE TABLE IF NOT EXISTS anomalies (
    id TEXT PRIMARY KEY,
    analysis_id TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    anomaly_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    description TEXT,
    metric_name TEXT,
    metric_value REAL,
    confidence_score REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (analysis_id) REFERENCES analyses(id) ON DELETE CASCADE
);

-- Create predictions table
CREATE TABLE IF NOT EXISTS predictions (
    id TEXT PRIMARY KEY,
    analysis_id TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    predicted_value REAL NOT NULL,
    confidence_score REAL,
    metric_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (analysis_id) REFERENCES analyses(id) ON DELETE CASCADE
);

-- Create alerts table
CREATE TABLE IF NOT EXISTS alerts (
    id TEXT PRIMARY KEY,
    analysis_id TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    alert_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    message TEXT NOT NULL,
    acknowledged BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (analysis_id) REFERENCES analyses(id) ON DELETE CASCADE
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_projects_created_at ON projects(created_at);
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_analyses_project_id ON analyses(project_id);
CREATE INDEX IF NOT EXISTS idx_analyses_status ON analyses(status);
CREATE INDEX IF NOT EXISTS idx_analyses_created_timestamp ON analyses(created_timestamp);
CREATE INDEX IF NOT EXISTS idx_applications_project_id ON applications(project_id);
CREATE INDEX IF NOT EXISTS idx_log_entries_application_id ON log_entries(application_id);
CREATE INDEX IF NOT EXISTS idx_log_entries_timestamp ON log_entries(timestamp);
CREATE INDEX IF NOT EXISTS idx_log_entries_level ON log_entries(level);
CREATE INDEX IF NOT EXISTS idx_time_series_analysis_id ON time_series_data(analysis_id);
CREATE INDEX IF NOT EXISTS idx_time_series_timestamp ON time_series_data(timestamp);
CREATE INDEX IF NOT EXISTS idx_time_series_metric_name ON time_series_data(metric_name);
CREATE INDEX IF NOT EXISTS idx_anomalies_analysis_id ON anomalies(analysis_id);
CREATE INDEX IF NOT EXISTS idx_anomalies_timestamp ON anomalies(timestamp);
CREATE INDEX IF NOT EXISTS idx_anomalies_severity ON anomalies(severity);
CREATE INDEX IF NOT EXISTS idx_predictions_analysis_id ON predictions(analysis_id);
CREATE INDEX IF NOT EXISTS idx_predictions_timestamp ON predictions(timestamp);
CREATE INDEX IF NOT EXISTS idx_alerts_analysis_id ON alerts(analysis_id);
CREATE INDEX IF NOT EXISTS idx_alerts_acknowledged ON alerts(acknowledged);
CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity);
CREATE INDEX IF NOT EXISTS idx_alerts_created_at ON alerts(created_at);

-- Insert sample data for development
INSERT OR IGNORE INTO projects (id, name, description, file_path, file_size, status) VALUES
    ('sample-project-1', 'Sample Project 1', 'Test project for development', '/uploads/sample1.tar.gz', 1024000, 'completed'),
    ('sample-project-2', 'Sample Project 2', 'Another test project', '/uploads/sample2.tar.gz', 2048000, 'processing');

-- Create views for common queries (after tables exist)
CREATE VIEW IF NOT EXISTS project_summary AS
SELECT 
    p.id,
    p.name,
    p.description,
    p.status,
    p.created_at,
    p.file_size,
    COUNT(DISTINCT a.id) as analysis_count,
    COUNT(DISTINCT app.id) as application_count,
    MAX(a.completed_timestamp) as last_analysis_timestamp
FROM projects p
LEFT JOIN analyses a ON p.id = a.project_id
LEFT JOIN applications app ON p.id = app.project_id
GROUP BY p.id;

CREATE VIEW IF NOT EXISTS analysis_summary AS
SELECT 
    a.id,
    a.project_id,
    p.name as project_name,
    a.status,
    a.progress_percentage,
    a.current_stage,
    a.created_timestamp,
    a.started_timestamp,
    a.completed_timestamp,
    COUNT(DISTINCT ts.id) as time_series_points,
    COUNT(DISTINCT an.id) as anomaly_count,
    COUNT(DISTINCT pr.id) as prediction_count,
    COUNT(DISTINCT al.id) as alert_count
FROM analyses a
JOIN projects p ON a.project_id = p.id
LEFT JOIN time_series_data ts ON a.id = ts.analysis_id
LEFT JOIN anomalies an ON a.id = an.analysis_id
LEFT JOIN predictions pr ON a.id = pr.analysis_id
LEFT JOIN alerts al ON a.id = al.analysis_id
GROUP BY a.id;

CREATE VIEW IF NOT EXISTS application_summary AS
SELECT 
    app.id,
    app.project_id,
    p.name as project_name,
    app.name as application_name,
    app.total_entries,
    app.time_range_start,
    app.time_range_end,
    app.created_at,
    COUNT(DISTINCT le.id) as log_entry_count,
    COUNT(DISTINCT CASE WHEN le.level = 'error' THEN le.id END) as error_count,
    COUNT(DISTINCT CASE WHEN le.level = 'warning' THEN le.id END) as warning_count
FROM applications app
JOIN projects p ON app.project_id = p.id
LEFT JOIN log_entries le ON app.id = le.application_id
GROUP BY app.id;

-- Vacuum and analyze for optimal performance
VACUUM;
ANALYZE;
