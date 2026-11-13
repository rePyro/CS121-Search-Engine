import helpers
import os
import json

INDEXED_COUNT = 0
INDEX = {}
DOC_MAP = {}

def index(filepath: str):
    global INDEXED_COUNT
    INDEXED_COUNT += 1
    with open(filepath, "r") as f:
        file_json = json.load(f)
    DOC_MAP[INDEXED_COUNT] = file_json["url"]
    content = file_json["content"]
    for word, tf in helpers.extract_word_frequency(content).items():
        INDEX.setdefault(word, []).append([INDEXED_COUNT, tf])

def main():
    for dirpath, dirnames, filenames in os.walk("developer"):
        dirnames.sort()
        for filename in sorted(filenames):
            index(os.path.join(dirpath, filename))
    with open("index.json", "w") as f:
        json.dump(INDEX, f)
    with open("doc_map.json", "w", encoding="utf-8") as f:
        json.dump(DOC_MAP, f)
    print("docs:", INDEXED_COUNT)
    print("unique terms:", len(INDEX))
    print("index KB:", helpers.get_file_size_kb("index.json"))

if __name__ == "__main__":
  main()