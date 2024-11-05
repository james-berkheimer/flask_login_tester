from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from .plex import AuthenticationError, PlexAuthentication
from .plex import config_instance as plex_config

main = Blueprint("main", __name__)
plex_auth = PlexAuthentication(config_instance=plex_config)


@main.route("/")
def home():
    if "username" in session:
        plex_auth.verify_authentication(session["token"])
        return render_template("home.html", logged_in=True, username=session["username"])
    else:
        return render_template("home.html", logged_in=False)


@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        print(f"Username: {username}, Password: {password}")

        # Call the method to fetch the token
        try:
            # Assuming you have an instance of the class with `fetch_plex_token` named `plex_auth_instance`
            token = plex_auth.fetch_plex_token(username, password)

            # Store the username and token in the session if successful
            if token:
                session.permanent = True
                session.modified = True
                session["username"] = username
                session["token"] = token
                plex_config.token = token

                flash("You were successfully logged in")
                return redirect(url_for("main.home"))

        except AuthenticationError as e:
            flash(str(e))  # Display the error message to the user

    return render_template("login.html")


@main.route("/logout")
def logout():
    session.pop("username", None)
    flash("You were successfully logged out")
    return redirect(url_for("main.home"))
