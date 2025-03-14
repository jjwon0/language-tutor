import pathlib
from flask import Flask, jsonify, request
from flask_cors import CORS


def create_app():
    # Get the directory containing web assets
    web_dir = pathlib.Path(__file__).parent
    static_dir = web_dir / "static"

    print(f"Web directory: {web_dir}")
    print(f"Static directory: {static_dir}")
    print(f"Static directory exists: {static_dir.exists()}")
    if static_dir.exists():
        print(f"Static directory contents: {list(static_dir.iterdir())}")

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
        # user_response = request.json.get("response", "")

        # Mock response data for testing
        return jsonify(
            {
                "evaluation": "很好！Your response was good. You used appropriate restaurant vocabulary.",
                "correction_zh": "",
                "correction_pinyin": "",
                "next_line_zh": "好的，您还需要别的吗？",
                "next_line_pinyin": "hǎo de, nín hái xū yào bié de ma?",
                "next_line_en": "OK, would you like anything else?",
                "suggested_words": [
                    "点菜 (diǎn cài) - to order food",
                    "服务员 (fú wù yuán) - waiter/waitress",
                    "菜单 (cài dān) - menu",
                ],
            }
        )

    return app
