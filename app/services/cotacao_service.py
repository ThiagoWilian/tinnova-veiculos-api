import logging, httpx
from decimal import Decimal, InvalidOperation
from redis import Redis
from redis.exceptions import RedisError
from app.core.config import get_settings
from app.core.errors import CurrencyRateUnavailable
from app.core.redis import get_redis_client

logger = logging.getLogger(__name__)


class CotacaoService:
    """
    Serviço de cotação de dólar para real.
    """
    cache_key = "usd_brl"

    def __init__(self, redis_client: Redis | None = None, http_client: httpx.Client | None = None) -> None:
        self.redis_client = redis_client
        self.http_client = http_client

    def usd_brl(self) -> Decimal:
        # Verifica se o valor está em cache. 
        # Ordem de prioridade: 1° - Redis -> 2° - AwesomeAPI -> 3° - Frankfurter
        cached = self._get_cached_rate()
        if cached is not None:
            logger.info("Cotacao USD-BRL recuperada do cache (Redis): %s", cached)
            return cached

        rate = self._fetch_awesomeapi_rate()
        if rate is not None:
            logger.info("Cotacao USD-BRL recuperada da AwesomeAPI: %s", rate)
        else:
            rate = self._fetch_frankfurter_rate()
            if rate is not None:
                logger.info("Cotacao USD-BRL recuperada da Frankfurter (fallback): %s", rate)

        if rate is None:
            logger.warning("Cotacao USD-BRL indisponivel: cache vazio e ambas APIs falharam")
            raise CurrencyRateUnavailable()

        self._set_cached_rate(rate)
        return rate

    def _redis(self) -> Redis:
        if self.redis_client is None:
            self.redis_client = get_redis_client()
        return self.redis_client

    def _client(self) -> httpx.Client:
        if self.http_client is None:
            self.http_client = httpx.Client(timeout=3)
        return self.http_client

    def _get_cached_rate(self) -> Decimal | None:
        try:
            value = self._redis().get(self.cache_key)
            return Decimal(value) if value else None
        except (RedisError, InvalidOperation):
            return None

    def _set_cached_rate(self, rate: Decimal) -> None:
        try:
            settings = get_settings()
            self._redis().setex(self.cache_key, settings.cotacao_ttl_seconds, str(rate))
        except RedisError:
            return

    def _fetch_awesomeapi_rate(self) -> Decimal | None:
        try:
            response = self._client().get("https://economia.awesomeapi.com.br/json/last/USD-BRL")
            response.raise_for_status()
            data = response.json()
            return Decimal(data["USDBRL"]["bid"])
        except (httpx.HTTPError, KeyError, InvalidOperation):
            return None

    def _fetch_frankfurter_rate(self) -> Decimal | None:
        try:
            response = self._client().get("https://api.frankfurter.app/latest?from=USD&to=BRL")
            response.raise_for_status()
            data = response.json()
            return Decimal(str(data["rates"]["BRL"]))
        except (httpx.HTTPError, KeyError, InvalidOperation):
            return None


cotacao_service = CotacaoService()