import helpers
import index_access

class SearchResult:
    url: str
    score: float

    def __init__(self, url: str, score: float):
        self.url = url
        self.score = score


def search(query: str, k: int = 5) -> list[SearchResult]:
    """Returns the top k search results and handles boolean search logic"""
    return [SearchResult("https://example.com", 5.0),SearchResult("https://mzecheru.com", 4.0),
            SearchResult("https://stevo.com", 3.0), SearchResult("https://test.com", 2.0),
            SearchResult("https://kevin.com", 1.0)]

def prompt_loop():
    """Prompt loop: read query, call search(), print results"""
    while True:
        try:
            query = input("Search query: ")
            print()
        except EOFError:
            break

        results: list[SearchResult] = search(query, k = 5)
        for i, result in enumerate(results):
            # Ex: 1. https://example.com
            print(f"{i+1}. {result.url}")
        
        input()
        helpers.clear_terminal()


if __name__ == "__main__":
    prompt_loop()