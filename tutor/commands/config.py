import click
import sys
from tutor.utils.config import get_config


@click.command()
@click.argument("deck", required=False)
def config(deck: str = None) -> None:
    """View or set the default deck configuration.

    If DECK is provided, sets the default deck.
    If no DECK is provided, shows current configuration.
    """
    if deck:
        get_config().default_deck = deck
        click.echo(f"Default deck set to: {deck}")
    else:
        try:
            current_deck = get_config().default_deck
            click.echo(f"Current default deck: {current_deck}")
        except ValueError as e:
            click.echo(str(e), err=True)
            click.echo("Use 'config DECK' to set a default deck")
            sys.exit(1)
