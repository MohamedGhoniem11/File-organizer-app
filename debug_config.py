from src.services.config_service import ConfigService, config_service

print(f"Class attribute: {ConfigService._config_path}")
print(f"Instance attribute: {config_service._config_path}")
