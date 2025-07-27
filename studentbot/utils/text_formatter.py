import re

def sanitize_markdown(text: str) -> str:
    """
    Escapes characters that have a special meaning in MarkdownV2.
    """
    escape_chars = r'\_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)
