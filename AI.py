import asyncio
from bs4 import BeautifulSoup
from helpers import clean_soup
import os
import requests
from openai import AsyncOpenAI
from dotenv import load_dotenv
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
  print("ERROR: Missing environment variable. OPENAI_API_KEY is not defined in .env")
  import sys
  sys.exit(1)

async_client = AsyncOpenAI()


async def _get_AI_summary(page_text: str) -> str:
  page_text = page_text[:20_000] # Truncate huge pages since budget is small
  try:
      response = await async_client.responses.create(
          # Cheapest model $0.10/$0.50 input/output
          model="gpt-6-luna",
          reasoning={"effort": "none"},
          instructions="Summarize the given page content in 2-3 brief sentences, " \
          "to be displayed under each search result in my UCI ICS Search Engine.",
          input=page_text,
          # Start a new converasation with each message
          previous_response_id=None

      )
      return response.output_text
  except Exception as e:
      print(f"\nError: {e}\n")
      return "There was an error generating AI summaries. Check the console output for details."


async def get_AI_summaries(page_urls: list[str]) -> list[str]:
    pages = [
      clean_soup(BeautifulSoup(requests.get(url).content, 'lxml')).get_text(separator=" ", strip=True)
      for url in page_urls
    ]
    coroutines = [_get_AI_summary(page) for page in pages]
    return await asyncio.gather(*coroutines)
