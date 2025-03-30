"""Command to set up Anki note types for Chinese Tutor."""

import click
from tutor.utils.anki import AnkiConnectClient, NoteTypeManager, AnkiAction


@click.command()
@click.option(
    "--languages",
    "-l",
    default="mandarin,cantonese",
    help="Comma-separated list of languages to set up note types for",
)
def setup_anki(languages: str):
    """Set up Anki note types for Chinese Tutor.

    This command creates the required note types in Anki for the specified languages.
    By default, it creates note types for both Mandarin and Cantonese.
    """
    # Parse languages
    language_list = [lang.strip().lower() for lang in languages.split(",")]

    # Create Anki client
    client = AnkiConnectClient()
    note_type_manager = NoteTypeManager(client)

    # Check connection to Anki
    try:
        client.list_decks()
        print("Connected to Anki successfully.")
    except Exception as e:
        print(f"Error connecting to Anki: {e}")
        print("Please make sure Anki is running with the AnkiConnect add-on installed.")
        return

    # Create note types for each language
    for language in language_list:
        if language not in ["mandarin", "cantonese"]:
            print(f"Unsupported language: {language}. Skipping.")
            continue

        try:
            # Check if note type already exists
            model_name = f"chinese-tutor-{language}"
            models = client.send_request(AnkiAction.MODEL_NAMES, {})

            if model_name in models:
                # Check if the note type has all the expected fields
                from tutor.llm_flashcards import get_flashcard_class_for_language

                flashcard_class = get_flashcard_class_for_language(language)

                # Get the expected fields
                expected_fields = list(flashcard_class.ANKI_FIELD_NAMES.values())
                expected_fields.append("Sample Usage (Audio)")
                expected_fields.append("Related Words")

                # Get the actual fields
                try:
                    note_fields = client.send_request(
                        AnkiAction.MODEL_FIELD_NAMES, {"modelName": model_name}
                    )
                    missing_fields = [
                        field for field in expected_fields if field not in note_fields
                    ]

                    if not missing_fields:
                        print(
                            f"Note type '{model_name}' already exists with all required fields. Skipping."
                        )
                        continue
                    else:
                        print(
                            f"Note type '{model_name}' exists but is missing fields: {', '.join(missing_fields)}"
                        )
                        print(f"Recreating note type '{model_name}'...")

                        # Delete the existing note type
                        client.send_request(
                            AnkiAction.DELETE_MODEL, {"modelName": model_name}
                        )
                        print(f"Deleted existing note type '{model_name}'")
                except Exception as e:
                    print(f"Error checking fields for note type '{model_name}': {e}")
                    print(f"Recreating note type '{model_name}'...")

                    # Delete the existing note type
                    try:
                        client.send_request(
                            AnkiAction.DELETE_MODEL, {"modelName": model_name}
                        )
                        print(f"Deleted existing note type '{model_name}'")
                    except Exception as delete_error:
                        print(
                            f"Error deleting note type '{model_name}': {delete_error}"
                        )
                        print(f"Skipping recreation of note type '{model_name}'")
                        continue

            # Create note type
            note_type_manager.create_note_type(language)
            print(f"Created note type '{model_name}' successfully.")
        except Exception as e:
            print(f"Error creating note type for {language}: {e}")

    print("\nSetup complete. You can now use Chinese Tutor to create flashcards.")
