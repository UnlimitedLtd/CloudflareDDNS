""" Pydantic models used across the project """

from datetime import datetime, timedelta, timezone
import pathlib
import logging

from src.models import CacheModel

logger = logging.getLogger(__name__)

_LOG_TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


class Cache:
    """ Class for handling caching of IP addresses """

    def __init__(self, path: str, expiry_minutes: int = 60, verbose: bool = False):
        if verbose:
            logger.setLevel(logging.DEBUG)

        self.path: pathlib.Path = None
        self.expiry = expiry_minutes

        if path:
            self.path = self._init_cache(path)

    def _init_cache(self, path: str) -> pathlib.Path:
        """
        Setup cache if path supplied but file does not exist.

        Args:
            path: Path to cache file.

        Returns:
            pathlib.Path: The cache path.
        """

        resolved = pathlib.Path(path).resolve()

        if resolved.is_file():
            return resolved

        new_cache = CacheModel.model_validate(
            {
                "ip": None,
                "expires": None
            }
        )

        resolved.write_text(new_cache.model_dump_json(), encoding="utf-8")

        return resolved

    def _time_now(self) -> datetime:
        """
        Get a UTC datetime object time now.

        Returns:
            A UTC datetime object.
        """

        return datetime.now(tz=timezone.utc)

    def _epoch_to_string(self, epoch: int) -> str:
        """
        Convert an epoch to a string in the format '%Y-%m-%dT%H:%M:%SZ'.

        Args:
            epoch: The time to convert.
        """

        return datetime.fromtimestamp(epoch, tz=timezone.utc).strftime(_LOG_TIME_FORMAT)

    def _datetime_to_string(self, obj: datetime) -> str:
        """
        Convert a datetime object to a string in the format '%Y-%m-%dT%H:%M:%SZ'.

        Args:
            obj: The datetime object to convert.
        """

        return obj.strftime(_LOG_TIME_FORMAT)

    def get_ip(self) -> str | None:
        """
        Get the IP address from the cache.

        Returns:
            An IP address if the cached value is valid.
        """

        if not self.path:
            return None

        data = self.path.read_text(encoding="utf-8")
        cache = CacheModel.model_validate_json(data)

        if not (cache.ip and cache.expires):
            return None

        if cache.expires < int(self._time_now().timestamp()):
            return None

        debug_str = f"Found record cache {cache.ip}|{
            self._epoch_to_string(cache.expires)}"
        logger.debug(debug_str)

        return cache.ip

    def set_ip(self, ip: str) -> None:
        """
        Set a new cache.

        Args:
            ip: The IP to set.
        """

        if self.path:
            expires = self._time_now() + timedelta(minutes=self.expiry)

            cache = CacheModel.model_validate(
                {
                    "ip": ip,
                    "expires": int(expires.timestamp())
                }
            )

            self.path.write_text(cache.model_dump_json(), encoding="utf-8")

            debug_str = f"Written record cache {ip}|{
                self._datetime_to_string(expires)}"
            logger.debug(debug_str)
