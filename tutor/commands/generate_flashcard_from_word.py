from tutor.utils.anki import AnkiConnectClient
from tutor.llm_flashcards import (
    generate_flashcards,
    maybe_add_flashcards_to_deck,
    get_word_exists_query,
)
from tutor.llm.prompts import get_generate_flashcard_from_word_prompt
from tutor.utils.logging import dprint
from tutor.utils.chinese import to_simplified


def generate_flashcard_from_word_inner(deck: str, words: tuple[str, ...]) -> None:
    """Generate flashcards for one or more words.

    For each word:
    1. Convert traditional characters to simplified (if any)
    2. Check if the card already exists in Anki
    3. Generate flashcard content using OpenAI if needed
    4. Add the flashcard to Anki if it doesn't already exist
    """
    ankiconnect_client = AnkiConnectClient()
    total = len(words)

    for i, word in enumerate(words, 1):
        # Convert traditional characters to simplified
        simplified_word = to_simplified(word)

        if total > 1:
            print(f"\nProcessing word {i}/{total}: {simplified_word}")

        # Check if card already exists
        existing_cards = ankiconnect_client.find_notes(
            get_word_exists_query(simplified_word)
        )
        if existing_cards:
            print(f"Card for '{simplified_word}' exists already:\n{existing_cards[0]}")
            continue

        # Generate new card content
        prompt = get_generate_flashcard_from_word_prompt(simplified_word)
        dprint(prompt)
        flashcards = generate_flashcards(prompt)
        dprint(flashcards)

        if maybe_add_flashcards_to_deck(flashcards, deck):
            print(f"Added new flashcard for '{simplified_word}'")
        else:
            print(f"No new flashcard added for '{simplified_word}'")
