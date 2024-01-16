import yaml

from tutor.utils import logging
from tutor.utils.anki import AnkiConnectClient, get_subdeck
from tutor.llm_flashcards import (
    generate_flashcards,
    maybe_add_flashcards,
    DEFAULT_DECK,
)


_PROMPT_TMPL = """Below the line is an article in Chinese: identify and extract key vocabulary and grammar phrases. For each identified item, generate a flashcard that includes the following information:

- Word/Phrase in Simplified Chinese: Extract the word or phrase from the article.
- Pinyin: Provide the Pinyin transliteration of the Chinese word or phrase.
- English Translation: Translate the word or phrase into English.
- Sample Usage in Chinese: Create or find a sentence from the article (or construct a new one) that uses the word or phrase in context.
- Sample Usage in English: Translate the sample usage sentence into English, ensuring that it reflects the usage of the word or phrase in context.

For each flashcard, focus on clarity and practical usage, ensuring the information is useful for an intermediate Chinese speaker looking to improve vocabulary and understanding of grammar.
--
{text}
"""


def generate_flashcards_from_article_inner(article_path: str, debug: bool):
    logging._DEBUG = debug

    with open(article_path) as f:
        article = yaml.safe_load(f)

    article_title = article["article"]["title"]
    article_text = article["content"]

    ankiconnect_client = AnkiConnectClient()
    ankiconnect_client.maybe_add_deck(get_subdeck(DEFAULT_DECK, article_title))

    flashcards = generate_flashcards(article_text)
    print(f"Generated {len(flashcards.flashcards)} flashcards for the following words:")
    maybe_add_flashcards(flashcards, article_title)
