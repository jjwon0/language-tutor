from enum import Enum
import json
from pathlib import Path
import platform
from typing import Dict, List, Optional

import requests

from tutor.llm.models import LanguageFlashcard


class AnkiConnectError(Exception):
    """Base exception for AnkiConnect-related errors."""

    def __init__(
        self,
        message: str,
        action: Optional[str] = None,
        response: Optional[Dict] = None,
    ):
        self.message = message
        self.action = action
        self.response = response
        super().__init__(self.full_message)

    @property
    def full_message(self) -> str:
        msg = self.message
        if self.action:
            msg += f" (action: {self.action})"
        if self.response:
            msg += f": {json.dumps(self.response)}"
        return msg


class AnkiAction(Enum):
    ADD_NOTE = "addNote"
    NOTES_INFO = "notesInfo"
    FIND_NOTES = "findNotes"
    DECK_NAMES = "deckNames"
    CREATE_DECK = "createDeck"
    UPDATE_NOTE_FIELDS = "updateNoteFields"
    MODEL_TEMPLATES = "modelTemplates"
    MODEL_STYLING = "modelStyling"
    UPDATE_MODEL_TEMPLATES = "updateModelTemplates"
    UPDATE_MODEL_STYLING = "updateModelStyling"
    NOTE_FIELDS = "notesInfo"  # Used to get fields for a single note
    MODEL_NAMES = "modelNames"  # Get all model names
    CREATE_MODEL = "createModel"  # Create a new model
    MODEL_FIELD_NAMES = "modelFieldNames"  # Get field names for a model
    DELETE_MODEL = "deleteModelAndNotes"  # Delete a model and its notes


