"""Каноническая нормализация текста с сохранением регистра."""

import unicodedata


def normalize_text(text: str) -> str:
    """Привести текст к NFC и свернуть пробелы; совместимые символы различаются."""
    return " ".join(unicodedata.normalize("NFC", text).split())
