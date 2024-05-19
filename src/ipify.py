"""
Interact with the IPify REST API. 
For more information see https://www.ipify.org
"""

import logging

import requests

logger = logging.getLogger(__name__)


class IPify:  # pylint: disable=too-few-public-methods
    """
    Interact with the IPify REST API.
    For more information see https://www.ipify.org
    """

    _IPIFY_API_ENDPOINT = "https://api.ipify.org"

    def __init__(self, timeout: int = 10, verbose: bool = False):
        if verbose:
            logger.setLevel(logging.DEBUG)

        self.timeout = timeout

    def get_current_ip(self) -> str:
        """
        Get current IP address.

        Returns:
            str: Current IP address object.
        """

        response = requests.get(
            url=self._IPIFY_API_ENDPOINT, timeout=self.timeout)
        logger.debug(
            "Request URL: %s, Status Code: %d",
            response.request.url,
            response.status_code,
        )

        response.raise_for_status()

        return response.text
