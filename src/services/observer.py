import time
from pathlib import Path
from typing import Dict, Any
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileMovedEvent
from src.services.logger import logger
from src.services.config_service import config_service
from src.core.classifier import classifier
from src.core.organizer import organizer

class DownloadHandler(FileSystemEventHandler):
    """Handles file system events in the watched directory."""

    def on_created(self, event):
        if event.is_directory:
            return
        self._process_file(Path(event.src_path))

    def on_moved(self, event):
        if event.is_directory:
            return
        # If a file is moved INTO the downloads folder from elsewhere
        self._process_file(Path(event.dest_path))

    def _process_file(self, file_path: Path):
        """Classifies and moves a single file."""
        # Small delay to ensure file is fully written/unlocked by OS
        time.sleep(1)
        
        if not file_path.exists():
            return

        category = classifier.classify(file_path)
        target_dir = file_path.parent / category
        
        # Prevent moving files that are already in a category folder
        if file_path.parent.name == category:
            return

        organizer.move_file(file_path, target_dir)

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
