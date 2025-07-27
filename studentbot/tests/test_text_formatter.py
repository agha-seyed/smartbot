import pytest
from studentbot.utils.text_formatter import sanitize_markdown

@pytest.mark.parametrize("input_text, expected_output", [
    # Basic cases
    ("Hello *bold* text", "Hello \\*bold\\* text"),
    ("Hello _italic_ text", "Hello \\_italic\\_ text"),
    ("Hello `code` text", "Hello \\`code\\` text"),
    ("Hello ~strikethrough~ text", "Hello \\~strikethrough\\~ text"),

    # Link and brackets
    ("[link](http://example.com)", "\\[link\\]\\(http://example\\.com\\)"),
    ("Just a [bracket]", "Just a \\[bracket\\]"),

    # Punctuation
    ("End with a dot.", "End with a dot\\."),
    ("End with an exclamation!", "End with an exclamation\\!"),

    # Multiple characters
    ("A*B_C`D~E[F]G(H)I.J!K", "A\\*B\\_C\\`D\\~E\\[F\\]G\\(H\\)I\\.J\\!K"),

    # Multiline text
    ("First line.\nSecond line* with star.", "First line\\.\nSecond line\\* with star\\."),

    # Combined with other languages
    ("سلام *ستاره*", "سلام \\*ستاره\\*"),
    ("Ciao _mondo_", "Ciao \\_mondo\\_"),

    # Edge cases
    ("", ""),
    ("No special characters", "No special characters"),
    ("Already escaped \\*text\\*", "Already escaped \\\\\\*text\\\\\\*"), # It will escape the backslash
])
def test_sanitize_markdown(input_text, expected_output):
    """
    Test the sanitize_markdown function with various inputs.
    """
    assert sanitize_markdown(input_text) == expected_output

def test_sanitize_markdown_non_string_input():
    """
    Test that sanitize_markdown handles non-string input gracefully.
    """
    assert sanitize_markdown(None) == ""
    assert sanitize_markdown(123) == ""
    assert sanitize_markdown(["list"]) == ""
