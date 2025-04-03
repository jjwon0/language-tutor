from typing import List, Literal, Union, ClassVar, Dict, Type, Any
from pydantic.json_schema import SkipJsonSchema
from pydantic import BaseModel, Field


class RelatedWord(BaseModel):
    """Base class for related words in flashcards.

    Each language should define its own RelatedWord subclass with appropriate fields.
    """

    word: str = Field(description="The related word/phrase in the target language")
    english: str = Field(
        description="The word translated into English (lowercased), with any important context or nuance in parentheses"
    )
    relationship: str = Field(
        description="Brief note on relationship (e.g., 'synonym', 'antonym', 'formal variant', 'casual variant', 'commonly paired', 'similar pattern')"
    )


class LanguageFlashcard(BaseModel):
    """Base class for all language flashcards.

    This provides common fields and functionality for all language-specific flashcard types.
    Language-specific classes should inherit from this and add specialized fields and behavior.
    """

    # Base Anki field mapping - language-specific classes should extend this
    ANKI_FIELD_NAMES: ClassVar[Dict[str, str]] = {
        "word": "Word",
        "english": "English",
        "sample_usage": "Sample Usage",
        "sample_usage_english": "Sample Usage (English)",
    }

    # Class attribute to identify the language - subclasses must override this
    LANGUAGE: ClassVar[str] = "base"

    # Registry to keep track of all language-specific flashcard classes
    _registry: ClassVar[Dict[str, Type["LanguageFlashcard"]]] = {}

    # Common fields for all language flashcards
    anki_note_id: SkipJsonSchema[Union[int, None]] = None
    word: str = Field(description="The word/phrase in the target language")
    english: str = Field(
        description="The word translated into English (lowercased). Include any important context or nuance in parentheses to help distinguish from similar words."
    )
    sample_usage: str = Field(
        description="A practical example sentence that shows how the word is naturally used in context. Should be appropriate for the configured learner level."
    )
    sample_usage_english: str = Field(
        description="Natural English translation of the sample usage sentence"
    )
    frequency: Literal[
        "very common", "common", "infrequent", "rare", "very rare", None
    ] = Field(
        default=None,
        description="How often the word is used in modern language",
    )

    def __init_subclass__(cls, **kwargs):
        """Register subclasses in the registry for easy lookup by language name."""
        super().__init_subclass__(**kwargs)
        if hasattr(cls, "LANGUAGE") and cls.LANGUAGE != "base":
            LanguageFlashcard._registry[cls.LANGUAGE] = cls

    @classmethod
    def get_class_for_language(cls, language: str) -> Type["LanguageFlashcard"]:
        """Get the appropriate flashcard class for a given language."""
        language = language.lower()
        if language in cls._registry:
            return cls._registry[language]
        raise ValueError(f"No flashcard class registered for language: {language}")

    @classmethod
    def from_anki_json(cls, anki_json: Dict[str, Any]):
        """Factory method to create the appropriate flashcard from Anki note JSON.

        This base implementation determines which language-specific class to use,
        then delegates to that class's _from_anki_json implementation.
        """
        # Determine language based on model name if available
        model_name = anki_json.get("modelName", "").lower()

        # Choose language class based on model name
        if "cantonese" in model_name:
            flashcard_class = CantoneseFlashcard
        else:
            # Default to Mandarin if not explicitly Cantonese
            flashcard_class = MandarinFlashcard

        # Delegate to the language-specific implementation
        return flashcard_class._from_anki_json(anki_json)

    @classmethod
    def _from_anki_json(cls, anki_json: Dict[str, Any]):
        """Language-specific implementation to create a flashcard from Anki note JSON.

        This should be overridden by subclasses to handle language-specific fields.
        """
        raise NotImplementedError("Subclasses must implement _from_anki_json")

    @staticmethod
    def _parse_related_words(
        related_words_text: str,
        related_word_class: Type[RelatedWord],
        pronunciation_field: str,
    ) -> List[RelatedWord]:
        """Parse related words text into a list of RelatedWord objects.

        Args:
            related_words_text: Text containing related words in the format "word (pronunciation) - english [relationship]"
            related_word_class: The class to use for creating related word objects
            pronunciation_field: The name of the pronunciation field in the related word class

        Returns:
            List of RelatedWord objects
        """
        related_words = []

        # Split by lines and process each line
        for line in related_words_text.split("\n"):
            line = line.strip()
            if not line:
                continue

            # Remove bullet points if present
            if line.startswith("•") or line.startswith("-"):
                line = line[1:].strip()

            # Parse format: "word (pronunciation) - english [relationship]"
            try:
                # Split into parts
                word_part, rest = line.split("(", 1)
                pronunciation_part, rest = rest.split(")", 1)
                rest = rest.strip()
                if rest.startswith("-"):
                    rest = rest[1:].strip()
                english_part, relationship_part = rest.split("[", 1)
                relationship_part = relationship_part.rstrip("]").strip()

                # Create RelatedWord object with the appropriate pronunciation field
                kwargs = {
                    "word": word_part.strip(),
                    "english": english_part.strip(),
                    "relationship": relationship_part,
                    pronunciation_field: pronunciation_part.strip(),
                }
                related_words.append(related_word_class(**kwargs))
            except (ValueError, IndexError):
                # Skip malformed entries
                continue

        return related_words

    @classmethod
    def get_required_anki_fields(cls) -> List[str]:
        """Get list of required Anki note fields."""
        fields = [
            cls.ANKI_FIELD_NAMES[field]
            for field in cls.model_fields
            if field not in ["anki_note_id", "frequency"]
            and field in cls.ANKI_FIELD_NAMES
        ]
        fields.append("Sample Usage (Audio)")
        return fields

    def __str__(self):
        """String representation of the flashcard.

        Subclasses should override this to include language-specific fields.
        """
        base_str = f"""
Language: {self.LANGUAGE.capitalize()}
Word: {self.word}
English: {self.english}
Sample Usage: {self.sample_usage}
Sample Usage (English): {self.sample_usage_english}
Frequency: {self.frequency}
        """.strip()

        # Related words handling should be implemented by subclasses
        return base_str


