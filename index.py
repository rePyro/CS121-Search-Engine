import helpers
import os
import json
from urllib.parse import urldefrag
import time

DUMP_EVERY = 10000  # every X documents parsed, dump the INDEX
LAST_DUMP_COUNT = 0 # counts how many documents parsed since last dump
PARTIAL_FILES = []  # lists each partial file name before merge for debug purposes

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

    # after extract_word_frequency succeeds, increment DOC_ID_COUNT and register to DOC_DICT and SEEN_URLS
    DOC_ID_COUNT += 1 
    DOC_DICT[DOC_ID_COUNT] = file_json[url]
    SEEN_URLS.add(url)

    # for every word-freqency pair, append it to the POSTING_LIST
    for word, tf in freqs.items():
        # if word isn't in POSTING_LIST, default-initialize; append Posting data
        POSTING_LIST.setdefault(word, []).append(
            [DOC_ID_COUNT, tf, title[word], heading[word], emphasis[word], 0, []]
        )



def main():
    start = time.time() # debug timer

    # walk through every directory found in the "developer" directory
    for dirpath, dirnames, filenames in os.walk("developer"):
        # sort any sub-directories and files for index order consistency
        dirnames.sort() 
        filenames.sort()

        # for every file, create its full Path and attempt to index it
        for filename in filenames:
            path = os.path.join(dirpath, filename)
            try:
                index(path)
            except Exception as e:
                print("ERROR indexing file: ", path, type(e).__name__, e)

    # TODO: implement write to disk
    with open("index.json", "w") as f:
        json.dump(POSTING_LIST, f)

    # dump DOC_DICT to doc_dict.json
    with open("doc_dict.json", "w") as f:
        json.dump(DOC_DICT, f)

    # debug print statements
    print("Indexing has completed! yippee! here's the debug statements")
    print("docs:", DOC_ID_COUNT)
    print("partial files:", len(PARTIAL_FILES))
    total_kb = sum(helpers.get_file_size_kb(p) for p in PARTIAL_FILES)
    print("partials total KB:", total_kb)
    # print("unique terms:", len(POSTING_LIST))
    # print("index KB:", helpers.get_file_size_kb("index.json"))
    print("fragment duplicates skipped:", SKIPPED_DUPE_COUNT)
    print("elapsed seconds:", int(time.time() - start))

if __name__ == "__main__":
  main()