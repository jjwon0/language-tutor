from tutor.utils.anki import AnkiConnectClient
from tutor.llm_flashcards import (
    generate_flashcards,
    maybe_add_flashcards_to_deck,
    get_word_exists_query,
)
from tutor.llm.prompts import get_generate_flashcard_from_word_prompt
from tutor.utils.logging import dprint
from tutor.utils.chinese import to_simplified


def generate_flashcard_from_word_inner(
    deck: str, words: tuple[str, ...], language: str = "mandarin"
) -> None:
    """Generate flashcards for one or more words.

    For each word:
    1. Convert traditional characters to simplified (if any)
    2. Check if the card already exists in Anki
    3. Generate flashcard content using OpenAI if needed
    4. Add the flashcard to Anki if it doesn't already exist

    Args:
        deck: The Anki deck to add flashcards to
        words: The words to generate flashcards for
        language: The language to generate flashcards for ("mandarin" or "cantonese")
    """
    ankiconnect_client = AnkiConnectClient()
    total = len(words)

    for i, word in enumerate(words, 1):
        # Convert traditional characters to simplified
        word = to_simplified(word)

        if total > 1:
            print(f"\nProcessing word {i}/{total}: {word}")

        # Check if card already exists
        existing_cards = ankiconnect_client.find_notes(
            get_word_exists_query(word, language)
        )
        if existing_cards:
            print(f"Card for '{word}' exists already:\n{existing_cards[0]}")
            continue

        # Generate new card content
        prompt = get_generate_flashcard_from_word_prompt(word, language)
        dprint(prompt)
        flashcards = generate_flashcards(prompt, language)
        dprint(flashcards)

        if maybe_add_flashcards_to_deck(flashcards, deck):
            # Use the actual word from the generated flashcard
            new_word = flashcards[0].word if flashcards else word
            print(f"Added new flashcard for '{new_word}' in {language}")
        else:
            print(f"No new flashcard added for '{word}'")
