import pytest
import time
from pathlib import Path
from src.services.observer import observer_service, DownloadHandler
from src.services.config_service import config_service

def test_observer_start_stop(mocker):
    # Mock observer to not actually start threads
    mocker.patch("watchdog.observers.Observer.start")
    mocker.patch("watchdog.observers.Observer.stop")
    mocker.patch("watchdog.observers.Observer.join")
    
    observer_service.start()
    assert observer_service.is_running is True
    
    observer_service.stop()
    assert observer_service.is_running is False

def test_handler_process_file(tmp_path, mocker):
    # Mock organizer and classifier
    mock_move = mocker.patch("src.core.organizer.organizer.move_file")
    mocker.patch("src.core.classifier.classifier.classify", return_value="Documents")
    
    handler = DownloadHandler()
    test_file = tmp_path / "test.txt"
    test_file.write_text("content")
    
    handler._process_file(test_file)
    
    # Verify move_file was called with correct target
    mock_move.assert_called_once()
    args, _ = mock_move.call_args
    assert args[0] == test_file
    assert args[1] == tmp_path / "Documents"

def test_observer_restart_on_config(mocker):
    mocker.patch("src.services.observer.ObserverService.start")
    mocker.patch("src.services.observer.ObserverService.stop")
    
    observer_service.is_running = True
    observer_service.restart_if_needed({"monitor_enabled": True})
    
    # Should call stop and then start
    observer_service.stop.assert_called()
    observer_service.start.assert_called()
