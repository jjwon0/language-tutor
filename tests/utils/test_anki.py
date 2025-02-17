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
from tutor.llm.models import ChineseFlashcard


@pytest.fixture
def anki_client():
    return AnkiConnectClient()


@pytest.fixture
def sample_flashcard():
    return ChineseFlashcard(
        word="你好",
        pinyin="ni hao",
        english="hello",
        sample_usage="你好，我叫小明。",
        sample_usage_english="Hello, my name is Xiao Ming.",
    )


def test_add_flashcard(anki_client, sample_flashcard):
    with patch("requests.post") as mock_post:
        # Configure the mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": 1234567890, "error": None}
        mock_post.return_value = mock_response

        result = anki_client.add_flashcard(
            "Test::Deck", sample_flashcard, "test_audio.wav"
        )

        # Verify the request was made correctly
        mock_post.assert_called_once()
        args = mock_post.call_args[1]
        data = args["data"]

        # Parse the JSON string back to a dict for assertion
        json_data = json.loads(data)

        assert json_data["action"] == AnkiAction.ADD_NOTE.value
        assert json_data["params"]["note"]["deckName"] == "Test::Deck"
        assert json_data["params"]["note"]["modelName"] == "chinese-tutor"
        assert json_data["params"]["note"]["fields"]["Chinese"] == "你好"
        assert json_data["params"]["note"]["fields"]["Pinyin"] == "ni hao"
        assert json_data["params"]["note"]["audio"][0]["filename"] == "test_audio.wav"

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
        assert first_data["params"]["note"]["fields"]["Chinese"] == "你好"
        assert first_data["params"]["note"]["fields"]["Pinyin"] == "ni hao"
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
        assert first_data["params"]["note"]["fields"]["Chinese"] == "你好"
        assert first_data["params"]["note"]["fields"]["Pinyin"] == "ni hao"
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
        assert data["params"]["note"]["fields"]["Chinese"] == "你好"
        assert data["params"]["note"]["fields"]["Pinyin"] == "ni hao"
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
