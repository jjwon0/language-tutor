from tutor.utils.anki import AnkiConnectClient
from tutor.llm_flashcards import (
    generate_flashcards,
    get_word_exists_query,
)
from tutor.utils.logging import dprint
from tutor.llm.prompts import get_generate_flashcard_from_word_prompt


def regenerate_flashcard_inner(word: str):
    ankiconnect_client = AnkiConnectClient()
    card_ids = ankiconnect_client.find_cards(get_word_exists_query(word))
    if not card_ids:
        print(f"Could not find any cards matching {word}, exiting")
        return

    assert len(card_ids) == 1, "Multiple cards match this query"
    card_id = card_ids[0]
    card_detail = ankiconnect_client.get_card_details([card_id])[0]
    # TODO: get existing card fields and prompt to confirm that we actually wanna update

    prompt = get_generate_flashcard_from_word_prompt(word)
    dprint(prompt)
    flashcards = generate_flashcards(prompt)
    dprint(flashcards)
    flashcard = flashcards.flashcards[0]
    ankiconnect_client.update_flashcard(card_detail["note"], flashcard)
    print("Updated! The new flashcard is below:")
    print(flashcard)
