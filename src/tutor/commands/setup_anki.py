"""Command to set up Anki note types for Chinese Tutor."""

import click
from pathlib import Path
from tutor.utils.anki import AnkiConnectClient, AnkiAction, AnkiConnectError


@click.command()
@click.option(
    "--languages",
    "-l",
    default="mandarin,cantonese",
    help="Comma-separated list of languages to set up note types for",
)
def setup_anki(languages: str):
    """Set up Anki note types for Chinese Tutor.

    This command creates the required note types in Anki for the specified languages
    and updates existing note types with the latest templates and styling.
    By default, it processes both Mandarin and Cantonese.
    """
    # Parse languages
    language_list = [lang.strip().lower() for lang in languages.split(",")]

    # Print header
    click.secho("=== Chinese Tutor - Anki Setup ===\n", fg="green", bold=True)

    # Create Anki client
    client = AnkiConnectClient()
    note_type_manager = NoteTypeManager(client)

    # Check connection to Anki
    try:
        client.list_decks()
        click.secho("✓ Connected to Anki successfully.\n", fg="green")
    except Exception as e:
        click.secho("✗ Error connecting to Anki:", fg="red", bold=True)
        click.echo(f"  {e}")
        click.echo(
            "  Please make sure Anki is running with the AnkiConnect add-on installed."
        )
        return

    # Track success/failure for each language
    success_count = 0
    failure_count = 0

    # Process note types for each language
    for language in language_list:
        click.secho(f"Processing {language.capitalize()} note type:", bold=True)

        if language not in ["mandarin", "cantonese"]:
            click.secho(f"  ✗ Unsupported language: {language}. Skipping.", fg="yellow")
            failure_count += 1
            continue

        try:
            # Check if note type already exists
            model_name = f"chinese-tutor-{language}"
            click.echo(f"  Checking if note type '{model_name}' exists...")
            models = client.send_request(AnkiAction.MODEL_NAMES, {})

            if model_name in models:
                # Check if the note type has all the expected fields
                from tutor.llm_flashcards import get_flashcard_class_for_language

                flashcard_class = get_flashcard_class_for_language(language)

                expected_fields = flashcard_class.get_required_anki_fields()

                try:
                    note_fields = client.send_request(
                        AnkiAction.MODEL_FIELD_NAMES, {"modelName": model_name}
                    )
                    missing_fields = [
                        field for field in expected_fields if field not in note_fields
                    ]

                    if not missing_fields:
                        click.secho(
                            f"  ✓ Note type '{model_name}' already exists with all required fields.",
                            fg="green",
                        )
                        click.echo("  Updating templates and styling...")
                        # Update the styling and templates
                        css = get_card_css(language)
                        templates = get_card_templates(language)
                        client.update_card_styling_and_templates(
                            model_name=model_name, css=css, templates=templates
                        )
                        click.secho(
                            "  ✓ Templates and styling updated successfully.\n",
                            fg="green",
                        )
                        success_count += 1
                        continue
                    else:
                        click.secho(
                            f"  ✗ Note type '{model_name}' exists but is missing fields:",
                            fg="red",
                        )
                        click.echo(f"    {', '.join(missing_fields)}")
                        click.echo("  Cannot update as it's missing required fields.")
                        click.echo(
                            "  Please manually recreate this note type or fix the missing fields.\n"
                        )
                        failure_count += 1
                        continue
                except Exception as e:
                    click.secho(f"  ✗ Error checking fields: {e}", fg="red")
                    click.echo("  Attempting to update templates and styling anyway...")
                    try:
                        # Try to update the styling and templates anyway
                        css = get_card_css(language)
                        templates = get_card_templates(language)
                        client.update_card_styling_and_templates(
                            model_name=model_name, css=css, templates=templates
                        )
                        click.secho(
                            "  ✓ Templates and styling updated successfully.\n",
                            fg="green",
                        )
                        success_count += 1
                    except Exception as update_error:
                        click.secho(
                            f"  ✗ Error updating templates: {update_error}\n", fg="red"
                        )
                        failure_count += 1
                    continue

            # Create note type with templates and CSS
            click.echo(f"  Creating new note type '{model_name}'...")
            note_type_manager.create_note_type(language)
            click.secho(
                f"  ✓ Created note type '{model_name}' successfully.\n", fg="green"
            )
            success_count += 1
        except Exception as e:
            click.secho(f"  ✗ Error creating note type: {e}\n", fg="red")
            failure_count += 1

    # Print summary based on success/failure
    click.secho("=== Setup Summary ===", fg="blue", bold=True)
    if success_count > 0:
        click.secho(
            f"✓ Successfully processed {success_count} note type(s)", fg="green"
        )
    if failure_count > 0:
        click.secho(f"✗ Failed to process {failure_count} note type(s)", fg="red")

    if success_count > 0 and failure_count == 0:
        click.secho(
            "\n✓ Setup complete! You can now use Chinese Tutor to create flashcards.",
            fg="green",
            bold=True,
        )
    elif success_count > 0:
        click.secho(
            "\n⚠ Setup partially complete. Some note types were processed successfully.",
            fg="yellow",
        )
        click.echo(
            "You can use Chinese Tutor with the successfully processed languages."
        )
    else:
        click.secho(
            "\n✗ Setup failed. Please fix the errors and try again.",
            fg="red",
            bold=True,
        )


