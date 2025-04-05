"""Utilities for handling Chinese text.

This module provides functions for converting between traditional and simplified Chinese characters.
"""

import opencc


def to_simplified(text: str) -> str:
    """Convert traditional Chinese characters to simplified Chinese characters."""
    converter = opencc.OpenCC("t2s")  # traditional to simplified
    return converter.convert(text)


def to_traditional(text: str) -> str:
    """Convert simplified Chinese characters to traditional Chinese characters."""
    converter = opencc.OpenCC("s2t")  # simplified to traditional
    return converter.convert(text)


def process_chinese_for_language(text: str, language: str) -> str:
    """Process Chinese text based on the specified language.

    For Mandarin, converts to simplified Chinese.
    For Cantonese, converts to traditional Chinese.

    Args:
        text: The Chinese text to process
        language: The language to process for ("mandarin" or "cantonese")

    Returns:
        The processed text in the appropriate form for the language
    """
    if language == "mandarin":
        return to_simplified(text)
    elif language == "cantonese":
        return to_traditional(text)
    return text  # Default case, return as-is
