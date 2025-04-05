import click
from ..web.app import create_app


@click.command()
@click.option("--port", default=5001, help="Port to run the web server on")
@click.option("--debug", is_flag=True, help="Run in debug mode")
def run_web(port, debug):
    """Run the web-based dialogue practice interface."""
    app = create_app()
    app.run(port=port, debug=debug)
