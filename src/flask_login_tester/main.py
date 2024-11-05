import os

import click

from .app import app
from .plex import config_instance as plex_config


@click.command()
@click.option("-d", "--debugger", is_flag=True, help="Runs the server with debugger.")
@click.option("-h", "--host", default="127.0.0.1", help="Specify the host IP address.")
@click.option("-p", "--port", default=5090, help="Specify the port to run on.")
def main(debugger, host, port):
    os.environ["FLASK_APP"] = "flask_login_tester.app"
    os.environ["FLASK_RUN_HOST"] = host
    os.environ["FLASK_RUN_PORT"] = str(port)
    plex_config.set_baseurl(server_ip="192.168.1.42", server_port="32400")
    if debugger:
        os.environ["FLASK_DEBUG"] = "1"
    app.run(host=host, port=port, debug=debugger)
