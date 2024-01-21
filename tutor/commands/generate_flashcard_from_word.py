from tutor.utils.anki import AnkiConnectClient
from tutor.llm_flashcards import (
    generate_flashcards,
    maybe_add_flashcards_to_deck,
    get_word_exists_query,
    DEFAULT_ROOT_DECK,
)
from tutor.llm.prompts import get_generate_flashcard_from_word_prompt
from tutor.utils.logging import dprint


def generate_flashcard_from_word_inner(deck: str, word: str):
    ankiconnect_client = AnkiConnectClient()
    if ankiconnect_client.find_cards(get_word_exists_query(word)):
        print("Card exists already!")
        return

    prompt = get_generate_flashcard_from_word_prompt(word)
    dprint(prompt)
    flashcards = generate_flashcards(prompt)
    dprint(flashcards)
    maybe_add_flashcards_to_deck(flashcards, deck, DEFAULT_ROOT_DECK)
