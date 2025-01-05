import os

import click

from .app import app

# from .plex import config_instance as plex_config


@click.command()
@click.option("-d", "--debugger", is_flag=True, help="Runs the server with debugger.")
@click.option("-c", "--config", type=click.Path(exists=True), help="Path to the config file.")
@click.option("-p", "--port", type=str, help="The port to bind to.")
def main(debugger, config, port):
    os.environ["FLASK_APP"] = "flask_login_tester.app"
    if debugger:
        os.environ["FLASK_DEBUG"] = "1"
    if config:
        os.environ["FLASK_CONFIG"] = config
    if not port:
        port = 5090

    app.run(host="127.0.0.1", port=port, debug=debugger)


# https://flask.palletsprojects.com/en/stable/config/
