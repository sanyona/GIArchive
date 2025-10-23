from urllib.parse import unquote


def clean_text(text: str) -> str:
    return unquote(text)
