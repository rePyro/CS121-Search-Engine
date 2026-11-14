import json

# TODO: replace the load_index functionality with reading from disk (instead of reading from RAM)

# dictionary of word, word's posting list. Posting is a list of ints.
_posting_list_collection: dict[str, list[list[int]]] = None

# dictionary of document ID, document URL
_doc_dict: dict[int, str] = {}

def load_index() -> None:
    """
    If the index and document dictionary haven't been loaded yet, load them.
    """
    global _posting_list_collection, _doc_dict

    if _posting_list_collection is None:
        with open("index.json") as f:
            _posting_list_collection = json.load(f) # TODO: replace with disk reading

        with open("doc_dict.json") as f:
            file = json.load(f)
            for doc_id, doc_url in file.items():
                _doc_dict[int(doc_id)] = doc_url

def get_postings(term: str) -> list[list[int]]:
    """
    Turn a tokenized term into a posting, structured [doc_id, tf], sorted ascending by doc_id
    Returns [] if the term isn't in the index
    Note: extra EC fields will be added later; use p[0] and p[1] for now
    """
    # return the term's posting list; if not found, return empty list
    return _posting_list_collection.get(term, [])

def get_df(term: str) -> int:
    """
    Number of documents containing the term, 0 if absent
    """
    # return the length of the term's posting list; default empty list
    return len(_posting_list_collection.get(term, []))

def num_docs() -> int:
    """
    Total number of indexed documents (N)
    """
    # return the length of the document dictionary
    return len(_doc_dict)

def get_url(doc_id: int) -> str:
    """
    URL for a doc_id
    """
    # return the URL in the value section of the document dictionary
    return _doc_dict[doc_id]


