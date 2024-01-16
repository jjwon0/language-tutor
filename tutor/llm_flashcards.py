from typing import List
import instructor
from pydantic import BaseModel, Field
from openai import OpenAI
from tutor.utils.logging import dprint
from tutor.utils.anki import AnkiConnectClient, get_subdeck


class ChineseFlashcard(BaseModel):
    word: str = Field("The word/phrase in simplified Chinese")
    pinyin: str = Field("The word romanized using Pinyin (lowercased)")
    english: str = Field("The word translated into English (lowercased)")
    sample_usage: str = Field("Example sentence with the word which contextualizes it")
    sample_usage_english: str = Field(
        description="The sample usage field translated to English"
    )


class ChineseFlashcards(BaseModel):
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
            # try to make sure the suggested flashcards are a bit more deterministic
            seed=69,
        )
        dprint(flashcards._raw_response.usage)
        return flashcards
    except Exception as e:
        print("Error generating flashcards:", e)


DEFAULT_ROOT_DECK = "Chinese"
DEFAULT_DECK = "Chinese::Jason's cards::chinese-tutor"


def get_word_exists_query(word: str):
    return f'"deck:{DEFAULT_DECK}" Chinese:*{word}*'


def maybe_add_flashcards_to_deck(
    flashcards_container: ChineseFlashcards, deck: str, root_deck: str
):
    ankiconnect_client = AnkiConnectClient()

    num_added = 0
    for f in flashcards_container.flashcards:
        dprint(f"{f.word}")
        query = get_word_exists_query(f.word)
        details = ankiconnect_client.find_cards(query)
        if details:
            dprint(f" - {len(details)} similar cards exist(s)! ")
        else:
            dprint(" - new card!")
            ankiconnect_client.add_flashcard(deck, f)
            dprint(" - added!")
            num_added += 1
    print(f"Added {num_added} new cards!")


def maybe_add_flashcards(flashcards_container: ChineseFlashcards, subdeck: str):
    return maybe_add_flashcards_to_deck(
        flashcards_container, get_subdeck(DEFAULT_DECK, subdeck), DEFAULT_ROOT_DECK
    )
