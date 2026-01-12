"""
Rate Limiter para el SEO Crawler.

Este módulo controla la velocidad de requests por dominio para evitar
sobrecargar los servidores y respetar las políticas de crawling.
"""

import asyncio
import time
from typing import Dict
from urllib.parse import urlparse
import logging

logger = logging.getLogger('SEOCrawler.RateLimiter')


class RateLimiter:
    """Rate limiter por dominio con soporte para crawl delay."""

    def __init__(self, default_delay: float = 1.0):
        """
        Inicializa el rate limiter.

        Args:
            default_delay: Delay por defecto entre requests en segundos
        """
        self.default_delay = default_delay
        self.domain_delays: Dict[str, float] = {}
        self.last_request_time: Dict[str, float] = {}
        self.locks: Dict[str, asyncio.Lock] = {}

    def _get_domain(self, url: str) -> str:
        """
        Extrae el dominio de una URL.

        Args:
            url: URL

        Returns:
            Dominio
        """
        return urlparse(url).netloc

    def set_domain_delay(self, domain: str, delay: float) -> None:
        """
        Establece un delay personalizado para un dominio.

        Args:
            domain: Dominio
            delay: Delay en segundos
        """
        self.domain_delays[domain] = delay
        logger.info(f"Delay personalizado para {domain}: {delay}s")

    def get_domain_delay(self, domain: str) -> float:
        """
        Obtiene el delay configurado para un dominio.

        Args:
            domain: Dominio

        Returns:
            Delay en segundos
        """
        return self.domain_delays.get(domain, self.default_delay)

    def _get_lock(self, domain: str) -> asyncio.Lock:
        """
        Obtiene o crea un lock para un dominio.

        Args:
            domain: Dominio

        Returns:
            Lock asyncio para el dominio
        """
        if domain not in self.locks:
            self.locks[domain] = asyncio.Lock()
        return self.locks[domain]

    async def acquire(self, url: str) -> None:
        """
        Adquiere permiso para hacer un request a una URL.
        Espera el tiempo necesario según el rate limit del dominio.

        Args:
            url: URL a la que se hará el request
        """
        domain = self._get_domain(url)
        lock = self._get_lock(domain)

        async with lock:
            delay = self.get_domain_delay(domain)
            current_time = time.time()

            if domain in self.last_request_time:
                elapsed = current_time - self.last_request_time[domain]
                wait_time = delay - elapsed

                if wait_time > 0:
                    logger.debug(f"Esperando {wait_time:.2f}s antes de request a {domain}")
                    await asyncio.sleep(wait_time)

            self.last_request_time[domain] = time.time()

    async def wait_if_needed(self, url: str) -> float:
        """
        Espera si es necesario para respetar el rate limit.
        Retorna el tiempo que esperó.

        Args:
            url: URL a la que se hará el request

        Returns:
            Tiempo esperado en segundos
        """
        domain = self._get_domain(url)
        lock = self._get_lock(domain)

        async with lock:
            delay = self.get_domain_delay(domain)
            current_time = time.time()
            waited_time = 0.0

            if domain in self.last_request_time:
                elapsed = current_time - self.last_request_time[domain]
                wait_time = delay - elapsed

                if wait_time > 0:
                    logger.debug(f"Rate limit: esperando {wait_time:.2f}s para {domain}")
                    await asyncio.sleep(wait_time)
                    waited_time = wait_time

            self.last_request_time[domain] = time.time()
            return waited_time

    def reset_domain(self, domain: str) -> None:
        """
        Resetea el rate limit de un dominio específico.

        Args:
            domain: Dominio a resetear
        """
        if domain in self.last_request_time:
            del self.last_request_time[domain]
        logger.debug(f"Rate limit reseteado para {domain}")

    def reset_all(self) -> None:
        """Resetea todos los rate limits."""
        self.last_request_time.clear()
        logger.info("Todos los rate limits reseteados")

    def get_stats(self) -> Dict[str, Dict[str, any]]:
        """
        Obtiene estadísticas de rate limiting.

        Returns:
            Diccionario con stats por dominio
        """
        stats = {}
        current_time = time.time()

        for domain in self.last_request_time:
            elapsed = current_time - self.last_request_time[domain]
            delay = self.get_domain_delay(domain)

            stats[domain] = {
                'delay': delay,
                'last_request': self.last_request_time[domain],
                'seconds_since_last': round(elapsed, 2),
                'can_request': elapsed >= delay
            }

        return stats


