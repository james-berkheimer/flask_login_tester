import os

import requests
from flask import Blueprint, flash, jsonify, redirect, render_template, request, session, url_for

from .plex import AuthenticationError, PlexAuthentication
from .plex import config_instance as plex_config

main = Blueprint("main", __name__)
plex_auth = PlexAuthentication(config_instance=plex_config)


@main.route("/config", methods=["GET", "POST"])
def config_page():
    if request.method == "POST":
        # Extract and process server IP and port from form
        server_ip = request.form.get("server_ip")
        port_number = request.form.get("port_number")

        if server_ip and port_number:
            # Save settings to session or database (as per your preference)
            # For now, just flash a message
            plex_config.set_baseurl(server_ip=server_ip, server_port=port_number)
            flash(f"Configuration updated: IP {server_ip}, Port {port_number}")
            return redirect(url_for("main.home"))

    return render_template("config.html")


@main.route("/save_settings", methods=["POST"])
def save_settings():
    server_ip = request.form.get("hostname")
    port_number = request.form.get("port")
    ssl = request.form.get("ssl") == "on"  # Checkbox value is 'on' if checked
    plex_config.set_baseurl(server_ip=server_ip, server_port=port_number)
    # Process the settings (e.g., save to a database or an in-memory store)
    # Add logic to validate or store the data as needed

    flash("Settings saved successfully!")
    return redirect(url_for("main.config"))  # Redirect back to the settings page


@main.route("/")
def home():
    if "username" in session:
        plex_auth.request_session_token(session["token"])
        username = session["username"]
        return render_template("home.html", logged_in=True, username=username)
    else:
        return render_template("home.html", logged_in=False)


@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_login = request.form["user_login"]
        password = request.form["password"]

        print(f"user_login: {user_login}, Password: {password}")

        try:
            user_id, username, user_email, token = plex_auth.fetch_plex_credentials(user_login, password)

            if token:
                session.permanent = True
                session.modified = True
                session["user_id"] = user_id
                session["username"] = username
                session["user_email"] = user_email
                session["token"] = token

                flash("You were successfully logged in")
                return redirect(url_for("main.home"))

        except AuthenticationError as e:
            flash(str(e))

    return render_template("login.html")


@main.route("/logout")
def logout():
    session.clear()
    flash("You were successfully logged out")
    return redirect(url_for("main.home"))


@main.route("/verify_server", methods=["POST"])
def verify_server():
    # Extract parameters from the request
    hostname = request.json.get("hostname")
    port = request.json.get("port")
    ssl = request.json.get("ssl", False)

    # Construct the URL for verification
    protocol = "https" if ssl else "http"
    url = f"{protocol}://{hostname}:{port}"

    try:
        response = requests.get(url, timeout=10)  # Adjust timeout as needed
        response.raise_for_status()

        # Assume server responds with JSON containing an identifier
        result = response.json()
        identifier = result.get("identifier")

        if identifier:
            return jsonify(
                {"status": "success", "message": "Server verified.", "identifier": identifier}
            ), 200
        else:
            return jsonify({"status": "error", "message": "Server did not return an identifier."}), 500

    except requests.exceptions.RequestException as e:
        return jsonify(
            {"status": "error", "message": f"Could not verify your server. Error: {str(e)}"}
        ), 500
