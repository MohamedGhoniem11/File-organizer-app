import re
from pathlib import Path

def sanitize_filename(filename: str) -> str:
    """Removes illegal characters from filenames."""
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

def get_safe_path(base_dir: Path, filename: str) -> Path:
    """Returns a sanitized path in the base directory."""
    clean_name = sanitize_filename(filename)
    return base_dir / clean_name
