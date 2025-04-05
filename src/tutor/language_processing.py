"""Module for language-specific processing operations.

This module contains classes and functions for handling language-specific preprocessing
operations such as character conversion between simplified and traditional Chinese,
and can be extended to support other languages in the future.
"""

from tutor.utils.chinese import to_simplified, to_traditional


class LanguagePreprocessor:
    """Handles language-specific preprocessing operations.

    Currently supports:
    - Mandarin: Converts to simplified Chinese
    - Cantonese: Converts to traditional Chinese

    Can be extended to support other languages in the future.
    """

    @staticmethod
    def process_for_language(text: str, language: str) -> str:
        """Preprocess text based on the specified language.

        For Mandarin, converts to simplified Chinese.
        For Cantonese, converts to traditional Chinese.
        For other languages, returns the text as-is.

        Args:
            text: The text to preprocess
            language: The language to process for (e.g., "mandarin", "cantonese")

        Returns:
            The preprocessed text in the appropriate form for the language
        """
        if language == "mandarin":
            return to_simplified(text)
        elif language == "cantonese":
            return to_traditional(text)
        return text  # Default case, return as-is
