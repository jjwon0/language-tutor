def get_generate_flashcard_from_word_prompt(word: str):
    return f"""Generate all of the following items as bullet points for the word/phrase: {word}:

- Word/phrase: Repeat the word/phrase verbatim.
- Pinyin: Provide the Pinyin transliteration of the Chinese word or phrase.
- English Translation: Translate the word or phrase into English.
- Sample Usage in Chinese: Create or find a sentence from the article (or construct a new one) that uses the word or phrase in context.
- Sample Usage in English: Translate the sample usage sentence into English, ensuring that it reflects the usage of the word or phrase in context."""


def get_generate_flashcard_from_paragraph_prompt(text: str):
    return f"""Below the line is a paragraph from an article in Chinese: identify and extract key vocabulary and grammar phrases, ignoring proper nouns. For each identified item, generate a flashcard that includes the following information:

- Word/Phrase in Simplified Chinese: Extract the word or phrase from the article.
- Pinyin: Provide the Pinyin transliteration of the Chinese word or phrase.
- English Translation: Translate the word or phrase into English.
- Sample Usage in Chinese: Create or find a sentence from the article (or construct a new one) that uses the word or phrase in context.
- Sample Usage in English: Translate the sample usage sentence into English, ensuring that it reflects the usage of the word or phrase in context.

For each flashcard, focus on clarity and practical usage, ensuring the information is useful for an intermediate Chinese speaker looking to improve vocabulary and understanding of grammar.
--
{text}"""


def get_generate_flashcard_from_llm_conversation_prompt(text: str):
    return f"""Below the line is a conversation between a language learner and a LLM assistant in Chinese. Identify and extract key vocabulary and grammar phrases from the LLM's responses, ignoring proper nouns. For each identified item, generate a flashcard that includes the following information:

- Word/Phrase in Simplified Chinese: Extract the word or phrase from the article.
- Pinyin: Provide the Pinyin transliteration of the Chinese word or phrase.
- English Translation: Translate the word or phrase into English.
- Sample Usage in Chinese: Create or find a sentence from the article (or construct a new one) that uses the word or phrase in context.
- Sample Usage in English: Translate the sample usage sentence into English, ensuring that it reflects the usage of the word or phrase in context.

For each flashcard, focus on clarity and practical usage, ensuring the information is useful for an intermediate Chinese speaker looking to improve vocabulary and understanding of grammar.
--
{text}"""
