import pytest
from unittest.mock import patch, Mock
from pathlib import Path
import json

from tutor.utils.anki import (
    AnkiConnectClient,
    AnkiAction,
    get_subdeck,
    get_default_anki_media_dir,
)
from tutor.llm.models import MandarinFlashcard


@pytest.fixture
def anki_client():
    # Use a non-existent server address to prevent accidental connections to real Anki
    # This ensures tests won't modify production data
    return AnkiConnectClient(address="http://non-existent-anki-test-server:9999")


@pytest.fixture
def sample_flashcard():
    return MandarinFlashcard(
        word="你好",
        pinyin="ni hao",
        english="hello",
        sample_usage="你好，我叫小明。",
        sample_usage_english="Hello, my name is Xiao Ming.",
        related_words=[],
    )


def test_add_flashcard(anki_client, sample_flashcard):
    # Mock the NoteTypeManager.check_note_type_exists method to return a model name
    with patch(
        "tutor.commands.setup_anki.NoteTypeManager.check_note_type_exists"
    ) as mock_check:
        # Configure the mock to return the model name
        mock_check.return_value = "chinese-tutor-mandarin"

        with patch("requests.post") as mock_post:
            # Configure the mock responses for different API calls
            def mock_response_handler(*args, **kwargs):
                data = json.loads(kwargs["data"])
                action = data["action"]

                mock_response = Mock()
                mock_response.status_code = 200

                if action == "deckNames":
                    # Return empty list for deck names
                    mock_response.json.return_value = {"result": [], "error": None}
                elif action == "createDeck":
                    # Return deck ID for deck creation
                    mock_response.json.return_value = {"result": 12345, "error": None}
                elif action == "addNote":
                    # Return note ID for note creation
                    mock_response.json.return_value = {
                        "result": 1234567890,
                        "error": None,
                    }
                else:
                    # Default response
                    mock_response.json.return_value = {"result": None, "error": None}

                return mock_response

            mock_post.side_effect = mock_response_handler

            result = anki_client.add_flashcard(
                "Test::Deck", sample_flashcard, "test_audio.wav"
            )

        # Verify the result is the expected note ID
        assert result == 1234567890

        # Verify the addNote request was made with correct parameters
        # Find the addNote call
        add_note_call = None
        for call in mock_post.call_args_list:
            args = call[1]
            data = json.loads(args["data"])
            if data["action"] == "addNote":
                add_note_call = data
                break

        assert add_note_call is not None

        assert add_note_call["action"] == AnkiAction.ADD_NOTE.value
        assert add_note_call["params"]["note"]["deckName"] == "Test::Deck"
        assert add_note_call["params"]["note"]["modelName"] == "chinese-tutor-mandarin"

        # Use the actual field names from the flashcard's ANKI_FIELD_NAMES mapping
        word_field = sample_flashcard.ANKI_FIELD_NAMES["word"]
        pinyin_field = sample_flashcard.ANKI_FIELD_NAMES["pinyin"]

        assert add_note_call["params"]["note"]["fields"][word_field] == "你好"
        assert add_note_call["params"]["note"]["fields"][pinyin_field] == "ni hao"
        assert (
            add_note_call["params"]["note"]["audio"][0]["filename"] == "test_audio.wav"
        )

        assert result == 1234567890


def test_update_flashcard(anki_client, sample_flashcard):
    with patch("requests.post") as mock_post:
        # Configure the mock response for both calls
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": None, "error": None}
        mock_post.return_value = mock_response

        anki_client.update_flashcard(1234567890, sample_flashcard, "test_audio.wav")

        # Verify both calls were made with correct data
        assert mock_post.call_count == 2
        calls = mock_post.call_args_list

        # First call should be updateNoteFields without audio
        first_call = calls[0][1]
        first_data = json.loads(first_call["data"])
        assert first_data["action"] == AnkiAction.UPDATE_NOTE_FIELDS.value
        assert first_data["params"]["note"]["id"] == 1234567890

        # Use the actual field names from the flashcard's ANKI_FIELD_NAMES mapping
        word_field = sample_flashcard.ANKI_FIELD_NAMES["word"]
        pinyin_field = sample_flashcard.ANKI_FIELD_NAMES["pinyin"]

        assert first_data["params"]["note"]["fields"][word_field] == "你好"
        assert first_data["params"]["note"]["fields"][pinyin_field] == "ni hao"
        assert first_data["params"]["note"]["fields"]["Sample Usage (Audio)"] == ""
        assert "audio" not in first_data["params"]["note"]

        # Second call should be updateNoteFields with audio
        second_call = calls[1][1]
        second_data = json.loads(second_call["data"])
        assert second_data["action"] == AnkiAction.UPDATE_NOTE_FIELDS.value
        assert second_data["params"]["note"]["id"] == 1234567890

        # Use the same field names as in the first call
        assert second_data["params"]["note"]["fields"][word_field] == "你好"
        assert second_data["params"]["note"]["fields"][pinyin_field] == "ni hao"
        assert "audio" in second_data["params"]["note"]
        assert second_data["params"]["note"]["audio"][0]["filename"] == "test_audio.wav"


