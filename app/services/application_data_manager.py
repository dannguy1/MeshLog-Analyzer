"""
Application Data Manager - SQLite-based data storage for applications
Handles log data, metadata, and analysis results in a unified structure
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import structlog

logger = structlog.get_logger(__name__)

class ApplicationDataManager:
    """Manages application data using SQLite for efficient querying and analysis"""
    
    def __init__(self, project_id: str, application_name: str, data_dir: str):
        self.project_id = project_id
        self.application_name = application_name
        self.data_dir = Path(data_dir)
        self.app_dir = self.data_dir / "projects" / project_id / "applications" / application_name
        self.db_path = self.app_dir / "data.db"
        self.metadata_path = self.app_dir / "metadata.json"
        self.analysis_results_path = self.app_dir / "analysis_results.json"
        
        # Ensure directory exists
        self.app_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Log entries table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS log_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    container_id TEXT,
                    log_level TEXT,
                    message_type TEXT,
                    message TEXT NOT NULL,
                    raw_line TEXT,
                    line_number INTEGER,
                    file_path TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for efficient querying
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON log_entries(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_log_level ON log_entries(log_level)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_container_id ON log_entries(container_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_message_type ON log_entries(message_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_message ON log_entries(message)")
            
            # Full-text search index
            cursor.execute("CREATE VIRTUAL TABLE IF NOT EXISTS log_entries_fts USING fts5(message, content='log_entries', content_rowid='id')")
            
            # Check if message_type column exists, if not add it (for existing databases)
            cursor.execute("PRAGMA table_info(log_entries)")
            columns = [column[1] for column in cursor.fetchall()]
            if 'message_type' not in columns:
                cursor.execute("ALTER TABLE log_entries ADD COLUMN message_type TEXT")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_message_type ON log_entries(message_type)")
                logger.info(f"Added message_type column to existing database for {self.application_name}")
            
            conn.commit()
            logger.info(f"Initialized database for {self.application_name}", db_path=str(self.db_path))
    
    def store_log_entries(self, log_entries: List[Any]) -> int:
        """Store log entries in SQLite database"""
        if not log_entries:
            return 0
            
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Prepare data for insertion
            data = []
            for entry in log_entries:
                # Handle both LogEntry objects and dictionaries
                if hasattr(entry, 'to_dict'):
                    # LogEntry object - convert to dict first
                    entry_dict = entry.to_dict()
                    data.append((
                        entry_dict.get('timestamp'),
                        entry_dict.get('container_id'),
                        entry_dict.get('log_level'),
                        entry_dict.get('message_type', 'general_info'),
                        entry_dict.get('message'),
                        entry_dict.get('raw_line'),
                        entry_dict.get('line_number'),
                        entry_dict.get('file_path')
                    ))
                elif isinstance(entry, dict):
                    # Already a dictionary
                    data.append((
                        entry.get('timestamp'),
                        entry.get('container_id'),
                        entry.get('log_level'),
                        entry.get('message_type', 'general_info'),
                        entry.get('message'),
                        entry.get('raw_line'),
                        entry.get('line_number'),
                        entry.get('file_path')
                    ))
                else:
                    # Direct attribute access for LogEntry objects without to_dict
                    data.append((
                        entry.timestamp.isoformat() if hasattr(entry.timestamp, 'isoformat') else str(entry.timestamp),
                        entry.container_id,
                        entry.log_level.value if hasattr(entry.log_level, 'value') else str(entry.log_level),
                        getattr(entry, 'message_type', 'general_info'),
                        entry.message,
                        entry.raw_line,
                        entry.line_number,
                        entry.file_path
                    ))
            
            # Insert in batches for performance
            cursor.executemany("""
                INSERT INTO log_entries (timestamp, container_id, log_level, message_type, message, raw_line, line_number, file_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, data)
            
            # Update FTS index
            cursor.execute("INSERT INTO log_entries_fts(log_entries_fts) VALUES('rebuild')")
            
            conn.commit()
            count = cursor.rowcount
            logger.info(f"Stored {count} log entries for {self.application_name}")
            return count
    
    def search_logs(self, 
                   query: Optional[str] = None,
                   log_level: Optional[str] = None,
                   container_id: Optional[str] = None,
                   message_type: Optional[str] = None,
                   message_types: Optional[List[str]] = None,
                   start_time: Optional[str] = None,
                   end_time: Optional[str] = None,
                   limit: int = 1000,
                   offset: int = 0) -> List[Dict[str, Any]]:
        """Search log entries with various filters including message type"""
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Build query
            where_conditions = []
            params = []
            
            if query:
                # Use FTS for full-text search
                where_conditions.append("id IN (SELECT rowid FROM log_entries_fts WHERE log_entries_fts MATCH ?)")
                params.append(query)
            
            if log_level:
                where_conditions.append("log_level = ?")
                params.append(log_level)
            
            if container_id:
                where_conditions.append("container_id = ?")
                params.append(container_id)
            
            if message_types and len(message_types) > 0:
                # Handle multiple message types with OR logic
                placeholders = ",".join(["?" for _ in message_types])
                where_conditions.append(f"message_type IN ({placeholders})")
                params.extend(message_types)
            elif message_type:
                where_conditions.append("message_type = ?")
                params.append(message_type)
            
            if start_time:
                where_conditions.append("timestamp >= ?")
                params.append(start_time)
            
            if end_time:
                where_conditions.append("timestamp <= ?")
                params.append(end_time)
            
            where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
            
            sql = f"""
                SELECT * FROM log_entries 
                WHERE {where_clause}
                ORDER BY timestamp DESC
                LIMIT ? OFFSET ?
            """
            params.extend([limit, offset])
            
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            # Convert to list of dicts
            results = []
            for row in rows:
                results.append(dict(row))
            
            logger.info(f"Found {len(results)} log entries for {self.application_name}")
            return results
    
    def get_log_statistics(self) -> Dict[str, Any]:
        """Get statistical summary of log data"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Total count
            cursor.execute("SELECT COUNT(*) FROM log_entries")
            total_logs = cursor.fetchone()[0]
            
            # Log levels
            cursor.execute("""
                SELECT log_level, COUNT(*) as count 
                FROM log_entries 
                GROUP BY log_level
            """)
            log_levels = dict(cursor.fetchall())
            
            # Time range
            cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM log_entries")
            time_range = cursor.fetchone()
            
            # Container IDs
            cursor.execute("""
                SELECT container_id, COUNT(*) as count 
                FROM log_entries 
                GROUP BY container_id
                ORDER BY count DESC
            """)
            containers = dict(cursor.fetchall())
            
            return {
                "total_logs": total_logs,
                "log_levels": log_levels,
                "time_range": {
                    "start": time_range[0],
                    "end": time_range[1]
                },
                "containers": containers
            }
    
    def store_metadata(self, metadata: Dict[str, Any]):
        """Store application metadata"""
        metadata["updated_at"] = datetime.now().isoformat()
        with open(self.metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        logger.info(f"Stored metadata for {self.application_name}")
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get application metadata"""
        if self.metadata_path.exists():
            with open(self.metadata_path, 'r') as f:
                return json.load(f)
        return {}
    
    def store_analysis_results(self, analysis_results: Dict[str, Any]):
        """Store analysis results"""
        analysis_results["stored_at"] = datetime.now().isoformat()
        with open(self.analysis_results_path, 'w') as f:
            json.dump(analysis_results, f, indent=2)
        logger.info(f"Stored analysis results for {self.application_name}")
    
    def get_analysis_results(self) -> Dict[str, Any]:
        """Get analysis results"""
        if self.analysis_results_path.exists():
            with open(self.analysis_results_path, 'r') as f:
                return json.load(f)
        return {}
    
    def get_total_log_count(self,
                           query: Optional[str] = None,
                           log_level: Optional[str] = None,
                           container_id: Optional[str] = None,
                           message_type: Optional[str] = None,
                           message_types: Optional[List[str]] = None,
                           start_time: Optional[str] = None,
                           end_time: Optional[str] = None) -> int:
        """Get total count of log entries matching the criteria"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            where_conditions = []
            params = []
            
            if query:
                where_conditions.append("(message LIKE ? OR raw_line LIKE ?)")
                params.extend([f"%{query}%", f"%{query}%"])
            
            if log_level:
                where_conditions.append("log_level = ?")
                params.append(log_level)
            
            if container_id:
                where_conditions.append("container_id = ?")
                params.append(container_id)
            
            if message_types and len(message_types) > 0:
                # Handle multiple message types with OR logic
                placeholders = ",".join(["?" for _ in message_types])
                where_conditions.append(f"message_type IN ({placeholders})")
                params.extend(message_types)
            elif message_type:
                where_conditions.append("message_type = ?")
                params.append(message_type)
            
            if start_time:
                where_conditions.append("timestamp >= ?")
                params.append(start_time)
            
            if end_time:
                where_conditions.append("timestamp <= ?")
                params.append(end_time)
            
            where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
            
            cursor.execute(f"SELECT COUNT(*) FROM log_entries {where_clause}", params)
            return cursor.fetchone()[0]

    def get_data_summary(self) -> Dict[str, Any]:
        """Get comprehensive data summary"""
        metadata = self.get_metadata()
        log_stats = self.get_log_statistics()
        analysis_results = self.get_analysis_results()
        
        return {
            "application_name": self.application_name,
            "project_id": self.project_id,
            "metadata": metadata,
            "log_statistics": log_stats,
            "has_analysis_results": bool(analysis_results),
            "analysis_timestamp": analysis_results.get("stored_at") if analysis_results else None,
            "data_directory": str(self.app_dir)
        }
    
    def cleanup_old_data(self, days_to_keep: int = 30) -> int:
        """Clean up old log entries"""
        cutoff_date = datetime.now().replace(day=datetime.now().day - days_to_keep).isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM log_entries WHERE timestamp < ?", (cutoff_date,))
            deleted_count = cursor.rowcount
            
            # Rebuild FTS index
            cursor.execute("INSERT INTO log_entries_fts(log_entries_fts) VALUES('rebuild')")
            conn.commit()
            
            logger.info(f"Cleaned up {deleted_count} old log entries for {self.application_name}")
            return deleted_count
    
    def export_to_csv(self, output_path: str, filters: Optional[Dict[str, Any]] = None) -> int:
        """Export log data to CSV"""
        import csv
        
        logs = self.search_logs(**filters) if filters else self.search_logs(limit=1000000)
        
        if not logs:
            return 0
        
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = logs[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(logs)
        
        logger.info(f"Exported {len(logs)} log entries to {output_path}")
        return len(logs)
    
    def get_database_size(self) -> int:
        """Get database file size in bytes"""
        return self.db_path.stat().st_size if self.db_path.exists() else 0
    
    def get_advanced_analytics(self) -> Dict[str, Any]:
        """Get advanced analytics including trends, correlations, and patterns"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                analytics = {}
                
                # Time series analysis
                cursor.execute("""
                    SELECT 
                        DATE(timestamp) as date,
                        strftime('%H', timestamp) as hour,
                        COUNT(*) as log_count,
                        COUNT(CASE WHEN log_level IN ('error', 'critical') THEN 1 END) as error_count
                    FROM log_entries
                    GROUP BY DATE(timestamp), strftime('%H', timestamp)
                    ORDER BY date, hour
                """)
                
                time_series = []
                for row in cursor.fetchall():
                    time_series.append({
                        'date': row['date'],
                        'hour': row['hour'],
                        'log_count': row['log_count'],
                        'error_count': row['error_count'],
                        'error_rate': round((row['error_count'] / row['log_count']) * 100, 2) if row['log_count'] > 0 else 0
                    })
                analytics['time_series'] = time_series
                
                # Trend analysis
                cursor.execute("""
                    SELECT 
                        DATE(timestamp) as date,
                        COUNT(*) as daily_count,
                        COUNT(CASE WHEN log_level IN ('error', 'critical') THEN 1 END) as daily_errors
                    FROM log_entries
                    GROUP BY DATE(timestamp)
                    ORDER BY date
                """)
                
                daily_trends = []
                for row in cursor.fetchall():
                    daily_trends.append({
                        'date': row['date'],
                        'log_count': row['daily_count'],
                        'error_count': row['daily_errors'],
                        'error_rate': round((row['daily_errors'] / row['daily_count']) * 100, 2) if row['daily_count'] > 0 else 0
                    })
                analytics['daily_trends'] = daily_trends
                
                # Error pattern analysis
                cursor.execute("""
                    SELECT 
                        message,
                        COUNT(*) as frequency,
                        MIN(timestamp) as first_occurrence,
                        MAX(timestamp) as last_occurrence
                    FROM log_entries
                    WHERE log_level IN ('error', 'critical', 'warning')
                    GROUP BY message
                    HAVING COUNT(*) > 1
                    ORDER BY frequency DESC
                    LIMIT 20
                """)
                
                error_patterns = []
                for row in cursor.fetchall():
                    error_patterns.append({
                        'message': row['message'][:200] + '...' if len(row['message']) > 200 else row['message'],
                        'frequency': row['frequency'],
                        'first_occurrence': row['first_occurrence'],
                        'last_occurrence': row['last_occurrence']
                    })
                analytics['error_patterns'] = error_patterns
                
                # Performance metrics
                cursor.execute("""
                    SELECT 
                        AVG(LENGTH(message)) as avg_message_length,
                        MIN(LENGTH(message)) as min_message_length,
                        MAX(LENGTH(message)) as max_message_length,
                        COUNT(CASE WHEN LENGTH(message) > 500 THEN 1 END) as long_messages,
                        COUNT(CASE WHEN message LIKE '%timeout%' OR message LIKE '%slow%' THEN 1 END) as performance_issues
                    FROM log_entries
                """)
                
                perf_stats = cursor.fetchone()
                analytics['performance_metrics'] = {
                    'avg_message_length': round(perf_stats['avg_message_length'], 2),
                    'min_message_length': perf_stats['min_message_length'],
                    'max_message_length': perf_stats['max_message_length'],
                    'long_messages_count': perf_stats['long_messages'],
                    'performance_issues_count': perf_stats['performance_issues']
                }
                
                # Container health analysis
                cursor.execute("""
                    SELECT 
                        container_id,
                        COUNT(*) as total_logs,
                        COUNT(CASE WHEN log_level IN ('error', 'critical') THEN 1 END) as error_count,
                        COUNT(CASE WHEN log_level = 'warning' THEN 1 END) as warning_count,
                        ROUND(COUNT(CASE WHEN log_level IN ('error', 'critical') THEN 1 END) * 100.0 / COUNT(*), 2) as error_rate
                    FROM log_entries
                    GROUP BY container_id
                    ORDER BY error_rate DESC
                """)
                
                container_health = []
                for row in cursor.fetchall():
                    container_health.append({
                        'container_id': row['container_id'],
                        'total_logs': row['total_logs'],
                        'error_count': row['error_count'],
                        'warning_count': row['warning_count'],
                        'error_rate': row['error_rate'],
                        'health_score': max(0, 100 - row['error_rate'])
                    })
                analytics['container_health'] = container_health
                
                return analytics
                
        except Exception as e:
            logger.error(f"Failed to get advanced analytics: {e}")
            return {}
    
    def get_correlation_analysis(self) -> Dict[str, Any]:
        """Analyze correlations between different log patterns"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                correlations = {}
                
                # Error correlation by hour
                cursor.execute("""
                    SELECT 
                        strftime('%H', timestamp) as hour,
                        COUNT(CASE WHEN log_level IN ('error', 'critical') THEN 1 END) as error_count,
                        COUNT(*) as total_count
                    FROM log_entries
                    GROUP BY strftime('%H', timestamp)
                    ORDER BY hour
                """)
                
                hourly_error_correlation = []
                for row in cursor.fetchall():
                    hourly_error_correlation.append({
                        'hour': row['hour'],
                        'error_count': row['error_count'],
                        'total_count': row['total_count'],
                        'error_rate': round((row['error_count'] / row['total_count']) * 100, 2) if row['total_count'] > 0 else 0
                    })
                correlations['hourly_error_pattern'] = hourly_error_correlation
                
                # Container correlation analysis
                cursor.execute("""
                    SELECT 
                        c1.container_id as container1,
                        c2.container_id as container2,
                        COUNT(*) as correlation_count
                    FROM log_entries c1
                    JOIN log_entries c2 ON ABS(strftime('%s', c1.timestamp) - strftime('%s', c2.timestamp)) <= 60
                    WHERE c1.container_id != c2.container_id
                    GROUP BY c1.container_id, c2.container_id
                    HAVING COUNT(*) > 10
                    ORDER BY correlation_count DESC
                    LIMIT 10
                """)
                
                container_correlations = []
                for row in cursor.fetchall():
                    container_correlations.append({
                        'container1': row['container1'],
                        'container2': row['container2'],
                        'correlation_count': row['correlation_count']
                    })
                correlations['container_correlations'] = container_correlations
                
                return correlations
                
        except Exception as e:
            logger.error(f"Failed to get correlation analysis: {e}")
            return {}

