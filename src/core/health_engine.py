"""
Health Engine
-------------
Audit tool for scanning directories for structural and data redundancy issues.
Identifies empty folders, duplicate files, zero-byte files, and orphans.
"""
import hashlib
import os
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from src.services.logger import logger
from src.services.config_service import config_service
from src.core.classifier import classifier

class HealthEngine:
    """Core logic for performing deep-scans and directory auditing."""

    def __init__(self):
        self.reset_results()

    def reset_results(self):
        self.results = {
            "empty_folders": [],
            "duplicates": {}, # {hash: [paths]}
            "orphans": [],
            "zero_byte_files": [],
            "space_waste_bytes": 0
        }

    def scan_directory(self, root_path: Path) -> Dict:
        """Performs a comprehensive scan of the given directory."""
        self.reset_results()
        if not root_path.exists():
            return self.results

        # Track file hashes for deduplication
        hashes: Dict[str, List[Path]] = {}

        for dirpath, dirnames, filenames in os.walk(root_path, topdown=False):
            current_dir = Path(dirpath)
            
            # 1. Check for empty folders
            if not dirnames and not filenames:
                self.results["empty_folders"].append(current_dir)
                continue

            for f in filenames:
                file_path = current_dir / f
                
                try:
                    stats = file_path.stat()
                    
                    # 2. Zero-byte files
                    if stats.st_size == 0:
                        self.results["zero_byte_files"].append(file_path)
                    
                    # 3. Orphans (extensions not in config)
                    if classifier.classify(file_path) == "Others":
                        self.results["orphans"].append(file_path)

                    # 4. Duplicates (hashing)
                    if stats.st_size > 0:
                        f_hash = self._calculate_hash(file_path)
                        if f_hash:
                            if f_hash not in hashes:
                                hashes[f_hash] = []
                            hashes[f_hash].append(file_path)

                except Exception as e:
                    logger.error(f"Error scanning file {file_path}: {e}")

        # Process duplicates
        for f_hash, paths in hashes.items():
            if len(paths) > 1:
                self.results["duplicates"][f_hash] = paths
                # Calculate wasted space (all but one copy)
                try:
                    single_size = paths[0].stat().st_size
                    self.results["space_waste_bytes"] += single_size * (len(paths) - 1)
                except:
                    pass

        return self.results

    def _calculate_hash(self, path: Path, chunk_size: int = 8192) -> Optional[str]:
        """Calculates SHA-256 hash of a file."""
        hasher = hashlib.sha256()
        try:
            with open(path, "rb") as f:
                while chunk := f.read(chunk_size):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            logger.error(f"Could not hash {path.name}: {e}")
            return None

health_engine = HealthEngine()