def test_update_flashcard_with_audio(anki_client, sample_flashcard):
    with patch("requests.post") as mock_post:
        # Configure the mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": None, "error": None}
        mock_post.return_value = mock_response

        anki_client.update_flashcard(1234567890, sample_flashcard, "test_audio.wav")

        # Verify both calls were made with correct data
        assert mock_post.call_count == 2
        calls = mock_post.call_args_list

        # First call should be updateNoteFields without audio
        first_call = calls[0][1]
        first_data = json.loads(first_call["data"])
        assert first_data["action"] == AnkiAction.UPDATE_NOTE_FIELDS.value
        assert first_data["params"]["note"]["id"] == 1234567890

        # Use the actual field names from the flashcard's ANKI_FIELD_NAMES mapping
        word_field = sample_flashcard.ANKI_FIELD_NAMES["word"]
        pinyin_field = sample_flashcard.ANKI_FIELD_NAMES["pinyin"]

        assert first_data["params"]["note"]["fields"][word_field] == "你好"
        assert first_data["params"]["note"]["fields"][pinyin_field] == "ni hao"
        assert first_data["params"]["note"]["fields"]["Sample Usage (Audio)"] == ""
        assert "audio" not in first_data["params"]["note"]

        # Second call should be updateNoteFields with audio
        second_call = calls[1][1]
        second_data = json.loads(second_call["data"])
        assert second_data["action"] == AnkiAction.UPDATE_NOTE_FIELDS.value
        assert second_data["params"]["note"]["id"] == 1234567890
        assert second_data["params"]["note"]["fields"]["Chinese"] == "你好"
        assert second_data["params"]["note"]["fields"]["Pinyin"] == "ni hao"
        assert "audio" in second_data["params"]["note"]
        assert second_data["params"]["note"]["audio"][0]["filename"] == "test_audio.wav"


def test_update_flashcard_without_audio(anki_client, sample_flashcard):
    with patch("requests.post") as mock_post:
        # Configure the mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": None, "error": None}
        mock_post.return_value = mock_response

        anki_client.update_flashcard(1234567890, sample_flashcard)

        # Verify only one call was made
        mock_post.assert_called_once()
        call = mock_post.call_args[1]
        data = json.loads(call["data"])

        # Verify the call data
        assert data["action"] == AnkiAction.UPDATE_NOTE_FIELDS.value
        assert data["params"]["note"]["id"] == 1234567890

        # Use the actual field names from the flashcard's ANKI_FIELD_NAMES mapping
        word_field = sample_flashcard.ANKI_FIELD_NAMES["word"]
        pinyin_field = sample_flashcard.ANKI_FIELD_NAMES["pinyin"]

        assert data["params"]["note"]["fields"][word_field] == "你好"
        assert data["params"]["note"]["fields"][pinyin_field] == "ni hao"
        assert "Sample Usage (Audio)" not in data["params"]["note"]["fields"]
        assert "audio" not in data["params"]["note"]


def test_find_notes(anki_client):
    with patch("requests.post") as mock_post:
        # Configure the mock responses
        find_response = Mock()
        find_response.status_code = 200
        find_response.json.return_value = {"result": [1234567890], "error": None}

        info_response = Mock()
        info_response.status_code = 200
        info_response.json.return_value = {
            "result": [
                {
                    "noteId": 1234567890,
                    "fields": {
                        "Chinese": {"value": "你好"},
                        "Pinyin": {"value": "ni hao"},
                        "English": {"value": "hello"},
                        "Sample Usage": {"value": "你好，我叫小明。"},
                        "Sample Usage (English)": {
                            "value": "Hello, my name is Xiao Ming."
                        },
                    },
                }
            ],
            "error": None,
        }

        mock_post.side_effect = [find_response, info_response]

        notes = anki_client.find_notes('deck:"Test::Deck" Chinese:你好')

        assert len(notes) == 1
        assert notes[0].word == "你好"
        assert notes[0].pinyin == "ni hao"
        assert notes[0].anki_note_id == 1234567890


def test_anki_connection_error(anki_client):
    with patch("requests.post") as mock_post:
        mock_post.side_effect = ConnectionError("Failed to connect to Anki")

        with pytest.raises(Exception) as exc_info:
            anki_client.find_notes('deck:"Test::Deck"')

        assert "Failed to connect to Anki" in str(exc_info.value)


def test_anki_error_response(anki_client):
    with patch("requests.post") as mock_post:
        # Configure the mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": None, "error": "Invalid deck name"}
        mock_post.return_value = mock_response

        with pytest.raises(Exception) as exc_info:
            anki_client.find_notes('deck:"Invalid::Deck"')

        assert "Invalid deck name" in str(exc_info.value)


def test_list_decks(anki_client):
    with patch("requests.post") as mock_post:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": ["Default", "Chinese::HSK1"],
            "error": None,
        }
        mock_post.return_value = mock_response

        decks = anki_client.list_decks()

        assert decks == ["Default", "Chinese::HSK1"]
        mock_post.assert_called_once()


