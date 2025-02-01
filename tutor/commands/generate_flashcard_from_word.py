from tutor.utils.anki import AnkiConnectClient
from tutor.llm_flashcards import (
    generate_flashcards,
    maybe_add_flashcards_to_deck,
    get_word_exists_query,
    get_similar_words_exists_query,
)
from tutor.llm.prompts import get_generate_flashcard_from_word_prompt
from tutor.utils.logging import dprint


def generate_flashcard_from_word_inner(deck: str, word: str):
    ankiconnect_client = AnkiConnectClient()
    exact_card = ankiconnect_client.find_notes(get_word_exists_query(word))
    if exact_card:
        print("Card exists already:")
        print(exact_card)
        return
    similar_cards = ankiconnect_client.find_notes(get_similar_words_exists_query(word))
    if similar_cards:
        print("Similar cards found:")
        for card in similar_cards:
            print(card)
        user_input = input("Generate a new card anyway? (y/N): ").strip().lower()
        if user_input != "y":
            print("Operation cancelled by user.")
            return

    prompt = get_generate_flashcard_from_word_prompt(word)
    dprint(prompt)
    flashcards = generate_flashcards(prompt)
    dprint(flashcards)
    maybe_add_flashcards_to_deck(flashcards, deck)
