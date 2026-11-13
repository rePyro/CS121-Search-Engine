from bs4 import BeautifulSoup
from collections import Counter
from pathlib import Path
import os

# Terms that go to search must be tokenized. Use helpers.tokenize

def tokenize(text: str) -> list[str]:
    """
    Tokenize the text, lowercasing, spliting alphanumerically, and Porter-stemming
    Returns tokens in order, duplicates kept
    """
    pass


def extract_word_frequency(content: str) -> Counter[str]:
    """
    Turn a string of HTML into BeautifulSoup, then get the text, and then return a Counter of text frequency
    """
    soup: BeautifulSoup = BeautifulSoup(content, 'html.parser')
    tokens: list[str]   = soup.get_text(separator=" ").split()
    words: Counter[str] = Counter(tokens)
    
    return words

def get_unique_words(content: str) -> set[str]:
    """
    Given an unprocessed string of HTML, extract words from it and return a set of distinct words
    """
    return set(extract_word_frequency(content))

def get_file_size_kb(file: Path | str) -> float:
    """
    Get size in kb
    """
    return os.path.getsize(file) / 1000

def clear_terminal():
  os.system('cls' if os.name == 'nt' else 'clear')