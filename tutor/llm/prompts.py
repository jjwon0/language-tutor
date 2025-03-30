from tutor.utils.config import get_config

_LANGUAGE_DESCRIPTIONS = {
    "mandarin": "Mandarin Chinese",
    "cantonese": "Cantonese Chinese",
}


def _get_flashcard_description(language: str) -> str:
    """Get the flashcard description for the specified language.

    Args:
        language: The language to get the description for ("mandarin" or "cantonese")

    Returns:
        The flashcard description for the language
    """
    language_name = _LANGUAGE_DESCRIPTIONS.get(language.lower(), "Mandarin Chinese")
    pronunciation_field = "pinyin" if language.lower() == "mandarin" else "jyutping"
    learner_level = get_config().learner_level

    return f"""
Generate a {language_name} flashcard that helps {learner_level} students understand:
1. The word's meaning and usage context
2. How it's naturally used in sentences
3. Its relationship to other commonly paired words or words with similar patterns

Your response must be a valid JSON object with these fields:
- "word": The Chinese character(s)
- "{pronunciation_field}": The pronunciation with tone marks/numbers
- "english": The English translation
- "sample_usage": A sample sentence in Chinese
- "sample_usage_english": The English translation of the sample sentence
- "related_words": An array of related words, each with these fields:
  - "word": The related Chinese character(s)
  - "{pronunciation_field}": The pronunciation with tone marks/numbers
  - "english": The English translation
  - "relationship": How this word relates to the main word (e.g., "synonym", "antonym", "similar pattern")
"""


def get_generate_flashcard_from_word_prompt(word: str, language: str = "mandarin"):
    """Generate a prompt for creating a flashcard from a word.

    Args:
        word: The word to create a flashcard for
        language: The language of the word ("mandarin" or "cantonese")

    Returns:
        A prompt for generating a flashcard
    """
    flashcard_description = _get_flashcard_description(language)

    return f"""Generate a {language} flashcard for the word/phrase {word}. If the input seems wrong, please select the most-likely intended phrase.

Respond with a single valid JSON object that follows this structure exactly.
{flashcard_description}"""


def get_generate_flashcard_from_paragraph_prompt(text: str, language: str = "mandarin"):
    """Generate a prompt for creating flashcards from a paragraph.

    Args:
        text: The paragraph to extract words from
        language: The language of the paragraph ("mandarin" or "cantonese")

    Returns:
        A prompt for generating flashcards
    """
    language_name = _LANGUAGE_DESCRIPTIONS.get(language.lower(), "Mandarin Chinese")
    flashcard_description = _get_flashcard_description(language)

    return f"""Below the line is a paragraph from an article in {language_name}. Extract 3-5 key vocabulary and grammar phrases, except proper nouns.
--
{text}
--

Respond with a valid JSON object that has a "flashcards" array containing multiple flashcard objects, one for each extracted word or phrase.
{flashcard_description}"""


def get_generate_flashcard_from_llm_conversation_prompt(
    text: str, language: str = "mandarin"
):
    """Generate a prompt for creating flashcards from a conversation.

    Args:
        text: The conversation to extract words from
        language: The language of the conversation ("mandarin" or "cantonese")

    Returns:
        A prompt for generating flashcards
    """
    language_name = _LANGUAGE_DESCRIPTIONS.get(language.lower(), "Mandarin Chinese")
    flashcard_description = _get_flashcard_description(language)

    return f"""Below the line is a conversation between a language learner and a LLM assistant in {language_name}. Extract 3-5 key vocabulary and grammar phrases, except proper nouns.
--
{text}
--

Respond with a valid JSON object that has a "flashcards" array containing multiple flashcard objects, one for each extracted word or phrase.
{flashcard_description}"""
