import yaml
import random
import pydantic

from typing import List


class ConversationTopic(pydantic.BaseModel):
    topic: str
    english_topic: str
    used: bool


def generate_topics_inner(conversation_topics_path):
    with open(conversation_topics_path) as f:
        conversation_topics: List[ConversationTopic] = []
        for item in yaml.safe_load(f):
            conversation_topics.append(ConversationTopic(**item))
    unused_cts = [ct for ct in conversation_topics if not ct.used]
    return random.choice(unused_cts)
