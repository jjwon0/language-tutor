from tutor.utils.anki import AnkiConnectClient
from tutor.llm_flashcards import (
    generate_flashcards,
    get_word_exists_query,
)
from tutor.utils.logging import dprint

_PROMPT_TMPL = """Generate all of the following items as bullet points for the word/phrase: {word}:

- Word/phrase: Repeat the word/phrase verbatim.
- Pinyin: Provide the Pinyin transliteration of the Chinese word or phrase.
- English Translation: Translate the word or phrase into English.
- Sample Usage in Chinese: Create or find a sentence from the article (or construct a new one) that uses the word or phrase in context.
- Sample Usage in English: Translate the sample usage sentence into English, ensuring that it reflects the usage of the word or phrase in context.
"""


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

    prompt = _PROMPT_TMPL.format(word=word)
    dprint(prompt)
    flashcards = generate_flashcards(prompt)
    dprint(flashcards)
    flashcard = flashcards.flashcards[0]
    ankiconnect_client.update_flashcard(card_detail["note"], flashcard)
    print("Updated! The new flashcard is below:")
    print(flashcard)
