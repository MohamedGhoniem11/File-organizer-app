"""
Reliability tests for the NLP Service.
Verifies that the system falls back to rules if spaCy is missing.
"""
import pytest
from unittest.mock import patch, MagicMock
from src.services.nlp_service import get_nlp_service

def test_nlp_fallback_mode():
    """Verifies that the service enters fallback mode if spaCy fails to load."""
    with patch("spacy.load", side_effect=OSError("Model not found")):
        # Mock spacy.cli.download to fail too
        with patch("spacy.cli.download", side_effect=Exception("No internet")):
            # Clear previous lazy instance for clean test
            from src.services import nlp_service
            nlp_service._nlp_service_instance = None
            service = get_nlp_service()
            assert service.is_fallback_mode is True
            assert service.nlp is None

def test_nlp_example_prompts_fallback():
    """Ensures major intents still work even in fallback (rule-based) mode."""
    with patch("spacy.load", side_effect=OSError):
        with patch("spacy.cli.download", side_effect=Exception):
            from src.services import nlp_service
            nlp_service._nlp_service_instance = None
            service = get_nlp_service()
            
            # Search fallback
            res_search = service.parse("find pdfs from today")
            assert res_search["intent"] == "search_files"
            assert res_search["entities"]["extension"] == ".pdf"
            
            # Config fallback
            res_config = service.parse("stop organizing zip files")
            assert res_config["intent"] == "update_config"
            assert res_config["entities"]["action"] == "toggle_monitor"
            
            # Cleanup fallback
            res_cleanup = service.parse("run cleanup")
            assert res_cleanup["intent"] == "run_cleanup"

def test_nlp_auto_download_success():
    """Verifies that auto-download is attempted if model is missing."""
    with patch("spacy.load") as mock_load:
        # First call fails, second succeeds after mock download
        mock_load.side_effect = [OSError("Missing"), MagicMock()]
        with patch("spacy.cli.download") as mock_download:
            from src.services import nlp_service
            nlp_service._nlp_service_instance = None
            service = get_nlp_service()
            assert mock_download.called
            assert service.is_fallback_mode is False
