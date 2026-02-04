import pytest
import json
from pathlib import Path
from src.services.config_service import ConfigService, config_service

@pytest.fixture
def mock_config(tmp_path, mocker):
    """Fixture to reset config_service and use a temp path."""
    cfg_file = tmp_path / "config.json"
    # Patch the instance variable
    mocker.patch.object(config_service, "_config_path", cfg_file)
    # Reset instance state to force reload
    config_service.config = {}
    return cfg_file

def test_config_default_fallback(mock_config):
    # Reload config to trigger fallback
    config_service.config = config_service._load_config()
    assert config_service.get("monitor_enabled") is True
    assert "Images" in config_service.get("categories")

def test_config_save_and_reload(mock_config):
    new_cfg = config_service.config.copy()
    new_cfg["monitor_enabled"] = False
    
    config_service.save_config(new_cfg)
    
    # Verify file content
    with open(mock_config, "r") as f:
        data = json.load(f)
        assert data["monitor_enabled"] is False

    # Verify internal state
    assert config_service.get("monitor_enabled") is False

def test_config_validation(mock_config):
    # Write invalid config (wrong type for monitor_enabled)
    with open(mock_config, "w") as f:
        json.dump({"monitor_enabled": "not_a_boolean"}, f)
        
    # Reload should trigger validation
    config_service.config = config_service._load_config()
    # Should fallback to default True
    assert config_service.get("monitor_enabled") is True
