"""
Main GUI Container
------------------
Root window for the CustomTkinter application.
Handles view switching, navigation, and global layout.
"""
import customtkinter as ctk
from src.services.config_service import config_service
from src.services.logger import logger
from .dashboard import DashboardFrame
from .logs import LogsFrame
from .settings import SettingsFrame
from .maintenance import MaintenanceFrame
from .chat import ChatFrame

class App(ctk.CTk):
    """Main application window container and navigation controller."""
    def __init__(self):
        super().__init__()

        # Window Setup
        self.title("Standard File Manager - Pro Edition")
        self.geometry(config_service.get("gui_preferences", {}).get("window_size", "1000x600"))
        
        # Grid layout (1x2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar_frame = ctk.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="FileManager", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.dashboard_btn = ctk.CTkButton(self.sidebar_frame, text="Dashboard", command=lambda: self.select_frame("dashboard"), corner_radius=0, height=40, border_spacing=10, fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), anchor="w")
        self.dashboard_btn.grid(row=1, column=0, sticky="ew")
        
        self.logs_btn = ctk.CTkButton(self.sidebar_frame, text="Logs", command=lambda: self.select_frame("logs"), corner_radius=0, height=40, border_spacing=10, fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), anchor="w")
        self.logs_btn.grid(row=2, column=0, sticky="ew")
        
        self.settings_btn = ctk.CTkButton(self.sidebar_frame, text="Settings", command=lambda: self.select_frame("settings"), corner_radius=0, height=40, border_spacing=10, fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), anchor="w")
        self.settings_btn.grid(row=3, column=0, sticky="ew")

        self.maintenance_btn = ctk.CTkButton(self.sidebar_frame, text="Maintenance", command=lambda: self.select_frame("maintenance"), corner_radius=0, height=40, border_spacing=10, fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), anchor="w")
        self.maintenance_btn.grid(row=4, column=0, sticky="ew")

        self.assistant_btn = ctk.CTkButton(self.sidebar_frame, text="Assistant", command=lambda: self.select_frame("assistant"), corner_radius=0, height=40, border_spacing=10, fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), anchor="w")
        self.assistant_btn.grid(row=5, column=0, sticky="ew")

        self.appearance_mode_menu = ctk.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"], command=self.change_appearance_mode)
        self.appearance_mode_menu.grid(row=6, column=0, padx=20, pady=20)
        self.appearance_mode_menu.set(config_service.get("gui_preferences", {}).get("theme", "Dark").capitalize())

        # Main Content Frames
        self.dashboard_frame = DashboardFrame(self, corner_radius=0, fg_color="transparent")
        self.logs_frame = LogsFrame(self, corner_radius=0, fg_color="transparent")
        self.settings_frame = SettingsFrame(self, corner_radius=0, fg_color="transparent")
        self.maintenance_frame = MaintenanceFrame(self, corner_radius=0, fg_color="transparent")
        self.assistant_frame = ChatFrame(self, corner_radius=0, fg_color="transparent")

        # Initial Frame
        self.select_frame("dashboard")

    def select_frame(self, name):
        # Reset button colors
        self.dashboard_btn.configure(fg_color=("gray75", "gray25") if name == "dashboard" else "transparent")
        self.logs_btn.configure(fg_color=("gray75", "gray25") if name == "logs" else "transparent")
        self.settings_btn.configure(fg_color=("gray75", "gray25") if name == "settings" else "transparent")
        self.maintenance_btn.configure(fg_color=("gray75", "gray25") if name == "maintenance" else "transparent")
        self.assistant_btn.configure(fg_color=("gray75", "gray25") if name == "assistant" else "transparent")

        # Show selected frame
        if name == "dashboard":
            self.dashboard_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.dashboard_frame.grid_forget()
            
        if name == "logs":
            self.logs_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.logs_frame.grid_forget()
            
        if name == "settings":
            self.settings_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.settings_frame.grid_forget()

        if name == "maintenance":
            self.maintenance_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.maintenance_frame.grid_forget()

        if name == "assistant":
            self.assistant_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.assistant_frame.grid_forget()

    def change_appearance_mode(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)
        # Update config
        pref = config_service.get("gui_preferences", {})
        pref["theme"] = new_appearance_mode.lower()
        config_service.save_config({"gui_preferences": pref})

def start_gui():
    ctk.set_appearance_mode(config_service.get("gui_preferences", {}).get("theme", "dark"))
    ctk.set_default_color_theme("blue")
    app = App()
    app.mainloop()