def get_card_css(language: str = "mandarin") -> str:
    """Get the CSS for the card styling based on language.

    Args:
        language: The language to get CSS for ("mandarin" or "cantonese").

    Returns:
        str: The CSS for the card styling.
    """
    base_dir = Path(__file__).parent.parent / "card_styling" / "css"

    # Common CSS files for all languages
    css_files = ["common.css", "english_front.css"]

    # Add language-specific CSS file
    if language.lower() == "mandarin":
        css_files.append("mandarin_front.css")
    elif language.lower() == "cantonese":
        css_files.append("cantonese_front.css")

    combined_css = []
    for css_file in css_files:
        try:
            with open(base_dir / css_file) as f:
                combined_css.append(f.read())
        except FileNotFoundError:
            print(f"Warning: CSS file {css_file} not found, skipping")

    return "\n\n".join(combined_css)


def get_card_templates(language: str = "mandarin") -> dict:
    """Get the templates for the card styling based on language.

    Args:
        language: The language to get templates for ("mandarin" or "cantonese").

    Returns:
        dict: The templates for the card styling.
    """
    base_dir = Path(__file__).parent.parent / "card_styling" / "templates" / language
    templates = {}

    # Load Chinese front templates
    with open(base_dir / "chinese_front_front.html") as f:
        chinese_front = f.read()
    with open(base_dir / "chinese_front_back.html") as f:
        chinese_back = f.read()
    templates["Chinese front"] = {"Front": chinese_front, "Back": chinese_back}

    # Load English front templates
    with open(base_dir / "english_front_front.html") as f:
        english_front = f.read()
    with open(base_dir / "english_front_back.html") as f:
        english_back = f.read()
    templates["English front"] = {"Front": english_front, "Back": english_back}

    return templates


class NoteTypeManager:
    """Manages the verification and creation of note types for different languages."""

    def __init__(self, client: AnkiConnectClient):
        self.client = client

    def check_note_type_exists(self, language: str) -> str:
        """Check if the note type for the given language exists in Anki.

        This does NOT create the note type if it doesn't exist.

        Args:
            language: The language to check the note type for ("mandarin" or "cantonese")

        Returns:
            The name of the note type if it exists

        Raises:
            AnkiConnectError: If the note type doesn't exist
        """
        # Determine the model name
        model_name = f"chinese-tutor-{language}"

        try:
            # Check if the model already exists
            models = self.client.send_request(AnkiAction.MODEL_NAMES, {})
            if model_name in models:
                return model_name
            else:
                raise AnkiConnectError(
                    f"Note type '{model_name}' does not exist in Anki. "
                    f"Please run the setup script to create the required note types: "
                    f"./ct setup-anki"
                )
        except Exception as e:
            if isinstance(e, AnkiConnectError):
                raise e
            raise AnkiConnectError(
                f"Failed to check if note type '{model_name}' exists",
                AnkiAction.MODEL_NAMES.value,
                str(e),
            )

    def create_note_type(self, language: str) -> str:
        """Create a note type for the given language in Anki.

        Args:
            language: The language to create the note type for ("mandarin" or "cantonese")

        Returns:
            The name of the created note type
        """
        # Get the appropriate flashcard class for this language
        from tutor.llm_flashcards import get_flashcard_class_for_language

        flashcard_class = get_flashcard_class_for_language(language)

        # Determine the model name
        model_name = f"chinese-tutor-{language}"

        try:
            # Get the field names from the flashcard class
            fields = list(flashcard_class.ANKI_FIELD_NAMES.values())
            # Add fields that aren't in the mapping
            fields.append("Sample Usage (Audio)")
            fields.append("Related Words")

            # Get the templates and CSS for this language
            templates = get_card_templates(language)
            css = get_card_css(language)

            # Create the model with both Chinese front and English front templates
            self.client.send_request(
                AnkiAction.CREATE_MODEL,
                {
                    "modelName": model_name,
                    "inOrderFields": fields,
                    "css": css,
                    "cardTemplates": [
                        {
                            "Name": "Chinese front",
                            "Front": templates["Chinese front"]["Front"],
                            "Back": templates["Chinese front"]["Back"],
                        },
                        {
                            "Name": "English front",
                            "Front": templates["English front"]["Front"],
                            "Back": templates["English front"]["Back"],
                        },
                    ],
                },
            )

            print(
                f"Created note type '{model_name}' with Chinese front and English front templates."
            )

            return model_name
        except Exception as e:
            raise AnkiConnectError(
                f"Failed to create note type for {language}",
                AnkiAction.CREATE_MODEL.value,
                str(e),
            )
