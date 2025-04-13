"""
Checks current machine IP address with and updates DNS A record accordingly.
"""

import argparse
import logging
import pathlib

from src import cloudflare
from src import ipify
from src import cache


def _parse_config(arg: str) -> cloudflare.DomainConfig:
    config_path = pathlib.Path(arg).resolve(strict=True)
    config_data = config_path.read_text(encoding="utf-8")
    return cloudflare.DomainConfig.model_validate_json(config_data)


parser = argparse.ArgumentParser(
    description="Check current domain A record and update if necessary."
)
parser.add_argument(
    "domain_config", help="Domain config path", type=_parse_config)
parser.add_argument("--cache", help="Cache path", type=str, default=None)
parser.add_argument(
    "--cache-expiry", help="Expiry in minutes for cache", type=int, default=60)
parser.add_argument("--timeout", help="Network timeout",
                    type=int, default=10)
parser.add_argument("-v", "--verbose", help="Verbose", action="store_true")
args = parser.parse_args()


logging.basicConfig(
    format="%(asctime)s:%(levelname)s:%(message)s",
    level=logging.INFO,
    datefmt="[%Y-%m-%dT%H:%M:%S]"
)

logger = logging.getLogger(__name__)

if args.verbose:
    logger.setLevel(logging.DEBUG)

domain_cache = cache.Cache(args.cache, args.cache_expiry, verbose=args.verbose)

ipify_connector = ipify.IPify(
    timeout=args.timeout,
    verbose=args.verbose
)

cloudflare_connector = cloudflare.API(
    config=args.domain_config, timeout=args.timeout, verbose=args.verbose)

current_ip = ipify_connector.get_current_ip()

logger.debug("Current Public IP: %s", current_ip)

record_ip = domain_cache.get_ip()

if not record_ip:
    record_ip = cloudflare_connector.get_a_record()
    domain_cache.set_ip(record_ip)

logger.debug("DNS A Record IP: %s", record_ip)

if current_ip != record_ip:
    logger.debug("Updating DNS A record to %s", current_ip)
    cloudflare_connector.update_a_record(current_ip)
    domain_cache.set_ip(current_ip)
else:
    logger.debug("No update required")
