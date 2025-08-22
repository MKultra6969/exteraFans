from . import storage


def check_for_banwords(text: str) -> str | None:
    banwords = storage.get_banwords()

    text_lower = text.lower()

    for word in banwords:
        if word.lower() in text_lower:
            return word

    return None