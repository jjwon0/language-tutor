from typing import List
import instructor
import pydantic
from openai import OpenAI
from tutor.utils.logging import dprint
from tutor.utils.anki import AnkiConnectClient, get_subdeck


class ChineseFlashcard(pydantic.BaseModel):
    word: str
    pinyin: str
    sample_usage: str
    english: str
    sample_usage_english: str


class ChineseFlashcards(pydantic.BaseModel):
    flashcards: List[ChineseFlashcard]


def generate_flashcards(text):
    """
    Generates flashcard content from the given text using OpenAI's GPT model.

    :param text: The text from which to generate flashcards.
    :return: Generated flashcard content.
    """

    openai_client = instructor.patch(OpenAI())

    try:
        dprint(text)
        flashcards: ChineseFlashcards = openai_client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            response_model=ChineseFlashcards,
            messages=[{"role": "user", "content": text}],
            # try to make sure the suggested flashcards are slightly more deterministic
            temperature=0.1,
            seed=69,
        )
        return flashcards
    except Exception as e:
        print("Error generating flashcards:", e)


DEFAULT_ROOT_DECK = "Chinese"
DEFAULT_DECK = "Chinese::Jason's cards::chinese-tutor"


def _maybe_add_flashcards(
    flashcards_container: ChineseFlashcards, deck: str, root_deck: str
):
    ankiconnect_client = AnkiConnectClient()

    num_added = 0
    for f in flashcards_container.flashcards:
        dprint(f"{f.word}")
        details = ankiconnect_client.maybe_get_card_details(f.word, root_deck)
        if details:
            dprint(f" - {len(details)} similar cards exist(s)! ")
        else:
            dprint(" - new card!")
            ankiconnect_client.add_flashcard(deck, f)
            dprint(" - added!")
            num_added += 1
    print(f"Added {num_added} new cards!")


def maybe_add_flashcards(flashcards_container: ChineseFlashcards, subdeck: str):
    return _maybe_add_flashcards(
        flashcards_container, get_subdeck(DEFAULT_DECK, subdeck), DEFAULT_ROOT_DECK
    )
