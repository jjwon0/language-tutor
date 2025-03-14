from typing import List, Literal, Union
from pydantic.json_schema import SkipJsonSchema
from pydantic import BaseModel, Field


class RelatedWord(BaseModel):
    word: str = Field(description="The related word/phrase in simplified Chinese")
    pinyin: str = Field(description="The word romanized using Pinyin (lowercased)")
    english: str = Field(
        description="The word translated into English (lowercased), with any important context or nuance in parentheses"
    )
    relationship: str = Field(
        description="Brief note on relationship (e.g., 'synonym', 'antonym', 'formal variant', 'casual variant', 'commonly paired', 'similar pattern'). Focus on words that are commonly used together or follow similar patterns."
    )


class ChineseFlashcard(BaseModel):
    anki_note_id: SkipJsonSchema[Union[int, None]] = None
    word: str = Field(description="The word/phrase in simplified Chinese")
    pinyin: str = Field(description="The word romanized using Pinyin (lowercased)")
    english: str = Field(
        description="The word translated into English (lowercased). Include any important context or nuance in parentheses to help distinguish from similar words."
    )
    sample_usage: str = Field(
        description="A practical example sentence that shows how the word is naturally used in context. Should be at an intermediate level."
    )
    sample_usage_english: str = Field(
        description="Natural English translation of the sample usage sentence"
    )
    related_words: List[RelatedWord] = Field(
        default_factory=list,
        description="2-3 semantically related words that help learn this word. Focus on words that are commonly used together or follow similar patterns, rather than just synonyms.",
    )
    frequency: Literal[
        "very common", "common", "infrequent", "rare", "very rare", None
    ] = Field(
        default=None,
        description="How often the word is used in modern Chinese",
    )

    def __str__(self):
        base_str = f"""
Word: {self.word}
Pinyin: {self.pinyin}
English: {self.english}
Sample Usage: {self.sample_usage}
Sample Usage (English): {self.sample_usage_english}
Frequency: {self.frequency}
        """.strip()

        if self.related_words:
            related_words_str = "\nRelated Words:"
            for rw in self.related_words:
                related_words_str += (
                    f"\n  • {rw.word} ({rw.pinyin}) - {rw.english} [{rw.relationship}]"
                )
            return base_str + related_words_str
        return base_str

    @classmethod
    def from_anki_json(cls, anki_json):
        fields = anki_json["fields"]
        instance = cls(
            anki_note_id=anki_json["noteId"],
            word=fields["Chinese"]["value"],
            pinyin=fields["Pinyin"]["value"],
            english=fields["English"]["value"],
            sample_usage=fields["Sample Usage"]["value"],
            sample_usage_english=fields["Sample Usage (English)"]["value"],
            frequency=None,  # currently field is only at generation
        )
        return instance


class ChineseFlashcards(BaseModel):
    flashcards: List[ChineseFlashcard]
