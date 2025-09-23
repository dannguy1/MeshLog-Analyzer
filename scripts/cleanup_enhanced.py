#!/usr/bin/env python3
"""
Enhanced Cleanup Script for prplOS LCM Log Analysis System
Supports both old and new extraction reuse architecture
"""

import os
import sys
import shutil
import argparse
import subprocess
import json
from pathlib import Path
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SystemCleanup:
    """Enhanced system cleanup with extraction reuse support"""
    
    def __init__(self, backup=False, dry_run=False, verbose=False):
        self.backup = backup
        self.dry_run = dry_run
        self.verbose = verbose
        self.project_name = "prplos-lcm-log-analysis"
        self.backup_dir = None
        
        if verbose:
            logging.getLogger().setLevel(logging.DEBUG)
    
    def log_info(self, message):
        """Log info message"""
        logger.info(message)
    
    def log_success(self, message):
        """Log success message"""
        logger.info(f"✅ {message}")
    
    def log_warning(self, message):
        """Log warning message"""
        logger.warning(f"⚠️  {message}")
    
    def log_error(self, message):
        """Log error message"""
        logger.error(f"❌ {message}")
    
    def create_backup(self):
        """Create backup before cleanup"""
        if not self.backup:
            return
        
        self.log_info("Creating backup before cleanup...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_dir = Path(f"backups/cleanup_{timestamp}")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Backup data directory
        data_dir = Path("data")
        if data_dir.exists() and any(data_dir.iterdir()):
            self.log_info("Backing up data directory...")
            if not self.dry_run:
                shutil.copytree(data_dir, self.backup_dir / "data")
            self.log_success(f"Data backed up to: {self.backup_dir / 'data'}")
        
        # Backup logs directory
        logs_dir = Path("logs")
        if logs_dir.exists() and any(logs_dir.iterdir()):
            self.log_info("Backing up logs directory...")
            if not self.dry_run:
                shutil.copytree(logs_dir, self.backup_dir / "logs")
            self.log_success(f"Logs backed up to: {self.backup_dir / 'logs'}")
        
        # Backup configuration files
        config_files = ["projects.json", "analyses.json", ".env"]
        for config_file in config_files:
            if Path(config_file).exists():
                self.log_info(f"Backing up {config_file}...")
                if not self.dry_run:
                    shutil.copy2(config_file, self.backup_dir / config_file)
        
        self.log_success(f"Backup created at: {self.backup_dir}")
    
    def stop_processes(self):
        """Stop running processes"""
        self.log_info("Stopping running processes...")
        
        processes_to_stop = ["uvicorn", "vite", "npm"]
        
        for process in processes_to_stop:
            try:
                # Check if process is running
                result = subprocess.run(
                    ["pgrep", "-f", process],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    pids = result.stdout.strip().split('\n')
                    self.log_info(f"Stopping {process} processes: {', '.join(pids)}")
                    
                    if not self.dry_run:
                        subprocess.run(["pkill", "-f", process], check=False)
                    
                    self.log_success(f"{process} processes stopped")
                else:
                    self.log_info(f"No {process} processes running")
                    
            except Exception as e:
                self.log_error(f"Failed to stop {process} processes: {e}")
    
    def stop_containers(self):
        """Stop Docker containers"""
        self.log_info("Stopping Docker containers...")
        
        try:
            # Check if Docker is available
            subprocess.run(["docker", "--version"], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.log_info("Docker not available, skipping container cleanup")
            return
        
        try:
            # Stop running containers
            result = subprocess.run(
                ["docker", "ps", "-q", "--filter", f"name={self.project_name}"],
                capture_output=True,
                text=True
            )
            
            if result.stdout.strip():
                container_ids = result.stdout.strip().split('\n')
                self.log_info(f"Stopping containers: {', '.join(container_ids)}")
                
                if not self.dry_run:
                    subprocess.run(
                        ["docker", "stop"] + container_ids,
                        check=False
                    )
                
                self.log_success("Running containers stopped")
            
            # Remove stopped containers
            result = subprocess.run(
                ["docker", "ps", "-aq", "--filter", f"name={self.project_name}"],
                capture_output=True,
                text=True
            )
            
            if result.stdout.strip():
                container_ids = result.stdout.strip().split('\n')
                self.log_info(f"Removing containers: {', '.join(container_ids)}")
                
                if not self.dry_run:
                    subprocess.run(
                        ["docker", "rm"] + container_ids,
                        check=False
                    )
                
                self.log_success("Containers removed")
            else:
                self.log_info("No containers to remove")
                
        except Exception as e:
            self.log_error(f"Failed to clean up containers: {e}")
    
    def clean_data_directories(self):
        """Clean data directories (both old and new structure)"""
        self.log_info("Cleaning data directories...")
        
        # Use configured data directory from environment
        try:
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from app.core.config import get_settings
            settings = get_settings()
            data_dir = Path(settings.DATA_DIR)
        except ImportError:
            # Fallback to relative data directory if app module not available
            data_dir = Path("data")
            self.log_warning("Could not import app module, using relative data directory")
        
        if not data_dir.exists():
            self.log_info("Data directory does not exist")
            return
        
        # Show what we're cleaning
        if any(data_dir.iterdir()):
            self.log_info("Data directory contents:")
            for item in list(data_dir.iterdir())[:20]:  # Show first 20 items
                size = self._get_directory_size(item) if item.is_dir() else item.stat().st_size
                self.log_info(f"  {item.name} ({self._format_size(size)})")
            
            total_items = len(list(data_dir.iterdir()))
            if total_items > 20:
                self.log_info(f"  ... and {total_items - 20} more items")
        
        # Clean both old and new extraction structures
        self._clean_extraction_directories(data_dir)
        
        # Clean other data files
        self._clean_data_files(data_dir)
        
        self.log_success("Data directories cleaned")
    
    def _clean_extraction_directories(self, data_dir):
        """Clean extraction directories (both old and new structure)"""
        
        # Clean old timestamp-based extractions
        old_extractions = list(data_dir.glob("extracted/extract_*"))
        if old_extractions:
            self.log_info(f"Found {len(old_extractions)} old timestamp-based extractions")
            for extraction in old_extractions:
                size = self._get_directory_size(extraction)
                self.log_info(f"  Removing: {extraction.name} ({self._format_size(size)})")
                if not self.dry_run:
                    shutil.rmtree(extraction)
        
        # Clean new project-based extractions
        projects_dir = data_dir / "projects"
        if projects_dir.exists():
            projects = list(projects_dir.iterdir())
            if projects:
                self.log_info(f"Found {len(projects)} project-based extractions")
                for project in projects:
                    if project.is_dir():
                        extraction_dir = project / "extracted"
                        if extraction_dir.exists():
                            size = self._get_directory_size(extraction_dir)
                            self.log_info(f"  Removing: {project.name}/extracted ({self._format_size(size)})")
                            if not self.dry_run:
                                shutil.rmtree(extraction_dir)
        
        # Clean empty directories
        if not self.dry_run:
            self._clean_empty_directories(data_dir)
    
    def _clean_data_files(self, data_dir):
        """Clean data files"""
        data_files = ["projects.json", "analyses.json", "*.db", "*.sqlite"]
        
        for pattern in data_files:
            for file_path in data_dir.glob(pattern):
                if file_path.is_file():
                    size = file_path.stat().st_size
                    self.log_info(f"  Removing: {file_path.name} ({self._format_size(size)})")
                    if not self.dry_run:
                        file_path.unlink()
    
    def _clean_empty_directories(self, directory):
        """Remove empty directories"""
        for item in directory.rglob("*"):
            if item.is_dir() and not any(item.iterdir()):
                self.log_info(f"  Removing empty directory: {item}")
                item.rmdir()
    
    def clean_logs(self):
        """Clean logs directory"""
        self.log_info("Cleaning logs directory...")
        
        logs_dir = Path("logs")
        if not logs_dir.exists():
            self.log_info("Logs directory does not exist")
            return
        
        if any(logs_dir.iterdir()):
            log_files = list(logs_dir.iterdir())
            total_size = sum(f.stat().st_size for f in log_files if f.is_file())
            self.log_info(f"Found {len(log_files)} log files ({self._format_size(total_size)})")
            
            if not self.dry_run:
                shutil.rmtree(logs_dir)
                logs_dir.mkdir()
            
            self.log_success("Logs directory cleaned")
        else:
            self.log_info("Logs directory is already empty")
    
    def clean_cache(self):
        """Clean cache directories"""
        self.log_info("Cleaning cache directories...")
        
        # Python cache
        self._clean_python_cache()
        
        # Node.js cache
        self._clean_node_cache()
        
        # Temporary files
        self._clean_temp_files()
        
        self.log_success("Cache directories cleaned")
    
    def reinitialize_database(self):
        """Reinitialize the database after cleanup"""
        self.log_info("Reinitializing database...")
        
        try:
            # Use configured data directory from environment
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from app.core.config import get_settings
            settings = get_settings()
            data_dir = Path(settings.DATA_DIR)
            
            # Create projects directory structure
            projects_dir = data_dir / "projects"
            projects_dir.mkdir(parents=True, exist_ok=True)
            self.log_info(f"Created projects directory: {projects_dir}")
            
            # Initialize empty projects.json
            projects_file = data_dir / "projects.json"
            with open(projects_file, 'w') as f:
                f.write('[]')
            self.log_info(f"Created empty projects.json: {projects_file}")
            
            self.log_success("Database reinitialized successfully")
            
        except ImportError:
            # Fallback to relative data directory if app module not available
            data_dir = Path("data")
            self.log_warning("Could not import app module, using relative data directory")
            
            # Create projects directory structure
            projects_dir = data_dir / "projects"
            projects_dir.mkdir(parents=True, exist_ok=True)
            self.log_info(f"Created projects directory: {projects_dir}")
            
            # Initialize empty projects.json
            projects_file = data_dir / "projects.json"
            with open(projects_file, 'w') as f:
                f.write('[]')
            self.log_info(f"Created empty projects.json: {projects_file}")
            
            self.log_success("Database reinitialized successfully")
            
        except Exception as e:
            self.log_error(f"Failed to reinitialize database: {e}")
    
    def _clean_python_cache(self):
        """Clean Python cache files"""
        cache_patterns = ["**/__pycache__", "**/*.pyc", "**/*.pyo"]
        
        for pattern in cache_patterns:
            for cache_path in Path(".").glob(pattern):
                if cache_path.is_dir():
                    self.log_info(f"  Removing Python cache: {cache_path}")
                    if not self.dry_run:
                        shutil.rmtree(cache_path)
                elif cache_path.is_file():
                    self.log_info(f"  Removing Python cache: {cache_path}")
                    if not self.dry_run:
                        cache_path.unlink()
    
    def _clean_node_cache(self):
        """Clean Node.js cache files"""
        node_cache_dirs = [
            "ui/node_modules/.cache",
            "ui/dist",
            "ui/.next"
        ]
        
        for cache_dir in node_cache_dirs:
            cache_path = Path(cache_dir)
            if cache_path.exists():
                size = self._get_directory_size(cache_path)
                self.log_info(f"  Removing Node.js cache: {cache_dir} ({self._format_size(size)})")
                if not self.dry_run:
                    shutil.rmtree(cache_path)
    
    def _clean_temp_files(self):
        """Clean temporary files"""
        temp_patterns = ["**/*.tmp", "**/*.temp", "**/.DS_Store", "**/Thumbs.db"]
        
        for pattern in temp_patterns:
            for temp_file in Path(".").glob(pattern):
                self.log_info(f"  Removing temp file: {temp_file}")
                if not self.dry_run:
                    temp_file.unlink()
    
    def show_status(self):
        """Show cleanup status"""
        self.log_info("=== Cleanup Status ===")
        
        # Check processes
        self._check_processes()
        
        # Check containers
        self._check_containers()
        
        # Check directories
        self._check_directories()
        
        # Show next steps
        self.log_info("=== Next Steps ===")
        self.log_info("1. Start backend: ./scripts/backend-start.sh")
        self.log_info("2. Start frontend: ./scripts/frontend-start.sh")
        self.log_info("3. Or start both: ./dev-start.sh")
        
        if self.backup_dir:
            self.log_info(f"4. Backup available at: {self.backup_dir}")
    
    def _check_processes(self):
        """Check running processes"""
        processes = ["uvicorn", "vite", "npm"]
        running_processes = []
        
        for process in processes:
            try:
                result = subprocess.run(
                    ["pgrep", "-f", process],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    running_processes.extend(result.stdout.strip().split('\n'))
            except Exception:
                pass
        
        if running_processes:
            self.log_warning(f"Some processes still running: {', '.join(running_processes)}")
        else:
            self.log_success("No processes running")
    
    def _check_containers(self):
        """Check Docker containers"""
        try:
            result = subprocess.run(
                ["docker", "ps", "-aq", "--filter", f"name={self.project_name}"],
                capture_output=True,
                text=True
            )
            
            if result.stdout.strip():
                self.log_warning("Some containers still exist")
            else:
                self.log_success("No containers exist")
        except Exception:
            self.log_info("Docker not available")
    
    def _check_directories(self):
        """Check directory status"""
        directories = ["data", "logs"]
        
        for directory in directories:
            dir_path = Path(directory)
            if dir_path.exists() and any(dir_path.iterdir()):
                items = list(dir_path.iterdir())
                self.log_warning(f"{directory} directory not empty ({len(items)} items)")
            else:
                self.log_success(f"{directory} directory is empty")
    
    def _get_directory_size(self, directory):
        """Get directory size in bytes"""
        total_size = 0
        try:
            for file_path in directory.rglob("*"):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
        except Exception:
            pass
        return total_size
    
    def _format_size(self, size_bytes):
        """Format size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    def run_cleanup(self):
        """Run the complete cleanup process"""
        self.log_info("Starting prplOS LCM Log Analysis System Cleanup")
        self.log_info("=" * 50)
        
        # Show configuration
        self.log_info("Configuration:")
        self.log_info(f"  Backup: {self.backup}")
        self.log_info(f"  Dry Run: {self.dry_run}")
        self.log_info(f"  Verbose: {self.verbose}")
        self.log_info("")
        
        if self.dry_run:
            self.log_warning("DRY RUN MODE - No actual cleanup will be performed")
            self.log_info("")
        
        # Confirm before proceeding (unless dry run)
        if not self.dry_run:
            self.log_warning("This will remove all data, logs, and stop all processes.")
            response = input("Are you sure you want to continue? (y/N): ")
            if response.lower() != 'y':
                self.log_info("Cleanup cancelled by user")
                return
        
        # Execute cleanup steps
        if self.backup:
            self.create_backup()
        self.stop_processes()
        self.stop_containers()
        self.clean_data_directories()
        self.clean_logs()
        self.clean_cache()
        self.reinitialize_database()
        
        # Show final status
        self.show_status()
        
        if self.dry_run:
            self.log_info("Dry run completed - no actual cleanup performed")
        else:
            self.log_success("Cleanup completed successfully!")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Enhanced Cleanup Script for prplOS LCM Log Analysis System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Basic cleanup
  %(prog)s --backup           # Cleanup with backup
  %(prog)s --dry-run          # See what would be cleaned
  %(prog)s --verbose          # Verbose output
  %(prog)s --no-processes     # Skip stopping processes
  %(prog)s --no-containers    # Skip stopping containers
  %(prog)s --no-data          # Skip cleaning data
  %(prog)s --no-cache         # Skip cleaning cache
        """
    )
    
    parser.add_argument(
        "-b", "--backup",
        action="store_true",
        help="Create backup before cleanup"
    )
    
    parser.add_argument(
        "-d", "--dry-run",
        action="store_true",
        help="Show what would be cleaned without actually cleaning"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )
    
    parser.add_argument(
        "--no-processes",
        action="store_true",
        help="Skip stopping processes"
    )
    
    parser.add_argument(
        "--no-containers",
        action="store_true",
        help="Skip stopping containers"
    )
    
    parser.add_argument(
        "--no-data",
        action="store_true",
        help="Skip cleaning data directories"
    )
    
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Skip cleaning cache"
    )
    
    parser.add_argument(
        "--no-reinit",
        action="store_true",
        help="Skip database reinitialization"
    )
    
    args = parser.parse_args()
    
    # Create cleanup instance
    cleanup = SystemCleanup(
        backup=args.backup,
        dry_run=args.dry_run,
        verbose=args.verbose
    )
    
    # Set skip flags
    if args.no_processes:
        cleanup.stop_processes = lambda: cleanup.log_info("Skipping process cleanup")
    if args.no_containers:
        cleanup.stop_containers = lambda: cleanup.log_info("Skipping container cleanup")
    if args.no_data:
        cleanup.clean_data_directories = lambda: cleanup.log_info("Skipping data cleanup")
    if args.no_cache:
        cleanup.clean_cache = lambda: cleanup.log_info("Skipping cache cleanup")
    if args.no_reinit:
        cleanup.reinitialize_database = lambda: cleanup.log_info("Skipping database reinitialization")
    
    # Run cleanup
    try:
        cleanup.run_cleanup()
    except KeyboardInterrupt:
        cleanup.log_info("Cleanup interrupted by user")
        sys.exit(1)
    except Exception as e:
        cleanup.log_error(f"Cleanup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
