import click
import sys
from typing import List, Optional, Tuple

from tutor.utils.anki import AnkiConnectClient
from tutor.llm_flashcards import (
    generate_flashcards,
    maybe_add_flashcards_to_deck,
    get_word_exists_query,
)
from tutor.llm.prompts import get_generate_flashcard_from_word_prompt
from tutor.utils.logging import dprint
from tutor.utils.config import get_config
from tutor.language_processing import LanguagePreprocessor


def read_words_from_stdin() -> List[str]:
    """Read words from stdin, handling both piped input and interactive input."""
    if sys.stdin.isatty():
        # No piped input, return empty list
        return []

    # Read from stdin and split on whitespace/newlines
    content = sys.stdin.read().strip()
    return [word for word in content.split() if word]


@click.command()
@click.argument("words", type=str, nargs=-1)
@click.option("--deck", type=str, default=None)
@click.option(
    "--language",
    type=click.Choice(["mandarin", "cantonese"]),
    default=None,
    help="Language for the flashcard (defaults to config setting)",
)
def generate_flashcard_from_word(
    deck: Optional[str], language: Optional[str], words: Tuple[str, ...]
) -> None:
    """Add new Anki flashcards for one or more WORDS to DECK.

    Examples:
        ct g 你好                           # Single word (using default language)
        ct g --language cantonese 你好       # Single word in Cantonese
        ct g 你好 再见 谢谢                 # Multiple space-separated words
        echo "你好\n再见" | ct g             # Read from stdin (newline-separated)
    """
    # Combine words from arguments and stdin
    all_words = list(words)
    stdin_words = read_words_from_stdin()
    if stdin_words:
        all_words.extend(stdin_words)

    if not all_words:
        click.echo("Please provide at least one word")
        return

    # Use provided values or defaults from config
    deck_name = deck or get_config().default_deck
    lang = language or get_config().default_language

    _generate_flashcard_from_word_impl(deck_name, tuple(all_words), lang)


def _generate_flashcard_from_word_impl(
    deck: str, words: tuple[str, ...], language: str = "mandarin"
) -> None:
    """Implementation of generate_flashcard_from_word command.

    For each word:
    1. Convert traditional characters to simplified (if any)
    2. Check if the card already exists in Anki
    3. Generate flashcard content using OpenAI if needed
    4. Add the flashcard to Anki if it doesn't already exist

    Args:
        deck: The Anki deck to add flashcards to
        words: The words to generate flashcards for
        language: The language to generate flashcards for ("mandarin" or "cantonese")
    """
    ankiconnect_client = AnkiConnectClient()
    total = len(words)

    for i, word in enumerate(words, 1):
        # Process word based on language (simplified for Mandarin, traditional for Cantonese)
        word = LanguagePreprocessor.process_for_language(word, language)

        if total > 1:
            click.echo(f"\nProcessing word {i}/{total}: {word}")

        # Check if card already exists
        existing_cards = ankiconnect_client.find_notes(
            get_word_exists_query(word, language)
        )
        if existing_cards:
            click.echo(f"Card for '{word}' exists already:\n{existing_cards[0]}")
            continue

        # Generate new card content
        prompt = get_generate_flashcard_from_word_prompt(word, language)
        dprint(prompt)
        flashcards = generate_flashcards(prompt, language)
        dprint(flashcards)

        if not maybe_add_flashcards_to_deck(flashcards, deck):
            click.echo(f"No new flashcard added for '{word}'")
