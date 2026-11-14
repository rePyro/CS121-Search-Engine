import helpers
import index_access

import math
import time

# Rename index_access to index_API

class SearchResult:
    url: str
    score: float

    def __init__(self, url: str, score: float):
        self.url = url
        self.score = score


def tf_idf(tf: int, df: int, N: int) -> float:
    """Calculate the tf_idf, which is 'term frequency inverse document frequency'.
       Equal to tf * log(N / df) """
    return tf * math.log10(N / df)


def search(query: str, k: int = 5) -> list[SearchResult]:
    """Returns the top k search results and handles boolean AND search logic"""
    # Use set to remove duplicates
    search_terms: set[str] = list(set(helpers.tokenize(query)))
    if not search_terms:
        return []

    N = index_access.num_docs()
    postings_container = {search_term: index_access.get_postings(search_term) for search_term in search_terms}

    # Since "AND" logic is used for all the terms, an empty set means the intersection is the null set
    if (any(len(p) == 0 for p in postings_container.values())):
        return []

    ### Handle 'AND' intersections below ###
    # Sort it to start with the smallest set to keep the intersection as small as it will be
    search_terms.sort(key=lambda t: len(postings_container[t]))
    intersection = set(p[0] for p in postings_container[search_terms[0]])
    if len(search_terms) > 1:
        for t in search_terms[1:]:
            # p[0] is doc_id    
            intersection &= set(p[0] for p in postings_container[t])

    scores = {doc_id: 0.0 for doc_id in intersection}
    for t, postings in postings_container.items():
        idf = math.log10(N / len(postings))
        for p in postings:
            # If the doc_id is one of the ones that is in the intersection (from the AND join)
            if p[0] in intersection:
                scores[p[0]] += p[1] * idf

    #                                              entry[1] is the score
    top = sorted(scores.items(), key=lambda entry: entry[1], reverse=True)
    top = top[:k]
    return [
        SearchResult(
            url=index_access.get_url(doc_id),
            score=score
        ) for doc_id, score in top
    ]


def prompt_loop():
    """Prompt loop: read query, call search(), print results"""
    while True:
        try:
            query = input("Search query: ")
            print()
        except EOFError:
            break

        start_time = time.perf_counter()
        results: list[SearchResult] = search(query, k = 5)
        for i, result in enumerate(results):
            # Ex: 1. https://example.com
            print(f"{i+1}. {result.url}")

        end_time = time.perf_counter()
        execution_time_ms = (end_time - start_time) * 1000
        print(f"Execution time: {execution_time_ms:.6f} ms")
        
        input()
        helpers.clear_terminal()


if __name__ == "__main__":
    print("Loading index...")
    index_access.load_index()
    helpers.clear_terminal()
    prompt_loop()