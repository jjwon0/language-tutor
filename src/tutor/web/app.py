import pathlib
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List, Optional
from ..cli_global_state import get_model

# Load environment variables
load_dotenv()


class DialogueResponse(BaseModel):
    """Response format for dialogue turns"""

    next_line_zh: str = Field(description="The next line of dialogue in Chinese")
    next_line_pinyin: Optional[str] = Field(description="Pinyin for the next line")
    next_line_en: Optional[str] = Field(
        description="English translation of the next line"
    )


class GrammarFeedback(BaseModel):
    """Feedback for a specific grammar point"""

    original: str = Field(description="Original phrase used by the student")
    correction: str = Field(description="Corrected native-like expression")
    explanation: str = Field(
        description="Explanation of why the correction is more natural"
    )
    example: str = Field(
        description="Another example using this grammar pattern correctly"
    )


class VocabItem(BaseModel):
    """Vocabulary item with context"""

    word: str = Field(description="The Chinese word or phrase")
    pinyin: str = Field(description="Pinyin pronunciation")
    meaning: str = Field(description="English meaning")
    usage_note: str = Field(description="Note about when/how to use this word")


class ConversationReview(BaseModel):
    """Review format for the entire conversation"""

    grammar_feedback: List[GrammarFeedback] = Field(
        description="Detailed grammar corrections for non-native expressions"
    )
    vocabulary_review: List[VocabItem] = Field(
        description="Key vocabulary from the conversation"
    )


def get_conversation_review(
    dialogue_history: List[dict], scenario: str
) -> ConversationReview:
    """Generate a comprehensive review of the entire conversation."""
    openai_client = OpenAI()

    # Format dialogue history for the prompt
    history_text = "\n".join(
        f"{'Tutor' if msg['role'] == 'tutor' else 'User'}: {msg['content']}"
        for msg in dialogue_history
    )

    try:
        completion = openai_client.beta.chat.completions.parse(
            model=get_model(),
            response_format=ConversationReview,
            messages=[
                {
                    "role": "system",
                    "content": "You are a Chinese language tutor focusing on helping students achieve native-like expression. Pay special attention to phrases that sound unnatural or non-native.",
                },
                {
                    "role": "user",
                    "content": f"Review this Chinese conversation practice. Scenario: {scenario}\n\nConversation:\n{history_text}",
                },
            ],
            seed=69,
        )
        return completion.choices[0].message.parsed
    except Exception as e:
        print(f"Error generating conversation review: {e}")
        return ConversationReview(
            grammar_feedback=[],
            vocabulary_review=[],
        )


def get_dialogue_response(
    user_response: str,
    dialogue_history: List[dict],
    scenario: str,
) -> DialogueResponse:
    """Generate the next dialogue response using OpenAI."""
    openai_client = OpenAI()

    # Format dialogue history for the prompt
    history_text = "\n".join(
        f"{'Tutor' if msg['role'] == 'tutor' else 'User'}: {msg['content']}"
        for msg in dialogue_history
    )

    prompt = f"""You are helping a student practice Chinese conversation. The scenario is: {scenario}.

Conversation history:
{history_text}

User's response: {user_response}

Provide the next line of dialogue naturally. Follow these rules:
1. Continue the dialogue naturally based on the scenario
2. Keep the conversation at an intermediate level
3. Focus on natural, practical dialogue
4. Keep responses concise and natural

Format your response as a JSON object with these fields:
- next_line_zh: Next line in Chinese
- next_line_pinyin: Pinyin for the next line
- next_line_en: English translation"""

    try:
        completion = openai_client.chat.completions.create(
            model=get_model(),  # Use the same model as flashcards
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful Chinese language tutor. Always respond in the exact JSON format requested.",
                },
                {"role": "user", "content": prompt},
            ],
        )
        response_json = completion.choices[0].message.content
        return DialogueResponse.model_validate_json(response_json)
    except Exception as e:
        print(f"Error generating dialogue response: {e}")
        # Return a fallback response
        return DialogueResponse(
            next_line_zh="好的，让我们继续",
            next_line_pinyin="hǎo de, ràng wǒ men jì xù",
            next_line_en="Okay, let's continue",
        )


def create_app():
    # Get the directory containing web assets
    web_dir = pathlib.Path(__file__).parent
    static_dir = web_dir / "static"

    # Create Flask app with explicit static file configuration
    app = Flask(
        __name__,
        static_folder=str(static_dir),
        static_url_path="",
        template_folder=str(static_dir),
    )
    CORS(app)

    @app.route("/")
    def serve_index():
        try:
            print("Serving index.html...")
            return app.send_static_file("index.html")
        except Exception as e:
            print(f"Error serving index.html: {e}")
            return str(e), 500

    @app.route("/api/start-dialogue", methods=["POST"])
    def start_dialogue():
        """Start a new dialogue simulation."""
        scenario = request.json.get("scenario", "restaurant")

        # Mock data for testing
        scenarios = {
            "restaurant": {
                "situation_zh": "你在一家中国餐馆",
                "situation_en": "You are in a Chinese restaurant",
                "initial_line_zh": "您好，请问想吃点什么？",
                "initial_line_pinyin": "nín hǎo, qǐng wèn xiǎng chī diǎn shén me?",
                "initial_line_en": "Hello, what would you like to eat?",
            },
            "shopping": {
                "situation_zh": "你在商场里找衣服",
                "situation_en": "You are looking for clothes in a mall",
                "initial_line_zh": "需要我帮您找什么吗？",
                "initial_line_pinyin": "xū yào wǒ bāng nín zhǎo shén me ma?",
                "initial_line_en": "Can I help you find something?",
            },
            "travel": {
                "situation_zh": "你在火车站买票",
                "situation_en": "You are buying tickets at the train station",
                "initial_line_zh": "您要去哪里？",
                "initial_line_pinyin": "nín yào qù nǎ lǐ?",
                "initial_line_en": "Where would you like to go?",
            },
            "work": {
                "situation_zh": "你在办公室和同事聊天",
                "situation_en": "You are chatting with a colleague at the office",
                "initial_line_zh": "周末有什么计划吗？",
                "initial_line_pinyin": "zhōu mò yǒu shén me jì huà ma?",
                "initial_line_en": "Do you have any plans for the weekend?",
            },
        }

        return jsonify(scenarios.get(scenario, scenarios["restaurant"]))

    @app.route("/api/respond", methods=["POST"])
    def respond_to_dialogue():
        """Process user's response and continue the dialogue."""
        user_response = request.json.get("response", "")
        history = request.json.get("history", [])
        scenario = request.json.get("scenario", "restaurant")
        response = get_dialogue_response(user_response, history, scenario)
        return jsonify(response.model_dump())

    @app.route("/api/review", methods=["POST"])
    def review_conversation():
        """Generate a comprehensive review of the conversation."""
        history = request.json.get("history", [])
        scenario = request.json.get("scenario", "restaurant")

        review = get_conversation_review(history, scenario)
        return jsonify(review.model_dump())

    return app
