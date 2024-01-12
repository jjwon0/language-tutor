import os

import yaml
from typing import List
import instructor
import pydantic
from openai import OpenAI

from tutor import utils
from tutor.anki import AnkiConnectClient
from tutor.utils import dprint


class ChineseFlashcard(pydantic.BaseModel):
    word: str
    pinyin: str
    sample_usage: str
    english: str
    sample_usage_english: str


class ChineseFlashcards(pydantic.BaseModel):
    flashcards: List[ChineseFlashcard]


_PROMPT_TMPL = "Below is a paragraph in Chinese. If there are any, please list key vocabulary or grammar phrases for an intermediate/upper-intermediate Chinese learner.\n\n{}"


def generate_flashcards(text):
    """
    Generates flashcard content from the given text using OpenAI's GPT model.

    :param text: The text from which to generate flashcards.
    :return: Generated flashcard content.
    """

    openai_client = instructor.patch(OpenAI())

    try:
        message_content = _PROMPT_TMPL.format(text)
        flashcards: ChineseFlashcards = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            response_model=ChineseFlashcards,
            messages=[{"role": "user", "content": message_content}],
        )
        return flashcards
    except Exception as e:
        print("Error generating flashcards:", e)


def generate_flashcards_from_article(article_path):
    """
    Generates flashcards from the given article.

    Parameters:
    article_path (str): The file path to the article.

    Returns:
    list: A list of flashcard data in JSON format.
    """
    # Validate that the article path exists
    if not os.path.exists(article_path):
        raise FileNotFoundError(
            f"The specified article path does not exist: {article_path}"
        )

    with open(article_path) as f:
        article = yaml.safe_load(f)

    article_text = article["content"].split("\n")[0]

    flashcards = generate_flashcards(article_text)

    return flashcards


def generate_flashcards_from_article_inner(article_path: str, debug: bool):
    ankiconnect_client = AnkiConnectClient()

    utils._DEBUG = debug

    try:
        flashcards_container = generate_flashcards_from_article(article_path)
        dprint(flashcards_container)
        flashcards = flashcards_container.flashcards
        print(f"Generated {len(flashcards)} flashcards for the following words:")
        for f in flashcards:
            print(f"{f.word}")
            details = ankiconnect_client.maybe_get_card_details(f.word, "Chinese")
            if details:
                print(f" - {len(details)} similar cards exist(s)! ")
            else:
                print(" - new card!")
                ankiconnect_client.add_flashcard(
                    "Chinese::Jason's cards::chinese-tutor", f
                )
                print(" - added!")
    except Exception as e:
        print(f"An error occurred: {e}")
