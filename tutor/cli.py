import click
from typing import Optional
from dotenv import load_dotenv

from tutor.commands.generate_topics import (
    generate_topics_prompt_inner,
    select_conversation_topic_inner,
)
from tutor.commands.generate_flashcard_from_word import (
    generate_flashcard_from_word_inner,
)
from tutor.commands.regenerate_flashcard import (
    regenerate_flashcard_inner,
)
from tutor.commands.list_lesser_known_cards import (
    list_lesser_known_cards_inner,
)
from tutor.commands.run_web import run_web
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


@cli.command()
@click.option(
    "--conversation-topics-path",
    type=str,
    help="Path to data file with past topics",
    default="data/conversation_topics.yaml",
)
@click.option(
    "--num-topics",
    type=int,
    help="Number of new topics to generate",
    default=10,
)
def generate_topics_prompt(conversation_topics_path: str, num_topics: int) -> None:
    """Prints a prompt to pass to ChatGPT to get new conversation topics."""
    click.echo(generate_topics_prompt_inner(conversation_topics_path, num_topics))


@cli.command()
@click.option(
    "--conversation-topics-path",
    type=str,
    help="Path to data file with past topics",
    default="data/conversation_topics.yaml",
)
def select_conversation_topic(conversation_topics_path: str):
    """Selects a random conversation topic from a file on disk."""
    click.echo(select_conversation_topic_inner(conversation_topics_path))


@cli.command()
@click.argument("word", type=str)
@click.option("--deck", type=str, default=None)
def generate_flashcard_from_word(deck: str, word: str):
    """Add a new Anki flashcard for a specific WORD to DECK."""
    deck = deck or get_config().default_deck
    click.echo(generate_flashcard_from_word_inner(deck, word))


# Shortcut for the most common action.
cli.add_command(generate_flashcard_from_word, name="g")


@cli.command()
@click.argument("word", type=str)
def regenerate_flashcard(word: str):
    """Regenerate Anki flashcard for a specific WORD."""
    click.echo(regenerate_flashcard_inner(word))


# Shortcut for the next-most common action.
cli.add_command(regenerate_flashcard, name="rg")


@cli.command()
@click.option("--deck", type=str, default=None)
@click.option("--count", type=int, default=5)
def list_lesser_known_cards(deck: str, count: int):
    """Regenerate Anki flashcard for a specific WORD."""
    deck = deck or get_config().default_deck
    click.echo(list_lesser_known_cards_inner(deck, count))


@cli.command()
@click.option("--deck", type=str, default=None, help="Deck to fix cards in")
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Show what would be updated without making changes",
)
@click.option(
    "--limit",
    type=int,
    default=None,
    help="Limit the number of cards to process",
)
@click.option(
    "--force-update",
    is_flag=True,
    default=False,
    help="Force update all cards even if they have all required fields",
)
def fix_cards(
    deck: Optional[str], dry_run: bool, limit: Optional[int], force_update: bool
) -> None:
    """Fix all cards in a deck by regenerating them with latest features.

    Only regenerates audio if the sample usage changes.
    """
    from tutor.commands.fix_cards import fix_cards_inner

    deck = deck or get_config().default_deck
    click.echo(fix_cards_inner(deck, dry_run, limit, force_update))


@cli.command()
@click.option(
    "--model",
    "-m",
    default="chinese-tutor",
    help="The name of the Anki model to update. Defaults to 'chinese-tutor'.",
)
def update_card_styling(model: str) -> None:
    """Update the styling of Anki cards without changing their content."""
    from tutor.commands.update_card_styling import update_card_styling_inner

    click.echo(update_card_styling_inner(model_name=model))


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


# Add web interface command
cli.add_command(run_web, name="web")
