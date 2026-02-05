import os
import sys
import winshell
from pathlib import Path
from win32com.client import Dispatch # type: ignore
from src.services.logger import logger

class StartupService:
    """
    Manages the application's auto-startup entry on Windows.
    Uses the user's Startup folder (shell:startup) to avoid needing Admin privileges.
    """

    def __init__(self):
        self.startup_dir = Path(winshell.startup())
        self.link_path = self.startup_dir / "FileManagerPro.lnk"
        self.executable_path = sys.executable if getattr(sys, 'frozen', False) else None
        self.script_path = str(Path(sys.modules['__main__'].__file__).parent.parent / "main.py") if not self.executable_path else None
        
        # Determine target: The EXE if frozen, else pythonw.exe running main.py
        if getattr(sys, 'frozen', False):
            self.target = sys.executable
            self.args = ""
            self.cwd = str(Path(sys.executable).parent)
        else:
            # Development mode: Run using pythonw.exe to avoid console window
            self.target = sys.executable.replace("python.exe", "pythonw.exe")
            # We need to point to the main module
            # Best effort assumption for dev mode
            self.cwd = os.getcwd()
            self.args = f"-m src.main"

    def is_enabled(self) -> bool:
        """Checks if the startup shortcut exists."""
        return self.link_path.exists()

    def enable_startup(self):
        """Creates a shortcut in the Windows Startup folder."""
        try:
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(str(self.link_path))
            shortcut.Targetpath = self.target
            shortcut.WorkingDirectory = self.cwd
            shortcut.Arguments = self.args
            shortcut.Description = "File Manager Pro Auto-Startup"
            shortcut.save()
            logger.info(f"Startup shortcut created at {self.link_path}")
        except Exception as e:
            logger.error(f"Failed to enable startup: {e}")

    def disable_startup(self):
        """Removes the shortcut from the Windows Startup folder."""
        try:
            if self.link_path.exists():
                os.remove(self.link_path)
                logger.info("Startup shortcut removed.")
        except Exception as e:
            logger.error(f"Failed to disable startup: {e}")

startup_service = StartupService()
