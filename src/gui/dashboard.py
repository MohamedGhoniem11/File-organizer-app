"""
Dashboard View
--------------
Primary status overview showing service state and current watch directory.
"""
import customtkinter as ctk
from src.services.observer import observer_service
from src.services.config_service import config_service
from src.services.logger import logger

class DashboardFrame(ctk.CTkFrame):
    """Visual representation of system health and real-time monitor status."""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.grid_columnconfigure(0, weight=1)
        
        # Title
        ctk.CTkLabel(self, text="System Dashboard", font=ctk.CTkFont(size=24, weight="bold")).grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        # Status Card
        self.status_frame = ctk.CTkFrame(self)
        self.status_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.status_frame.grid_columnconfigure(0, weight=1)
        
        self.status_label = ctk.CTkLabel(self.status_frame, text="Status: STOPPED", font=ctk.CTkFont(size=14))
        self.status_label.grid(row=0, column=0, padx=20, pady=10)
        
        # Control Buttons
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.grid(row=2, column=0, padx=20, pady=20, sticky="w")
        
        self.start_btn = ctk.CTkButton(self.btn_frame, text="Start Monitor", command=self.toggle_monitor)
        self.start_btn.grid(row=0, column=0, padx=(0, 10))
        
        self.info_label = ctk.CTkLabel(self, text=f"Watching: {config_service.get('watch_directory')}", font=ctk.CTkFont(size=12, slant="italic"))
        self.info_label.grid(row=3, column=0, padx=20, pady=5, sticky="w")
        
        # Additional Settings
        self.settings_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.settings_frame.grid(row=4, column=0, padx=20, pady=10, sticky="w")
        
        from src.services.startup_service import startup_service
        self.startup_var = ctk.BooleanVar(value=startup_service.is_enabled())
        
        self.startup_switch = ctk.CTkSwitch(
            self.settings_frame, 
            text="Run on Windows Startup", 
            command=self.toggle_startup,
            variable=self.startup_var
        )
        self.startup_switch.grid(row=0, column=0)

        self.update_status()

    def toggle_startup(self):
        from src.services.startup_service import startup_service
        from src.services.config_service import config_service
        
        if self.startup_var.get():
            startup_service.enable_startup()
            logger.info("Startup enabled via dashboard.")
        else:
            startup_service.disable_startup()
            logger.info("Startup disabled via dashboard.")
            
        # Persist preference
        auto = config_service.get("automation", {}).copy()
        auto["run_on_startup"] = self.startup_var.get()
        config_service.save_config({"automation": auto})

    def toggle_monitor(self):
        if observer_service.is_running:
            observer_service.stop()
            logger.info("Monitor stopped manually via dashboard.")
        else:
            observer_service.start()
            logger.info("Monitor started manually via dashboard.")
        self.update_status()

    def update_status(self):
        if observer_service.is_running:
            self.status_label.configure(text="Status: ACTIVE", text_color="#2ecc71")
            self.start_btn.configure(text="Stop Monitor", fg_color="#e74c3c", hover_color="#c0392b")
        else:
            self.status_label.configure(text="Status: INACTIVE", text_color="#95a5a6")
            self.start_btn.configure(text="Start Monitor", fg_color="#3498db", hover_color="#2980b9")
        
        self.info_label.configure(text=f"Watching: {config_service.get('watch_directory')}")
        self.after(1000, self.update_status)
