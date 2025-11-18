#!/usr/bin/env python3
"""
Diagnostic script to check project paths for cross-machine compatibility issues.

This script identifies projects with paths that don't match the current machine's DATA_DIR.
"""

import json
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import get_settings

def diagnose_project_paths():
    """Check projects.json for path compatibility issues"""
    settings = get_settings()
    projects_file = os.path.join(settings.DATA_DIR, "projects.json")
    
    print(f"🔍 Project Path Diagnostic Tool")
    print(f"=" * 60)
    print(f"Current DATA_DIR: {settings.DATA_DIR}")
    print(f"Projects file: {projects_file}")
    print(f"=" * 60)
    print()
    
    if not os.path.exists(projects_file):
        print(f"❌ ERROR: projects.json not found at {projects_file}")
        return
    
    try:
        with open(projects_file, 'r') as f:
            projects_data = json.load(f)
    except Exception as e:
        print(f"❌ ERROR: Failed to load projects.json: {e}")
        return
    
    print(f"Found {len(projects_data)} projects")
    print()
    
    issues = []
    warnings = []
    
    for project_id, project_dict in projects_data.items():
        project_name = project_dict.get("name", "Unknown")
        stored_project_root = project_dict.get("project_root_path", "")
        stored_extraction_path = project_dict.get("extraction_path", "")
        stored_metadata_path = project_dict.get("extraction_metadata_path", "")
        
        # Expected paths based on current DATA_DIR
        expected_project_root = os.path.join(settings.DATA_DIR, "projects", project_id)
        expected_extraction_path = os.path.join(expected_project_root, "extracted")
        expected_metadata_path = os.path.join(expected_extraction_path, "metadata")
        
        print(f"📁 Project: {project_name} ({project_id[:8]}...)")
        
        # Check project_root_path
        if stored_project_root != expected_project_root:
            print(f"  ⚠️  project_root_path mismatch:")
            print(f"     Stored:    {stored_project_root}")
            print(f"     Expected:  {expected_project_root}")
            if stored_project_root and os.path.exists(stored_project_root):
                print(f"     ✅ Stored path exists")
            elif expected_project_root and os.path.exists(expected_project_root):
                print(f"     ✅ Expected path exists")
            else:
                print(f"     ❌ Neither path exists")
                issues.append({
                    "project_id": project_id,
                    "field": "project_root_path",
                    "stored": stored_project_root,
                    "expected": expected_project_root,
                    "issue": "Path mismatch and neither location exists"
                })
        else:
            print(f"  ✅ project_root_path matches")
        
        # Check extraction_path
        if stored_extraction_path and not stored_extraction_path.startswith(settings.DATA_DIR):
            print(f"  ⚠️  extraction_path outside DATA_DIR:")
            print(f"     Stored:    {stored_extraction_path}")
            print(f"     Expected:  {expected_extraction_path}")
            if os.path.exists(stored_extraction_path):
                print(f"     ✅ Stored path exists")
            elif os.path.exists(expected_extraction_path):
                print(f"     ✅ Expected path exists")
            else:
                print(f"     ❌ Neither path exists")
                warnings.append({
                    "project_id": project_id,
                    "field": "extraction_path",
                    "stored": stored_extraction_path,
                    "expected": expected_extraction_path
                })
        
        # Check extraction_metadata_path
        if stored_metadata_path and not stored_metadata_path.startswith(settings.DATA_DIR):
            print(f"  ⚠️  extraction_metadata_path outside DATA_DIR:")
            print(f"     Stored:    {stored_metadata_path}")
            print(f"     Expected:  {expected_metadata_path}")
            if os.path.exists(stored_metadata_path):
                print(f"     ✅ Stored path exists")
            elif os.path.exists(expected_metadata_path):
                print(f"     ✅ Expected path exists")
            else:
                print(f"     ❌ Neither path exists")
                warnings.append({
                    "project_id": project_id,
                    "field": "extraction_metadata_path",
                    "stored": stored_metadata_path,
                    "expected": expected_metadata_path
                })
        
        print()
    
    # Summary
    print("=" * 60)
    print("📊 Summary")
    print("=" * 60)
    print(f"Total projects: {len(projects_data)}")
    print(f"Critical issues: {len(issues)}")
    print(f"Warnings: {len(warnings)}")
    
    if issues:
        print("\n❌ Critical Issues Found:")
        for issue in issues:
            print(f"  - Project {issue['project_id'][:8]}: {issue['field']}")
            print(f"    Stored: {issue['stored']}")
            print(f"    Expected: {issue['expected']}")
    
    if warnings:
        print("\n⚠️  Warnings:")
        for warning in warnings:
            print(f"  - Project {warning['project_id'][:8]}: {warning['field']}")
    
    if not issues and not warnings:
        print("\n✅ All project paths are compatible with current DATA_DIR")
    
    return issues, warnings

if __name__ == "__main__":
    diagnose_project_paths()

