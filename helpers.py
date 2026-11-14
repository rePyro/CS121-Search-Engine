from bs4 import BeautifulSoup
from collections import Counter
from pathlib import Path
import os
import re
from nltk.stem.snowball import SnowballStemmer

_stemmer_cache = {} # cache of stemmer results, avoiding rerunning Snowball on already-stemmed words
_stemmer = SnowballStemmer("english") # stemmer object, set to English
_TOKEN_RE = re.compile(r"[a-z0-9]+")  # regex for one or more alphanumeric (lowercase)

def _stem(word: str) -> str:
    """
    Return the stemmed verison of the word, running _stemmer if it hasn't been stemmed before.
    """
    if word not in _stemmer_cache:
        _stemmer_cache[word] = _stemmer.stem(word)
    return _stemmer_cache[word]

def tokenize(raw_text: str) -> list[str]:
    """
    Tokenize the text, lowercasing, spliting alphanumerically, and Porter-stemming
    Returns tokens in order, duplicates kept
    """
    words: list[str]  = _TOKEN_RE.findall(raw_text.lower())
    tokens: list[str] = [_stem(word) for word in words]
    return tokens

def extract_word_frequency(content: str) -> Counter[str]:
    """
    Turn a string of HTML into BeautifulSoup, then get the text, and then return a Counter of text frequency
    """
    soup: BeautifulSoup = BeautifulSoup(content, 'html.parser')

    for tag in soup(["script", "style", "noscript", "template", "svg"]):
        tag.decompose() # destroy content in the above tags
    
    raw_text: str       = soup.get_text(separator=" ")
    tokens: list[str]   = tokenize(raw_text)
    words: Counter[str] = Counter(tokens)
    
    return words

# def get_unique_words(content: str) -> set[str]:
#     """
#     Given an unprocessed string of HTML, extract words from it and return a set of distinct words
#     """
#     return set(extract_word_frequency(content))

def get_file_size_kb(file: Path | str) -> float:
    """
    Get size in kb
    """
    return os.path.getsize(file) / 1000

def clear_terminal():
  os.system('cls' if os.name == 'nt' else 'clear')