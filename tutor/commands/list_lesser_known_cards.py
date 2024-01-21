import random
from tutor.utils.anki import AnkiConnectClient
from tutor.llm_flashcards import ChineseFlashcard
from tutor.utils.logging import dprint


def list_lesser_known_cards_inner(deck: str, count: int):
    ankiconnect_client = AnkiConnectClient()
    # cards rated "again" or "hard" in the past 7 days
    query = f'(deck:"{deck}" rated:7:1 OR deck:"{deck}" rated:7:2)'
    dprint(query)
    card_ids = ankiconnect_client.find_cards(query)
    card_details = ankiconnect_client.get_card_details(card_ids)
    for cd in random.sample(card_details, count):
        fc = ChineseFlashcard.from_anki_json(cd)
        print(f"- {fc.word} ({fc.pinyin}): {fc.english}")
