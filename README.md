# chinese-tutor

A CLI tool to help generate and manage Chinese language flashcards in Anki.

## Setup

1. **Prerequisites**
   - Install Anki and the AnkiConnect extension
   - Python with virtualenv/pyenv

2. **Installation**
   ```bash
   # Create and activate a virtualenv (using your preferred method)
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows

   # Install dependencies
   pip install -r requirements.txt
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

   Edit the config file to set your default Anki deck:
   ```yaml
   default_deck: "Your::Deck::Name"
   ```

   You can also manage configuration via CLI:
   ```bash
   # View current configuration
   ./ct config

   # Set default deck
   ./ct config "Your::Deck::Name"
   ```

4. **OpenAI Setup**
   Create a `.env` file in the project root:
   ```
   OPENAI_API_KEY=your-api-key-here
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
   pip install -r requirements-dev.txt
   ```

2. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Future Plans

- Support for other languages
- Additional customization options
- Enhanced card generation features
