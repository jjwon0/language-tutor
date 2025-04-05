import click
import random
from typing import Optional
from tutor.utils.anki import AnkiConnectClient
from tutor.utils.logging import dprint
from tutor.utils.config import get_config


@click.command()
@click.option("--deck", type=str, default=None, help="Deck to search in")
@click.option("--count", type=int, default=5, help="Number of cards to show")
def list_lesser_known_cards(deck: Optional[str], count: int):
    """List cards that you've rated as 'again' or 'hard' in the past week.

    This helps you focus on reviewing cards you're struggling with.
    """
    # Use default deck from config if not specified
    deck = deck or get_config().default_deck
    result = _list_lesser_known_cards_impl(deck, count)
    click.echo(result)


def _list_lesser_known_cards_impl(deck: str, count: int) -> str:
    """Implementation of list_lesser_known_cards command.

    Args:
        deck: Name of the deck to search in
        count: Number of cards to show

    Returns:
        Formatted string with the list of cards
    """
    ankiconnect_client = AnkiConnectClient()
    # cards rated "again" or "hard" in the past 7 days
    query = f'(deck:"{deck}" rated:7:1 OR deck:"{deck}" rated:7:2)'
    dprint(query)
    cards = ankiconnect_client.find_notes(query)

    if not cards:
        return f"No lesser-known cards found in deck: {deck}"

    # Make sure we don't try to sample more cards than exist
    sample_count = min(count, len(cards))

    # Build the result string
    result = [f"Lesser-known cards from deck '{deck}':"]

    for fc in random.sample(cards, sample_count):
        result.append(f"- {fc.word} ({fc.pinyin}): {fc.english}")

    return "\n".join(result)
