import json
import requests
from bs4 import BeautifulSoup

import pydantic

from tutor.utils import logging
from tutor.llm_flashcards import (
    generate_flashcards,
    maybe_add_flashcards,
)
from tutor.utils.logging import dprint


def toposort(graph):
    visited = {k: False for k in graph}
    result = []

    def DFS(node):
        if visited[node]:
            return
        visited[node] = True
        for c in graph[node]["children"]:
            DFS(c)
        result.append(node)

    for k in graph:
        DFS(k)

    return result


class ChatGPTMessage(pydantic.BaseModel):
    create_time: float
    role: str
    content: str


def scrape_chatgpt_messages(share_link):
    try:
        response = requests.get(share_link)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching the webpage: {e}")

    soup = BeautifulSoup(response.content, "html.parser")
    nextjs_data = soup.find("script", id="__NEXT_DATA__").get_text()
    jsondata = json.loads(nextjs_data)
    mapping = jsondata["props"]["pageProps"]["serverResponse"]["data"]["mapping"]

    sortedkeys = toposort(mapping)
    sortedvalues = [mapping[k] for k in sortedkeys][::-1]

    messages = []
    for v in sortedvalues:
        # for some reason there are messages with blank parts like ['']
        if v.get("message") and v["message"]["content"]["parts"] != [""]:
            messages.append(
                ChatGPTMessage(
                    create_time=v["message"]["create_time"],
                    role=v["message"]["author"]["role"],
                    content=v["message"]["content"]["parts"][0],
                )
            )

    return messages


_PROMPT_TMPL = """Below the line is a conversation between a language learner and a LLM assistant in Chinese. Identify and extract key vocabulary and grammar phrases from the LLM's responses, ignoring proper nouns. For each identified item, generate a flashcard that includes the following information:

- Word/Phrase in Simplified Chinese: Extract the word or phrase from the article.
- Pinyin: Provide the Pinyin transliteration of the Chinese word or phrase.
- English Translation: Translate the word or phrase into English.
- Sample Usage in Chinese: Create or find a sentence from the article (or construct a new one) that uses the word or phrase in context.
- Sample Usage in English: Translate the sample usage sentence into English, ensuring that it reflects the usage of the word or phrase in context.

For each flashcard, focus on clarity and practical usage, ensuring the information is useful for an intermediate Chinese speaker looking to improve vocabulary and understanding of grammar.
--
{text}
"""


def generate_flashcards_from_chatgpt_inner(chatgpt_share_link, debug):
    logging._DEBUG = debug
    messages = scrape_chatgpt_messages(chatgpt_share_link)
    conversation_parts = []
    for m in messages:
        conversation_parts.append(f"{m.role}: {m.content}")
    conversation = "\n\n".join(conversation_parts)
    prompt = _PROMPT_TMPL.format(text=conversation)
    flashcards = generate_flashcards(prompt)
    dprint(flashcards)
    print(f"Generated {len(flashcards.flashcards)} flashcards for the following words:")
    maybe_add_flashcards(flashcards, "ChatGPT")
