import click

from dotenv import load_dotenv

from tutor.commands.generate_topics import (
    generate_topics_prompt_inner,
    select_conversation_topic_inner,
)
from tutor.commands.generate_flashcards_from_article import (
    generate_flashcards_from_article_inner,
)
from tutor.commands.generate_flashcards_from_chatgpt import (
    generate_flashcards_from_chatgpt_inner,
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
from tutor.llm_flashcards import DEFAULT_DECK, GPT_3_5_TURBO, GPT_4, GPT_4o

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
    "--skip-confirm",
    type=bool,
    default=False,
    help="Skip confirmation for commands"
)
def cli(model: str, debug: bool, skip_confirm: bool):
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
def generate_topics_prompt(conversation_topics_path: str, num_topics: int):
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
@click.argument("article-path", type=click.Path(exists=True))
def generate_flashcards_from_article(article_path: str):
    """Generates new Anki flashcards from an article at ARTICLE_PATH."""
    click.echo(generate_flashcards_from_article_inner(article_path))


@cli.command()
@click.argument("chatgpt-share-link", type=str)
def generate_flashcards_from_chatgpt(chatgpt_share_link: str):
    """Generates new Anki flashcards from the ChatGPT conversation at CHATGPT_SHARE_LINK."""
    click.echo(generate_flashcards_from_chatgpt_inner(chatgpt_share_link))


@cli.command()
@click.argument("deck", type=str)
@click.argument("word", type=str)
def generate_flashcard_from_word(deck: str, word: str):
    """Add a new Anki flashcard for a specific WORD to DECK."""
    click.echo(generate_flashcard_from_word_inner(deck, word))


@cli.command()
@click.argument("word", type=str)
def regenerate_flashcard(word: str):
    """Regenerate Anki flashcard for a specific WORD."""
    click.echo(regenerate_flashcard_inner(word))


@cli.command()
@click.option("--deck", type=str, default=DEFAULT_DECK)
@click.option("--count", type=int, default=5)
def list_lesser_known_cards(deck: str, count: int):
    """Regenerate Anki flashcard for a specific WORD."""
    click.echo(list_lesser_known_cards_inner(deck, count))
