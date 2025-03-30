from tutor.llm.models import (
    LanguageFlashcard,
    MandarinFlashcard,
    CantoneseFlashcard,
    MandarinRelatedWord,
    CantoneseRelatedWord,
)


class TestLanguageFlashcard:
    """Tests for the base LanguageFlashcard class."""

    def test_from_anki_json_factory(self):
        """Test that from_anki_json factory method correctly routes to the right subclass."""
        # Mandarin note
        mandarin_note = {
            "noteId": 1234,
            "modelName": "Mandarin",
            "fields": {
                "Chinese": {"value": "你好"},
                "Pinyin": {"value": "nǐ hǎo"},
                "English": {"value": "hello"},
                "Sample Usage": {"value": "你好吗？"},
                "Sample Usage (English)": {"value": "How are you?"},
                "Related Words": {"value": ""},
            },
        }

        # Cantonese note
        cantonese_note = {
            "noteId": 5678,
            "modelName": "Cantonese",
            "fields": {
                "Chinese": {"value": "你好"},
                "Jyutping": {"value": "nei5 hou2"},
                "English": {"value": "hello"},
                "Sample Usage": {"value": "你好吗？"},
                "Sample Usage (English)": {"value": "How are you?"},
                "Related Words": {"value": ""},
            },
        }

        # Test factory method with Mandarin note
        flashcard = LanguageFlashcard.from_anki_json(mandarin_note)
        assert isinstance(flashcard, MandarinFlashcard)
        assert flashcard.word == "你好"
        assert flashcard.pinyin == "nǐ hǎo"

        # Test factory method with Cantonese note
        flashcard = LanguageFlashcard.from_anki_json(cantonese_note)
        assert isinstance(flashcard, CantoneseFlashcard)
        assert flashcard.word == "你好"
        assert flashcard.jyutping == "nei5 hou2"

    def test_parse_related_words(self):
        """Test the _parse_related_words helper method."""
        # Sample related words text
        related_words_text = """
        学习 (xué xí) - to study [similar usage]
        • 教育 (jiào yù) - education [related field]
        - 考试 (kǎo shì) - exam [common context]
        """

        # Parse for Mandarin
        mandarin_words = LanguageFlashcard._parse_related_words(
            related_words_text, MandarinRelatedWord, "pinyin"
        )

        # Verify results
        assert len(mandarin_words) == 3
        assert mandarin_words[0].word == "学习"
        assert mandarin_words[0].pinyin == "xué xí"
        assert mandarin_words[0].english == "to study"
        assert mandarin_words[0].relationship == "similar usage"

        assert mandarin_words[1].word == "教育"
        assert mandarin_words[1].relationship == "related field"

        assert mandarin_words[2].word == "考试"
        assert mandarin_words[2].relationship == "common context"


class TestMandarinFlashcard:
    """Tests for the MandarinFlashcard class."""

    def test_from_anki_json(self):
        """Test creating a MandarinFlashcard from Anki JSON."""
        # Create a sample Anki note JSON
        anki_json = {
            "noteId": 1234,
            "fields": {
                "Chinese": {"value": "学习"},
                "Pinyin": {"value": "xué xí"},
                "English": {"value": "to study, to learn"},
                "Sample Usage": {"value": "我每天学习中文。"},
                "Sample Usage (English)": {"value": "I study Chinese every day."},
                "Related Words": {
                    "value": "教育 (jiào yù) - education [related field]\n考试 (kǎo shì) - exam [common context]"
                },
            },
        }

        # Create flashcard from JSON
        flashcard = MandarinFlashcard._from_anki_json(anki_json)

        # Verify basic fields
        assert flashcard.anki_note_id == 1234
        assert flashcard.word == "学习"
        assert flashcard.pinyin == "xué xí"
        assert flashcard.english == "to study, to learn"
        assert flashcard.sample_usage == "我每天学习中文。"
        assert flashcard.sample_usage_english == "I study Chinese every day."

        # Verify related words
        assert len(flashcard.related_words) == 2
        assert flashcard.related_words[0].word == "教育"
        assert flashcard.related_words[0].pinyin == "jiào yù"
        assert flashcard.related_words[0].english == "education"
        assert flashcard.related_words[0].relationship == "related field"

        assert flashcard.related_words[1].word == "考试"
        assert flashcard.related_words[1].pinyin == "kǎo shì"
        assert flashcard.related_words[1].english == "exam"
        assert flashcard.related_words[1].relationship == "common context"

    def test_get_required_anki_fields(self):
        """Test that get_required_anki_fields returns the correct fields."""
        fields = MandarinFlashcard.get_required_anki_fields()
        assert "Chinese" in fields
        assert "Pinyin" in fields
        assert "English" in fields
        assert "Sample Usage" in fields
        assert "Sample Usage (English)" in fields
        assert "Related Words" in fields


