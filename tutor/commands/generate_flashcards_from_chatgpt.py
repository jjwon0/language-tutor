import json
import requests
from bs4 import BeautifulSoup

import pydantic

from tutor.llm_flashcards import (
    generate_flashcards,
    maybe_add_flashcards,
)
from tutor.utils.logging import dprint
from tutor.llm.prompts import get_generate_flashcard_from_llm_conversation_prompt


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


def generate_flashcards_from_chatgpt_inner(chatgpt_share_link: str):
    messages = scrape_chatgpt_messages(chatgpt_share_link)
    conversation_parts = []
    for m in messages:
        conversation_parts.append(f"{m.role}: {m.content}")
    conversation = "\n\n".join(conversation_parts)
    prompt = get_generate_flashcard_from_llm_conversation_prompt(conversation)
    flashcards = generate_flashcards(prompt)
    dprint(flashcards)
    print(f"Generated {len(flashcards.flashcards)} flashcards for the following words:")
    maybe_add_flashcards(flashcards, "ChatGPT")
