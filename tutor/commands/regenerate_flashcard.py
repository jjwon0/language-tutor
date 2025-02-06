from tutor.utils.anki import AnkiConnectClient
from tutor.llm_flashcards import (
    generate_flashcards,
    get_word_exists_query,
)
from tutor.utils.logging import dprint
from tutor.llm.prompts import get_generate_flashcard_from_word_prompt
from tutor.utils.azure import text_to_speech


def regenerate_flashcard_inner(word: str):
    ankiconnect_client = AnkiConnectClient()
    flashcards = ankiconnect_client.find_notes(get_word_exists_query(word))
    if not flashcards:
        print(f"Could not find any cards matching {word}, exiting")
        return

    assert len(flashcards) == 1, "Multiple cards match this query"
    flashcard = flashcards[0]
    print(flashcard)
    user_input = input("Regenerate this card? (y/N): ").strip().lower()
    if user_input != "y":
        print("Operation cancelled by user.")
        return

    note_id = flashcard.anki_note_id
    prompt = get_generate_flashcard_from_word_prompt(word)
    dprint(prompt)
    flashcards = generate_flashcards(prompt)
    dprint(flashcards)
    flashcard = flashcards.flashcards[0]
    audio_filepath = text_to_speech(flashcard.sample_usage)
    ankiconnect_client.update_flashcard(note_id, flashcard, audio_filepath)
    print("Updated! The new flashcard is below:")
    print(flashcard)