class TestCantoneseFlashcard:
    """Tests for the CantoneseFlashcard class."""

    def test_from_anki_json(self):
        """Test creating a CantoneseFlashcard from Anki JSON."""
        # Create a sample Anki note JSON
        anki_json = {
            "noteId": 5678,
            "fields": {
                "Chinese": {"value": "學習"},
                "Jyutping": {"value": "hok6 zaap6"},
                "English": {"value": "to study, to learn"},
                "Sample Usage": {"value": "我每日學習廣東話。"},
                "Sample Usage (English)": {"value": "I study Cantonese every day."},
                "Related Words": {
                    "value": "教育 (gaau3 juk6) - education [related field]\n考試 (haau2 si5) - exam [common context]"
                },
            },
        }

        # Create flashcard from JSON
        flashcard = CantoneseFlashcard._from_anki_json(anki_json)

        # Verify basic fields
        assert flashcard.anki_note_id == 5678
        assert flashcard.word == "學習"
        assert flashcard.jyutping == "hok6 zaap6"
        assert flashcard.english == "to study, to learn"
        assert flashcard.sample_usage == "我每日學習廣東話。"
        assert flashcard.sample_usage_english == "I study Cantonese every day."

        # Verify related words
        assert len(flashcard.related_words) == 2
        assert flashcard.related_words[0].word == "教育"
        assert flashcard.related_words[0].jyutping == "gaau3 juk6"
        assert flashcard.related_words[0].english == "education"
        assert flashcard.related_words[0].relationship == "related field"

        assert flashcard.related_words[1].word == "考試"
        assert flashcard.related_words[1].jyutping == "haau2 si5"
        assert flashcard.related_words[1].english == "exam"
        assert flashcard.related_words[1].relationship == "common context"

    def test_get_required_anki_fields(self):
        """Test that get_required_anki_fields returns the correct fields."""
        fields = CantoneseFlashcard.get_required_anki_fields()
        assert "Chinese" in fields
        assert "Jyutping" in fields
        assert "English" in fields
        assert "Sample Usage" in fields
        assert "Sample Usage (English)" in fields
        assert "Related Words" in fields


class TestRelatedWords:
    """Tests for the RelatedWord classes."""

    def test_mandarin_related_word(self):
        """Test creating and using MandarinRelatedWord."""
        word = MandarinRelatedWord(
            word="学习",
            pinyin="xué xí",
            english="to study",
            relationship="similar usage",
        )

        assert word.word == "学习"
        assert word.pinyin == "xué xí"
        assert word.english == "to study"
        assert word.relationship == "similar usage"

        # Test string representation
        assert str(word) == "学习 (xué xí) - to study [similar usage]"

    def test_cantonese_related_word(self):
        """Test creating and using CantoneseRelatedWord."""
        word = CantoneseRelatedWord(
            word="學習",
            jyutping="hok6 zaap6",
            english="to study",
            relationship="similar usage",
        )

        assert word.word == "學習"
        assert word.jyutping == "hok6 zaap6"
        assert word.english == "to study"
        assert word.relationship == "similar usage"

        # Test string representation
        assert str(word) == "學習 (hok6 zaap6) - to study [similar usage]"
