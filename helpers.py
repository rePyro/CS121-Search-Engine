from bs4 import BeautifulSoup, Tag
from collections import Counter
from pathlib import Path
import os
import re
from nltk.stem.snowball import SnowballStemmer

_stemmer_cache = {} # cache of stemmer results, avoiding rerunning Porter2 on already-stemmed words
_stemmer = SnowballStemmer("english") # stemmer object, set to English (Porter2)
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
    Tokenize the text, lowercasing, spliting alphanumerically, and Porter2-stemming
    Returns tokens in order, duplicates kept
    """
    words: list[str]  = _TOKEN_RE.findall(raw_text.lower())
    tokens: list[str] = [_stem(word) for word in words]
    return tokens

def _count_tags(soup: BeautifulSoup, names: list[str]) -> Counter[str]:
    """
    Find all HTML sections with the tag(s) in names, extract the text out of each section, 
    join each extracted text together, tokenize, and return a Counter of those tokens
    """
    tags: list[Tag]   = soup.find_all(names)
    texts: list[str]  = [tag.get_text(" ") for tag in tags]
    combined: str     = " ".join(texts)
    tokens: list[str] = tokenize(combined)

    return Counter(tokens)

def extract_word_frequency(content: str) -> tuple[Counter[str], Counter[str], Counter[str], Counter[str]]:
    """
    Turn a string of HTML into BeautifulSoup, strips extraneous tags, and extracts term frequencies.
    Returns a tuple of four Counters: tf, tf_title, tf_heading, and tf_emphasis.
    """
    soup: BeautifulSoup = BeautifulSoup(content, 'lxml')

    for tag in soup(["script", "style", "noscript", "template", "svg", "nav", "footer"]):
        tag.decompose() # destroy content in the above tags

    # extract all text from soup, tokenize, and convert into a Counter (automatically counts input keys into value)
    raw_text: str           = soup.get_text(separator=" ")
    tokens: list[str]       = tokenize(raw_text)
    all_words: Counter[str] = Counter(tokens)

    # extract specific tags from soup for weighting purposes
    title: Counter[str]    = _count_tags(soup, ["title"])
    heading: Counter[str]  = _count_tags(soup, ["h1", "h2", "h3"])
    emphasis: Counter[str] = _count_tags(soup, ["h4", "h5", "h6", "strong", "b"])
    
    return (all_words, title, heading, emphasis)

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