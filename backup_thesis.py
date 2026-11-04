"""
Automated Backup Script for Master's Thesis Repository (d:\\Thesis)
Author: Bright / Thesis Assistant
Usage:
    python backup_thesis.py
    (Or run in PowerShell / Command Prompt / double-click)
"""

import os
import sys
import zipfile
import datetime
from pathlib import Path
import shutil

# Configuration
SOURCE_DIR = Path(r"d:\Thesis")
DEFAULT_BACKUP_DIR = Path(r"d:\Thesis_Backups")

# File patterns and directories to exclude from backup to keep archive lightweight
EXCLUDE_DIRS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".venv",
    "venv",
    "env",
    ".ipynb_checkpoints"
}

EXCLUDE_EXTENSIONS = {
    ".pyc",
    ".pyo",
    ".tmp",
    ".log",
    ".env"
}

EXCLUDE_FILES = {
    ".env",
    ".env.local"
}

def create_backup(backup_target_dir=DEFAULT_BACKUP_DIR):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_target_dir.mkdir(parents=True, exist_ok=True)
    
    zip_filename = backup_target_dir / f"Thesis_Backup_{timestamp}.zip"
    
    print("=" * 70)
    print("THESIS AUTOMATED BACKUP UTILITY")
    print("=" * 70)
    print(f"Source Directory: {SOURCE_DIR}")
    print(f"Target Backup:   {zip_filename}")
    print("Collecting files...")
    
    file_count = 0
    total_uncompressed_bytes = 0
    
    with zipfile.ZipFile(zip_filename, 'w', compression=zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(SOURCE_DIR):
            # Modify dirs in-place to skip excluded directories
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            
            for file in files:
                if file in EXCLUDE_FILES or file.startswith(".env"):
                    continue
                file_path = Path(root) / file
                if file_path.suffix.lower() in EXCLUDE_EXTENSIONS:
                    continue
                
                # Relative path inside the zip
                rel_path = file_path.relative_to(SOURCE_DIR)
                
                try:
                    zipf.write(file_path, arcname=rel_path)
                    file_count += 1
                    total_uncompressed_bytes += file_path.stat().st_size
                except Exception as e:
                    print(f"  [WARNING] Could not archive {rel_path}: {e}")
                    
    zip_size_bytes = zip_filename.stat().st_size
    zip_size_mb = zip_size_bytes / (1024 * 1024)
    orig_size_mb = total_uncompressed_bytes / (1024 * 1024)
    
    print("-" * 70)
    print(f"Backup Complete!")
    print(f"Files Archived:       {file_count} files")
    print(f"Original Size:        {orig_size_mb:.2f} MB")
    print(f"Compressed Size:      {zip_size_mb:.2f} MB (Compression ratio: {zip_size_mb/orig_size_mb*100:.1f}%)")
    print(f"Saved to:             {zip_filename}")
    print("=" * 70)
    
    # Check for common cloud sync directories to offer optional secondary backup
    cloud_locations = [
        Path(os.environ.get("USERPROFILE", "")) / "OneDrive" / "Thesis_Backups",
        Path(os.environ.get("USERPROFILE", "")) / "Google Drive" / "Thesis_Backups",
        Path(r"c:\Thesis_Backups")
    ]
    
    for c_path in cloud_locations:
        if c_path.parent.exists():
            try:
                c_path.mkdir(parents=True, exist_ok=True)
                cloud_dest = c_path / zip_filename.name
                shutil.copy2(zip_filename, cloud_dest)
                print(f"-> Cloud/Secondary Sync: Copied to {cloud_dest}")
                break
            except Exception:
                pass

if __name__ == "__main__":
    create_backup()
