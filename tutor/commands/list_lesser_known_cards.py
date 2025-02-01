import random
from tutor.utils.anki import AnkiConnectClient
from tutor.llm.models import ChineseFlashcard
from tutor.utils.logging import dprint


def list_lesser_known_cards_inner(deck: str, count: int):
    ankiconnect_client = AnkiConnectClient()
    # cards rated "again" or "hard" in the past 7 days
    query = f'(deck:"{deck}" rated:7:1 OR deck:"{deck}" rated:7:2)'
    dprint(query)
    cards = ankiconnect_client.find_notes(query)
    for fc in random.sample(cards, count):
        print(f"- {fc.word} ({fc.pinyin}): {fc.english}")
