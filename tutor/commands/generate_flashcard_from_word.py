from tutor.utils.anki import AnkiConnectClient
from tutor.llm_flashcards import (
    generate_flashcards,
    maybe_add_flashcards_to_deck,
    get_word_exists_query,
    DEFAULT_ROOT_DECK,
)
from tutor.utils.logging import dprint


_PROMPT_TMPL = """Generate the following for the word/phrase {word}:

- Word/phrase: Repeat the word/phrase verbatim.
- Pinyin: Provide the Pinyin transliteration of the Chinese word or phrase.
- English Translation: Translate the word or phrase into English.
- Sample Usage in Chinese: Create or find a sentence from the article (or construct a new one) that uses the word or phrase in context.
- Sample Usage in English: Translate the sample usage sentence into English, ensuring that it reflects the usage of the word or phrase in context.
"""


def generate_flashcard_from_word_inner(deck: str, word: str):
    ankiconnect_client = AnkiConnectClient()
    if ankiconnect_client.find_cards(get_word_exists_query(word)):
        print("Card exists already!")
        return

    prompt = _PROMPT_TMPL.format(word=word)
    dprint(prompt)
    flashcards = generate_flashcards(prompt)
    dprint(flashcards)
    maybe_add_flashcards_to_deck(flashcards, deck, DEFAULT_ROOT_DECK)
