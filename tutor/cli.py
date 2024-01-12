import click

from dotenv import load_dotenv

from tutor.commands.generate_topics import generate_topics_inner
from tutor.commands.generate_flashcards_from_article import (
    generate_flashcards_from_article_inner,
)

load_dotenv()


@click.group()
def cli():
    """chinese-tutor tool"""


@cli.command()
@click.option(
    "--conversation-topics-path",
    type=str,
    help="Path to data file with past topics",
    default="data/conversation_topics.yaml",
)
def generate_topics(conversation_topics_path: str):
    click.echo(generate_topics_inner(conversation_topics_path))


@cli.command()
@click.argument("article_path", type=click.Path(exists=True))
@click.option("--debug", is_flag=True, help="Turn on extra debug logging")
def generate_flashcards_from_article(article_path: str, debug: bool):
    click.echo(generate_flashcards_from_article_inner(article_path, debug))
