from openai import OpenAI
from typing import List, Type
from tutor.utils.logging import dprint
from tutor.utils.anki import AnkiConnectClient, get_subdeck
from tutor.llm.models import LanguageFlashcard, MandarinFlashcard, CantoneseFlashcard
from tutor.cli_global_state import get_model, get_skip_confirm
from tutor.utils.azure import text_to_speech
from tutor.utils.config import get_config

GPT_3_5_TURBO = "gpt-3.5-turbo"
GPT_4 = "gpt-4"
GPT_4o = "gpt-4o"


def generate_flashcards(text, language: str = "mandarin"):
    """
    Generates flashcard content from the given text using OpenAI's GPT model.

    :param text: The text from which to generate flashcards.
    :param language: The language to generate flashcards for ("mandarin" or "cantonese").
    :return: Generated flashcard content.
    """
    openai_client = OpenAI()

    # Select the appropriate flashcard class based on language
    flashcard_class = get_flashcard_class_for_language(language)

    try:
        dprint(text)
        # Use the standard completion API instead of parse
        completion = openai_client.chat.completions.create(
            model=get_model(),
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": text}],
            seed=69,
        )

        # Extract the JSON content from the response
        response_content = completion.choices[0].message.content
        dprint(f"Response content: {response_content}")

        # Parse the JSON content into flashcard objects
        import json
        from pydantic import TypeAdapter

        # Parse the JSON response
        response_data = json.loads(response_content)

        # Handle both single flashcard and list of flashcards
        if isinstance(response_data, list):
            flashcards_data = response_data
        else:
            # If it's a single object or has a nested structure
            if "flashcards" in response_data:
                flashcards_data = response_data["flashcards"]
            else:
                # Treat as a single flashcard
                flashcards_data = [response_data]

        # Use TypeAdapter to convert the JSON data to flashcard objects
        adapter = TypeAdapter(List[flashcard_class])
        flashcards = adapter.validate_python(flashcards_data)

        return flashcards
    except Exception as e:
        print(f"Error generating {language} flashcards:", e)
        import traceback

        traceback.print_exc()
        return []


def get_flashcard_class_for_language(language: str) -> Type[LanguageFlashcard]:
    """
    Returns the appropriate flashcard class for the given language.

    :param language: The language to get the flashcard class for.
    :return: The flashcard class for the language.
    """
    language = language.lower()
    if language == "cantonese":
        return CantoneseFlashcard
    else:
        # Default to Mandarin
        return MandarinFlashcard


def get_word_exists_query(word: str, language: str = "mandarin"):
    """
    Returns a query to check if a word exists in Anki.

    :param word: The word to check for.
    :param language: The language of the word.
    :return: An Anki query string.
    """
    return f'"deck:{get_config().default_deck}" Chinese:{word}'


def get_similar_words_exists_query(word: str):
    return f'"deck:{get_config().default_deck}" Chinese:*{word}*'


def maybe_add_flashcards_to_deck(
    flashcards: List[LanguageFlashcard], deck: str
) -> bool:
    """Add flashcards to deck.

    The caller should have already checked if the cards exist in Anki.
    This function will only ask for confirmation and add the cards.

    Returns:
        bool: True if any cards were added, False if all cards were skipped
    """
    ankiconnect_client = AnkiConnectClient()
    num_added = 0

    try:
        for f in flashcards:
            dprint(f"{f.word}")
            print(f)

            if not get_skip_confirm():
                try:
                    if not input("Add this to deck (y/n)? ").lower().strip() == "y":
                        dprint(" - skipped")
                        continue
                except (KeyboardInterrupt, EOFError):
                    print("\nAborted by user")
                    return False

            try:
                audio_filepath = text_to_speech(f.sample_usage)
                note_id = ankiconnect_client.add_flashcard(deck, f, audio_filepath)
                dprint(f" - added with note ID: {note_id}!")
                num_added += 1
            except Exception as e:
                print(f"Error adding flashcard for '{f.word}': {str(e)}")
                continue

    except KeyboardInterrupt:
        print("\nAborted by user")
        return False
    finally:
        if num_added > 0:
            print(f"Added {num_added} new card(s)!")
        return num_added > 0


def maybe_add_flashcards(flashcards: List[LanguageFlashcard], subdeck: str):
    return maybe_add_flashcards_to_deck(
        flashcards, get_subdeck(get_config().default_deck, subdeck)
    )
