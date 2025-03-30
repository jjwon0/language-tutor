import click
from tutor.utils.anki import AnkiConnectClient
from tutor.llm_flashcards import (
    generate_flashcards,
    get_word_exists_query,
)
from tutor.utils.logging import dprint
from tutor.llm.prompts import get_generate_flashcard_from_word_prompt
from tutor.utils.azure import text_to_speech
from tutor.utils.chinese import to_simplified
from tutor.cli_global_state import get_skip_confirm


@click.command()
@click.argument("word", type=str)
def regenerate_flashcard(word: str) -> None:
    """Regenerate Anki flashcard for a specific WORD."""
    result = _regenerate_flashcard_impl(word)
    if result:
        click.echo(result)


def _regenerate_flashcard_impl(word: str) -> str:
    """Implementation of regenerate_flashcard command.

    Args:
        word: The word to regenerate the flashcard for

    Returns:
        A message describing the result of the operation, or None if operation was cancelled
    """
    # Convert traditional characters to simplified for consistency
    simplified_word = to_simplified(word)

    ankiconnect_client = AnkiConnectClient()
    flashcards = ankiconnect_client.find_notes(get_word_exists_query(simplified_word))
    if not flashcards:
        return f"Could not find any cards matching '{simplified_word}', exiting"

    if len(flashcards) > 1:
        return (
            f"Error: Multiple cards match '{simplified_word}'. Please be more specific."
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
    prompt = get_generate_flashcard_from_word_prompt(simplified_word)
    dprint(prompt)
    flashcards = generate_flashcards(prompt)
    dprint(flashcards)
    new_flashcard = flashcards.flashcards[0]
    audio_filepath = text_to_speech(new_flashcard.sample_usage)
    ankiconnect_client.update_flashcard(note_id, new_flashcard, audio_filepath)

    return f"Updated! The new flashcard is below:\n{new_flashcard}"