class TokenBucketRateLimiter:
    """
    Rate limiter basado en Token Bucket para control más granular.
    Permite ráfagas controladas de requests.
    """

    def __init__(self, rate: float = 1.0, capacity: int = 10):
        """
        Inicializa el token bucket rate limiter.

        Args:
            rate: Tokens generados por segundo
            capacity: Capacidad máxima del bucket
        """
        self.rate = rate
        self.capacity = capacity
        self.buckets: Dict[str, Dict] = {}
        self.locks: Dict[str, asyncio.Lock] = {}

    def _get_domain(self, url: str) -> str:
        """Extrae el dominio de una URL."""
        return urlparse(url).netloc

    def _get_lock(self, domain: str) -> asyncio.Lock:
        """Obtiene o crea un lock para un dominio."""
        if domain not in self.locks:
            self.locks[domain] = asyncio.Lock()
        return self.locks[domain]

    def _get_bucket(self, domain: str) -> Dict:
        """Obtiene o crea un bucket para un dominio."""
        if domain not in self.buckets:
            self.buckets[domain] = {
                'tokens': self.capacity,
                'last_update': time.time()
            }
        return self.buckets[domain]

    def _refill_bucket(self, bucket: Dict) -> None:
        """Rellena el bucket con tokens basado en el tiempo transcurrido."""
        current_time = time.time()
        elapsed = current_time - bucket['last_update']

        # Calcular tokens a añadir
        tokens_to_add = elapsed * self.rate
        bucket['tokens'] = min(self.capacity, bucket['tokens'] + tokens_to_add)
        bucket['last_update'] = current_time

    async def acquire(self, url: str, tokens: int = 1) -> None:
        """
        Adquiere tokens del bucket. Espera si no hay suficientes tokens.

        Args:
            url: URL a la que se hará el request
            tokens: Número de tokens a consumir
        """
        domain = self._get_domain(url)
        lock = self._get_lock(domain)

        async with lock:
            bucket = self._get_bucket(domain)

            while True:
                self._refill_bucket(bucket)

                if bucket['tokens'] >= tokens:
                    bucket['tokens'] -= tokens
                    break

                # Calcular tiempo de espera
                wait_time = (tokens - bucket['tokens']) / self.rate
                logger.debug(f"Token bucket: esperando {wait_time:.2f}s para {domain}")
                await asyncio.sleep(wait_time)

    async def try_acquire(self, url: str, tokens: int = 1) -> bool:
        """
        Intenta adquirir tokens sin esperar.

        Args:
            url: URL
            tokens: Número de tokens

        Returns:
            True si se pudieron adquirir los tokens, False en caso contrario
        """
        domain = self._get_domain(url)
        lock = self._get_lock(domain)

        async with lock:
            bucket = self._get_bucket(domain)
            self._refill_bucket(bucket)

            if bucket['tokens'] >= tokens:
                bucket['tokens'] -= tokens
                return True

            return False

    def get_available_tokens(self, url: str) -> float:
        """
        Obtiene el número de tokens disponibles para un dominio.

        Args:
            url: URL

        Returns:
            Número de tokens disponibles
        """
        domain = self._get_domain(url)
        if domain not in self.buckets:
            return self.capacity

        bucket = self.buckets[domain]
        self._refill_bucket(bucket)
        return bucket['tokens']
