from enum import Enum
import json

import requests

from tutor.llm.models import ChineseFlashcard


class AnkiAction(Enum):
    ADD_NOTE = "addNote"
    CARDS_INFO = "cardsInfo"
    FIND_CARDS = "findCards"
    DECK_NAMES = "deckNames"
    CREATE_DECK = "createDeck"
    DELETE_CARDS = "deleteCards"
    UPDATE_NOTE_FIELDS = "updateNoteFields"


class AnkiConnectClient:
    def __init__(self, address="http://localhost:8765"):
        self.address = address
        self.headers = {"Content-Type": "application/json"}

    def send_request(self, action, params=None):
        if not isinstance(action, AnkiAction):
            raise ValueError("Invalid action type")

        payload = json.dumps(
            {"action": action.value, "version": 6, "params": params or {}}
        )
        response = requests.post(self.address, data=payload, headers=self.headers)

        if response.status_code != 200:
            raise Exception(
                f"AnkiConnect request failed with status {response.status_code}"
            )

        result = response.json()
        if "error" in result and result["error"]:
            raise Exception(f"AnkiConnect error: {result['error']}")

        return result.get("result")

    def get_card_details(self, card_ids):
        card_details = self.send_request(AnkiAction.CARDS_INFO, {"cards": card_ids})
        cards = [ChineseFlashcard.from_anki_json(cd) for cd in card_details]
        return cards

    def find_cards(self, query):
        card_ids = self.send_request(AnkiAction.FIND_CARDS, {"query": query})
        return self.get_card_details(card_ids)

    def add_flashcard(self, deck_name, flashcard):
        note = {
            "deckName": deck_name,
            "modelName": "chinese-tutor",
            "fields": {
                "Chinese": flashcard.word,
                "Pinyin": flashcard.pinyin,
                "English": flashcard.english,
                "Sample Usage": flashcard.sample_usage,
                "Sample Usage (English)": flashcard.sample_usage_english,
            },
            "tags": [],
        }
        return self.send_request(AnkiAction.ADD_NOTE, {"note": note})

    def delete_flashcards(self, card_ids):
        return self.send_request(AnkiAction.DELETE_CARDS, {"cards": card_ids})

    def update_flashcard(self, note_id, flashcard):
        payload = {
            "note": {
                "id": note_id,
                # update everything except the Chinese "id"
                "fields": {
                    "Chinese": flashcard.word,
                    "Pinyin": flashcard.pinyin,
                    "English": flashcard.english,
                    "Sample Usage": flashcard.sample_usage,
                    "Sample Usage (English)": flashcard.sample_usage_english,
                },
            }
        }
        return self.send_request(AnkiAction.UPDATE_NOTE_FIELDS, payload)

    def list_decks(self):
        return self.send_request(AnkiAction.DECK_NAMES)

    def add_deck(self, deck_name):
        return self.send_request(AnkiAction.CREATE_DECK, {"deck": deck_name})

    def maybe_add_deck(self, deck_name):
        decks = self.list_decks()
        if deck_name not in decks:
            return self.add_deck(deck_name)


def get_subdeck(base_deck_name: str, subdeck_name: str):
    return f"{base_deck_name}::{subdeck_name}"
