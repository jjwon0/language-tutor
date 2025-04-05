# language-tutor

A CLI tool to help generate and manage language flashcards in Anki.

## Setup

1. **Prerequisites**
   - Install Anki and the AnkiConnect extension
   - Python with Poetry installed

2. **Installation**
   ```bash
   # Install dependencies
   poetry install
   ```

3. **Configuration**
   ```bash
   # Windows
   mkdir %APPDATA%\chinese-tutor
   copy config-template.yaml %APPDATA%\chinese-tutor\config.yaml

   # Unix/Mac
   mkdir -p ~/.config/chinese-tutor
   cp config-template.yaml ~/.config/chinese-tutor/config.yaml
   ```

   Edit the config file to set your configuration:
   ```yaml
   default_deck: "Your::Deck::Name"
   default_language: "mandarin"  # or "cantonese"
   learner_level: "intermediate"  # or "beginner", "advanced", etc.
   ```

   You can also manage configuration via CLI:
   ```bash
   # View current configuration
   ./ct config

   # Set default deck
   ./ct config --deck "Your::Deck::Name"

   # Set default language
   ./ct config --language "mandarin"

   # Set learner level (affects difficulty of generated content)
   ./ct config --learner-level "intermediate"

   # Set multiple options at once
   ./ct config --deck "Your::Deck::Name" --language "cantonese" --learner-level "beginner"
   ```

4. **Setup**
   Create a `.env` file in the project root:
   ```
   OPENAI_API_KEY=your-api-key-here
   AZURE_SPEECH_SERVICE_KEY=your-azure-speech-service-key
   AZURE_SPEECH_SERVICE_REGION=your-azure-speech-service-region
   ```

## Usage

Generate a flashcard for a word:
```bash
./ct g 松弛感
```

List recently challenging cards:
```bash
./ct list-lesser-known-cards
```

View all commands:
```bash
./ct --help
```

## Development

1. Install development dependencies:
   ```bash
   poetry install
   ```

2. Install pre-commit hooks:
   ```bash
   poetry run pre-commit install
   ```

## Future Plans

- Support for other languages
- Additional customization options
- Enhanced card generation features
