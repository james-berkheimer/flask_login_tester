import os
from datetime import timedelta

from flask import Flask
from flask_talisman import Talisman
from flask_wtf.csrf import CSRFProtect

from .routes import main

csrf = CSRFProtect()


def create_app():
    app = Flask(__name__)
    app.secret_key = os.urandom(24)

    # Security settings
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=1)  # Short lifetime for testing
    app.config["SESSION_COOKIE_SECURE"] = True  # Only send cookies over HTTPS
    app.config["SESSION_COOKIE_HTTPONLY"] = True  # Prevent JavaScript access to session cookie
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"  # Protect against CSRF attacks

    # Apply CSRF protection and secure headers directly
    csrf.init_app(app)
    # CSRFProtect(app)
    # Talisman(app)

    # Register blueprints
    app.register_blueprint(main)
    return app


app = create_app()
