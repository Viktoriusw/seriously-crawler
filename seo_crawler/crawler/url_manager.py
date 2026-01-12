"""
Gestor de URLs para el SEO Crawler.

Este módulo maneja la cola de URLs a crawlear, deduplicación,
prioridades y filtrado de URLs.
"""

import asyncio
from typing import Set, Optional, List, Tuple
from urllib.parse import urlparse, urljoin
from collections import deque
import logging

from ..utils.helpers import (
    normalize_url,
    is_valid_url,
    is_same_domain,
    is_crawlable_url,
    get_domain
)

logger = logging.getLogger('SEOCrawler.URLManager')


class URLQueue:
    """Cola de URLs con soporte para prioridades."""

    def __init__(self):
        """Inicializa la cola de URLs."""
        self.queue = deque()
        self.lock = asyncio.Lock()

    async def put(self, url: str, priority: int = 0, depth: int = 0, parent: Optional[str] = None) -> None:
        """
        Añade una URL a la cola.

        Args:
            url: URL a añadir
            priority: Prioridad (mayor = más prioritario)
            depth: Profundidad desde la URL inicial
            parent: URL padre
        """
        async with self.lock:
            # Insertar manteniendo orden de prioridad
            item = (priority, depth, url, parent)

            if not self.queue:
                self.queue.append(item)
            else:
                # Buscar posición según prioridad
                inserted = False
                for i, (p, _, _, _) in enumerate(self.queue):
                    if priority > p:
                        self.queue.insert(i, item)
                        inserted = True
                        break

                if not inserted:
                    self.queue.append(item)

    async def get(self) -> Optional[Tuple[str, int, Optional[str]]]:
        """
        Obtiene y elimina la siguiente URL de la cola.

        Returns:
            Tupla (url, depth, parent) o None si la cola está vacía
        """
        async with self.lock:
            if self.queue:
                priority, depth, url, parent = self.queue.popleft()
                return (url, depth, parent)
            return None

    async def size(self) -> int:
        """
        Retorna el tamaño de la cola.

        Returns:
            Número de URLs en la cola
        """
        async with self.lock:
            return len(self.queue)

    async def is_empty(self) -> bool:
        """
        Verifica si la cola está vacía.

        Returns:
            True si está vacía, False en caso contrario
        """
        async with self.lock:
            return len(self.queue) == 0

    async def clear(self) -> None:
        """Vacía la cola."""
        async with self.lock:
            self.queue.clear()

    async def peek(self, n: int = 10) -> List[Tuple]:
        """
        Obtiene las próximas N URLs sin eliminarlas de la cola.

        Args:
            n: Número de URLs a obtener

        Returns:
            Lista de tuplas (priority, depth, url, parent)
        """
        async with self.lock:
            return list(self.queue)[:n]


