import helpers
import os
import json

INDEXED_COUNT = 0
INDEX = {}
DOC_DICT = {}

def index(filepath: str):
    global INDEXED_COUNT
    with open(filepath, "r", encoding="utf-8") as f:
        file_json = json.load(f)
    freqs = helpers.extract_word_frequency(file_json["content"])
    # only claim a doc ID once the file has parsed successfully
    INDEXED_COUNT += 1
    DOC_DICT[INDEXED_COUNT] = file_json["url"]
    for word, tf in freqs.items():
        INDEX.setdefault(word, []).append([INDEXED_COUNT, tf])

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

if __name__ == "__main__":
  main()