"""
Smart Config Agent
------------------
Safety layer that validates and applies configuration changes from the NLP engine.
Ensures that natural language commands don't break the system schema.
"""
from typing import Dict, Any, Tuple
from src.services.config_service import config_service
from src.services.logger import logger

class ConfigAgent:
    """Validates NLP entities and translates them into ConfigService calls."""
    
    def validate_and_propose(self, entities: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Validates the request and returns a proposal.
        Returns: (is_valid, description, suggested_patch)
        """
        action = entities.get("action")
        if not action:
            return False, "No clear configuration action detected.", {}

        if action == "update_mapping":
            target = entities.get("target")
            exts = entities.get("extensions", [])
            if not target:
                return False, "I'm not sure which category or folder you want to create.", {}
            
            current_categories = config_service.get_categories()
            new_categories = current_categories.copy()
            new_categories[target] = list(set(new_categories.get(target, []) + exts))
            
            return True, f"Add {exts} to category '{target}'?", {"categories": new_categories}

        if action == "toggle_monitor":
            val = entities.get("value", True)
            return True, f"{'Enable' if val else 'Disable'} real-time monitoring?", {"monitor_enabled": val}

        if action == "set_interval":
            val = entities.get("value")
            if val and 1 <= val <= 1440: # 1 min to 24 hours
                auto = config_service.get("automation", {}).copy()
                auto["auto_scan_interval_min"] = val
                auto["enable_auto_scan"] = True
                return True, f"Set auto-scan interval to {val} minutes?", {"automation": auto}
            return False, "Interval must be between 1 and 1440 minutes.", {}

        if action == "set_cleanup_mode":
            # value=False means dry_run=False (i.e. Enable Real Cleanup)
            dry_run = entities.get("value", True) 
            cleanup = config_service.get("cleanup", {}).copy()
            cleanup["dry_run"] = dry_run
            mode_str = "DRY RUN (Safe Mode)" if dry_run else "LIVE MODE (Real Deletions)"
            return True, f"Set cleanup to {mode_str}?", {"cleanup": cleanup}

        return False, f"Unknown configuration action: {action}", {}

    def apply_patch(self, patch: Dict[str, Any]):
        """Applies a verified patch to the active configuration."""
        current_config = config_service.config.copy()
        # Shallow merge the patches
        for key, value in patch.items():
            current_config[key] = value
        
        config_service.save_config(current_config)
        logger.info(f"Smart Config Agent applied changes: {list(patch.keys())}")

config_agent = ConfigAgent()
