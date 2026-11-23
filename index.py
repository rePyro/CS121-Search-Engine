import helpers
import os
import json
from urllib.parse import urldefrag

INDEXED_COUNT = 0
SKIPPED_DUPES = 0
SEEN_URLS = set()
INDEX = {}
DOC_DICT = {}

def index(filepath: str) -> None:
    global INDEXED_COUNT, SKIPPED_DUPES

    with open(filepath, "r", encoding="utf-8") as f:
        file_json = json.load(f)

    url, _ = urldefrag(file_json["url"]) # defrag the URL

    # if URL was already seen, increment SEEN_URLS and exit
    if url in SEEN_URLS:  
        SKIPPED_DUPES += 1
        return

    # attempt to extract word frequencies from file_json
    freqs, title, heading, emphasis = helpers.extract_word_frequency(file_json["content"])

    # after extract_word_frequency succeeds, increment INDEXED_COUNT and register to DOC_DICT
    INDEXED_COUNT += 1 
    DOC_DICT[INDEXED_COUNT] = file_json["url"]

    # for every word-freqency pair, append it to the INDEX
    for word, tf in freqs.items():
        # if word isn't in INDEX, default-initialize; append Posting data
        INDEX.setdefault(word, []).append(
            [INDEXED_COUNT, tf, title[word], heading[word], emphasis[word], 0, []]
        )



def main():
    for dirpath, dirnames, filenames in os.walk("developer"):
        dirnames.sort()
        for filename in sorted(filenames):
            path = os.path.join(dirpath, filename)
            try:
                index(path)
            except Exception as e:
                print("skipped", path, type(e).__name__, e)
    with open("index.json", "w") as f:
        json.dump(INDEX, f)
    with open("doc_dict.json", "w") as f:
        json.dump(DOC_DICT, f)
    print("docs:", INDEXED_COUNT)
    print("unique terms:", len(INDEX))
    print("index KB:", helpers.get_file_size_kb("index.json"))
    print("fragment duplicates skipped:", SKIPPED_DUPES)

if __name__ == "__main__":
  main()