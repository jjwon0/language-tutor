"""Utilities for handling Chinese text."""

import opencc


def to_simplified(text: str) -> str:
    """Convert traditional Chinese characters to simplified Chinese characters."""
    converter = opencc.OpenCC("t2s")  # traditional to simplified
    return converter.convert(text)
