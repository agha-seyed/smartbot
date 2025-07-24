import pytest
import json
from studentbot.utils.text_formatter import sanitize_markdown

def test_sanitize_markdown():
    text = "This is a *test* with [some] special characters."
    sanitized_text = sanitize_markdown(text)
    assert sanitized_text == r"This is a \*test\* with \[some\] special characters\."

def test_load_language_files():
    langs = ["en", "fa", "it"]
    for lang in langs:
        try:
            with open(f'studentbot/lang/{lang}.json', 'r', encoding='utf-8') as f:
                json.load(f)
        except FileNotFoundError:
            pytest.fail(f"Language file for '{lang}' not found.")
        except json.JSONDecodeError:
            pytest.fail(f"Could not decode JSON for language '{lang}'.")

def test_knowledge_base_format():
    try:
        with open('studentbot/lang/knowledge_base.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            assert isinstance(data, dict)
            assert "en" in data
            assert "fa" in data
            assert "it" in data
    except FileNotFoundError:
        pytest.fail("knowledge_base.json not found.")
    except json.JSONDecodeError:
        pytest.fail("Could not decode knowledge_base.json.")
