from typing import List, Literal
from pydantic import BaseModel, Field


class ChineseFlashcard(BaseModel):
    word: str = Field("The word/phrase in simplified Chinese")
    pinyin: str = Field("The word romanized using Pinyin (lowercased)")
    english: str = Field("The word translated into English (lowercased)")
    sample_usage: str = Field("Example sentence with the word which contextualizes it")
    sample_usage_english: str = Field(
        description="The sample usage field translated to English"
    )
    frequency: Literal[
        "very common", "common", "infrequent", "rare", "very rare"
    ] = Field(
        description="Correctly assign one one of the predefined relative frequencies to this word/phrase"
    )

    def __str__(self):
        return f"""
Word: {self.word}
Pinyin: {self.pinyin}
English: {self.english}
Sample Usage: {self.sample_usage}
Sample Usage (English): {self.sample_usage_english}
Frequency: {self.frequency}
        """.strip()

    @classmethod
    def from_anki_json(cls, anki_json):
        fields = anki_json["fields"]
        instance = cls(
            word=fields["Chinese"]["value"],
            pinyin=fields["Pinyin"]["value"],
            english=fields["English"]["value"],
            sample_usage=fields["Sample Usage"]["value"],
            sample_usage_english=fields["Sample Usage (English)"]["value"],
        )
        return instance


class ChineseFlashcards(BaseModel):
    flashcards: List[ChineseFlashcard]
