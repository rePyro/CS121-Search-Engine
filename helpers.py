from bs4 import BeautifulSoup
from collections import Counter
from pathlib import Path
import os


def extract_word_frequency(content: str) -> Counter[str]:
    """
    Turn a string of HTML into BeautifulSoup, then get the text, and then return a Counter of text frequency.
    """
    soup: BeautifulSoup = BeautifulSoup(content, 'html.parser')
    tokens: list[str]   = soup.get_text(separator=" ").split()
    words: Counter[str] = Counter(tokens)
    
    return words

def get_unique_words(content: str) -> set[str]:
    """
    Given an unprocessed string of HTML, extract words from it and return a set of distinct words.
    """
    return set(extract_word_frequency(content))

def get_file_size(file: Path) -> float:
    return os.path.getsize(file) / 1000