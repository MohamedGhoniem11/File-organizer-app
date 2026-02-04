import threading
import time
from pathlib import Path
from typing import Dict, Any, Optional
from src.core.health_engine import health_engine
from src.core.organizer import organizer
from src.services.logger import logger
from src.services.config_service import config_service

class HealthService:
    """Service to coordinate directory health audits and cleanups."""

    def __init__(self):
        self.last_report = {}
        self.is_scanning = False

    def run_audit(self) -> Dict:
        """Runs a scan and returns the results without taking action."""
        self.is_scanning = True
        try:
            watch_dir = Path(config_service.get("watch_directory"))
            logger.info(f"Starting health audit for {watch_dir}...")
            self.last_report = health_engine.scan_directory(watch_dir)
            logger.info(f"Audit complete. Formatted report generated.")
            return self.last_report
        finally:
            self.is_scanning = False

    def execute_cleanup(self, report: Dict) -> Dict:
        """
        Takes actions (delete/move) based on the report and config.
        Default is dry-run.
        """
        cleanup_cfg = config_service.get("cleanup", {})
        dry_run = cleanup_cfg.get("dry_run", True)
        
        stat_summary = {
            "deleted": 0,
            "moved": 0,
            "saved_bytes": 0
        }

        if dry_run:
            logger.info("DRY-RUN MODE: No real changes will be made.")

        # 1. Handle Duplicates
        if cleanup_cfg.get("deduplicate", True):
            for f_hash, paths in report["duplicates"].items():
                # Keep the first one, delete others
                for path in paths[1:]:
                    if not dry_run:
                        size = path.stat().st_size
                        organizer.delete_file(path)
                        stat_summary["deleted"] += 1
                        stat_summary["saved_bytes"] += size
                    else:
                        logger.info(f"[DRY-RUN] Would delete duplicate: {path}")

        # 2. Handle Zero-byte files
        if cleanup_cfg.get("remove_zero_byte_files", True):
            for path in report["zero_byte_files"]:
                if not dry_run:
                    organizer.delete_file(path)
                    stat_summary["deleted"] += 1
                else:
                    logger.info(f"[DRY-RUN] Would delete 0-byte file: {path}")

        # 3. Handle Orphans
        strategy = cleanup_cfg.get("handle_orphans", "ignore")
        if strategy != "ignore":
            for path in report["orphans"]:
                if not dry_run:
                    if strategy == "delete":
                        organizer.delete_file(path)
                        stat_summary["deleted"] += 1
                    elif strategy == "move_to_misc":
                        organizer.move_to_misc(path)
                        stat_summary["moved"] += 1
                else:
                    logger.info(f"[DRY-RUN] Would {strategy} orphan: {path}")

        # 4. Handle Empty Folders
        if cleanup_cfg.get("remove_empty_folders", True):
            # Sort by depth (deepest first) to handle nested empty folders
            sorted_folders = sorted(report["empty_folders"], key=lambda x: len(x.parts), reverse=True)
            for folder in sorted_folders:
                if not dry_run:
                    try:
                        folder.rmdir()
                        logger.info(f"Removed empty folder: {folder}")
                    except:
                        pass
                else:
                    logger.info(f"[DRY-RUN] Would remove empty folder: {folder}")

        return stat_summary

    def run_auto_maintenance(self):
        """Threaded function for scheduled maintenance."""
        while True:
            auto_cfg = config_service.get("automation", {})
            if auto_cfg.get("enable_auto_scan", False):
                interval = auto_cfg.get("auto_scan_interval_min", 60) * 60
                time.sleep(interval)
                logger.info("Scheduled maintenance starting...")
                report = self.run_audit()
                self.execute_cleanup(report)
            else:
                time.sleep(300) # Check config every 5 mins

health_service = HealthService()
