import os

import yaml
from typing import List
import instructor
import pydantic
from openai import OpenAI

from tutor.utils import logging
from tutor.utils.anki import AnkiConnectClient
from tutor.utils.logging import dprint


class ChineseFlashcard(pydantic.BaseModel):
    word: str
    pinyin: str
    sample_usage: str
    english: str
    sample_usage_english: str


class ChineseFlashcards(pydantic.BaseModel):
    flashcards: List[ChineseFlashcard]


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


def generate_flashcards(text):
    """
    Generates flashcard content from the given text using OpenAI's GPT model.

    :param text: The text from which to generate flashcards.
    :return: Generated flashcard content.
    """

    openai_client = instructor.patch(OpenAI())

    try:
        message_content = _PROMPT_TMPL.format(text=text)
        dprint(message_content)
        flashcards: ChineseFlashcards = openai_client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            response_model=ChineseFlashcards,
            messages=[{"role": "user", "content": message_content}],
            # try to make sure the suggested flashcards are slightly more deterministic
            temperature=0.2,
            seed=69,
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

    article_text = article["content"]
    flashcards = generate_flashcards(article_text)
    return flashcards


def generate_flashcards_from_article_inner(article_path: str, debug: bool):
    ankiconnect_client = AnkiConnectClient()

    logging._DEBUG = debug

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
