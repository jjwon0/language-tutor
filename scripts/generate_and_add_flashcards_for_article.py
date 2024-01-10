import argparse
import json
import os

import requests
import yaml
from typing import List
import instructor
import pydantic
from openai import OpenAI


client = instructor.patch(OpenAI())


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

    try:
        flashcards: ChineseFlashcards = client.chat.completions.create(
            model="gpt-3.5-turbo",
            response_model=ChineseFlashcards,
            messages=[{"role": "user", "content": _PROMPT_TMPL.format(text)}],
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

    with open("articles/2023年五大健康趋势.yaml") as f:
        article = yaml.safe_load(f)

    # TODO: skip the [0]
    article_text = article["content"].split("\n")[0]

    flashcards = generate_flashcards(article_text)

    return flashcards


def get_card_details(card_ids):
    """
    Retrieve details for a list of card IDs.

    :param card_ids: List of card IDs.
    :return: A list of dictionaries containing card details.
    """
    url = "http://localhost:8765"
    headers = {"Content-Type": "application/json"}

    payload = json.dumps(
        {"action": "cardsInfo", "version": 6, "params": {"cards": card_ids}}
    )

    response = requests.post(url, data=payload, headers=headers)
    result = json.loads(response.text)
    return result.get("result", [])


def maybe_get_card_details(text, deck_name):
    """
    Check if a card with the specified front content exists in the given deck.

    :param text: The content on the front side of the card to check.
    :param deck_name: The name of the deck to search in.
    :return: True if the card exists, False otherwise.
    """
    url = "http://localhost:8765"
    headers = {"Content-Type": "application/json"}

    # Payload to find cards in a specific deck with the given front content
    payload = json.dumps(
        {
            "action": "findCards",
            "version": 6,
            "params": {"query": f'deck:"{deck_name}" "{text}"'},
        }
    )

    response = requests.post(url, data=payload, headers=headers)
    result = json.loads(response.text)
    card_ids = result.get("result", [])
    if card_ids:
        return get_card_details(card_ids)


def add_flashcard_to_anki(deck_name: str, flashcard: ChineseFlashcard):
    """
    Adds a flashcard to an Anki deck with the 'chinese-tutor' note type.

    Parameters:
    deck_name (str): Name of the Anki deck.
    chinese (str): The Chinese text.
    pinyin (str): The corresponding Pinyin.
    english (str): The English translation.
    sample_usage (str): A sample sentence in Chinese.
    sample_usage_english (str): English translation of the sample sentence.
    """

    # URL for AnkiConnect
    url = "http://localhost:8765"

    # AnkiConnect payload
    payload = json.dumps(
        {
            "action": "addNote",
            "version": 6,
            "params": {
                "note": {
                    "deckName": deck_name,
                    "modelName": "chinese-tutor",
                    "fields": {
                        "Chinese": flashcard.word,
                        "Pinyin": flashcard.pinyin,
                        "English": flashcard.english,
                        "Sample Usage": flashcard.sample_usage,
                        "Sample Usage (English)": flashcard.sample_usage_english,
                    },
                    "tags": [],
                }
            },
        }
    )

    headers = {"Content-Type": "application/json"}

    response = requests.request("POST", url, data=payload, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(
            "Error: Could not add card to Anki. Status Code: {}".format(
                response.status_code
            )
        )


def main():
    parser = argparse.ArgumentParser(description="Generate flashcards from an article.")
    parser.add_argument("article_path", type=str, help="Path to the article file")

    args = parser.parse_args()

    try:
        flashcards_container = generate_flashcards_from_article(args.article_path)
        flashcards = flashcards_container.flashcards
        print(f"Generated {len(flashcards)} flashcards for the following words:")
        for f in flashcards:
            print(f"{f.word}")
            details = maybe_get_card_details(f.word, "Chinese")
            if details:
                print(f" - {len(details)} similar cards exist(s)! ")
            else:
                print(" - new card!")
                add_flashcard_to_anki("Chinese::Jason's cards::chinese-tutor", f)
                print(" - added!")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
