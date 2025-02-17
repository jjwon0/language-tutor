# chinese-tutor

make language flashcards more easily

## usage

- install Anki and AnkiConnect extension
- create the expected deck structure (see `tutor/llm_flashcards.py` and `tutor/utils/anki.py`)
- create a virtualenv and install all the requirements
- run `python main.py`, or alternatively the shell script `./ct`

example:

```
./ct g 松弛感
```

## requirements

- pyenv or other virtualenv manager

## oai keys

- add `OPENAI_API_KEY=my-api-key` to a file called `.env` at the repo root

## development setup

- create a new virtualenv
- install dependencies in the virtualenv:
    ```
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
    ```

## future

- customize Anki deck structure
- support other languages

## Configuration

Before using the tool, you need to set up your configuration:

1. Copy the template configuration file:
   ```bash
   # Windows
   mkdir %APPDATA%\chinese-tutor
   copy config-template.yaml %APPDATA%\chinese-tutor\config.yaml

   # Unix/Mac
   mkdir -p ~/.config/chinese-tutor
   cp config-template.yaml ~/.config/chinese-tutor/config.yaml
   ```

2. Edit the configuration file to set your default Anki deck:
   ```yaml
   default_deck: "Your::Deck::Name"
   ```

   You can also set/view the default deck using the CLI:
   ```bash
   # View current configuration
   ./ct config

   # Set default deck
   ./ct config "Your::Deck::Name"
   ```
