from pathlib import Path

# src
PARENT_DIR = Path(__file__).parent.parent.resolve()

HTML_DIR = PARENT_DIR / "html"
LINKS_DIR = PARENT_DIR / "links"
ARCHIVE_DIR = PARENT_DIR / "archive"
TEXT_DIR = ARCHIVE_DIR / "txt"
JSON_DIR = ARCHIVE_DIR / "json"
