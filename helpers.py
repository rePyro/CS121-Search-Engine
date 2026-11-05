from bs4 import BeautifulSoup
import re

TOKEN_RE = re.compile(r"[a-z0-9]+")

# take in a full HTML document and return the number of unique words in the document

def get_text_in_page(soup: BeautifulSoup) -> list[str]:
    # delete any script, style, and noscript tags from the parsing
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    # apply TOKEN_RE word definition to text extracted by soup and return the processed text
    return TOKEN_RE.findall(soup.get_text(separator=" ").lower())

def get_unique_words_in_page(soup: BeautifulSoup) -> set[str]:
    return set(get_text_in_page(soup))

def helper_function() -> None:
	"""
	docstring
	"""

    soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
    text: list[str] = get_text_in_page(soup)

	raise NotImplementedError("Implement helper_function")
