import pytest
from pathlib import Path
from src.core.health_engine import HealthEngine
from src.services.health_service import HealthService

def test_hashing_duplicates(tmp_path):
    engine = HealthEngine()
    
    # Create two identical files
    file1 = tmp_path / "file1.txt"
    file2 = tmp_path / "file2.txt"
    content = "identical content"
    file1.write_text(content)
    file2.write_text(content)
    
    # Create a different file
    file3 = tmp_path / "file3.txt"
    file3.write_text("different content")
    
    report = engine.scan_directory(tmp_path)
    
    assert len(report["duplicates"]) == 1
    # Check that both duplicate paths are captured
    duplicate_paths = list(report["duplicates"].values())[0]
    assert file1 in duplicate_paths
    assert file2 in duplicate_paths
    assert file3 not in duplicate_paths

def test_empty_folders(tmp_path):
    engine = HealthEngine()
    
    empty_dir = tmp_path / "EmptyDir"
    empty_dir.mkdir()
    
    non_empty_dir = tmp_path / "FullDir"
    non_empty_dir.mkdir()
    (non_empty_dir / "file.txt").write_text("data")
    
    report = engine.scan_directory(tmp_path)
    
    assert empty_dir in report["empty_folders"]
    assert non_empty_dir not in report["empty_folders"]

def test_dry_run_safety(tmp_path, mocker):
    # Mock config to force dry_run ON
    mocker.patch("src.services.config_service.config_service.get", side_effect=lambda k, default=None: {"dry_run": True} if k == "cleanup" else default)
    
    # Mock deletion to verify it's NOT called
    mock_delete = mocker.patch("src.core.organizer.organizer.delete_file")
    
    service = HealthService()
    report = {
        "duplicates": {"hash1": [tmp_path / "keep", tmp_path / "delete"]},
        "zero_byte_files": [tmp_path / "empty"],
        "orphans": [],
        "empty_folders": []
    }
    
    service.execute_cleanup(report)
    
    # delete_file should NOT be called in dry-run
    mock_delete.assert_not_called()

def test_zero_byte_detection(tmp_path):
    engine = HealthEngine()
    
    zero_file = tmp_path / "zero.txt"
    zero_file.write_text("")
    
    real_file = tmp_path / "real.txt"
    real_file.write_text("content")
    
    report = engine.scan_directory(tmp_path)
    
    assert zero_file in report["zero_byte_files"]
    assert real_file not in report["zero_byte_files"]
