"""Command to update Anki card styling.

This module provides a command to update the styling of Anki cards without
modifying the content of the cards themselves.
"""

from pathlib import Path
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
    base_dir = Path(__file__).parent.parent / "card_styling" / "css"
    css_files = ["common.css", "chinese_front.css", "english_front.css"]

    combined_css = []
    for css_file in css_files:
        with open(base_dir / css_file) as f:
            combined_css.append(f.read())

    return "\n\n".join(combined_css)


def get_card_templates() -> dict:
    """Get the templates for the card styling.

    Returns:
        dict: The templates for the card styling.
    """
    base_dir = Path(__file__).parent.parent / "card_styling" / "templates"
    templates = {}

    # Load Chinese front templates
    with open(base_dir / "chinese_front_front.html") as f:
        chinese_front = f.read()
    with open(base_dir / "chinese_front_back.html") as f:
        chinese_back = f.read()
    templates["Chinese front"] = {"Front": chinese_front, "Back": chinese_back}

    # Load English front templates
    with open(base_dir / "english_front_front.html") as f:
        english_front = f.read()
    with open(base_dir / "english_front_back.html") as f:
        english_back = f.read()
    templates["English front"] = {"Front": english_front, "Back": english_back}

    return templates
