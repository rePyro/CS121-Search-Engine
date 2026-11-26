import json
import math
from helpers import tokenize
from typing import BinaryIO

# INDEX_PATH's opened stream in binary mode
INDEX_FILE: BinaryIO = None
# dictionary of term : (offset, document frequency)
LEXICON: dict[str, tuple[int, int]] = None
# dictionary of document ID : document URL
DOC_DICT: dict[int, str] = {}
# int of document count
DOC_COUNT: int = 0

# Weights
TITLE_WEIGHT = 5.0
HEADING_WEIGHT = 3.0
EMPHASIS_WEIGHT = 1.0

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

    def _calculateTF(self) -> float:
        """
        Calculate term frequency based on the given weights
        """
        tf_eff = self.tf + (TITLE_WEIGHT*self.tf_title) + (HEADING_WEIGHT*self.tf_heading) + (EMPHASIS_WEIGHT*self.tf_emphasis)
        if tf_eff <= 0:
            return 0.0 # avoid log10(0)
        return 1 + math.log10(tf_eff)

    @staticmethod
    def _calculateIDF(df: int, N: int) -> float:
        """
        Inverse document frequency: log10(N / df)
        df: number of documents containing the term
        N: total number of documents
        """
        if df <= 0:
            return 0.0 # term not in index
        return math.log10(N / df)

    def calculateScore(self, df: int, N: int) -> float:
        """
        tf-idf score of this posting's term in this posting's document
        """
        return self._calculateTF() * Posting._calculateIDF(df, N)


def load_index() -> None:
    """
    If the lexicon, doc. dictionary, doc. count, and index stream haven't been loaded yet, load them
    """
    global INDEX_FILE, LEXICON, DOC_DICT, DOC_COUNT

    if LEXICON is None:
        with open("lexicon.json", "r", encoding="utf-8") as file:
            LEXICON = json.load(file)

        # json.load() loads as dict[str, str]; need to convert to dict[int, str]
        with open("doc_dict.json", "r", encoding="utf-8") as file:
            dd_strings = json.load(file)
            for doc_id, doc_url in dd_strings.items():
                DOC_DICT[int(doc_id)] = doc_url

        with open("doc_count.json", "r", encoding="utf-8") as file:
            DOC_COUNT = json.load(file)["N"]

        INDEX_FILE = open("index_final.txt", "rb")




def get_postings(term: str, with_positions: bool = False) -> list[Posting]:
    """
    Postings for an already-stemmed term, as Posting objects sorted by doc_id, ascending
    Returns [] if the term isn't in the index
    Note: with_positions currently ignored; positions are [] until implemented
    """
    # (offset, df)
    lexicon_term: tuple[int, int] | None = LEXICON.get(term)

    if lexicon_term == None:
        return []

    # move stream to correct offset and pull the line data up until "\n" byte
    offset = lexicon_term[0]
    INDEX_FILE.seek(offset)
    line: str = INDEX_FILE.readline().decode("utf-8").rstrip("\n")

    # split line into term, postings_text
    _, postings_text = line.split("\t", 1)
    # convert postings_text from str to list[list[data]]
    raw_postings = json.loads(postings_text)

    # convert raw postings (list[list[data]]) to class postings (list[Posting])
    class_postings = []
    for raw_posting in raw_postings:
        class_posting = Posting(*raw_posting)
        class_postings.append(class_posting)

    return class_postings



def get_df(term: str) -> int:
    """
    Number of documents containing the term, 0 if absent
    """
    lexicon_term: tuple[int, int] | None = LEXICON.get(term)
    
    if lexicon_term is None:
        return 0

    return lexicon_term[1]



def num_docs() -> int:
    """
    Total number of indexed documents (N)
    """
    return DOC_COUNT



def get_url(doc_id: int) -> str:
    """
    URL for a doc_id
    """
    # return the URL in the value section of the document dictionary
    return DOC_DICT[doc_id]



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