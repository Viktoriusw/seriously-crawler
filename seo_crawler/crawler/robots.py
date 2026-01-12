"""
Gestor de robots.txt para el SEO Crawler.

Este módulo maneja la descarga, parseo y consulta de archivos robots.txt
para respetar las directivas de los sitios web.
"""

import asyncio
import aiohttp
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse, urljoin
from typing import Dict, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger('SEOCrawler.Robots')


class RobotsManager:
    """Gestor de robots.txt con caché por dominio."""

    def __init__(self, user_agent: str, cache_time: int = 3600):
        """
        Inicializa el gestor de robots.txt.

        Args:
            user_agent: User-Agent del crawler
            cache_time: Tiempo de caché en segundos
        """
        self.user_agent = user_agent
        self.cache_time = cache_time
        self.parsers: Dict[str, RobotFileParser] = {}
        self.cache_timestamps: Dict[str, datetime] = {}
        self.fetch_lock = asyncio.Lock()

    def _get_robots_url(self, url: str) -> str:
        """
        Construye la URL del robots.txt a partir de una URL.

        Args:
            url: URL de la página

        Returns:
            URL del robots.txt
        """
        parsed = urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        return robots_url

    def _get_domain(self, url: str) -> str:
        """
        Extrae el dominio de una URL.

        Args:
            url: URL

        Returns:
            Dominio
        """
        return urlparse(url).netloc

    def _is_cache_valid(self, domain: str) -> bool:
        """
        Verifica si el caché para un dominio sigue siendo válido.

        Args:
            domain: Dominio a verificar

        Returns:
            True si el caché es válido, False en caso contrario
        """
        if domain not in self.cache_timestamps:
            return False

        cache_age = datetime.now() - self.cache_timestamps[domain]
        return cache_age < timedelta(seconds=self.cache_time)

    async def fetch_robots_txt(self, url: str) -> Optional[str]:
        """
        Descarga el contenido del robots.txt de forma asíncrona.

        Args:
            url: URL del robots.txt

        Returns:
            Contenido del robots.txt o None si no existe
        """
        try:
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                headers = {'User-Agent': self.user_agent}
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        content = await response.text()
                        logger.info(f"Robots.txt descargado exitosamente: {url}")
                        return content
                    else:
                        logger.warning(f"No se encontró robots.txt en {url} (Status: {response.status})")
                        return None
        except Exception as e:
            logger.error(f"Error al descargar robots.txt de {url}: {str(e)}")
            return None

    async def get_parser(self, url: str) -> RobotFileParser:
        """
        Obtiene el parser de robots.txt para una URL (con caché).

        Args:
            url: URL de la página

        Returns:
            Parser de robots.txt configurado
        """
        domain = self._get_domain(url)

        # Verificar caché
        if domain in self.parsers and self._is_cache_valid(domain):
            return self.parsers[domain]

        # Si no está en caché o expiró, descargar
        async with self.fetch_lock:
            # Double-check después del lock
            if domain in self.parsers and self._is_cache_valid(domain):
                return self.parsers[domain]

            robots_url = self._get_robots_url(url)
            content = await self.fetch_robots_txt(robots_url)

            parser = RobotFileParser()
            parser.set_url(robots_url)

            if content:
                # Parsear el contenido
                parser.parse(content.splitlines())
            else:
                # Si no hay robots.txt, permitir todo
                logger.info(f"No hay robots.txt para {domain}, permitiendo todo")

            # Guardar en caché
            self.parsers[domain] = parser
            self.cache_timestamps[domain] = datetime.now()

            return parser

    async def can_fetch(self, url: str) -> bool:
        """
        Verifica si se puede crawlear una URL según robots.txt.

        Args:
            url: URL a verificar

        Returns:
            True si se puede crawlear, False en caso contrario
        """
        try:
            parser = await self.get_parser(url)
            result = parser.can_fetch(self.user_agent, url)

            if not result:
                logger.info(f"URL bloqueada por robots.txt: {url}")

            return result
        except Exception as e:
            logger.error(f"Error al verificar robots.txt para {url}: {str(e)}")
            # En caso de error, ser conservador y permitir el crawl
            return True

    async def get_crawl_delay(self, url: str) -> Optional[float]:
        """
        Obtiene el crawl delay especificado en robots.txt.

        Args:
            url: URL del sitio

        Returns:
            Crawl delay en segundos o None si no está especificado
        """
        try:
            parser = await self.get_parser(url)
            delay = parser.crawl_delay(self.user_agent)

            if delay:
                logger.info(f"Crawl delay para {self._get_domain(url)}: {delay}s")

            return delay
        except Exception as e:
            logger.error(f"Error al obtener crawl delay para {url}: {str(e)}")
            return None

    async def get_request_rate(self, url: str) -> Optional[tuple]:
        """
        Obtiene el request rate especificado en robots.txt.

        Args:
            url: URL del sitio

        Returns:
            Tupla (requests, seconds) o None si no está especificado
        """
        try:
            parser = await self.get_parser(url)
            rate = parser.request_rate(self.user_agent)

            if rate:
                logger.info(f"Request rate para {self._get_domain(url)}: {rate}")

            return rate
        except Exception as e:
            logger.error(f"Error al obtener request rate para {url}: {str(e)}")
            return None

    def clear_cache(self) -> None:
        """Limpia toda la caché de robots.txt."""
        self.parsers.clear()
        self.cache_timestamps.clear()
        logger.info("Caché de robots.txt limpiada")

    def clear_domain_cache(self, domain: str) -> None:
        """
        Limpia la caché de un dominio específico.

        Args:
            domain: Dominio a limpiar
        """
        if domain in self.parsers:
            del self.parsers[domain]
        if domain in self.cache_timestamps:
            del self.cache_timestamps[domain]
        logger.info(f"Caché de robots.txt limpiada para {domain}")
