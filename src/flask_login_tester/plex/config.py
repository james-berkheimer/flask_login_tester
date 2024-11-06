# src/plex_api_tester/plex/config.py
"""
config.py for Plex API Module

This module sets up and manages configuration settings required for interacting with the Plex API.
"""

import re
from typing import Optional


class PlexConfig:
    """
    Manages configuration settings for Plex API access, including server URLs, tokens, and headers.
    """

    def __init__(self) -> None:
        self._baseurl: Optional[str] = None
        self._token: Optional[str] = None

    @property
    def baseurl(self) -> Optional[str]:
        """Get the base URL for the Plex server."""
        return self._baseurl

    def set_baseurl(self, server_ip: str, server_port: int) -> None:
        """
        Set the base URL for the Plex server.

        :param server_ip: IP address of the Plex server.
        :param server_port: Port number for the Plex server.
        :raises ValueError: If server_ip or server_port is empty.
        """
        if not server_ip or not server_port:
            raise ValueError("Server IP and port must be provided.")

        server_ip = re.sub(r"^https?://", "", server_ip)

        self._baseurl = f"http://{server_ip}:{server_port}"

    @property
    def token(self) -> Optional[str]:
        """Get the authentication token."""
        return self._token

    @token.setter
    def token(self, token: Optional[str]) -> None:
        """
        Set the authentication token.

        :param token: Plex authentication token.
        """
        self._token = token
