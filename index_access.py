def get_postings(term: str) -> list[list[int]]:
    """
    Turn a tokenized term into a posting, structured [doc_id, tf], sorted ascending by doc_id
    Returns [] if the term isn't in the index
    Note: extra EC fields will be added later; use p[0] and p[1] for now
    """
    pass

def get_df(term: str) -> int:
    """
    Number of documents containing the term, 0 if absent
    """
    pass

def num_docs() -> int:
    """
    Total number of indexed documents (N)
    """
    pass

def get_url(doc_id: int) -> str:
    """
    URL for a doc_id
    """
    pass