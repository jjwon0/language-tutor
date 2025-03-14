"""Command to update Anki card styling.

This module provides a command to update the styling of Anki cards without
modifying the content of the cards themselves.
"""

from tutor.utils.anki import AnkiConnectClient


def update_card_styling_inner(model_name: str = "chinese-tutor") -> str:
    """Update the styling of Anki cards.

    Args:
        model_name: The name of the Anki model to update. Defaults to "chinese-tutor".

    Returns:
        str: A message indicating the result of the operation.
    """
    client = AnkiConnectClient()

    # Get the CSS and templates for the Chinese tutor cards
    css = get_card_css()
    templates = get_card_templates()

    # Update the card styling and templates
    client.update_card_styling_and_templates(
        model_name=model_name, css=css, templates=templates
    )
    return f"Card styling updated successfully for model '{model_name}'."


def get_card_css() -> str:
    """Get the CSS for the card styling.

    Returns:
        str: The CSS for the card styling.
    """
    return """.card {
    font-family: "Helvetica", "Arial", sans-serif;
    font-size: 28px;
    text-align: center;
    color: #333;
    background-color: #f9f9f9;
    padding: 20px;
    max-width: 100%;
    box-sizing: border-box;
}

.hanzi {
    font-family: "SimSun", "Noto Sans CJK SC", sans-serif;
    font-size: 30px;
    color: #2c3e50;
    margin-bottom: 10px;
}

.pinyin {
    font-family: "Helvetica", "Arial", sans-serif;
    font-size: 20px;
    color: #7f8c8d;
    margin-bottom: 5px;
}

.english {
    font-family: "Helvetica", "Arial", sans-serif;
    font-size: 22px;
    color: #34495e;
    margin-bottom: 15px;
    max-width: 100%;
    overflow-wrap: break-word;
}

.translation {
    font-size: 22px;
    color: #34495e;
    margin-bottom: 10px;
    max-width: 100%;
    overflow-wrap: break-word;
}

.notes {
    font-family: "Helvetica", "Arial", sans-serif;
    font-size: 18px;
    color: #34495e;
    background-color: #f5f6fa;
    padding: 10px;
    border-radius: 5px;
    margin: 10px auto;
    text-align: left;
    max-width: 95%;
    box-sizing: border-box;
}

.spacer { height: 20px; }
.spacerSmall { height: 5px; }
.spacerMedium { height: 15px; }

.audio {
    font-family: "Helvetica", "Arial", sans-serif;
    font-size: 16px;
    color: #3498db;
    margin-top: 10px;
}

.audio:hover {
    color: #2980b9;
    cursor: pointer;
}

/* Related words section */
.related-words {
    font-family: "Helvetica", "Arial", sans-serif;
    font-size: 18px;
    color: #34495e;
    background-color: #f5f6fa;
    padding: 12px;
    border-radius: 5px;
    margin: 10px auto;
    text-align: left;
    max-width: 95%;
    line-height: 1.4;
    box-sizing: border-box;
}

.related-words-title {
    font-weight: bold;
    color: #2c3e50;
    margin-bottom: 8px;
    font-size: 18px;
    display: block;
    border-bottom: 1px solid #e0e0e0;
    padding-bottom: 5px;
}

.related-words-content {
    white-space: pre-wrap; /* Preserve newlines but wrap text */
    font-family: "Helvetica", "Arial", sans-serif;
    font-size: 16px;
    color: #34495e;
    overflow-wrap: break-word;
    word-break: break-word;
}"""


def get_card_templates() -> dict:
    """Get the templates for the card styling.

    Returns:
        dict: The templates for the card styling.
    """
    return {
        "Chinese front": {
            "Front": """<div class="hanzi">{{Chinese}}</div>
<div class="spacerSmall"></div>
<div style="border-bottom: 1px solid #ddd; width: 50%; margin: 0 auto;"></div>
<div class="spacer"></div>
<div class="english">
    <div class="spacerMedium"></div>
    <div class="notes">
        <strong>Sample Usage:</strong> {{Sample Usage}}
    </div>
</div>""",
            "Back": """<div class="hanzi">{{Chinese}}</div>
<div class="spacerSmall"></div>
<div style="border-bottom: 1px solid #ddd; width: 50%; margin: 0 auto;"></div>
<div class="spacer"></div>
<div class="english">
    <div class="pinyin">{{Pinyin}}</div>
    <div class="spacerSmall"></div>
    <div class="translation">{{English}}</div>
    <div class="spacerMedium"></div>
    <div class="notes">
        <strong>Sample Usage:</strong> {{Sample Usage}}
        <div class="spacerSmall"></div>
        <strong>Translation:</strong> {{Sample Usage (English)}}
    </div>
    <div class="spacerSmall"></div>
    {{#Related Words}}
    <div class="related-words">
        <div class="related-words-title">Related Words</div>
        <div class="related-words-content">{{Related Words}}</div>
    </div>
    {{/Related Words}}
    <div class="audio">{{Sample Usage (Audio)}}</div>
</div>""",
        },
        "English front": {
            "Front": """<div class="hanzi">{{English}}</div>
<div class="spacerSmall"></div>
<div class="notes">
    <strong>Translation:</strong> {{Sample Usage (English)}}
</div>""",
            "Back": """<div class="hanzi">{{English}}</div>
<div class="spacerSmall"></div>
<div style="border-bottom: 1px solid #ddd; width: 50%; margin: 0 auto;"></div>
<div class="spacer"></div>
<div class="english">
    <div class="pinyin">{{Pinyin}}</div>
    <div class="spacerSmall"></div>
    <div class="translation">{{Chinese}}</div>
    <div class="spacerMedium"></div>
    <div class="notes">
        <strong>Sample Usage:</strong> {{Sample Usage}}
        <div class="spacerSmall"></div>
        <strong>Translation:</strong> {{Sample Usage (English)}}
    </div>
    <div class="spacerSmall"></div>
    {{#Related Words}}
    <div class="related-words">
        <div class="related-words-title">Related Words</div>
        <div class="related-words-content">{{Related Words}}</div>
    </div>
    {{/Related Words}}
    <div class="audio">{{Sample Usage (Audio)}}</div>
</div>""",
        },
    }
