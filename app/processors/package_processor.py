# prplOS LCM Log Analysis System - Package Processor

import os
import tarfile
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import logging

from app.models.core import PackageStructure, PackageMetadata, ContainerInfo, PackageStatus
from app.core.config import get_settings
from app.services.application_data_manager import ApplicationDataManager

logger = logging.getLogger(__name__)

class PackageProcessor:
    """Process containerized syslog packages"""
    
    def __init__(self):
        self.config = get_settings()
        self.supported_applications = [
            "wnc-steer",
            "wnc-acs", 
            "wnc-tpyopt",
            "otbr-agent",
            "prplos-lcm"
        ]
    
    def process_package(self, package_path: str, project_id: str = None, 
                       reuse_extraction: bool = True) -> PackageStructure:
        """Process package with optional extraction reuse"""
        logger.info(f"Processing package: {package_path} with project_id: {project_id}, reuse: {reuse_extraction}")
        
        if reuse_extraction and project_id:
            # Check for existing extraction
            existing_extraction = self._get_existing_extraction(project_id)
            if existing_extraction and self._validate_extraction_integrity(existing_extraction):
                logger.info(f"Reusing existing extraction for project {project_id}")
                return self._reconstruct_package_structure(existing_extraction)
            else:
                logger.warning(f"No valid extraction found for project {project_id}, cannot reuse")
                if not package_path:
                    raise ValueError("Cannot create new extraction without package_path and no existing extraction to reuse")
        
        # Create new extraction
        if not package_path:
            raise ValueError("Cannot create new extraction without package_path")
        
        extraction_path = self._extract_package(package_path, project_id)
        containers = self._analyze_package_structure(extraction_path)
        
        # Create PackageStructure object
        package_structure = self._create_package_structure(extraction_path, containers)
        
        # Set original filename from package path
        if package_path:
            package_structure.metadata.original_filename = os.path.basename(package_path)
        
        # Persist metadata for future reuse
        if project_id:
            logger.info(f"Persisting metadata for project {project_id}")
            self._persist_extraction_metadata(project_id, package_structure)
            logger.info(f"Metadata persistence completed for project {project_id}")
            
            # Store logs in SQLite using ApplicationDataManager
            if package_structure.is_valid:
                self._store_logs_in_sqlite(package_structure, project_id)
        
        return package_structure
    
    def _extract_package(self, package_path: str, project_id: str = None) -> str:
        """Extract tarball package to project-specific directory"""
        logger.info(f"Extracting package: {package_path}")
        
        if project_id:
            # Use configured data directory instead of hardcoded path
            from app.core.config import get_settings
            settings = get_settings()
            extraction_dir = os.path.join(
                settings.DATA_DIR,
                "projects",
                project_id,
                "extracted"
            )
        else:
            # No project_id provided - this should not happen in normal operation
            raise ValueError("project_id is required for package extraction")
        
        os.makedirs(extraction_dir, exist_ok=True)
        
        try:
            # Extract tarball
            with tarfile.open(package_path, 'r:*') as tar:
                tar.extractall(extraction_dir)
            
            logger.info(f"Package extracted to: {extraction_dir}")
            return extraction_dir
            
        except Exception as e:
            logger.error(f"Package extraction failed: {e}")
            # Cleanup on failure
            if os.path.exists(extraction_dir):
                shutil.rmtree(extraction_dir)
            raise
    
    def _analyze_package_structure(self, extraction_path: str) -> List[ContainerInfo]:
        """Analyze the structure of extracted package"""
        logger.info(f"Analyzing package structure: {extraction_path}")
        
        containers = []
        
        try:
            # Walk through extraction directory
            for root, dirs, files in os.walk(extraction_path):
                # Look for container directories (UUID-named)
                for dir_name in dirs:
                    if self._is_container_directory(dir_name):
                        container_path = os.path.join(root, dir_name)
                        container_info = self._analyze_container(container_path, dir_name)
                        if container_info:
                            containers.append(container_info)
            
            logger.info(f"Found {len(containers)} containers in package")
            return containers
            
        except Exception as e:
            logger.error(f"Package structure analysis failed: {e}")
            raise
    
    def _create_package_structure(self, extraction_path: str, containers: List[ContainerInfo]) -> PackageStructure:
        """Create PackageStructure object from containers list"""
        logger.info(f"Creating PackageStructure from {len(containers)} containers")
        
        # Calculate total statistics
        total_log_files = sum(container.log_file_count for container in containers)
        total_log_size = sum(container.total_log_size_bytes for container in containers)
        
        # Create metadata
        metadata = PackageMetadata(
            extraction_path=extraction_path,
            total_containers=len(containers),
            total_log_files=total_log_files,
            total_log_size_bytes=total_log_size,
            upload_timestamp=datetime.now(),
            original_filename="",  # Will be set by the calling function
            applications_detected=[]  # Will be populated during application discovery
        )
        
        # Create PackageStructure
        package_structure = PackageStructure(
            containers=containers,
            metadata=metadata,
            status=PackageStatus.COMPLETED if containers else PackageStatus.FAILED
        )
        
        logger.info(f"Created PackageStructure: {len(containers)} containers, {total_log_files} log files, {total_log_size} bytes")
        return package_structure
    
    def _calculate_package_hash_from_containers(self, containers: List[ContainerInfo]) -> str:
        """Calculate hash for package structure based on containers"""
        import hashlib
        
        # Create a string representation of the package structure
        structure_data = []
        for container in sorted(containers, key=lambda c: c.container_id):
            structure_data.append(f"{container.container_id}:{container.log_file_count}:{container.total_log_size_bytes}")
        
        structure_string = "|".join(structure_data)
        
        # Calculate hash
        hash_obj = hashlib.md5(structure_string.encode())
        return hash_obj.hexdigest()
    
    def _is_container_directory(self, dir_name: str) -> bool:
        """Check if directory name looks like a container ID (UUID)"""
        # UUID format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
        import re
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        return bool(re.match(uuid_pattern, dir_name.lower()))
    
    def _analyze_container(self, container_path: str, container_id: str) -> Optional[ContainerInfo]:
        """Analyze individual container directory"""
        logger.debug(f"Analyzing container: {container_id}")
        
        try:
            # Look for messages file (not directory)
            messages_file = os.path.join(container_path, "messages")
            if not os.path.exists(messages_file) or not os.path.isfile(messages_file):
                logger.warning(f"No messages file found in container: {container_id}")
                return None
            
            # Analyze log files
            log_files = []
            total_size = 0
            
            # Check for additional log files (like messages.1, messages.2, etc.)
            for file_name in os.listdir(container_path):
                file_path = os.path.join(container_path, file_name)
                if os.path.isfile(file_path) and file_name.startswith("messages"):
                    log_files.append(file_name)
                    total_size += os.path.getsize(file_path)
            
            # Determine application type
            application_name, functional_domain = self._detect_application(container_path)
            
            # Create container info
            # Calculate relative path from extraction root
            extraction_root = os.path.dirname(os.path.dirname(container_path))  # Go up two levels from container_id
            relative_path = os.path.relpath(container_path, extraction_root)
            
            container_info = ContainerInfo(
                container_id=container_id,
                application_name=application_name,
                functional_domain=functional_domain,
                relative_path=relative_path,
                log_file_count=len(log_files),
                total_log_size_bytes=total_size,
                log_files=log_files
            )
            
            logger.debug(f"Container analysis completed: {container_id} -> {application_name}")
            return container_info
            
        except Exception as e:
            logger.error(f"Container analysis failed for {container_id}: {e}")
            return None
    
    def _detect_application(self, container_path: str) -> tuple[str, str]:
        """Detect application type based on container contents"""
        logger.debug(f"Detecting application in: {container_path}")
        
        # Application detection patterns
        app_patterns = {
            "wnc-steer": {
                "patterns": ["steer_info", "sta_info.mac", "weak signal clients", "RSSI"],
                "domain": "WiFi Network Controller - Client Steering"
            },
            "wnc-acs": {
                "patterns": ["channelList", "opClass", "X_PRPL-ORG_WiFiController"],
                "domain": "WiFi Network Controller - Auto Channel Selection"
            },
            "wnc-tpyopt": {
                "patterns": ["topology optimization", "State: WaitTrigger --> SendScan", "Build topology fail!"],
                "domain": "WiFi Network Controller - Topology Optimizer"
            },
            "otbr-agent": {
                "patterns": ["Mle-----------: Send Advertisement", "MeshForwarder-: Sent IPv6 UDP msg", "Beacon Request"],
                "domain": "OpenThread Border Router Agent"
            }
        }
        
        # Check for configuration files
        config_files = [
            "Containerization_Configurations_Data_Model_list.json",
            "Cthulhu_Data_Model_list.json",
            "SoftwareModules_Data_Model_list.json"
        ]
        
        # Look for configuration files first
        for config_file in config_files:
            config_path = os.path.join(container_path, config_file)
            if os.path.exists(config_path):
                try:
                    with open(config_path, 'r') as f:
                        config_data = json.load(f)
                    
                    # Extract application info from config
                    if "bundleName" in config_data:
                        bundle_name = config_data["bundleName"]
                        for app_name, app_info in app_patterns.items():
                            if app_name in bundle_name:
                                return app_name, app_info["domain"]
                except Exception as e:
                    logger.warning(f"Failed to parse config file {config_file}: {e}")
        
        # Fallback: analyze log content
        messages_file = os.path.join(container_path, "messages")
        if os.path.exists(messages_file) and os.path.isfile(messages_file):
            # Sample log content for pattern matching
            sample_content = self._sample_log_content_from_file(messages_file)
            
            for app_name, app_info in app_patterns.items():
                for pattern in app_info["patterns"]:
                    if pattern.lower() in sample_content.lower():
                        return app_name, app_info["domain"]
        
        # Default fallback
        return "unknown", "Unknown Application"
    
    def _sample_log_content_from_file(self, messages_file: str, max_lines: int = 50) -> str:
        """Sample content from a single messages file for pattern matching"""
        sample_content = ""
        
        try:
            with open(messages_file, 'r', encoding='utf-8', errors='ignore') as f:
                # Read first few lines
                for i, line in enumerate(f):
                    if i >= max_lines:  # Limit to first max_lines
                        break
                    sample_content += line
        except Exception as e:
            logger.warning(f"Failed to read messages file: {e}")
        
        return sample_content

    def _sample_log_content(self, messages_dir: str, max_files: int = 3) -> str:
        """Sample content from log files for pattern matching"""
        sample_content = ""
        
        try:
            files = os.listdir(messages_dir)
            sample_files = files[:max_files]
            
            for file_name in sample_files:
                file_path = os.path.join(messages_dir, file_name)
                if os.path.isfile(file_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            # Read first few lines
                            for i, line in enumerate(f):
                                if i >= 10:  # Limit to first 10 lines
                                    break
                                sample_content += line
                    except Exception as e:
                        logger.warning(f"Failed to read log file {file_name}: {e}")
        except Exception as e:
            logger.warning(f"Failed to sample log content: {e}")
        
        return sample_content
    
    def _create_package_metadata(self, package_path: str, containers: List[ContainerInfo], extraction_path: str) -> PackageMetadata:
        """Create package metadata"""
        logger.info("Creating package metadata")
        
        # Calculate totals
        total_containers = len(containers)
        total_log_files = sum(container.log_file_count for container in containers)
        total_log_size = sum(container.total_log_size_bytes for container in containers)
        applications_detected = list(set(container.application_name for container in containers))
        
        # Get file info
        file_size = os.path.getsize(package_path)
        file_name = os.path.basename(package_path)
        
        metadata = PackageMetadata(
            original_filename=file_name,
            file_size_bytes=file_size,
            extraction_path=extraction_path,
            total_containers=total_containers,
            total_log_files=total_log_files,
            total_log_size_bytes=total_log_size,
            applications_detected=applications_detected
        )
        
        logger.info(f"Package metadata created: {total_containers} containers, {total_log_files} log files")
        return metadata
    
    def _validate_package(self, containers: List[ContainerInfo]) -> List[str]:
        """Validate package structure and contents"""
        logger.info("Validating package")
        
        validation_errors = []
        
        # Check if any containers found
        if not containers:
            validation_errors.append("No container directories found in package")
        
        # Check for supported applications
        unsupported_apps = []
        for container in containers:
            if container.application_name not in self.supported_applications:
                unsupported_apps.append(container.application_name)
        
        if unsupported_apps:
            validation_errors.append(f"Unsupported applications found: {', '.join(unsupported_apps)}")
        
        # Check for empty containers
        empty_containers = [c.container_id for c in containers if c.log_file_count == 0]
        if empty_containers:
            validation_errors.append(f"Empty containers found: {', '.join(empty_containers)}")
        
        logger.info(f"Package validation completed: {len(validation_errors)} errors found")
        return validation_errors
    
    def cleanup_extraction(self, extraction_path: str):
        """Clean up extracted package files"""
        try:
            if os.path.exists(extraction_path):
                shutil.rmtree(extraction_path)
                logger.info(f"Cleaned up extraction directory: {extraction_path}")
        except Exception as e:
            logger.warning(f"Failed to cleanup extraction directory: {e}")
    
    # Extraction Reuse Methods
    
    def _get_existing_extraction(self, project_id: str) -> Optional[str]:
        """Get existing extraction path for project"""
        # Use configured DATA_DIR instead of hardcoded paths
        extraction_path = os.path.join(
            self.config.DATA_DIR,
            "projects",
            project_id,
            "extracted"
        )
        if os.path.exists(extraction_path):
            return extraction_path
        return None
    
    def _validate_extraction_integrity(self, extraction_path: str) -> bool:
        """Validate existing extraction integrity"""
        metadata_path = os.path.join(extraction_path, "metadata", "extraction_info.json")
        if not os.path.exists(metadata_path):
            return False
        
        try:
            # Load and validate metadata
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            # Check file counts, sizes, and integrity hash
            return self._verify_extraction_completeness(extraction_path, metadata)
        except Exception as e:
            logger.warning(f"Failed to validate extraction integrity: {e}")
            return False
    
    def _persist_extraction_metadata(self, project_id: str, package_structure: PackageStructure):
        """Persist extraction metadata for future reuse"""
        # Use configured data directory instead of hardcoded path
        metadata_dir = os.path.join(
            self.config.DATA_DIR,
            "projects",
            project_id,
            "extracted",
            "metadata"
        )
        os.makedirs(metadata_dir, exist_ok=True)
        
        # Save package structure metadata
        from app.models.core import PackageStructureMetadata
        structure_metadata = PackageStructureMetadata(
            project_id=project_id,
            extraction_path=package_structure.metadata.extraction_path,
            original_filename=package_structure.metadata.original_filename,
            extraction_timestamp=datetime.now(),
            package_hash=self._calculate_package_hash(package_structure),
            total_containers=len(package_structure.containers),
            total_log_files=package_structure.metadata.total_log_files,
            total_log_size_bytes=package_structure.metadata.total_log_size_bytes,
            applications_detected=package_structure.metadata.applications_detected,
            extraction_integrity_hash=self._calculate_integrity_hash(package_structure)
        )
        
        with open(os.path.join(metadata_dir, "package_structure.json"), 'w') as f:
            json.dump(structure_metadata.to_dict(), f, indent=2)
        
        # Save application discovery metadata
        from app.models.core import ApplicationDiscoveryMetadata, ApplicationDiscoveryResult
        discovery_results = [self._convert_to_discovery_result(c) for c in package_structure.containers]
        discovery_metadata = ApplicationDiscoveryMetadata(
            project_id=project_id,
            discovery_timestamp=datetime.now(),
            applications=discovery_results,
            discovery_methods_used=["pattern_match", "config_file"],
            confidence_scores={c.application_name: 0.9 for c in package_structure.containers},
            validation_status="validated"
        )
        
        # Update the package structure metadata with discovered applications
        unique_apps = list(set(app.application_name for app in discovery_results))
        structure_metadata.applications_detected = unique_apps
        
        # Save updated package structure metadata
        with open(os.path.join(metadata_dir, "package_structure.json"), 'w') as f:
            json.dump(structure_metadata.to_dict(), f, indent=2)
        
        with open(os.path.join(metadata_dir, "application_discovery.json"), 'w') as f:
            json.dump(discovery_metadata.to_dict(), f, indent=2)
        
        # Save extraction info
        extraction_info = {
            "project_id": project_id,
            "extraction_timestamp": datetime.now().isoformat(),
            "package_hash": structure_metadata.package_hash,
            "integrity_hash": structure_metadata.extraction_integrity_hash,
            "total_files": structure_metadata.total_log_files,
            "total_size": structure_metadata.total_log_size_bytes
        }
        
        with open(os.path.join(metadata_dir, "extraction_info.json"), 'w') as f:
            json.dump(extraction_info, f, indent=2)
    
    def _reconstruct_package_structure(self, extraction_path: str) -> PackageStructure:
        """Reconstruct package structure from existing extraction"""
        metadata_path = os.path.join(extraction_path, "metadata", "package_structure.json")
        
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        # Reconstruct package structure from metadata
        return self._build_package_structure_from_metadata(metadata, extraction_path)
    
    def _calculate_package_hash(self, package_structure: PackageStructure) -> str:
        """Calculate hash for package structure"""
        import hashlib
        content = f"{package_structure.metadata.original_filename}_{package_structure.metadata.file_size_bytes}_{len(package_structure.containers)}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _calculate_integrity_hash(self, package_structure: PackageStructure) -> str:
        """Calculate integrity hash for extraction"""
        import hashlib
        content = f"{package_structure.metadata.total_log_files}_{package_structure.metadata.total_log_size_bytes}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def _verify_extraction_completeness(self, extraction_path: str, metadata: Dict[str, Any]) -> bool:
        """Verify extraction completeness against metadata"""
        try:
            # Check if all expected files exist
            expected_files = metadata.get("total_files", 0)
            actual_files = self._count_files_in_extraction(extraction_path)
            
            # Check file sizes
            expected_size = metadata.get("total_size", 0)
            actual_size = self._calculate_extraction_size(extraction_path)
            
            # Allow for small variations
            size_tolerance = 0.1  # 10% tolerance
            size_diff = abs(actual_size - expected_size) / max(expected_size, 1)
            
            return (actual_files >= expected_files and 
                   size_diff <= size_tolerance)
        except Exception as e:
            logger.warning(f"Failed to verify extraction completeness: {e}")
            return False
    
    def _count_files_in_extraction(self, extraction_path: str) -> int:
        """Count files in extraction directory"""
        count = 0
        for root, dirs, files in os.walk(extraction_path):
            # Skip metadata directory
            if "metadata" in root:
                continue
            count += len(files)
        return count
    
    def _calculate_extraction_size(self, extraction_path: str) -> int:
        """Calculate total size of extraction directory"""
        total_size = 0
        for root, dirs, files in os.walk(extraction_path):
            # Skip metadata directory
            if "metadata" in root:
                continue
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.exists(file_path):
                    total_size += os.path.getsize(file_path)
        return total_size
    
    def _convert_to_discovery_result(self, container: ContainerInfo) -> 'ApplicationDiscoveryResult':
        """Convert ContainerInfo to ApplicationDiscoveryResult"""
        from app.models.core import ApplicationDiscoveryResult
        return ApplicationDiscoveryResult(
            container_id=container.container_id,
            application_name=container.application_name,
            functional_domain=container.functional_domain,
            relative_path=container.relative_path,
            log_file_count=container.log_file_count,
            total_log_size_bytes=container.total_log_size_bytes,
            confidence_score=container.confidence_score,
            discovery_method="pattern_match"
        )
    
    def _build_package_structure_from_metadata(self, metadata: Dict[str, Any], extraction_path: str) -> PackageStructure:
        """Build PackageStructure from cached metadata"""
        from app.models.core import PackageMetadata, PackageStatus
        
        # Create metadata object
        package_metadata = PackageMetadata(
            original_filename=metadata["original_filename"],
            file_size_bytes=metadata.get("total_log_size_bytes", 0),
            extraction_path=extraction_path,
            total_containers=metadata["total_containers"],
            total_log_files=metadata["total_log_files"],
            total_log_size_bytes=metadata["total_log_size_bytes"],
            applications_detected=metadata["applications_detected"]
        )
        
        # Load containers from application discovery metadata
        containers = self._load_containers_from_metadata(extraction_path)
        
        # Create package structure
        package_structure = PackageStructure(
            metadata=package_metadata,
            containers=containers,
            status=PackageStatus.VALID,
            validation_errors=[]
        )
        
        return package_structure
    
    def _load_containers_from_metadata(self, extraction_path: str) -> List[ContainerInfo]:
        """Load containers from application discovery metadata"""
        metadata_path = os.path.join(extraction_path, "metadata", "application_discovery.json")
        
        if not os.path.exists(metadata_path):
            return []
        
        with open(metadata_path, 'r') as f:
            discovery_data = json.load(f)
        
        containers = []
        for app_data in discovery_data.get("applications", []):
            # Scan the container directory to find actual log files
            container_path = os.path.join(extraction_path, app_data["relative_path"])
            log_files = []
            
            if os.path.exists(container_path):
                # Find all log files in the container directory
                for file_name in os.listdir(container_path):
                    file_path = os.path.join(container_path, file_name)
                    if os.path.isfile(file_path) and file_name.startswith("messages"):
                        log_files.append(file_name)
            
            container = ContainerInfo(
                container_id=app_data["container_id"],
                application_name=app_data["application_name"],
                functional_domain=app_data["functional_domain"],
                relative_path=app_data["relative_path"],
                log_file_count=app_data["log_file_count"],
                total_log_size_bytes=app_data["total_log_size_bytes"],
                confidence_score=app_data.get("confidence_score", 0.0),
                log_files=log_files
            )
            containers.append(container)
        
        return containers
    
    def _store_logs_in_sqlite(self, package_structure: PackageStructure, project_id: str):
        """Parse logs from package structure and store in SQLite using ApplicationDataManager"""
        try:
            logger.info(f"Parsing logs and storing in SQLite for project: {project_id}")
            
            # Dictionary to store logs by application
            app_logs = {}
            
            for container in package_structure.containers:
                app_name = container.application_name
                logger.info(f"Processing container {app_name} with {len(container.log_files)} log files")
                
                # Initialize app-specific log list
                if app_name not in app_logs:
                    app_logs[app_name] = []
                
                # Parse log files for this container
                for log_file in container.log_files:
                    # Construct the correct file path using the relative path
                    file_path = os.path.join(package_structure.metadata.extraction_path, container.relative_path, log_file)
                    
                    if not os.path.exists(file_path):
                        logger.warning(f"Log file not found: {file_path}")
                        continue
                    
                    logger.info(f"Parsing log file: {file_path}")
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            for line_num, line in enumerate(f, 1):
                                line = line.strip()
                                if not line:
                                    continue
                                
                                # Parse log entry
                                log_entry = self._parse_log_line(line, app_name, log_file, line_num)
                                if log_entry:
                                    app_logs[app_name].append(log_entry)
                                    
                    except Exception as e:
                        logger.warning(f"Failed to read log file {file_path}: {e}")
                        continue
            
            # Store logs in SQLite using ApplicationDataManager
            for app_name, logs in app_logs.items():
                if logs:
                    logger.info(f"Storing {len(logs)} logs in SQLite for application: {app_name}")
                    data_manager = ApplicationDataManager(project_id, app_name, self.config.DATA_DIR)
                    data_manager.store_log_entries(logs)
                    logger.info(f"Successfully stored {len(logs)} logs in SQLite for {app_name}")
            
            total_logs = sum(len(logs) for logs in app_logs.values())
            logger.info(f"Successfully stored {total_logs} total logs in SQLite for {len(app_logs)} applications")
            
        except Exception as e:
            logger.error(f"Failed to store logs in SQLite: {e}")
            import traceback
            traceback.print_exc()
    
    def _parse_log_line(self, line: str, app_name: str, log_file: str, line_num: int) -> Optional[Dict[str, Any]]:
        """Parse a single log line and return log entry dictionary with message type categorization"""
        try:
            # Basic log parsing - can be enhanced based on log format
            from datetime import datetime
            import re
            
            # Extract timestamp from log line - handle multiple formats
            timestamp = None
            
            # Format 1: 2025 Sep 03 08:10:11.689216 (with microseconds)
            timestamp_match = re.search(r'(\d{4}\s+\w+\s+\d+\s+\d+:\d+:\d+\.\d+)', line)
            if timestamp_match:
                try:
                    timestamp_str = timestamp_match.group(1)
                    timestamp = datetime.strptime(timestamp_str, '%Y %b %d %H:%M:%S.%f').isoformat()
                except ValueError:
                    pass
            
            # Format 2: 2025 Sep 03 08:10:11 (without microseconds)
            if not timestamp:
                timestamp_match = re.search(r'(\d{4}\s+\w+\s+\d+\s+\d+:\d+:\d+)', line)
                if timestamp_match:
                    try:
                        timestamp_str = timestamp_match.group(1)
                        timestamp = datetime.strptime(timestamp_str, '%Y %b %d %H:%M:%S').isoformat()
                    except ValueError:
                        pass
            
            # Format 3: ISO format 2025-01-09T10:30:00 or 2025-01-09 10:30:00
            if not timestamp:
                timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?)', line)
                if timestamp_match:
                    try:
                        timestamp_str = timestamp_match.group(1).replace(' ', 'T')
                        timestamp = timestamp_str
                    except:
                        pass
            
            # Format 4: Unix timestamp
            if not timestamp:
                timestamp_match = re.search(r'(\d{10}(?:\.\d+)?)', line)
                if timestamp_match:
                    try:
                        timestamp_str = timestamp_match.group(1)
                        timestamp = datetime.fromtimestamp(float(timestamp_str)).isoformat()
                    except ValueError:
                        pass
            
            # If no timestamp found, use current time as fallback
            if not timestamp:
                timestamp = datetime.now().isoformat()
                logger.warning(f"No timestamp found in log line {line_num}, using current time: {line[:100]}...")
            
            # Extract log level
            log_level = "info"  # Default
            if "ERROR" in line.upper():
                log_level = "error"
            elif "WARN" in line.upper():
                log_level = "warning"
            elif "DEBUG" in line.upper():
                log_level = "debug"
            
            # Categorize message type based on content patterns
            message_type = self._categorize_message_type(line, app_name)
            
            return {
                "timestamp": timestamp,
                "container_id": app_name,
                "log_level": log_level,
                "message_type": message_type,
                "message": line,
                "raw_line": line,
                "line_number": line_num,
                "file_path": log_file
            }
            
        except Exception as e:
            logger.warning(f"Failed to parse log line {line_num}: {e}")
            return None
    
    def _categorize_message_type(self, line: str, app_name: str) -> str:
        """Categorize log message by type based on content patterns"""
        line_upper = line.upper()
        
        # Application-specific message type categorization
        if app_name == "wnc-steer":
            return self._categorize_wnc_steer_message(line, line_upper)
        elif app_name == "wnc-acs":
            return self._categorize_wnc_acs_message(line, line_upper)
        elif app_name == "otbr-agent":
            return self._categorize_otbr_agent_message(line, line_upper)
        elif app_name == "wnc-tpyopt":
            return self._categorize_wnc_tpyopt_message(line, line_upper)
        else:
            return self._categorize_generic_message(line, line_upper)
    
    def _categorize_wnc_steer_message(self, line: str, line_upper: str) -> str:
        """Categorize wnc-steer specific messages"""
        # Client steering operations
        if any(keyword in line_upper for keyword in ["RSSI", "BSSID", "CLIENT", "STEERING"]):
            if "FOUND BETTER" in line_upper:
                return "steering_decision"
            elif "RSSI IMPROVEMENT" in line_upper:
                return "steering_evaluation"
            elif "STEERING" in line_upper:
                return "steering_action"
            else:
                return "client_management"
        
        # Network operations
        elif any(keyword in line_upper for keyword in ["NETWORK", "CONNECTION", "DISCONNECT"]):
            return "network_operation"
        
        # Performance metrics
        elif any(keyword in line_upper for keyword in ["LATENCY", "THROUGHPUT", "PERFORMANCE"]):
            return "performance_metric"
        
        # Error conditions
        elif any(keyword in line_upper for keyword in ["ERROR", "FAILED", "TIMEOUT", "EXCEPTION"]):
            return "error_condition"
        
        # Configuration changes
        elif any(keyword in line_upper for keyword in ["CONFIG", "SETTING", "PARAMETER"]):
            return "configuration"
        
        # System status
        elif any(keyword in line_upper for keyword in ["STATUS", "HEALTH", "MONITORING"]):
            return "system_status"
        
        # Default categorization
        else:
            return "general_info"
    
    def _categorize_wnc_acs_message(self, line: str, line_upper: str) -> str:
        """Categorize wnc-acs specific messages"""
        if any(keyword in line_upper for keyword in ["ACCESS", "CONTROL", "AUTHENTICATION"]):
            return "access_control"
        elif any(keyword in line_upper for keyword in ["POLICY", "RULE", "ENFORCEMENT"]):
            return "policy_enforcement"
        elif any(keyword in line_upper for keyword in ["USER", "SESSION", "LOGIN"]):
            return "user_session"
        else:
            return "general_info"
    
    def _categorize_otbr_agent_message(self, line: str, line_upper: str) -> str:
        """Categorize otbr-agent specific messages"""
        if any(keyword in line_upper for keyword in ["THREAD", "MESH", "ROUTING"]):
            return "mesh_operation"
        elif any(keyword in line_upper for keyword in ["COMMISSION", "JOIN", "LEAVE"]):
            return "device_management"
        elif any(keyword in line_upper for keyword in ["BORDER", "ROUTER", "GATEWAY"]):
            return "border_router"
        else:
            return "general_info"
    
    def _categorize_wnc_tpyopt_message(self, line: str, line_upper: str) -> str:
        """Categorize wnc-tpyopt specific messages"""
        if any(keyword in line_upper for keyword in ["OPTIMIZATION", "ALGORITHM", "CALCULATION"]):
            return "optimization"
        elif any(keyword in line_upper for keyword in ["TOPOLOGY", "PATH", "ROUTE"]):
            return "topology_analysis"
        else:
            return "general_info"
    
    def _categorize_generic_message(self, line: str, line_upper: str) -> str:
        """Categorize generic messages"""
        if any(keyword in line_upper for keyword in ["ERROR", "FAILED", "EXCEPTION"]):
            return "error_condition"
        elif any(keyword in line_upper for keyword in ["WARNING", "WARN"]):
            return "warning_condition"
        elif any(keyword in line_upper for keyword in ["DEBUG", "TRACE"]):
            return "debug_info"
        elif any(keyword in line_upper for keyword in ["START", "INIT", "INITIALIZE"]):
            return "system_startup"
        elif any(keyword in line_upper for keyword in ["STOP", "SHUTDOWN", "EXIT"]):
            return "system_shutdown"
        else:
            return "general_info"
