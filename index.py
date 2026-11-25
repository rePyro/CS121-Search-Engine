import helpers
import os
import json
from urllib.parse import urldefrag
import time
import contextlib
from typing import TextIO, BinaryIO
import heapq

# merge-specific globals
FINAL_INDEX_PATH = "index_final.txt"
LEXICON_PATH     = "lexicon.json"
META_PATH        = "meta.json"

# dump-specific globals
DUMP_EVERY = 100    # every X documents parsed, dump the INDEX
LAST_DUMP_COUNT = 0 # counts how many documents parsed since last dump
PARTIAL_PATHS = []  # lists each partial file name before merge

# general globals
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
    new_file = f"partials/partial_{len(PARTIAL_PATHS)}.txt"

    # writing into newly-created new_file...
    with open(new_file, "w", encoding="utf-8", newline="\n") as file:
        # sort POSTING_LIST and extract each token-postings pair
        for token, postings in sorted(POSTING_LIST.items()):

            # json.dumps() converts list of postings into a JSON-formatted string, with spaceless separators
            postings_json = json.dumps(postings, separators=(",", ":"))
            # Writes to file, example format: "bacon\t[[1,11,1,0,0,0,[]],[2,222,0,22,2,0,[]]]\n"
            file.write(f"{token}\t{postings_json}\n")

    # track new_file in PARTIAL_PATHS, clear the POSTING_LIST, and reset LAST_DUMP_COUNT counter
    print(f"dumped {new_file} after {DUMP_EVERY} documents indexed; total of {SKIPPED_DUPE_COUNT} skipped docs so far") # NOTE: debug statement
    PARTIAL_PATHS.append(new_file)
    POSTING_LIST.clear()
    LAST_DUMP_COUNT = 0



def _extract_line_data(line: str) -> list[str]:
    return line.rstrip("\n").split("\t", 1)

def merge(partial_paths: list[str]) -> None:
    """
    Combines all partial files into a final index, creating a lexicon (index-of-the-index) for seek(). 
    * 1: Opens every file in PARTIAL_PATHS simultaneously as streams to read.
    * 2: Collects every first line into a min-heap, keyed by term with file_num as tiebreaker.
    * 3: Repeat until the min-heap is empty (meaning, every stream is exhausted) to create the final index:
        * 3a: Pop the smallest alphanumeric term on the min-heap.
        * 3b: Combines the lines that contain the term, from partial_0 to partial_n to maintain DOC_ID order.
        * 3c: Writes the combined term line to the final index.
        * 3d: Record the position of the term into the lexicon.
        * 3e: Refill min-heap with the used files' next lines.
    * 4: Save the lexicon and document count.
    """
    ## Step 1 ##
    # Note: ExitStack() manages the context managers of a variable number of files, closing them in LIFO/stack order.
    with contextlib.ExitStack() as stack:
        # list of opened files
        files: list[TextIO] = []

        # list of paths -> list of opened files set to "r"
        for path in partial_paths:
            # enter_context() returns open()'s __enter__ and adds its __exit__ to stack's own __exit__.
            files.append(
                stack.enter_context(
                    open(path, "r", encoding="utf-8")
                )
            )

        # create the final index file and lexicon
        final_index: BinaryIO = stack.enter_context(open(FINAL_INDEX_PATH, "wb"))
        offset: int = 0 # bytes written so far
        lexicon: dict[str, tuple[int, int]] = {} # term : (offset, df)

        ## Step 2 ##
        heap: list[tuple[str, int, str]] = [] # formatted as (term, file_num, postings)

        for file_num in range(len(files)):
            file = files[file_num]
            line = file.readline()
            if (line == ""): continue

            # extract term and posting list from the line
            term, postings_text = _extract_line_data(line)

            # push (add to end and bubble up) to heap
            heapq.heappush(heap, (term, file_num, postings_text))

        ## Step 3 ##
        while (heap != []):
            ## Step 3a: pop smallest term from heap ##
            smallest_term: tuple[str, int, str]       = heapq.heappop(heap)
            smallest_term_list: list[tuple[int, str]] = [(smallest_term[1], smallest_term[2])]

            ## Step 3b: combine the lines that contain the term ##
            # collect data from other partials that match the smallest_term
            while (heap != []) and (heap[0][0] == smallest_term[0]):
                smallest_term_list.append((heapq.heappop(heap))[1:])
            
            # de-JSON each postings_text and combine into a final posting list
            current_term = smallest_term[0]
            combined: list[list] = []
            for _, postings_text in smallest_term_list:
                # turn JSON-formatted postings_text into Pythonic postings
                postings: list[list] = json.loads(postings_text)

                # append each list in postings' list[list] to combined's list[list]
                combined.extend(postings)

            # record the document frequency of this posting list, for the lexicon
            df = len(combined)

            # re-JSON the Pythonic postings
            postings_json: str = json.dumps(combined, separators=(",", ":"))
            line_bytes: bytes = (f"{current_term}\t{postings_json}\n").encode("utf-8")

            ## Step 3c: write postings into the final_index ##
            final_index.write(line_bytes)
            
            ## Step 3d: create lexicon entry ##
            lexicon[current_term] = (offset, df) # term : (offset, df)
            # increment byte offset for the next term loop
            offset += len(line_bytes)

            ## Step 3e: refill the heap with the used files' next lines ##
            for file_num, _ in smallest_term_list:
                # get the next line from the used files
                line = files[file_num].readline()

                # if the file is not exhausted yet, add the next term to heap.
                if line:  
                    term, postings_text = _extract_line_data(line)
                    heapq.heappush(heap, (term, file_num, postings_text))
            
    ## Step 4 ##
    # save lexicon
    with open(LEXICON_PATH, "w", encoding="utf-8") as file:
        json.dump(lexicon, file)

    # fetch N from doc_dict.json
    with open("doc_dict.json", "r", encoding="utf-8") as file:
        n = len(json.load(file))
    # save N to meta
    with open(META_PATH, "w", encoding="utf-8") as file:
        json.dump({"N": n}, file)



def main():
    start = time.time() # NOTE: debug timer

    # walk through every directory found in the "developer" directory
    for dirpath, dirnames, filenames in os.walk("developer_mini"): # NOTE: Debug developer_mini for now. CHANGE LATER!
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
    with open("doc_dict.json", "w", encoding="utf-8") as file:
        json.dump(DOC_DICT, file)

    # create final index, alongside lexicon and document count, N, in META_PATH
    merge(PARTIAL_PATHS)

    # NOTE: debug print statements
    print("Indexing has completed! yippee! here's the debug statements")
    print("docs:", DOC_ID_COUNT)
    print("partial files:", len(PARTIAL_PATHS))
    total_kb = sum(helpers.get_file_size_kb(p) for p in PARTIAL_PATHS)
    print("partials total KB:", total_kb)
    with open(META_PATH, "r", encoding="utf-8") as file:
        print("unique terms:", json.load(file)["N"])
    print("index KB:", helpers.get_file_size_kb(FINAL_INDEX_PATH))
    print("fragment duplicates skipped:", SKIPPED_DUPE_COUNT)
    print("elapsed seconds:", int(time.time() - start))

if __name__ == "__main__":
  main()