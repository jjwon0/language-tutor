import click
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


@click.command()
@click.option(
    "--conversation-topics-path",
    type=str,
    help="Path to data file with past topics",
    default="data/conversation_topics.yaml",
)
@click.option(
    "--num-topics",
    type=int,
    help="Number of new topics to generate",
    default=10,
)
def generate_topics_prompt(conversation_topics_path: str, num_topics: int) -> None:
    """Prints a prompt to pass to ChatGPT to get new conversation topics."""
    result = _generate_topics_prompt_impl(conversation_topics_path, num_topics)
    click.echo(result)


def _generate_topics_prompt_impl(conversation_topics_path: str, num_topics: int) -> str:
    """Implementation of generate_topics_prompt command.

    Args:
        conversation_topics_path: Path to YAML file with existing topics
        num_topics: Number of new topics to generate

    Returns:
        Formatted prompt for generating new conversation topics
    """
    conversation_topics = _load_conversation_topics(conversation_topics_path)
    return (
        _PROMPT.format(num_topics=num_topics)
        + "\n"
        + "\n".join([f"- {ct.topic}" for ct in conversation_topics])
    )


@click.command()
@click.option(
    "--conversation-topics-path",
    type=str,
    help="Path to data file with past topics",
    default="data/conversation_topics.yaml",
)
def select_conversation_topic(conversation_topics_path: str) -> None:
    """Selects a random conversation topic from a file on disk."""
    result = _select_conversation_topic_impl(conversation_topics_path)
    click.echo(f"{result.topic} ({result.english_topic})")


def _select_conversation_topic_impl(conversation_topics_path: str) -> ConversationTopic:
    """Implementation of select_conversation_topic command.

    Args:
        conversation_topics_path: Path to YAML file with existing topics

    Returns:
        A randomly selected conversation topic
    """
    conversation_topics = _load_conversation_topics(conversation_topics_path)
    unused_cts = [ct for ct in conversation_topics if not ct.used]
    if not unused_cts:
        # If all topics have been used, just select from all topics
        unused_cts = conversation_topics
    return random.choice(unused_cts)
