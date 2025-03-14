_FLASHCARD_DESCRIPTION = """
Generate a flashcard with the following fields:
- Word, Pinyin, and English translation
- A practical sample usage sentence with English translation
- Frequency of use
- 2-3 related words that share patterns or common usage, each with Chinese, pinyin, English, and relationship type

Focus on practical usage for intermediate students. For related words, prefer words that are commonly used together or follow similar patterns.
"""


def get_generate_flashcard_from_word_prompt(word: str):
    return f"""Generate the following fields to be used as a flashcard for the word/phrase {word}. If the input seems wrong, please select the most-likely intended phrase:
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
