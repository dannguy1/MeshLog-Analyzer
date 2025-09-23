#!/usr/bin/env python3
"""
SQLite Database Setup Script for prplOS LCM Log Analysis System
"""

import os
import sys
import sqlite3
import json
from datetime import datetime
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.config import get_settings

def setup_sqlite_database():
    """Setup SQLite database with schema and initial data"""
    
    settings = get_settings()
    database_url = settings.DATABASE_URL
    
    # Extract database path from SQLite URL
    if database_url.startswith('sqlite:///'):
        db_path = database_url.replace('sqlite:///', '')
    elif database_url.startswith('sqlite://'):
        db_path = database_url.replace('sqlite://', '')
    else:
        db_path = database_url
    
    # Ensure directory exists
    db_dir = os.path.dirname(db_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
    
    print(f"🔧 Setting up SQLite database: {db_path}")
    
    # Connect to SQLite database (creates it if it doesn't exist)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Enable row factory for better access
    
    try:
        # Read and execute schema
        schema_file = os.path.join(os.path.dirname(__file__), 'sqlite_schema.sql')
        if os.path.exists(schema_file):
            print("📖 Reading schema file...")
            with open(schema_file, 'r') as f:
                schema_sql = f.read()
            
            # Split and execute SQL statements
            statements = schema_sql.split(';')
            for statement in statements:
                statement = statement.strip()
                if statement and not statement.startswith('--'):
                    try:
                        conn.execute(statement)
                    except sqlite3.Error as e:
                        print(f"⚠️  Warning: {e}")
                        continue
            
            conn.commit()
            print("✅ Schema created successfully")
        else:
            print("⚠️  Schema file not found, creating basic tables...")
            create_basic_tables(conn)
        
        # Insert sample data
        insert_sample_data(conn)
        
        # Verify setup
        verify_database_setup(conn)
        
        print("🎉 SQLite database setup completed successfully!")
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        raise
    finally:
        conn.close()

def create_basic_tables(conn):
    """Create basic tables if schema file is not available"""
    
    tables = [
        """
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            file_path TEXT NOT NULL,
            file_size INTEGER,
            status TEXT DEFAULT 'uploading',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
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
            result_data TEXT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS applications (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            name TEXT NOT NULL,
            log_file_path TEXT,
            total_entries INTEGER DEFAULT 0,
            time_range_start TIMESTAMP,
            time_range_end TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    ]
    
    for table_sql in tables:
        conn.execute(table_sql)
    
    conn.commit()

def insert_sample_data(conn):
    """Insert sample data for development"""
    
    print("📝 Inserting sample data...")
    
    # Sample projects
    projects = [
        ('sample-project-1', 'Sample Project 1', 'Test project for development', '/uploads/sample1.tar.gz', 1024000, 'completed'),
        ('sample-project-2', 'Sample Project 2', 'Another test project', '/uploads/sample2.tar.gz', 2048000, 'processing'),
        ('sample-project-3', 'Sample Project 3', 'Third test project', '/uploads/sample3.tar.gz', 512000, 'uploading')
    ]
    
    for project in projects:
        try:
            conn.execute("""
                INSERT OR IGNORE INTO projects (id, name, description, file_path, file_size, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, project)
        except sqlite3.Error as e:
            print(f"⚠️  Warning inserting project {project[0]}: {e}")
    
    # Sample analyses
    analyses = [
        ('analysis-1', 'sample-project-1', 'completed', 100, 'completed', datetime.now(), datetime.now(), datetime.now(), None, json.dumps({'summary': 'Test analysis completed'})),
        ('analysis-2', 'sample-project-2', 'running', 45, 'anomaly_detection', datetime.now(), datetime.now(), None, None, None)
    ]
    
    for analysis in analyses:
        try:
            conn.execute("""
                INSERT OR IGNORE INTO analyses (id, project_id, status, progress_percentage, current_stage, 
                                               created_timestamp, started_timestamp, completed_timestamp, error_message, result_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, analysis)
        except sqlite3.Error as e:
            print(f"⚠️  Warning inserting analysis {analysis[0]}: {e}")
    
    # Sample applications
    applications = [
        ('app-1', 'sample-project-1', 'wnc-steer', '/logs/wnc-steer.log', 1500, datetime.now(), datetime.now()),
        ('app-2', 'sample-project-1', 'wnc-acs', '/logs/wnc-acs.log', 2300, datetime.now(), datetime.now()),
        ('app-3', 'sample-project-2', 'wnc-tpyopt', '/logs/wnc-tpyopt.log', 800, datetime.now(), datetime.now())
    ]
    
    for app in applications:
        try:
            conn.execute("""
                INSERT OR IGNORE INTO applications (id, project_id, name, log_file_path, total_entries, 
                                                  time_range_start, time_range_end)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, app)
        except sqlite3.Error as e:
            print(f"⚠️  Warning inserting application {app[0]}: {e}")
    
    conn.commit()
    print("✅ Sample data inserted successfully")

def verify_database_setup(conn):
    """Verify that the database setup was successful"""
    
    print("🔍 Verifying database setup...")
    
    # Check tables exist
    tables = ['projects', 'analyses', 'applications', 'log_entries', 'time_series_data', 'anomalies', 'predictions', 'alerts']
    
    for table in tables:
        try:
            cursor = conn.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            if cursor.fetchone():
                print(f"✅ Table '{table}' exists")
            else:
                print(f"⚠️  Table '{table}' not found")
        except sqlite3.Error as e:
            print(f"❌ Error checking table '{table}': {e}")
    
    # Check sample data
    try:
        project_count = conn.execute("SELECT COUNT(*) FROM projects").fetchone()[0]
        analysis_count = conn.execute("SELECT COUNT(*) FROM analyses").fetchone()[0]
        app_count = conn.execute("SELECT COUNT(*) FROM applications").fetchone()[0]
        
        print(f"📊 Sample data counts: {project_count} projects, {analysis_count} analyses, {app_count} applications")
    except sqlite3.Error as e:
        print(f"❌ Error checking sample data: {e}")
    
    # Check SQLite configuration
    try:
        pragmas = [
            ("foreign_keys", "PRAGMA foreign_keys"),
            ("journal_mode", "PRAGMA journal_mode"),
            ("synchronous", "PRAGMA synchronous"),
            ("cache_size", "PRAGMA cache_size")
        ]
        
        for name, pragma in pragmas:
            result = conn.execute(pragma).fetchone()
            print(f"⚙️  {name}: {result[0] if result else 'N/A'}")
    except sqlite3.Error as e:
        print(f"❌ Error checking SQLite configuration: {e}")

def get_database_info(conn):
    """Get database information"""
    
    try:
        # Get database file size
        db_path = conn.execute("PRAGMA database_list").fetchone()[2]
        file_size = os.path.getsize(db_path) if os.path.exists(db_path) else 0
        
        # Get table counts
        tables = {}
        for table in ['projects', 'analyses', 'applications', 'log_entries', 'time_series_data', 'anomalies', 'predictions', 'alerts']:
            try:
                count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                tables[table] = count
            except sqlite3.Error:
                tables[table] = 0
        
        return {
            'file_path': db_path,
            'file_size_bytes': file_size,
            'file_size_mb': round(file_size / (1024 * 1024), 2),
            'tables': tables
        }
    except Exception as e:
        print(f"❌ Error getting database info: {e}")
        return {}

def main():
    """Main function"""
    
    print("🚀 prplOS LCM Log Analysis System - SQLite Database Setup")
    print("=" * 60)
    
    try:
        # Setup database
        setup_sqlite_database()
        
        # Get and display database info
        settings = get_settings()
        database_url = settings.DATABASE_URL
        
        if database_url.startswith('sqlite:///'):
            db_path = database_url.replace('sqlite:///', '')
        elif database_url.startswith('sqlite://'):
            db_path = database_url.replace('sqlite://', '')
        else:
            db_path = database_url
        
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            info = get_database_info(conn)
            conn.close()
            
            print("\n📋 Database Information:")
            print(f"   File: {info.get('file_path', 'N/A')}")
            print(f"   Size: {info.get('file_size_mb', 0)} MB")
            print(f"   Tables: {len(info.get('tables', {}))}")
            
            print("\n📊 Table Row Counts:")
            for table, count in info.get('tables', {}).items():
                print(f"   {table}: {count} rows")
        
        print("\n✅ Setup completed successfully!")
        print("\nNext steps:")
        print("1. Start the application: python -m uvicorn app.main:app --reload")
        print("2. Access the API at: http://localhost:8000")
        print("3. Check the health endpoint: http://localhost:8000/api/v1/health")
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
