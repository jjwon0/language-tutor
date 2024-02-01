_FLASHCARD_DESCRIPTION = """
- Word (repeat the word/phrase verbatim).
- Pinyin (provide the Pinyin transliteration of the Chinese word or phrase)
- English (translate the word or phrase into English)
- Sample Usage: (create a new sentence that uses the word or phrase in context)
- Sample Usage English: (translate the created sample usage sentence into English)

Ensure that fields in each flashcard focuses on clarity and practical usage for an intermediate Chinese student."""


def get_generate_flashcard_from_word_prompt(word: str):
    return f"""Generate the following fields to be used as a flashcard for the word {word}:
{_FLASHCARD_DESCRIPTION}"""


def get_generate_flashcard_from_paragraph_prompt(text: str):
    return f"""Below the line is a paragraph from an article in Chinese. Extract key vocabulary and grammar phrases, except proper nouns.
--
{text}
--
For each word or phrase, generate the following fields to be used as a flashcard for that word or phrase:
{_FLASHCARD_DESCRIPTION}"""


def get_generate_flashcard_from_llm_conversation_prompt(text: str):
    return f"""Below the line is a conversation between a language learner and a LLM assistant in Chinese. Extract key vocabulary and grammar phrases, except proper nouns.
--
{text}
--
For each word or phrase, generate the following fields to be used as a flashcard for that word or phrase:
{_FLASHCARD_DESCRIPTION}"""
