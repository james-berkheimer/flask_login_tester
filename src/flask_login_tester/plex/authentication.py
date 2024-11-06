# src/plex_api_tester/plex/authentication.py

"""
authentication.py for Plex API Module

This module handles authentication with the Plex API, including obtaining and verifying tokens.
"""

import logging
import xml.etree.ElementTree as ET

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

    def fetch_plex_credentials(
        self, user_login: str, password: str = None, stored_token: str = None
    ) -> str:
        """
        Retrieve the Plex auth token using provided credentials.

        :param user_login: Plex username or email address.
        :param password: Plex password.
        :return: Authentication token as a string.
        :raises AuthenticationError: If authentication fails or token is not found.
        """
        if stored_token:
            self.config_instance.token = stored_token
            return True
        signin_url = "https://plex.tv/api/v2/users/signin"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        payload = f"login={user_login}&password={password}&X-Plex-Client-Identifier=PlexAPI"

        try:
            response = requests.request("POST", signin_url, data=payload, headers=headers)
            response.raise_for_status()
            parsed_response = ET.fromstring(response.content)

            token = parsed_response.get("authToken")
            user_id = parsed_response.get("id")
            username = parsed_response.get("username")
            user_email = parsed_response.get("email")
            if token:
                self.config_instance.token = token
                return user_id, username, user_email, token
            else:
                raise AuthenticationError("Token not found in the response.")

        except requests.RequestException as e:
            logger.error(f"Failed to fetch Plex credentials: {e}")
            raise AuthenticationError("Authentication failed") from e

    def request_session_token(self, token: str) -> None:
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
