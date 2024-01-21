import yaml

from tutor.utils.anki import AnkiConnectClient, get_subdeck
from tutor.llm_flashcards import (
    generate_flashcards,
    maybe_add_flashcards,
    DEFAULT_DECK,
)
from tutor.llm.prompts import get_generate_flashcard_from_paragraph_prompt


def generate_flashcards_from_article_inner(article_path: str):
    with open(article_path) as f:
        article = yaml.safe_load(f)

    article_title = article["article"]["title"]
    article_text = article["content"]

    ankiconnect_client = AnkiConnectClient()
    ankiconnect_client.maybe_add_deck(get_subdeck(DEFAULT_DECK, article_title))

    for paragraph in article_text.split("\n"):
        prompt = get_generate_flashcard_from_paragraph_prompt(paragraph)
        flashcards = generate_flashcards(prompt)
        print(
            f"Generated {len(flashcards.flashcards)} flashcards for the following words:"
        )
        maybe_add_flashcards(flashcards, article_title)
