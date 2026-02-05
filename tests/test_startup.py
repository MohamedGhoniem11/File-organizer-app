import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Ensure src is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock winshell and win32com before importing startup_service
sys.modules['winshell'] = MagicMock()
sys.modules['win32com'] = MagicMock()
sys.modules['win32com.client'] = MagicMock()

from src.services.startup_service import StartupService

class TestStartupService(unittest.TestCase):
    def test_enable_startup(self):
        # Setup mocks
        mock_dispatch = sys.modules['win32com.client'].Dispatch
        mock_winshell = sys.modules['winshell']
        
        mock_winshell.startup.return_value = "C:\\Startup"
        mock_shortcut = MagicMock()
        mock_shell = MagicMock()
        mock_shell.CreateShortCut.return_value = mock_shortcut
        mock_dispatch.return_value = mock_shell
        
        service = StartupService()
        service.enable_startup()
        
        # Verify Dispatch called (WScript.Shell)
        mock_dispatch.assert_called_with('WScript.Shell')
        # Verify Save called
        mock_shortcut.save.assert_called_once()
        
    @patch('src.services.startup_service.winshell')
    @patch('src.services.startup_service.os.remove')
    @patch('pathlib.Path.exists')
    def test_disable_startup(self, mock_exists, mock_remove, mock_winshell):
         mock_winshell.startup.return_value = "C:\\Startup"
         mock_exists.return_value = True
         
         service = StartupService()
         service.disable_startup()
         mock_remove.assert_called_once()

if __name__ == "__main__":
    unittest.main()