class MandarinRelatedWord(RelatedWord):
    """Related word specifically for Mandarin Chinese."""

    pinyin: str = Field(description="The word romanized using Pinyin with tone marks")

    def __str__(self) -> str:
        return f"{self.word} ({self.pinyin}) - {self.english} [{self.relationship}]"


class MandarinFlashcard(LanguageFlashcard):
    """Flashcard specifically for Mandarin Chinese."""

    LANGUAGE: ClassVar[str] = "mandarin"

    # Update field mappings to include Mandarin-specific fields
    ANKI_FIELD_NAMES: ClassVar[Dict[str, str]] = {
        **LanguageFlashcard.ANKI_FIELD_NAMES,
        "word": "Chinese",  # In Anki, the field is called "Chinese"
        "pinyin": "Pinyin",
        "related_words": "Related Words",
    }

    # Mandarin-specific fields
    pinyin: str = Field(description="The word romanized using Pinyin with tone marks")
    related_words: List[MandarinRelatedWord] = Field(
        default_factory=list,
        description="2-3 semantically related words that help learn this word.",
    )

    @classmethod
    def _from_anki_json(cls, anki_json: Dict[str, Any]):
        """Create a Mandarin flashcard from Anki note JSON."""
        fields = anki_json["fields"]

        # Extract basic fields
        instance = cls(
            anki_note_id=anki_json["noteId"],
            word=fields["Chinese"]["value"],
            pinyin=fields["Pinyin"]["value"],
            english=fields["English"]["value"],
            sample_usage=fields["Sample Usage"]["value"],
            sample_usage_english=fields["Sample Usage (English)"]["value"],
            frequency=None,  # Currently field is only at generation
        )

        # Parse related words if present
        if "Related Words" in fields and fields["Related Words"]["value"]:
            related_words_text = fields["Related Words"]["value"]
            instance.related_words = cls._parse_related_words(
                related_words_text, MandarinRelatedWord, "pinyin"
            )

        return instance

    def __str__(self):
        base_str = f"""
Language: {self.LANGUAGE.capitalize()}
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
                related_words_str += f"\n  • {rw}"
            return base_str + related_words_str
        return base_str


class CantoneseRelatedWord(RelatedWord):
    """Related word specifically for Cantonese."""

    jyutping: str = Field(
        description="The word romanized using Jyutping with tone numbers"
    )

    def __str__(self) -> str:
        return f"{self.word} ({self.jyutping}) - {self.english} [{self.relationship}]"


class CantoneseFlashcard(LanguageFlashcard):
    """Flashcard specifically for Cantonese."""

    LANGUAGE: ClassVar[str] = "cantonese"

    # Update field mappings to include Cantonese-specific fields
    ANKI_FIELD_NAMES: ClassVar[Dict[str, str]] = {
        **LanguageFlashcard.ANKI_FIELD_NAMES,
        "word": "Chinese",  # In Anki, the field is called "Chinese"
        "jyutping": "Jyutping",
        "related_words": "Related Words",
    }

    # Cantonese-specific fields
    jyutping: str = Field(
        description="The word romanized using Jyutping with tone numbers"
    )
    related_words: List[CantoneseRelatedWord] = Field(
        default_factory=list,
        description="2-3 semantically related words that help learn this word.",
    )

    @classmethod
    def _from_anki_json(cls, anki_json: Dict[str, Any]):
        """Create a Cantonese flashcard from Anki note JSON."""
        fields = anki_json["fields"]

        # Extract basic fields
        instance = cls(
            anki_note_id=anki_json["noteId"],
            word=fields["Chinese"]["value"],
            jyutping=fields["Jyutping"]["value"],
            english=fields["English"]["value"],
            sample_usage=fields["Sample Usage"]["value"],
            sample_usage_english=fields["Sample Usage (English)"]["value"],
            frequency=None,  # Currently field is only at generation
        )

        # Parse related words if present
        if "Related Words" in fields and fields["Related Words"]["value"]:
            related_words_text = fields["Related Words"]["value"]
            instance.related_words = cls._parse_related_words(
                related_words_text, CantoneseRelatedWord, "jyutping"
            )

        return instance

    def __str__(self):
        base_str = f"""
Language: {self.LANGUAGE.capitalize()}
Word: {self.word}
Jyutping: {self.jyutping}
English: {self.english}
Sample Usage: {self.sample_usage}
Sample Usage (English): {self.sample_usage_english}
Frequency: {self.frequency}
        """.strip()

        if self.related_words:
            related_words_str = "\nRelated Words:"
            for rw in self.related_words:
                related_words_str += f"\n  • {rw}"
            return base_str + related_words_str
        return base_str


class LanguageFlashcards(BaseModel):
    """Container for multiple flashcards of any language type."""

    flashcards: List[LanguageFlashcard]


# For backward compatibility
ChineseFlashcard = MandarinFlashcard
ChineseFlashcards = LanguageFlashcards
