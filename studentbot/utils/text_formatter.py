import re

def sanitize_markdown(text: str) -> str:
    """
    Sanitizes a string to be safely used with Telegram's MarkdownV2 parse mode.

    This function escapes characters that have a special meaning in MarkdownV2.
    See: https://core.telegram.org/bots/api#markdownv2-style

    Args:
        text (str): The input string to be sanitized.

    Returns:
        str: The sanitized string with special characters escaped.

    Example:
        >>> sanitize_markdown("This is a *bold* text with a [link](http://example.com)!")
        'This is a \\*bold\\* text with a \\[link\\]\\(http://example\\.com\\)\\!'
    """
    if not isinstance(text, str):
        return ""

    # Characters to escape
    escape_chars = r'\_*[]()~`>#+-=|{}.!'

    # Create a regex pattern to find and escape the characters
    # This pattern will match any of the special characters
    pattern = f'([{re.escape(escape_chars)}])'

    # Substitute the matched character with its escaped version
    return re.sub(pattern, r'\\\1', text)