def test_add_deck(anki_client):
    with patch("requests.post") as mock_post:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": 1234567890, "error": None}
        mock_post.return_value = mock_response

        anki_client.add_deck("Chinese::HSK1")

        mock_post.assert_called_once()
        args = mock_post.call_args[1]
        data = json.loads(args["data"])
        assert data["action"] == AnkiAction.CREATE_DECK.value
        assert data["params"]["deck"] == "Chinese::HSK1"


def test_maybe_add_deck_existing(anki_client):
    with patch("requests.post") as mock_post:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": ["Default", "Chinese::HSK1"],
            "error": None,
        }
        mock_post.return_value = mock_response

        anki_client.maybe_add_deck("Default")

        # Should only call list_decks, not create_deck
        assert mock_post.call_count == 1


def test_maybe_add_deck_new(anki_client):
    with patch("requests.post") as mock_post:
        list_response = Mock()
        list_response.status_code = 200
        list_response.json.return_value = {"result": ["Default"], "error": None}

        create_response = Mock()
        create_response.status_code = 200
        create_response.json.return_value = {"result": 1234567890, "error": None}

        mock_post.side_effect = [list_response, create_response]

        anki_client.maybe_add_deck("Chinese::HSK1")

        assert mock_post.call_count == 2


def test_get_subdeck():
    result = get_subdeck("Chinese", "HSK1")
    assert result == "Chinese::HSK1"


def test_invalid_action_type(anki_client):
    with pytest.raises(ValueError) as exc_info:
        anki_client.send_request("invalid_action")
    assert "Invalid action type" in str(exc_info.value)


@pytest.mark.parametrize(
    "system,expected_path",
    [
        ("Windows", "AppData/Roaming/Anki2/User 1/collection.media"),
        ("Darwin", "Library/Application Support/Anki2/User 1/collection.media"),
        ("Linux", ".local/share/Anki2/User 1/collection.media"),
    ],
)
def test_get_default_anki_media_dir(system, expected_path):
    with patch("platform.system", return_value=system):
        with patch("pathlib.Path.home", return_value=Path("/home/user")):
            result = get_default_anki_media_dir()
            assert str(result).endswith(expected_path)


def test_get_default_anki_media_dir_unsupported():
    with patch("platform.system", return_value="Unsupported"):
        with pytest.raises(NotImplementedError) as exc_info:
            get_default_anki_media_dir()
        assert "Unsupported operating system" in str(exc_info.value)


def test_update_model_styling(anki_client):
    with patch("requests.post") as mock_post:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": None, "error": None}
        mock_post.return_value = mock_response

        model_name = "test-model"
        css = ".card { font-size: 20px; }"

        anki_client.update_model_styling(model_name, css)

        mock_post.assert_called_once()
        args = mock_post.call_args[1]
        data = json.loads(args["data"])
        assert data["action"] == AnkiAction.UPDATE_MODEL_STYLING.value
        assert data["params"]["model"]["name"] == model_name
        assert data["params"]["model"]["css"] == css


def test_update_model_templates(anki_client):
    with patch("requests.post") as mock_post:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": None, "error": None}
        mock_post.return_value = mock_response

        model_name = "test-model"
        templates = {
            "Card 1": {
                "Front": "<div>{{Front}}</div>",
                "Back": "<div>{{Front}}<hr>{{Back}}</div>",
            }
        }

        anki_client.update_model_templates(model_name, templates)

        mock_post.assert_called_once()
        args = mock_post.call_args[1]
        data = json.loads(args["data"])
        assert data["action"] == AnkiAction.UPDATE_MODEL_TEMPLATES.value
        assert data["params"]["model"]["name"] == model_name
        assert data["params"]["model"]["templates"] == templates


def test_update_card_styling_and_templates(anki_client):
    with patch("requests.post") as mock_post:
        # Configure the mock responses for both API calls
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": None, "error": None}
        mock_post.return_value = mock_response

        # Test data
        model_name = "test-model"
        css = ".card { font-size: 20px; }"
        templates = {
            "Card 1": {
                "Front": "<div>{{Front}}</div>",
                "Back": "<div>{{Front}}<hr>{{Back}}</div>",
            }
        }

        # Call the method
        anki_client.update_card_styling_and_templates(
            model_name=model_name, css=css, templates=templates
        )

        # Verify both API calls were made correctly
        assert mock_post.call_count == 2
        calls = mock_post.call_args_list

        # First call should be updateModelStyling
        first_call = calls[0][1]
        first_data = json.loads(first_call["data"])
        assert first_data["action"] == AnkiAction.UPDATE_MODEL_STYLING.value
        assert first_data["params"]["model"]["name"] == model_name
        assert first_data["params"]["model"]["css"] == css

        # Second call should be updateModelTemplates
        second_call = calls[1][1]
        second_data = json.loads(second_call["data"])
        assert second_data["action"] == AnkiAction.UPDATE_MODEL_TEMPLATES.value
        assert second_data["params"]["model"]["name"] == model_name
        assert second_data["params"]["model"]["templates"] == templates
