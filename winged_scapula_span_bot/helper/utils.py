def is_not_empty_string(string: str | None) -> bool:
    return string is not None and len(string.strip()) > 0
