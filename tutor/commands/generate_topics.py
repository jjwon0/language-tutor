import yaml
import random
import pydantic

from typing import List


class ConversationTopic(pydantic.BaseModel):
    topic: str
    english_topic: str
    used: bool


def _load_conversation_topics(conversation_topics_path):
    with open(conversation_topics_path) as f:
        conversation_topics: List[ConversationTopic] = []
        for item in yaml.safe_load(f):
            conversation_topics.append(ConversationTopic(**item))
        return conversation_topics


_PROMPT = "Generate {num_topics} unique and engaging conversation-starters designed for an intermediate Chinese speaker. Each topic should be simple enough for someone with moderate language proficiency to discuss, avoiding region-specific or advanced subjects. Focus on universally relatable and interesting themes such as daily activities, hobbies, popular culture, basic travel experiences, food preferences, and current technology trends. Ensure that these starters are open-ended to encourage a dialogue and are not overly technical. Output this as a YAML list, with each object having the fields `topic` (in Chinese), `english_topic`, and `used` set to a default value of False. Do not output anything other than the list. Below is a list of past topics, DO NOT generate duplicate topics."


def generate_topics_prompt_inner(conversation_topics_path, num_topics):
    conversation_topics = _load_conversation_topics(conversation_topics_path)
    return (
        _PROMPT.format(num_topics=num_topics)
        + "\n"
        + "\n".join([f"- {ct.topic}" for ct in conversation_topics])
    )


def select_conversation_topic_inner(conversation_topics_path):
    conversation_topics = _load_conversation_topics(conversation_topics_path)
    unused_cts = [ct for ct in conversation_topics if not ct.used]
    return random.choice(unused_cts)
