# import helpers

import os
import json

INDEXED_COUNT = 0

def index(filepath: str):
  global INDEXED_COUNT
  INDEXED_COUNT += 1
  with open(filepath, "r") as f:
    file_json = json.load(f)
  url = file_json["url"]
  content = file_json["content"]
  encoding = file_json["encoding"]
  # helpers.count_unique_words(content)

def main():
  for dirpath, _, filenames in os.walk("developer"):
    for filename in filenames:
      index(os.path.join(dirpath, filename))
  global INDEXED_COUNT
  print(INDEXED_COUNT)


if __name__ == "__main__":
  main()
