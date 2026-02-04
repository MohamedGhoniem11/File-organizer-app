import json
import threading
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from .logger import logger

DEFAULT_CONFIG = {
    "watch_directory": str(Path.home() / "Downloads"),
    "monitor_enabled": True,
    "categories": {
        "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"],
        "PDFs": [".pdf"],
        "Documents": [".docx", ".txt", ".md", ".pptx", ".odt"],
        "Setups": [".exe", ".msi", ".dmg", ".pkg"],
        "Sheets": [".xlsx", ".xls", ".ods", ".csv"],
        "Videos": [".mp4", ".mkv", ".avi", ".mov"],
        "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
        "Audio": [".mp3", ".wav", ".flac", ".aac"]
    },
    "collision_strategy": "rename",
    "cleanup": {
        "dry_run": True,
        "remove_empty_folders": True,
        "remove_zero_byte_files": True,
        "handle_orphans": "move_to_misc",  # options: delete, move_to_misc, ignore
        "deduplicate": True,
        "backup_enabled": False,
        "backup_dir": str(Path.home() / "FileManager_Backups")
    },
    "automation": {
        "run_on_startup": True,
        "auto_scan_interval_min": 60,
        "enable_auto_scan": False
    },
    "gui_preferences": {
        "theme": "dark",
        "show_logs": True,
        "window_size": "1000x600"
    },
    "max_folder_files": 1000,
    "log_level": "INFO"
}

class ConfigService:
    _instance = None
    _config_path = Path("config/config.json")
    _callbacks: List[Callable] = []

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigService, cls).__new__(cls)
            cls._instance.config = cls._instance._load_config()
            cls._instance._last_mtime = cls._instance._get_mtime()
        return cls._instance

    def _get_mtime(self) -> float:
        try:
            return self._config_path.stat().st_mtime
        except OSError:
            return 0.0

    def _load_config(self) -> Dict[str, Any]:
        """Loads config from JSON file, validates it, and merges with defaults."""
        if not self._config_path.exists():
            self._config_path.parent.mkdir(exist_ok=True)
            self.save_config(DEFAULT_CONFIG)
            return DEFAULT_CONFIG.copy()

        try:
            with open(self._config_path, "r") as f:
                loaded = json.load(f)
                return self._validate_and_merge(loaded)
        except Exception as e:
            logger.error(f"Failed to load config: {e}. Using defaults.")
            return DEFAULT_CONFIG.copy()

    def _validate_and_merge(self, loaded: Dict[str, Any]) -> Dict[str, Any]:
        """Ensures all required keys exist and types are correct."""
        merged = DEFAULT_CONFIG.copy()
        
        # Shallow merge for top-level keys
        for key, value in loaded.items():
            if key in DEFAULT_CONFIG:
                # Basic type validation
                if isinstance(value, type(DEFAULT_CONFIG[key])):
                    merged[key] = value
        
        # Deep merge for nested dicts (categories, gui_preferences)
        if "categories" in loaded and isinstance(loaded["categories"], dict):
            merged["categories"] = loaded["categories"]
        
        if "gui_preferences" in loaded and isinstance(loaded["gui_preferences"], dict):
            for k, v in loaded["gui_preferences"].items():
                if k in DEFAULT_CONFIG["gui_preferences"]:
                    merged["gui_preferences"][k] = v

        return merged

    def save_config(self, new_config: Dict[str, Any]):
        """Persists config to JSON file."""
        try:
            with open(self._config_path, "w") as f:
                json.dump(new_config, f, indent=4)
            self.config = new_config
            self._last_mtime = self._get_mtime()
            logger.info("Configuration saved and updated.")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")

    def check_for_updates(self):
        """Checks if the config file was modified externally and reloads if so."""
        current_mtime = self._get_mtime()
        if current_mtime > self._last_mtime:
            logger.info("External config change detected. Reloading...")
            self.config = self._load_config()
            self._last_mtime = current_mtime
            self._trigger_callbacks()

    def register_callback(self, callback: Callable):
        """Registers a function to be called when config is reloaded."""
        if callback not in self._callbacks:
            self._callbacks.append(callback)

    def _trigger_callbacks(self):
        for cb in self._callbacks:
            try:
                cb(self.config)
            except Exception as e:
                logger.error(f"Error in config callback: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        return self.config.get(key, default)

    def get_categories(self) -> Dict[str, List[str]]:
        return self.config.get("categories", DEFAULT_CONFIG["categories"])

config_service = ConfigService()
