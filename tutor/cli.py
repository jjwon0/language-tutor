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
from tutor.utils.logging import set_debug

load_dotenv()


@click.group()
@click.option("--debug", is_flag=True, help="Turn on extra debug logging")
def cli(debug: bool):
    """chinese-tutor tool"""
    set_debug(debug)


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
