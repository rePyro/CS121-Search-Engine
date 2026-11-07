import helpers

import os
import json

INDEXED_COUNT = 0

def index(filepath: str):
  INDEXED_COUNT += 1
  file_json = json.load(filepath)
  url = file_json["url"]
  content = file_json["content"]
  encoding = file_json["encoding"]
  helpers.count_unique_words(content)

def main():
  for dirpath, _, filenames in os.walk("developer"):
    for filename in filenames:
      index(os.path.join(dirpath, filename))


if __name__ == "__main__":
  pass
