import click
from tutor.utils.anki import AnkiConnectClient
from tutor.llm_flashcards import (
    generate_flashcards,
    get_word_exists_query,
)
from tutor.utils.logging import dprint
from tutor.llm.prompts import get_generate_flashcard_from_word_prompt
from tutor.utils.azure import text_to_speech
from tutor.cli_global_state import get_skip_confirm
from tutor.utils.config import get_config
from tutor.language_processing import LanguagePreprocessor


@click.command()
@click.argument("word", type=str)
@click.option(
    "--language",
    type=click.Choice(["mandarin", "cantonese"]),
    default=None,
    help="Language for the flashcard (defaults to config setting)",
)
def regenerate_flashcard(word: str, language: str = None) -> None:
    """Regenerate Anki flashcard for a specific WORD."""
    # Use provided language or default from config
    lang = language or get_config().default_language
    result = _regenerate_flashcard_impl(word, lang)
    if result:
        click.echo(result)


def _regenerate_flashcard_impl(word: str, language: str = "mandarin") -> str:
    """Implementation of regenerate_flashcard command.

    Args:
        word: The word to regenerate the flashcard for
        language: The language to generate flashcards for ("mandarin" or "cantonese")

    Returns:
        A message describing the result of the operation, or None if operation was cancelled
    """
    # Process word based on language (simplified for Mandarin, traditional for Cantonese)
    processed_word = LanguagePreprocessor.process_for_language(word, language)

    ankiconnect_client = AnkiConnectClient()
    flashcards = ankiconnect_client.find_notes(
        get_word_exists_query(processed_word, language)
    )
    if not flashcards:
        return f"Could not find any cards matching '{processed_word}', exiting"

    if len(flashcards) > 1:
        return (
            f"Error: Multiple cards match '{processed_word}'. Please be more specific."
        )

    flashcard = flashcards[0]
    click.echo(f"Found flashcard: {flashcard}")

    # Check if we should skip confirmation
    if not get_skip_confirm():
        user_input = input("Regenerate this card? (y/N): ").strip().lower()
        if user_input != "y":
            click.echo("Operation cancelled by user.")
            return None

    note_id = flashcard.anki_note_id
    prompt = get_generate_flashcard_from_word_prompt(processed_word, language)
    dprint(prompt)
    flashcards = generate_flashcards(prompt, language)
    dprint(flashcards)
    new_flashcard = flashcards.flashcards[0]
    audio_filepath = text_to_speech(new_flashcard.sample_usage, language)
    ankiconnect_client.update_flashcard(note_id, new_flashcard, audio_filepath)

    return f"Updated! The new flashcard is below:\n{new_flashcard}"