class URLManager:
    """Gestor completo de URLs con deduplicación y filtrado."""

    def __init__(self,
                 seed_urls: List[str],
                 max_depth: int = 5,
                 follow_external: bool = False,
                 allow_subdomains: bool = True,
                 exclude_patterns: List[str] = None):
        """
        Inicializa el gestor de URLs.

        Args:
            seed_urls: URLs iniciales
            max_depth: Profundidad máxima de crawling
            follow_external: Si True, sigue enlaces externos
            allow_subdomains: Si True, permite subdominios del dominio principal
            exclude_patterns: Patrones regex de URLs a excluir
        """
        self.seed_urls = [normalize_url(url) for url in seed_urls]
        self.max_depth = max_depth
        self.follow_external = follow_external
        self.allow_subdomains = allow_subdomains
        self.exclude_patterns = exclude_patterns or []

        # Obtener dominios semilla
        self.seed_domains = [get_domain(url) for url in self.seed_urls]

        # Cola de URLs a procesar
        self.queue = URLQueue()

        # Sets para deduplicación
        self.seen_urls: Set[str] = set()
        self.queued_urls: Set[str] = set()
        self.crawled_urls: Set[str] = set()
        self.failed_urls: Set[str] = set()

        # Locks
        self.seen_lock = asyncio.Lock()
        self.queued_lock = asyncio.Lock()
        self.crawled_lock = asyncio.Lock()

        logger.info(f"URLManager inicializado con {len(self.seed_urls)} URLs semilla")

    async def initialize(self) -> None:
        """Inicializa el manager añadiendo las URLs semilla a la cola."""
        for url in self.seed_urls:
            await self.add_url(url, depth=0, priority=10)  # Alta prioridad para seeds

        logger.info(f"{len(self.seed_urls)} URLs semilla añadidas a la cola")

    async def add_url(self,
                     url: str,
                     depth: int = 0,
                     parent: Optional[str] = None,
                     priority: int = 0) -> bool:
        """
        Añade una URL a la cola si pasa todos los filtros.

        Args:
            url: URL a añadir
            depth: Profundidad desde la URL inicial
            parent: URL padre
            priority: Prioridad

        Returns:
            True si se añadió, False en caso contrario
        """
        # Normalizar URL
        try:
            url = normalize_url(url, parent)
        except Exception as e:
            logger.debug(f"Error al normalizar URL {url}: {str(e)}")
            return False

        # Verificar si ya fue vista
        async with self.seen_lock:
            if url in self.seen_urls:
                return False
            self.seen_urls.add(url)

        # Validar URL
        if not is_valid_url(url):
            logger.debug(f"URL inválida: {url}")
            return False

        # Verificar profundidad
        if depth > self.max_depth:
            logger.debug(f"Profundidad máxima excedida para: {url}")
            return False

        # Verificar si es crawleable
        if not is_crawlable_url(url, self.exclude_patterns):
            logger.debug(f"URL excluida por patrones: {url}")
            return False

        # Verificar dominios
        if not self._is_allowed_domain(url):
            logger.debug(f"Dominio no permitido: {url}")
            return False

        # Añadir a la cola
        async with self.queued_lock:
            if url not in self.queued_urls:
                self.queued_urls.add(url)
                await self.queue.put(url, priority, depth, parent)
                logger.debug(f"URL añadida a la cola: {url} (depth={depth})")
                return True

        return False

    def _is_allowed_domain(self, url: str) -> bool:
        """
        Verifica si el dominio de la URL está permitido.

        Args:
            url: URL a verificar

        Returns:
            True si está permitido, False en caso contrario
        """
        url_domain = get_domain(url)

        # Verificar contra cada dominio semilla
        for seed_domain in self.seed_domains:
            if self.allow_subdomains:
                # Permitir si es el mismo dominio o subdominio
                if seed_domain in url_domain or url_domain in seed_domain:
                    return True
            else:
                # Requiere coincidencia exacta
                if url_domain == seed_domain:
                    return True

        # Si follow_external es True, permitir cualquier dominio
        if self.follow_external:
            return True

        return False

    async def get_next_url(self) -> Optional[Tuple[str, int, Optional[str]]]:
        """
        Obtiene la siguiente URL a crawlear.

        Returns:
            Tupla (url, depth, parent) o None si no hay más URLs
        """
        item = await self.queue.get()

        if item:
            url, depth, parent = item
            async with self.queued_lock:
                if url in self.queued_urls:
                    self.queued_urls.remove(url)

        return item

    async def mark_crawled(self, url: str, success: bool = True) -> None:
        """
        Marca una URL como crawleada.

        Args:
            url: URL crawleada
            success: Si el crawl fue exitoso
        """
        async with self.crawled_lock:
            if success:
                self.crawled_urls.add(url)
            else:
                self.failed_urls.add(url)

    async def has_seen(self, url: str) -> bool:
        """
        Verifica si una URL ya fue vista.

        Args:
            url: URL a verificar

        Returns:
            True si ya fue vista, False en caso contrario
        """
        url = normalize_url(url)
        async with self.seen_lock:
            return url in self.seen_urls

    async def has_crawled(self, url: str) -> bool:
        """
        Verifica si una URL ya fue crawleada.

        Args:
            url: URL a verificar

        Returns:
            True si ya fue crawleada, False en caso contrario
        """
        url = normalize_url(url)
        async with self.crawled_lock:
            return url in self.crawled_urls

    async def get_stats(self) -> dict:
        """
        Obtiene estadísticas del gestor de URLs.

        Returns:
            Diccionario con estadísticas
        """
        return {
            'seen': len(self.seen_urls),
            'queued': await self.queue.size(),
            'crawled': len(self.crawled_urls),
            'failed': len(self.failed_urls),
            'pending': await self.queue.size()
        }

    async def is_finished(self) -> bool:
        """
        Verifica si el crawling ha terminado.

        Returns:
            True si no hay más URLs en la cola, False en caso contrario
        """
        return await self.queue.is_empty()

    async def add_urls_batch(self,
                            urls: List[str],
                            depth: int,
                            parent: Optional[str] = None) -> int:
        """
        Añade múltiples URLs de forma eficiente.

        Args:
            urls: Lista de URLs a añadir
            depth: Profundidad de las URLs
            parent: URL padre

        Returns:
            Número de URLs añadidas exitosamente
        """
        added = 0
        for url in urls:
            if await self.add_url(url, depth, parent):
                added += 1

        if added > 0:
            logger.info(f"{added} URLs añadidas a la cola desde {parent}")

        return added

    async def get_queued_urls_preview(self, n: int = 10) -> List[str]:
        """
        Obtiene una vista previa de las próximas URLs en la cola.

        Args:
            n: Número de URLs a obtener

        Returns:
            Lista de URLs
        """
        items = await self.queue.peek(n)
        return [url for _, _, url, _ in items]

    def get_seed_domains(self) -> List[str]:
        """
        Obtiene los dominios semilla.

        Returns:
            Lista de dominios semilla
        """
        return self.seed_domains.copy()

    async def clear(self) -> None:
        """Limpia todos los datos del manager."""
        await self.queue.clear()
        self.seen_urls.clear()
        self.queued_urls.clear()
        self.crawled_urls.clear()
        self.failed_urls.clear()
        logger.info("URLManager limpiado")
