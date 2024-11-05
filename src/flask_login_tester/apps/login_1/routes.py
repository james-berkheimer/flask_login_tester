import time
import xml.etree.ElementTree as ET
from urllib.parse import urlencode

import requests
from flask import Blueprint, jsonify, redirect, render_template, request, session, url_for

main = Blueprint("main", __name__)


# @main.route("/")
# def index():
#     return "Index Page"


# @main.route("/hello")
# def hello():
#     return "Hello, World"

CLIENT_ID = "plex_app_tester"
# CLIENT_SECRET = "your_client_secret"
REDIRECT_URI = "http://localhost:5000/callback"

# Plex OAuth endpoints
PIN_URL = "https://plex.tv/api/v2/pins"
AUTH_URL = "https://app.plex.tv/auth#?clientID={client_id}&code={code}&context[device][product]=Plex%20Web&context[device][environment]=bundled&context[device][layout]=desktop&context[device][platform]=Chrome&context[device][platformVersion]=89.0&context[device][screenResolution]=1920x1080&context[device][model]=hosted&context[device][device]=Windows&context[device][deviceID]={client_id}"
USER_INFO_URL = "https://plex.tv/api/v2/user"

CODE = "gpy78iyvd1onpqbn32nr5e0gs"


@main.route("/")
def home():
    username = session.get("username")
    access_token = session.get("access_token")

    if not username and access_token:
        # Use the access token to get user info from Plex
        user_info_response = requests.get(USER_INFO_URL, headers={"X-Plex-Token": access_token})
        if user_info_response.status_code == 200:
            # Parse the XML response
            root = ET.fromstring(user_info_response.content)
            username = root.attrib.get("username")
            session["username"] = username
        else:
            # If the token is invalid or expired, clear the session
            session.pop("access_token", None)

    return render_template("home.html", username=username)


@main.route("/login")
def login():
    print("Starting Login route")
    try:
        # Request a new PIN from Plex
        response = requests.post(PIN_URL, headers={"X-Plex-Client-Identifier": CLIENT_ID})
        response.raise_for_status()  # Raise an error for bad status codes

        # Log the response content for debugging
        print(f"Login Response status code: {response.status_code}")
        print(f"Login Response content: {response.content}")

        # Parse the XML response
        root = ET.fromstring(response.content)
        pin_id = root.attrib["id"]
        pin_code = root.attrib["code"]

        # Store the PIN ID in the session
        session["pin_id"] = pin_id

        # Redirect the user to the Plex OAuth authorization URL
        auth_url = AUTH_URL.format(client_id=CLIENT_ID, code=pin_code)
        return render_template("login.html", auth_url=auth_url)
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"
    except ET.ParseError as e:
        return f"Error parsing XML: {e}"


@main.route("/auth/logout")
def logout():
    # Clear the session
    session.clear()
    # Redirect to the home page or login page
    return redirect(url_for("home"))


@main.route("/check_auth")
def check_auth():
    print("Starting check_auth route")
    pin_id = session.get("pin_id")
    if not pin_id:
        return jsonify({"status": "error", "message": "No PIN ID found in session."})

    try:
        response = requests.get(f"{PIN_URL}/{pin_id}", headers={"X-Plex-Client-Identifier": CLIENT_ID})
        response.raise_for_status()  # Raise an error for bad status codes

        # Log the response content for debugging
        print(f"Check Auth Response status code: {response.status_code}")
        print(f"Check Auth Response content: {response.content}")

        # Parse the XML response
        root = ET.fromstring(response.content)
        auth_token = root.attrib.get("authToken")
        if auth_token:
            session["access_token"] = auth_token
            return jsonify({"status": "success"})
        else:
            return jsonify({"status": "pending"})
    except requests.exceptions.RequestException as e:
        return jsonify({"status": "error", "message": str(e)})
    except ET.ParseError as e:
        return jsonify({"status": "error", "message": str(e)})


@main.route("/callback")
def callback():
    print("Starting callback route")
    pin_id = session.get("pin_id")
    if not pin_id:
        return "Error: No PIN ID found in session."

    # Poll for the PIN status
    for _ in range(10):
        try:
            response = requests.get(
                f"{PIN_URL}/{pin_id}", headers={"X-Plex-Client-Identifier": CLIENT_ID}
            )
            response.raise_for_status()  # Raise an error for bad status codes

            # Log the response content for debugging
            print(f"Response status code: {response.status_code}")
            print(f"Response content: {response.content}")

            # Parse the XML response
            root = ET.fromstring(response.content)
            auth_token = root.attrib.get("authToken")
            if auth_token:
                session["access_token"] = auth_token
                return redirect(url_for("profile"))
        except requests.exceptions.RequestException as e:
            return f"Error: {e}"
        except ET.ParseError as e:
            return f"Error parsing XML: {e}"
        time.sleep(2)

    return "Error: Authentication timed out."


@main.route("/profile")
def profile():
    print("Starting profile route")
    access_token = session.get("access_token")
    if not access_token:
        return redirect(url_for("login"))

    try:
        # Use the access token to get user info from Plex
        user_info_response = requests.get(USER_INFO_URL, headers={"X-Plex-Token": access_token})
        user_info_response.raise_for_status()  # Raise an error for bad status codes

        # Log the response content for debugging
        print(f"Profile Response status code: {user_info_response.status_code}")
        print(f"Profile Response content: {user_info_response.content}")

        # Parse the XML response
        root = ET.fromstring(user_info_response.content)
        username = root.attrib.get("username")

        return f"Logged in as: {username}"
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"
    except ET.ParseError as e:
        return f"Error parsing XML: {e}"
