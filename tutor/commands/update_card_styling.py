"""Command to update Anki card styling.

This module provides a command to update the styling of Anki cards without
modifying the content of the cards themselves.
"""

from tutor.utils.anki import AnkiConnectClient
from tutor.commands.setup_anki import get_card_css, get_card_templates


def update_card_styling_inner(model_name: str = "chinese-tutor") -> str:
    """Update the styling of Anki cards.

    Args:
        model_name: The name of the Anki model to update. Defaults to "chinese-tutor".

    Returns:
        str: A message indicating the result of the operation.
    """
    client = AnkiConnectClient()

    # Determine which language templates to use based on the model name
    language = "mandarin"  # Default
    if "cantonese" in model_name.lower():
        language = "cantonese"

    # Get the CSS and templates for the specified language
    css = get_card_css(language)
    templates = get_card_templates(language)

    # Update the card styling and templates
    client.update_card_styling_and_templates(
        model_name=model_name, css=css, templates=templates
    )
    return f"Card styling updated successfully for model '{model_name}'."


# Note: get_card_css and get_card_templates functions are now imported from setup_anki.py
