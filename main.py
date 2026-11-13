import helpers
import os
import json

INDEXED_COUNT = 0
INDEX = {}

def index(filepath: str):
    global INDEXED_COUNT
    INDEXED_COUNT += 1
    with open(filepath, "r") as f:
        file_json = json.load(f)
    # url = file_json["url"]
    content = file_json["content"]
    # encoding = file_json["encoding"]
    for word in helpers.get_unique_words(content):
        INDEX.setdefault(word, []).append(INDEXED_COUNT)

def main():
    for dirpath, _, filenames in os.walk("developer"):
        for filename in filenames:
            index(os.path.join(dirpath, filename))
    with open("index.txt", "w") as f:
        json.dump(INDEX, f)
    print(INDEXED_COUNT)
    print(len(INDEX))
    print(helpers.get_file_size_kb("index.txt"))


if __name__ == "__main__":
  main()