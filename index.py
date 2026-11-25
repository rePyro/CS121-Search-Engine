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
    # global, to save reassignment across runtime (mutators/accessors don't need global)
    global DOC_ID_COUNT, SKIPPED_DUPE_COUNT, LAST_DUMP_COUNT

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

    # after extract_word_frequency succeeds, increment DOC_ID_COUNT + LAST_DUMP_COUNT and register to DOC_DICT and SEEN_URLS
    DOC_ID_COUNT += 1 
    LAST_DUMP_COUNT += 1
    DOC_DICT[DOC_ID_COUNT] = url
    SEEN_URLS.add(url)

    # for every word-freqency pair, append it to the POSTING_LIST
    for word, tf in freqs.items():
        # if word isn't in POSTING_LIST, default-initialize; append Posting data
        POSTING_LIST.setdefault(word, []).append(
            [DOC_ID_COUNT, tf, title[word], heading[word], emphasis[word], 0, []]
        )



def dump() -> None:
    # global, to save reassignment across runtime
    global LAST_DUMP_COUNT

    # if "partials" directory doesn't exist, make one.
    os.makedirs("partials", exist_ok=True)
    # new file's name is "partials/partial_#.txt". where # is the number, starting from 0. 
    new_file = f"partials/partial_{len(PARTIAL_FILES)}.txt"

    # writing into newly-created new_file...
    with open(new_file, "w", encoding="utf-8", newline="\n") as f:
        # sort POSTING_LIST and extract each token-postings pair
        for token, postings in sorted(POSTING_LIST.items()):

            # json.dumps() converts list of postings into a JSON-formatted string, with spaceless separators
            postings_json = json.dumps(postings, separators=(",", ":"))
            # Writes to file, example format: "bacon\t[[1,11,1,0,0,0,[]],[2,222,0,22,2,0,[]]]\n"
            f.write(f"{token}\t{postings_json}\n")

    # track new_file in PARTIAL_FILES, clear the POSTING_LIST, and reset LAST_DUMP_COUNT counter
    PARTIAL_FILES.append(new_file)
    POSTING_LIST.clear()
    LAST_DUMP_COUNT = 0



def main():
    start = time.time() # debug timer

    # walk through every directory found in the "developer" directory
    for dirpath, dirnames, filenames in os.walk("developer_mini"): # TODO: Debug developer_mini for now. CHANGE LATER!
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

            # dump to a partial file every DUMP_EVERY successfully-indexed files
            if (LAST_DUMP_COUNT >= DUMP_EVERY): 
                dump()

    # dump remaining items in POSTING_LIST, if there are any
    if (POSTING_LIST):
        dump()

    # dump DOC_DICT to doc_dict.json
    with open("doc_dict.json", "w", encoding="utf-8") as f:
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