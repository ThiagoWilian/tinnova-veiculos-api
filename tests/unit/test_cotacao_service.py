from decimal import Decimal

import httpx
import pytest
from redis.exceptions import RedisError

from app.core.errors import CurrencyRateUnavailable
from app.services.cotacao_service import CotacaoService


class FakeRedis:
    def __init__(self, value: str | None = None) -> None:
        self.value = value
        self.saved: str | None = None

    def get(self, key: str) -> str | None:
        return self.value

    def setex(self, key: str, ttl: int, value: str) -> None:
        self.saved = value


class BrokenRedis(FakeRedis):
    def get(self, key: str) -> str | None:
        raise RedisError

    def setex(self, key: str, ttl: int, value: str) -> None:
        raise RedisError


class FakeHttpClient:
    def __init__(self, responses: list[httpx.Response]) -> None:
        self.responses = responses

    def get(self, url: str) -> httpx.Response:
        return self.responses.pop(0)


def test_cotacao_uses_cache() -> None:
    service = CotacaoService(redis_client=FakeRedis("5.25"))

    assert service.usd_brl() == Decimal("5.25")


def test_cotacao_fetches_awesomeapi_and_caches() -> None:
    redis = FakeRedis()
    client = FakeHttpClient(
        [httpx.Response(200, json={"USDBRL": {"bid": "5.10"}}, request=httpx.Request("GET", "x"))]
    )
    service = CotacaoService(redis_client=redis, http_client=client)

    assert service.usd_brl() == Decimal("5.10")
    assert redis.saved == "5.10"


def test_cotacao_uses_frankfurter_fallback() -> None:
    client = FakeHttpClient(
        [
            httpx.Response(500, request=httpx.Request("GET", "x")),
            httpx.Response(200, json={"rates": {"BRL": 5.2}}, request=httpx.Request("GET", "x")),
        ]
    )
    service = CotacaoService(redis_client=BrokenRedis(), http_client=client)

    assert service.usd_brl() == Decimal("5.2")


def test_cotacao_raises_when_all_sources_fail() -> None:
    client = FakeHttpClient(
        [
            httpx.Response(500, request=httpx.Request("GET", "x")),
            httpx.Response(500, request=httpx.Request("GET", "x")),
        ]
    )
    service = CotacaoService(redis_client=BrokenRedis(), http_client=client)

    with pytest.raises(CurrencyRateUnavailable):
        service.usd_brl()
