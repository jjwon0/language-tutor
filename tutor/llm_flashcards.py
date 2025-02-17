from openai import OpenAI
from tutor.utils.logging import dprint
from tutor.utils.anki import AnkiConnectClient, get_subdeck
from tutor.llm.models import ChineseFlashcards
from tutor.cli_global_state import get_model, get_skip_confirm
from tutor.utils.azure import text_to_speech
from tutor.utils.config import get_config

GPT_3_5_TURBO = "gpt-3.5-turbo"
GPT_4 = "gpt-4"
GPT_4o = "gpt-4o"


def generate_flashcards(text):
    """
    Generates flashcard content from the given text using OpenAI's GPT model.

    :param text: The text from which to generate flashcards.
    :return: Generated flashcard content.
    """
    openai_client = OpenAI()

    try:
        dprint(text)
        completion = openai_client.beta.chat.completions.parse(
            model=get_model(),
            response_format=ChineseFlashcards,
            messages=[{"role": "user", "content": text}],
            seed=69,
        )
        dprint(completion.model_dump())
        dprint(completion.__dict__)
        return completion.choices[0].message.parsed
    except Exception as e:
        print("Error generating flashcards:", e)


def get_word_exists_query(word: str):
    return f'"deck:{get_config().default_deck}" Chinese:{word}'


def get_similar_words_exists_query(word: str):
    return f'"deck:{get_config().default_deck}" Chinese:*{word}*'


def maybe_add_flashcards_to_deck(flashcards_container: ChineseFlashcards, deck: str):
    ankiconnect_client = AnkiConnectClient()

    num_added = 0
    for f in flashcards_container.flashcards:
        dprint(f"{f.word}")
        query = get_word_exists_query(f.word)
        existing_cards = ankiconnect_client.find_notes(query)
        if existing_cards:
            dprint(f" - {len(existing_cards)} similar cards exist(s)! ")
        else:
            dprint(" - new card!")
            print(f)
            if not get_skip_confirm():
                if not input("Add this to deck (y/n)? ") == "y":
                    dprint(" - skipped")
                    continue
            audio_filepath = text_to_speech(f.sample_usage)
            ankiconnect_client.add_flashcard(deck, f, audio_filepath)
            dprint(" - added!")
            num_added += 1
    print(f"Added {num_added} new card(s)!")


def maybe_add_flashcards(flashcards_container: ChineseFlashcards, subdeck: str):
    return maybe_add_flashcards_to_deck(
        flashcards_container, get_subdeck(get_config().default_deck, subdeck)
    )
