""" Pydantic models used across the project. """

import typing

import pydantic


class DomainConfig(pydantic.BaseModel):
    """ Model for domain config file. """

    domain: str
    domain_id: str
    zone_id: str
    api_key: str
    ttl: pydantic.PositiveInt
    proxied: bool


class _LookupARecord(pydantic.BaseModel):
    """ Model for 'result' field in _LookupARecordResult. """

    id: str
    name: str
    type: typing.Literal["A"]
    content: str


class LookupARecordResult(pydantic.BaseModel):
    """ Model for response body from Cloudlare A record lookup. """

    result: _LookupARecord


class CacheModel(pydantic.BaseModel):
    """ Model for cache file. """

    ip: str | None
    expires: int | None
