import click
import sys
from typing import Optional, List
from dotenv import load_dotenv

from tutor.commands.generate_topics import (
    generate_topics_prompt,
    select_conversation_topic,
)
from tutor.commands.generate_flashcard_from_word import (
    generate_flashcard_from_word_inner,
)
from tutor.commands.regenerate_flashcard import regenerate_flashcard
from tutor.commands.list_lesser_known_cards import list_lesser_known_cards
from tutor.commands.run_web import run_web
from tutor.commands.setup_anki import setup_anki
from tutor.commands.fix_cards import fix_cards
from tutor.llm_flashcards import GPT_3_5_TURBO, GPT_4, GPT_4o
from tutor.utils.config import get_config

from tutor.cli_global_state import set_debug, set_model, set_skip_confirm

load_dotenv()


@click.group()
@click.option(
    "--model",
    type=click.Choice([GPT_3_5_TURBO, GPT_4, GPT_4o]),
    default=GPT_4o,
    help="Customize the OpenAI model used",
)
@click.option("--debug/--no-debug", default=False, help="Turn on extra debug logging")
@click.option(
    "--skip-confirm", type=bool, default=False, help="Skip confirmation for commands"
)
def cli(model: str, debug: bool, skip_confirm: bool) -> None:
    """chinese-tutor tool"""
    set_model(model)
    set_debug(debug)
    set_skip_confirm(skip_confirm)


def read_words_from_stdin() -> List[str]:
    """Read words from stdin, handling both piped input and interactive input."""
    if sys.stdin.isatty():
        # No piped input, return empty list
        return []

    # Read from stdin and split on whitespace/newlines
    content = sys.stdin.read().strip()
    return [word for word in content.split() if word]


@cli.command()
@click.argument("words", type=str, nargs=-1)
@click.option("--deck", type=str, default=None)
@click.option(
    "--language",
    type=click.Choice(["mandarin", "cantonese"]),
    default=None,
    help="Language for the flashcard (defaults to config setting)",
)
def generate_flashcard_from_word(deck: str, language: str, words: tuple[str, ...]):
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
        print("Please provide at least one word")
        return

    # Use provided values or defaults from config
    deck = deck or get_config().default_deck
    language = language or get_config().default_language
    click.echo(generate_flashcard_from_word_inner(deck, tuple(all_words), language))


# Shortcut for the most common action.
cli.add_command(generate_flashcard_from_word, name="g")


# Add regenerate_flashcard command and shortcut
cli.add_command(regenerate_flashcard, name="regenerate-flashcard")
cli.add_command(regenerate_flashcard, name="rg")


@cli.command()
@click.argument("deck", required=False)
def config(deck: Optional[str]) -> None:
    """View or set the default deck configuration.

    If DECK is provided, sets the default deck.
    If no DECK is provided, shows current configuration.
    """
    if deck:
        get_config().default_deck = deck
        click.echo(f"Default deck set to: {deck}")
    else:
        try:
            current_deck = get_config().default_deck
            click.echo(f"Current default deck: {current_deck}")
        except ValueError as e:
            click.echo(str(e), err=True)
            click.echo("Use 'config DECK' to set a default deck")
            exit(1)


# Add commands
cli.add_command(run_web, name="web")
cli.add_command(setup_anki, name="setup-anki")
cli.add_command(fix_cards, name="fix-cards")
cli.add_command(list_lesser_known_cards, name="list-lesser-known-cards")
cli.add_command(generate_topics_prompt, name="generate-topics-prompt")
cli.add_command(select_conversation_topic, name="select-conversation-topic")
