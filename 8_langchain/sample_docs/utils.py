"""Utility functions for data processing."""

def clean_text(text: str) -> str:
    """Remove extra whitespace from text."""
    return ' '.join(text.split())

def chunk_list(lst: list, size: int) -> list:
    """Split a list into chunks of given size."""
    return [lst[i:i+size] for i in range(0, len(lst), size)]

def count_tokens(text: str) -> int:
    """Approximate token count (words / 0.75)."""
    return int(len(text.split()) / 0.75)