class AnkiConnectClient:
    def __init__(self, address="http://localhost:8765"):
        self.address = address
        self.headers = {"Content-Type": "application/json"}

    def send_request(self, action: AnkiAction, params: Optional[Dict] = None) -> Dict:
        """Send a request to AnkiConnect and return the response."""
        if not isinstance(action, AnkiAction):
            raise ValueError("Invalid action type")

        try:
            payload = json.dumps(
                {"action": action.value, "version": 6, "params": params or {}}
            )
            response = requests.post(self.address, data=payload, headers=self.headers)

            if response.status_code != 200:
                raise AnkiConnectError(
                    f"Request failed with status {response.status_code}", action.value
                )

            result = response.json()
            if "error" in result and result["error"]:
                raise AnkiConnectError(result["error"], action.value, result)

            return result.get("result")
        except requests.exceptions.ConnectionError:
            raise AnkiConnectError(
                "Failed to connect to Anki. Is it running with AnkiConnect?",
                action.value,
            )
        except json.JSONDecodeError:
            raise AnkiConnectError(
                "Invalid JSON response from AnkiConnect", action.value
            )

    def get_note_details(self, note_ids: List[int]) -> List[LanguageFlashcard]:
        """Get detailed information about notes by their IDs."""
        try:
            note_details = self.send_request(AnkiAction.NOTES_INFO, {"notes": note_ids})
            return [LanguageFlashcard.from_anki_json(nd) for nd in note_details]
        except AnkiConnectError as e:
            raise AnkiConnectError(
                f"Failed to get note details for IDs: {note_ids}", e.action, e.response
            )

    def find_note_ids(self, query: str) -> List[int]:
        """Search for notes by query (e.g., deck name or tags)."""
        try:
            return self.send_request(AnkiAction.FIND_NOTES, {"query": query})
        except AnkiConnectError as e:
            raise AnkiConnectError(
                f"Failed to find notes with query: {query}", e.action, e.response
            )

    def find_notes(self, query: str) -> List[LanguageFlashcard]:
        """Search for and fetch notes by query."""
        try:
            note_ids = self.find_note_ids(query)
            return self.get_note_details(note_ids)
        except AnkiConnectError as e:
            raise AnkiConnectError(
                f"Failed to find and fetch notes with query: {query}",
                e.action,
                e.response,
            )

    def add_flashcard(
        self,
        deck_name,
        flashcard: LanguageFlashcard,
        sample_usage_audio_filepath=None,
        word_audio_filepath=None,
    ):
        """Add a new flashcard and return its note ID.

        Args:
            deck_name: The name of the deck to add the flashcard to
            flashcard: The flashcard to add (MandarinFlashcard or CantoneseFlashcard)
            sample_usage_audio_filepath: Path to the audio file for the sample usage
            word_audio_filepath: Path to the audio file for the word itself

        Returns:
            The note ID of the added flashcard
        """
        try:
            # Check if the note type exists for this language
            from tutor.commands.setup_anki import NoteTypeManager

            note_type_manager = NoteTypeManager(self)
            model_name = note_type_manager.check_note_type_exists(flashcard.LANGUAGE)

            # Get the fields required by this flashcard type
            fields = {}
            for field_name, anki_field_name in flashcard.ANKI_FIELD_NAMES.items():
                # Skip fields that don't exist on this flashcard
                if hasattr(flashcard, field_name):
                    value = getattr(flashcard, field_name)
                    fields[anki_field_name] = value

            # Handle related words specially - this is not in ANKI_FIELD_NAMES mapping
            if hasattr(flashcard, "related_words") and flashcard.related_words:
                # Format each related word as a bullet point
                related_words_text = []
                for rw in flashcard.related_words:
                    # Format: word (pronunciation) - english [relationship]
                    pronunciation_field = (
                        "pinyin" if flashcard.LANGUAGE == "mandarin" else "jyutping"
                    )
                    pronunciation = getattr(rw, pronunciation_field)
                    related_words_text.append(
                        f"• {rw.word} ({pronunciation}) - {rw.english} [{rw.relationship}]"
                    )

                fields["Related Words"] = "\n".join(related_words_text)

            note = {
                "deckName": deck_name,
                "modelName": model_name,
                "fields": fields,
                "tags": [],
            }

            # Add audio attachments if provided
            audio_attachments = []

            if sample_usage_audio_filepath:
                audio_attachments.append(
                    {
                        "path": sample_usage_audio_filepath,
                        "filename": sample_usage_audio_filepath,
                        "fields": ["Sample Usage (Audio)"],
                    }
                )

            if word_audio_filepath:
                audio_attachments.append(
                    {
                        "path": word_audio_filepath,
                        "filename": word_audio_filepath,
                        "fields": ["Word (Audio)"],
                    }
                )

            if audio_attachments:
                note["audio"] = audio_attachments

            note_id = self.send_request(AnkiAction.ADD_NOTE, {"note": note})
            if not note_id:
                raise AnkiConnectError(
                    f"Failed to add note for '{flashcard.word}' - no note ID returned",
                    AnkiAction.ADD_NOTE.value,
                )
            return note_id
        except AnkiConnectError as e:
            raise AnkiConnectError(
                f"Failed to add flashcard for '{flashcard.word}':", e.action, e.response
            )

    def update_model_styling(self, model_name: str, css: str) -> None:
        """Update the CSS styling for a model.

        Args:
            model_name: Name of the model to update styling for
            css: The new CSS styling
        """
        try:
            self.send_request(
                AnkiAction.UPDATE_MODEL_STYLING,
                {"model": {"name": model_name, "css": css}},
            )
        except Exception as e:
            raise AnkiConnectError(
                f"Failed to update styling for model '{model_name}'.",
                AnkiAction.UPDATE_MODEL_STYLING,
                e,
            )

    def update_model_templates(self, model_name: str, templates: Dict) -> None:
        """Update the templates for a model.

        Args:
            model_name: Name of the model to update templates for
            templates: Dict containing the new templates
        """
        try:
            self.send_request(
                AnkiAction.UPDATE_MODEL_TEMPLATES,
                {"model": {"name": model_name, "templates": templates}},
            )
        except Exception as e:
            raise AnkiConnectError(
                f"Failed to update templates for model '{model_name}'.",
                AnkiAction.UPDATE_MODEL_TEMPLATES,
                e,
            )

    def get_note_fields(self, note_id: int) -> Dict[str, str]:
        """Get the fields of a note by its ID.

        Args:
            note_id: ID of the note to get fields for

        Returns:
            Dict mapping field names to their values
        """
        try:
            result = self.send_request(AnkiAction.NOTE_FIELDS, {"notes": [note_id]})
            if not result or not isinstance(result, list) or len(result) != 1:
                raise AnkiConnectError(
                    f"Invalid response format for note ID {note_id}",
                    AnkiAction.NOTE_FIELDS.value,
                    result,
                )
            # Anki returns fields as {"fieldName": {"value": "content", "order": N}}
            # Transform to simple {"fieldName": "content"} format
            fields = result[0]["fields"]
            return {name: info["value"] for name, info in fields.items()}
        except AnkiConnectError as e:
            raise AnkiConnectError(
                f"Failed to get fields for note ID {note_id}", e.action, e.response
            )

    def update_card_styling_and_templates(
        self, model_name: str, css: str, templates: Dict
    ) -> None:
        """Update the card styling and templates for the specified model.

        Args:
            model_name: The name of the model to update.
            css: The CSS styling to apply.
            templates: The templates to apply.
        """
        # Update CSS
        self.update_model_styling(model_name, css)

        # Update templates
        self.update_model_templates(model_name, templates)

    def get_model_styling(self, model_name: str) -> Dict:
        """Get the CSS styling for a model.

        Args:
            model_name: Name of the model to get styling for

        Returns:
            Dict containing the model's CSS styling
        """
        try:
            return self.send_request(
                AnkiAction.MODEL_STYLING, {"modelName": model_name}
            )
        except Exception as e:
            raise AnkiConnectError(
                f"Failed to get styling for model '{model_name}'.",
                AnkiAction.MODEL_STYLING,
                e,
            )

    def get_model_templates(self, model_name: str) -> Dict:
        """Get the templates (styling, front, back) for a model.

        Args:
            model_name: Name of the model to get templates for

        Returns:
            Dict containing the model's templates
        """
        try:
            return self.send_request(
                AnkiAction.MODEL_TEMPLATES, {"modelName": model_name}
            )
        except Exception as e:
            raise AnkiConnectError(
                f"Failed to get templates for model '{model_name}'.",
                AnkiAction.MODEL_TEMPLATES,
                e,
            )

    def update_flashcard(
        self,
        note_id: int,
        flashcard: LanguageFlashcard,
        audio_filepath: Optional[str] = None,
    ) -> None:
        """Update an existing flashcard.

        Args:
            note_id: The ID of the note to update
            flashcard: The updated flashcard data
            audio_filepath: Optional path to the audio file for the sample usage
        """
        try:
            # Prepare fields based on the flashcard's ANKI_FIELD_NAMES mapping
            fields = {}
            for field_name, anki_field_name in flashcard.ANKI_FIELD_NAMES.items():
                # Skip fields that don't exist on this flashcard
                if hasattr(flashcard, field_name):
                    value = getattr(flashcard, field_name)
                    fields[anki_field_name] = value

            # Handle related words specially - this is not in ANKI_FIELD_NAMES mapping
            if hasattr(flashcard, "related_words") and flashcard.related_words:
                # Format each related word as a bullet point
                related_words_text = []
                for rw in flashcard.related_words:
                    # Format: word (pronunciation) - english [relationship]
                    pronunciation_field = (
                        "pinyin" if flashcard.LANGUAGE == "mandarin" else "jyutping"
                    )
                    pronunciation = getattr(rw, pronunciation_field)
                    related_words_text.append(
                        f"• {rw.word} ({pronunciation}) - {rw.english} [{rw.relationship}]"
                    )

                fields["Related Words"] = "\n".join(related_words_text)

            payload = {
                "note": {
                    "id": note_id,
                    "fields": fields,
                }
            }

            if audio_filepath:
                # Clear the audio field first
                payload["note"]["fields"]["Sample Usage (Audio)"] = ""
                self.send_request(AnkiAction.UPDATE_NOTE_FIELDS, payload)

                # Then update with new audio
                payload["note"]["audio"] = [
                    {
                        "path": audio_filepath,
                        "filename": audio_filepath,
                        "fields": ["Sample Usage (Audio)"],
                    }
                ]

            self.send_request(AnkiAction.UPDATE_NOTE_FIELDS, payload)
        except AnkiConnectError as e:
            raise AnkiConnectError(
                f"Failed to update flashcard '{flashcard.word}' (note ID: {note_id})",
                e.action,
                e.response,
            )

    def list_decks(self) -> List[str]:
        """List all available deck names."""
        try:
            return self.send_request(AnkiAction.DECK_NAMES)
        except AnkiConnectError as e:
            raise AnkiConnectError("Failed to list decks", e.action, e.response)

    def add_deck(self, deck_name: str) -> None:
        """Create a new deck."""
        try:
            self.send_request(AnkiAction.CREATE_DECK, {"deck": deck_name})
        except AnkiConnectError as e:
            raise AnkiConnectError(
                f"Failed to create deck: {deck_name}", e.action, e.response
            )

    def maybe_add_deck(self, deck_name: str) -> None:
        """Create a deck if it doesn't exist."""
        try:
            decks = self.list_decks()
            if deck_name not in decks:
                self.add_deck(deck_name)
        except AnkiConnectError as e:
            raise AnkiConnectError(
                f"Failed to create/verify deck: {deck_name}", e.action, e.response
            )


def get_subdeck(base_deck_name: str, subdeck_name: str):
    return f"{base_deck_name}::{subdeck_name}"


# Note: The NoteTypeManager class has been moved to tutor/commands/setup_anki.py


def get_default_anki_media_dir() -> Path:
    """Returns the default Anki media directory path based on the operating system."""
    system = platform.system()
    home = Path.home()

    if system == "Windows":
        return home / "AppData/Roaming/Anki2/User 1/collection.media"
    elif system == "Darwin":  # macOS
        return home / "Library/Application Support/Anki2/User 1/collection.media"
    elif system == "Linux":
        return home / ".local/share/Anki2/User 1/collection.media"
    else:
        raise NotImplementedError(f"Unsupported operating system: {system}")
