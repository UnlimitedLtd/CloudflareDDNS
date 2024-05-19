"""
Interact with the Cloudflare REST API. 
For more information see https://developers.cloudflare.com/api/
"""

import logging

import requests

from src.models import DomainConfig, LookupARecordResult

logger = logging.getLogger(__name__)


class API:
    """ 
    Interact with the Cloudflare REST API. 
    For more information see https://developers.cloudflare.com/api/
    """

    def __init__(self, config: DomainConfig, timeout: int = 10, verbose: bool = False):
        if verbose:
            logger.setLevel(logging.DEBUG)

        self.domain = config.domain
        self.domain_id = config.domain_id
        self.zone_id = config.zone_id
        self.ttl = config.ttl
        self.proxied = config.proxied
        self.headers = {
            "Authorization": f"Bearer {config.api_key}"
        }
        self.endpoint = f"https://api.cloudflare.com/client/v4/zones/{
            config.zone_id}/dns_records/{config.domain_id}"
        self.timeout = timeout

    def get_a_record(self) -> str:
        """
        Get a the domain's DNS A record.

        Returns:
            str: The IP address.

        Raises:
            HTTPError: If there is a HTTP error.
        """

        response = requests.get(
            url=self.endpoint,
            headers=self.headers,
            timeout=self.timeout
        )

        logger.debug(
            "Request URL: %s, Status Code: %d",
            response.request.url,
            response.status_code,
        )

        response.raise_for_status()

        parsed = LookupARecordResult.model_validate_json(response.content)

        return parsed.result.content

    def update_a_record(self, ip: str) -> None:
        """
        Update a domain DNS A record.

        Args:
            ip: IP address to set to.

        Raises:
            HTTPError: If there is a HTTP error.
        """

        response = requests.put(
            url=self.endpoint,
            timeout=self.timeout,
            json={
                "type": "A",
                "name": self.domain,
                "content": ip,
                "ttl": self.ttl,
                "proxied": self.proxied
            },
            headers=self.headers
        )

        logger.debug(
            "Request URL: %s, Status Code: %d",
            response.request.url,
            response.status_code,
        )

        print(response.request.body)
        print(response.request.headers)

        # 200 indicates success, no need to check JSON response.
        response.raise_for_status()
