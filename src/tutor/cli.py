import click
from dotenv import load_dotenv

from tutor.commands.generate_topics import (
    generate_topics_prompt,
    select_conversation_topic,
)
from tutor.commands.generate_flashcard_from_word import generate_flashcard_from_word
from tutor.commands.regenerate_flashcard import regenerate_flashcard
from tutor.commands.list_lesser_known_cards import list_lesser_known_cards
from tutor.commands.run_web import run_web
from tutor.commands.setup_anki import setup_anki
from tutor.commands.fix_cards import fix_cards
from tutor.commands.config import config
from tutor.llm_flashcards import GPT_3_5_TURBO, GPT_4, GPT_4o

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
    "--skip-confirm/--no-skip-confirm",
    default=False,
    help="Skip confirmation for commands",
)
def main(model: str, debug: bool, skip_confirm: bool) -> None:
    """chinese-tutor tool"""
    set_model(model)
    set_debug(debug)
    set_skip_confirm(skip_confirm)


# Add generate_flashcard_from_word command and shortcut
main.add_command(generate_flashcard_from_word, name="generate-flashcard-from-word")
main.add_command(generate_flashcard_from_word, name="g")


# Add regenerate_flashcard command and shortcut
main.add_command(regenerate_flashcard, name="regenerate-flashcard")
main.add_command(regenerate_flashcard, name="rg")


# Add commands
main.add_command(run_web, name="web")
main.add_command(setup_anki, name="setup-anki")
main.add_command(fix_cards, name="fix-cards")
main.add_command(list_lesser_known_cards, name="list-lesser-known-cards")
main.add_command(generate_topics_prompt, name="generate-topics-prompt")
main.add_command(select_conversation_topic, name="select-conversation-topic")
main.add_command(config, name="config")
