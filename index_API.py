import json
import math
from helpers import tokenize

# TODO: replace the load_index functionality with reading from disk (instead of reading from RAM)

# dictionary of word, word's posting list.
_posting_list_collection: dict[str, list[list]] = None

# dictionary of document ID, document URL
_doc_dict: dict[int, str] = {}

class Posting:
    """
    Data about a word's term frequency, as well as the position(s) it was found in the document

    doc_id: ID of the document where the word appeared in
    tf: Term frequency; how many times it showed up (total; includes all non-dropped HTML segments)
    tf_title: TF in <title> segments. Suggested +5.0 weight
    tf_heading: TF in <h1-3> segments. Suggested +3.0 weight
    tf_emphasis: TF in <h4-6>, <strong>, and <b> segments. Suggested +1.0 weight
    tf_anchor: Number of distinct linking pages whose anchor text contains the term. Calculated on index merge
    positions: Where the word was found in the document
    """
    def __init__(self, doc_id, tf, tf_title=0, tf_heading=0, tf_emphasis=0, tf_anchor=0, positions=None):
        self.doc_id      = doc_id
        self.tf          = tf
        self.tf_title    = tf_title
        self.tf_heading  = tf_heading
        self.tf_emphasis = tf_emphasis
        self.tf_anchor   = tf_anchor
        self.positions   = positions or []

    def calculateScore(self) -> float:
        tf_eff = self.tf + 5*self.tf_title + 3*self.tf_heading + 1*self.tf_emphasis
        return 1 + math.log10(tf_eff)


def load_index() -> None:
    """
    If the index and document dictionary haven't been loaded yet, load them
    """
    global _posting_list_collection, _doc_dict

    if _posting_list_collection is None:
        with open("index.json") as f:
            _posting_list_collection = json.load(f) # TODO: replace with disk reading

        with open("doc_dict.json") as f:
            file = json.load(f)
            for doc_id, doc_url in file.items():
                _doc_dict[int(doc_id)] = doc_url



def get_postings(term: str, with_positions: bool = False) -> list[Posting]:
    """
    Postings for an already-stemmed term, as Posting objects sorted ascending by doc_id
    Returns [] if the term isn't in the index
    Note: with_positions currently ignored; positions are [] until implemented
    """
    # return the term's posting list; if not found, return empty list
    return [Posting(*row) for row in _posting_list_collection.get(term, [])] # TODO: refactor



def get_df(term: str) -> int: # TODO: compute on index creation instead of on search.
    """
    Number of documents containing the term, 0 if absent
    """
    # return the length of the term's posting list; default empty list
    return len(_posting_list_collection.get(term, []))



def num_docs() -> int: # TODO: compute on index creation instead of on search.
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



def get_norm(doc_id: int) -> float: # TODO: implement norm calculation
    """
    Document length for cosine norming 
        Note: 1.0 until norms are computed
    """
    return 1.0



def get_static_score(doc_id: int) -> float: # TODO: implement score calculation
    """
    PageRank/HITS score
        Note: 0.0 until implemented
    """
    return 0.0