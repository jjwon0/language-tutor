import os
import yaml
from pathlib import Path
from typing import Optional


class Config:
    def __init__(self):
        self.config_path = self._get_config_path()
        self._config = self._load_config()

        # Require default_deck to be set
        if not self._config.get("default_deck"):
            raise ValueError(
                f"No default deck configured. Please set one in {self.config_path}"
            )

    def _get_config_path(self) -> Path:
        if os.name == "nt":  # Windows
            config_dir = Path(os.getenv("APPDATA")) / "chinese-tutor"
        else:  # Unix-like
            config_dir = Path.home() / ".config" / "chinese-tutor"

        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / "config.yaml"

    def _load_config(self) -> dict:
        if not self.config_path.exists():
            # Create empty config file if it doesn't exist
            self.save_config({})
            return {}

        with open(self.config_path, "r") as file:
            return yaml.safe_load(file) or {}

    def save_config(self, config: dict) -> None:
        with open(self.config_path, "w") as file:
            yaml.safe_dump(config, file, default_flow_style=False)

    @property
    def default_deck(self) -> str:
        return self._config["default_deck"]

    @default_deck.setter
    def default_deck(self, value: str) -> None:
        self._config["default_deck"] = value
        self.save_config(self._config)


# Singleton instance
_config: Optional[Config] = None


def get_config() -> Config:
    global _config
    if _config is None:
        _config = Config()
    return _config
