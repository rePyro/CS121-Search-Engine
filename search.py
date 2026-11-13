import helpers
import index_access

class SearchResult:
    url: str
    score: float

def search(query: str, k: int = 5) -> list[SearchResult]:
    """Returns the top k search results and handles boolean search logic"""
    pass

def prompt_loop():
    """Prompt loop: read query, call search(), print results"""
    while True:
        try:
            query = input("Search query: ")
        except EOFError:
            break
        results: list[SearchResult] = search(query, k = 5)
        for i, result in enumerate(results):
            # Ex: 1. https://example.com
            print(f"{i+1}. {result.url}")
        