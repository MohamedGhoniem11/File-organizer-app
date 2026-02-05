"""
NLP Service
-----------
Parses natural language queries to extract user intent and entities.
Supports searching, configuration changes, and maintenance commands.
"""
import spacy
import re
from typing import Dict, Any, List, Optional
from src.services.logger import logger
from datetime import datetime, timedelta

class NlpService:
    """Uses spaCy and pattern matching to interpret user requests."""
    
    def __init__(self):
        self.nlp = None
        self.is_fallback_mode = False
        self._load_model()

    def _load_model(self):
        """Attempts to load spaCy model, auto-downloads if missing, falls back to rules if failed."""
        model_name = "en_core_web_sm"
        try:
            # 1. Try loading existing
            self.nlp = spacy.load(model_name)
            logger.info(f"NLP Service: '{model_name}' loaded successfully.")
        except (IOError, ImportError, OSError):
            logger.warning(f"NLP Service: '{model_name}' missing. Attempting auto-download...")
            try:
                # 2. Try auto-download
                from spacy.cli import download
                download(model_name)
                self.nlp = spacy.load(model_name)
                logger.info(f"NLP Service: '{model_name}' downloaded and loaded successfully.")
            except Exception as e:
                # 3. Final fallback to rules
                self.is_fallback_mode = True
                logger.error(f"NLP Service: Failed to download/load model: {e}. Reverting to rule-based fallback.")
        except Exception as e:
            self.is_fallback_mode = True
            logger.error(f"NLP Service: Unexpected error during init: {e}. Using rule-based fallback.")

    def parse(self, text: str) -> Dict[str, Any]:
        """Translates user text into a structured command."""
        text = text.lower().strip()
        
        # 1. Intent Detection (Rule-based first for speed/certainty)
        # 1. Intent Detection - Specific commands first
        if any(w in text for w in ["scan", "index", "reindex"]):
            match = re.search(r'(?:scan|index|reindex)\s+(.+)', text)
            path = match.group(1).strip() if match else None
            return {"intent": "scan_path", "entities": {"path": path}}

        elif any(w in text for w in ["stats", "info", "overview", "debug", "status"]):
            return {"intent": "debug_info", "entities": {}}
            
        elif any(w in text for w in ["config", "make", "stop", "change", "set", "category", "folder", "enable", "disable"]):
            return self._handle_config(text)

        elif any(w in text for w in ["clean", "cleanup", "fix", "health", "audit"]):
            return {"intent": "run_cleanup", "entities": {}}

        # 2. General Search (Lowest priority)
        if any(w in text for w in ["find", "show", "search", "where is", "where are", "look for"]):
            return self._handle_search(text)
            
        # Fallback to general search if unsure
        return self._handle_search(text)
            
        # Fallback to general search if unsure
        return self._handle_search(text)

    def _handle_search(self, text: str) -> Dict[str, Any]:
        """Extracts search criteria."""
        entities = {}
        
        # Extension extraction (e.g. "pdfs", "images", "text files")
        ext_map = {
            "pdf": ".pdf", "pdfs": ".pdf",
            "image": "Images", "images": "Images",
            "video": "Videos", "videos": "Videos",
            "document": "Documents", "documents": "Documents",
            "music": "Audio", "audio": "Audio",
            "zip": ".zip", "zips": ".zip", "archive": ".zip"
        }
        for word, val in ext_map.items():
            if word in text:
                if val.startswith("."):
                    entities["extension"] = val
                else:
                    entities["category"] = val

        # Size extraction (e.g. "large", "> 5mb", "bigger than 10gb")
        if "large" in text or "big" in text:
            entities["min_size"] = 10 * 1024 * 1024 # 10MB
        
        # Improved regex to handle "larger than", "bigger than", etc.
        size_match = re.search(r'(?:larger|bigger|more than|above|>)\s*(?:than\s*)?(\d+)\s*(mb|gb|kb)', text)
        if size_match:
            val = int(size_match.group(1))
            unit = size_match.group(2).lower()
            mult = {"kb": 1024, "mb": 1024*1024, "gb": 1024*1024*1024}
            entities["min_size"] = val * mult[unit]

        # Date extraction (e.g. "today", "yesterday", "last week")
        now = datetime.now()
        if "today" in text:
            entities["date_after"] = now.replace(hour=0, minute=0, second=0).isoformat()
        elif "yesterday" in text:
            entities["date_after"] = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0).isoformat()
        elif "last week" in text:
            entities["date_after"] = (now - timedelta(days=7)).isoformat()

        # Filename extraction (everything else between quotes or common markers)
        name_match = re.search(r'"([^"]+)"', text)
        if name_match:
            entities["filename"] = name_match.group(1)

        if not entities:
            # If we didn't extract any meaningful search criteria, don't just return all files.
            # Convert "unknown" text to a filename search if it looks like a single word query?
            # Or just return unknown.
            # Let's try to interpret the whole text as a filename if it's short
            if len(text.split()) < 3:
                entities["filename"] = text
            else:
                 return {"intent": "unknown", "entities": {}}

        return {"intent": "search_files", "entities": entities}

    def _handle_config(self, text: str) -> Dict[str, Any]:
        """Extracts configuration change requests."""
        entities = {}
        
        # Category creation/modification
        if "category" in text or "folder" in text:
            # "make music go into Audio folder"
            # "create a category for screenshots"
            entities["action"] = "update_mapping"
            
            # Simple keyword extraction for now
            if "screenshot" in text:
                entities["target"] = "Screenshots"
                entities["extensions"] = [".png", ".jpg"]
            
        if "stop" in text:
            entities["action"] = "toggle_monitor"
            entities["value"] = False
            
        if "enable cleanup" in text or "real cleanup" in text:
            entities["action"] = "set_cleanup_mode"
            entities["value"] = False # dry_run = False
            
        if any(w in text for w in ["run", "every", "minutes"]):
            interval_match = re.search(r'(\d+)\s*minutes', text)
            if interval_match:
                entities["action"] = "set_interval"
                entities["value"] = int(interval_match.group(1))

        return {"intent": "update_config", "entities": entities}

# Lazy initialization to avoid recursive process issues on import
_nlp_service_instance = None

def get_nlp_service():
    global _nlp_service_instance
    if _nlp_service_instance is None:
        _nlp_service_instance = NlpService()
    return _nlp_service_instance
