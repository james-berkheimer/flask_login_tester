# src/plex_api_tester/plex/authentication.py

"""
authentication.py for Plex API Module

This module handles authentication with the Plex API, including obtaining and verifying tokens.
"""

import logging
from typing import Optional

import requests

from .. import utils
from .config import PlexConfig

logger = utils.create_logger(level=logging.INFO)


class AuthenticationError(Exception):
    """Custom exception for authentication errors."""

    pass


class PlexAuthentication:
    def __init__(self, config_instance: PlexConfig) -> None:
        """
        Initialize PlexAuthentication with a configuration instance.

        :param config_instance: Instance of PlexConfig to store token and headers.
        """
        self.config_instance = config_instance

    def fetch_plex_token(self, username: str, password: str = None, stored_token: str = None) -> str:
        """
        Retrieve the Plex auth token using provided credentials.

        :param username: Plex username.
        :param password: Plex password.
        :return: Authentication token as a string.
        :raises AuthenticationError: If authentication fails or token is not found.
        """
        if stored_token:
            self.config_instance.token = stored_token
            return True
        signin_url = self.config_instance.SIGNIN_URL
        headers = self.config_instance.get_x_plex_headers()
        data = {"user[login]": username, "user[password]": password}

        try:
            response = requests.post(
                signin_url, headers=headers, data=data, timeout=self.config_instance.TIMEOUT
            )
            response.raise_for_status()

            user_data = response.json()
            if "user" in user_data and "authToken" in user_data["user"]:
                return user_data["user"]["authToken"]
            else:
                raise AuthenticationError("Token not found in the response.")

        except requests.RequestException as e:
            logger.error(f"Failed to fetch Plex token: {e}")
            raise AuthenticationError("Authentication failed") from e

    def verify_authentication(self, token: str) -> None:
        """
        Authenticate with credentials and store token in configuration.

        :param username: Plex username.
        :param password: Plex password.
        :raises AuthenticationError: If authentication fails.
        """
        try:
            if token:
                self.config_instance.token = token
                logger.info("Authentication successful; token stored.")
        except AuthenticationError as e:
            logger.error(f"Authentication failed: {e}")
            logger.info("No valid token found; attempting to authenticate with Plex")
            raise e
