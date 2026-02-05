import time
"""
Observer Service
----------------
Manages real-time filesystem monitoring using the watchdog library.
Coordinates initial synchronization and event-driven file organization.
"""
import os
import threading
from pathlib import Path
from typing import Dict, Any
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileMovedEvent
from src.services.logger import logger
from src.services.config_service import config_service
from src.core.classifier import classifier
from src.core.organizer import organizer
from src.services.db_service import db_service

class DownloadHandler(FileSystemEventHandler):
    """Event handler for processing new or moved files in the watched directory."""

    def on_created(self, event):
        if event.is_directory:
            return
        self._process_file(Path(event.src_path))

    def on_moved(self, event):
        if event.is_directory:
            return
        # Remove old path from index, add new path
        db_service.remove_file(Path(event.src_path))
        self._process_file(Path(event.dest_path))

    def on_deleted(self, event):
        if event.is_directory:
            return
        db_service.remove_file(Path(event.src_path))

    def _process_file(self, file_path: Path):
        """Classifies and moves a single file."""
        # Small delay to ensure file is fully written/unlocked by OS
        time.sleep(1)
        
        if not file_path.exists():
            return

        category = classifier.classify(file_path)
        target_dir = file_path.parent / category
        
        if file_path.parent.name == category:
            db_service.upsert_file(file_path)
            return

        final_path = organizer.move_file(file_path, target_dir)
        if final_path:
            db_service.upsert_file(final_path)

class ObserverService:
    """Manages the lifecycle of the watchdog Observer."""

    def __init__(self):
        self.observer = None
        self.is_running = False

    def start(self):
        enabled = config_service.get("monitor_enabled", True)
        if not enabled:
            logger.info("Monitoring is disabled in config. Not starting.")
            return

        watch_path = config_service.get("watch_directory")
        if not watch_path:
            logger.error("No watch directory configured.")
            return

        path = Path(watch_path)
        if not path.exists():
            logger.error(f"Watch directory {path} does not exist.")
            return

        logger.info(f"Starting observer on: {path}")
        
        event_handler = DownloadHandler()
        self.observer = Observer()
        self.observer.schedule(event_handler, str(path), recursive=False)
        self.observer.start()
        self.is_running = True
        
        # Proactively organize existing files
        threading.Thread(target=self.sync_existing_files, daemon=True).start()

    def sync_existing_files(self):
        """Iterates through existing files in the directory and organizes them."""
        watch_path = config_service.get("watch_directory")
        if not watch_path:
            return
            
        path = Path(watch_path)
        if not path.exists():
            return
            
        logger.info(f"Performing initial sync for: {path}")
        handler = DownloadHandler()
        
        for item in path.iterdir():
            if item.is_file():
                handler._process_file(item)
        
        logger.info("Initial sync complete.")

    def restart_if_needed(self, new_config: Dict[str, Any]):
        """Restarts the observer if monitoring was toggled or path changed."""
        logger.info("Re-evaluating observer status due to config change...")
        should_be_enabled = new_config.get("monitor_enabled", True)
        current_path = config_service.get("watch_directory")
        
        if self.is_running:
            self.stop()
        
        if should_be_enabled:
            # Small delay to ensure OS released old file handles
            time.sleep(0.5)
            self.start()

    def stop(self):
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.is_running = False
            logger.info("Observer stopped.")

observer_service = ObserverService()
