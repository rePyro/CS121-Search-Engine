import helpers
import os
import json
from urllib.parse import urldefrag

DUMP_EVERY = 10000  # every X documents parsed, dump the INDEX
LAST_DUMP_COUNT = 0 # counts how many documents parsed since last dump

DOC_ID_COUNT = 0       # counts how many documents were parsed for ID purposes
SKIPPED_DUPE_COUNT = 0 # counts how many documents were already in SEEN_URLS 
SEEN_URLS = set()      # tracks all seen documents (defragged first)
POSTING_LIST = {}      # tracks each document's Posting data
DOC_DICT = {}          # tracks each document's ID and URL as a pair

def index(filepath: str) -> None:
    global DOC_ID_COUNT, SKIPPED_DUPE_COUNT

    with open(filepath, "r", encoding="utf-8") as f:
        file_json = json.load(f)

    # defrag the URL
    url, _ = urldefrag(file_json["url"]) 

    # if URL was already seen, increment SKIPPED_DUPE_COUNT and exit
    if url in SEEN_URLS:  
        SKIPPED_DUPE_COUNT += 1
        return

    # attempt to extract word frequencies from file_json
    freqs, title, heading, emphasis = helpers.extract_word_frequency(file_json["content"])

    # after extract_word_frequency succeeds, increment DOC_ID_COUNT and register to DOC_DICT
    DOC_ID_COUNT += 1 
    DOC_DICT[DOC_ID_COUNT] = file_json["url"]

    # for every word-freqency pair, append it to the POSTING_LIST
    for word, tf in freqs.items():
        # if word isn't in POSTING_LIST, default-initialize; append Posting data
        POSTING_LIST.setdefault(word, []).append(
            [DOC_ID_COUNT, tf, title[word], heading[word], emphasis[word], 0, []]
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
        json.dump(POSTING_LIST, f)
    with open("doc_dict.json", "w") as f:
        json.dump(DOC_DICT, f)
    print("docs:", DOC_ID_COUNT)
    print("unique terms:", len(POSTING_LIST))
    print("index KB:", helpers.get_file_size_kb("index.json"))
    print("fragment duplicates skipped:", SKIPPED_DUPE_COUNT)

if __name__ == "__main__":
  main()