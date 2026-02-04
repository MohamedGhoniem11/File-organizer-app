import customtkinter as ctk
from src.services.config_service import config_service
from src.services.logger import logger

class SettingsFrame(ctk.CTkFrame):
    """A frame for editing configuration settings."""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(self, text="Configuration Settings", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        # Watch Directory
        ctk.CTkLabel(self, text="Watch Directory:").grid(row=1, column=0, padx=20, pady=(10, 0), sticky="w")
        self.watch_dir_entry = ctk.CTkEntry(self, width=400)
        self.watch_dir_entry.insert(0, config_service.get("watch_directory", ""))
        self.watch_dir_entry.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="w")
        
        # Monitor Toggle
        self.monitor_var = ctk.BooleanVar(value=config_service.get("monitor_enabled", True))
        self.monitor_switch = ctk.CTkSwitch(self, text="Enable Real-time Monitoring", variable=self.monitor_var)
        self.monitor_switch.grid(row=3, column=0, padx=20, pady=10, sticky="w")
        
        # Collision Strategy
        ctk.CTkLabel(self, text="Collision Strategy:").grid(row=4, column=0, padx=20, pady=(10, 0), sticky="w")
        self.strategy_option = ctk.CTkOptionMenu(self, values=["rename", "skip", "overwrite"])
        self.strategy_option.set(config_service.get("collision_strategy", "rename"))
        self.strategy_option.grid(row=5, column=0, padx=20, pady=(0, 10), sticky="w")
        
        # Save Button
        self.save_button = ctk.CTkButton(self, text="Save Settings", command=self.save_settings, fg_color="#2ecc71", hover_color="#27ae60")
        self.save_button.grid(row=6, column=0, padx=20, pady=20, sticky="w")

    def save_settings(self):
        new_config = config_service.config.copy()
        new_config["watch_directory"] = self.watch_dir_entry.get()
        new_config["monitor_enabled"] = self.monitor_var.get()
        new_config["collision_strategy"] = self.strategy_option.get()
        
        config_service.save_config(new_config)
        logger.info("Settings saved via GUI")
