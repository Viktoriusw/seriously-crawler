"""
Motor principal del SEO Crawler.

Este módulo implementa el crawler asíncrono que coordina todas las operaciones
de crawling, extracción de datos y almacenamiento.
"""

import asyncio
import aiohttp
import time
from typing import List, Optional, Dict, Any
from datetime import datetime
from urllib.parse import urljoin
import logging

from .robots import RobotsManager
from .rate_limiter import RateLimiter
from .url_manager import URLManager
from ..storage.database import Database
from ..extractors.html_parser import HTMLParser
from ..extractors.metadata_extractor import MetadataExtractor
from ..extractors.keyword_analyzer import KeywordAnalyzer
from ..utils.helpers import (
    get_domain,
    hash_content,
    normalize_url,
    format_time_delta,
    estimate_remaining_time
)
from ..config.settings import Config

logger = logging.getLogger('SEOCrawler.Core')


class CrawlerStatistics:
    """Clase para rastrear estadísticas del crawling."""

    def __init__(self):
        """Inicializa las estadísticas."""
        self.pages_crawled = 0
        self.pages_failed = 0
        self.total_keywords = 0
        self.total_links = 0
        self.total_images = 0
        self.start_time = time.time()
        self.bytes_downloaded = 0
        self.lock = asyncio.Lock()

    async def increment_crawled(self) -> None:
        """Incrementa el contador de páginas crawleadas."""
        async with self.lock:
            self.pages_crawled += 1

    async def increment_failed(self) -> None:
        """Incrementa el contador de páginas fallidas."""
        async with self.lock:
            self.pages_failed += 1

    async def add_keywords(self, count: int) -> None:
        """Añade keywords al contador."""
        async with self.lock:
            self.total_keywords += count

    async def add_links(self, count: int) -> None:
        """Añade enlaces al contador."""
        async with self.lock:
            self.total_links += count

    async def add_images(self, count: int) -> None:
        """Añade imágenes al contador."""
        async with self.lock:
            self.total_images += count

    async def add_bytes(self, bytes_count: int) -> None:
        """Añade bytes descargados."""
        async with self.lock:
            self.bytes_downloaded += bytes_count

    def get_elapsed_time(self) -> float:
        """Retorna el tiempo transcurrido en segundos."""
        return time.time() - self.start_time

    async def get_stats(self) -> Dict[str, Any]:
        """Obtiene todas las estadísticas."""
        async with self.lock:
            elapsed = self.get_elapsed_time()
            return {
                'pages_crawled': self.pages_crawled,
                'pages_failed': self.pages_failed,
                'total_keywords': self.total_keywords,
                'total_links': self.total_links,
                'total_images': self.total_images,
                'bytes_downloaded': self.bytes_downloaded,
                'elapsed_time': elapsed,
                'pages_per_second': self.pages_crawled / elapsed if elapsed > 0 else 0
            }


class SEOCrawler:
    """Motor principal del SEO Crawler."""

    def __init__(self, config: Config):
        """
        Inicializa el crawler.

        Args:
            config: Configuración del crawler
        """
        self.config = config
        self.db: Optional[Database] = None
        self.session_id: Optional[int] = None
        self.url_manager: Optional[URLManager] = None
        self.robots_manager: Optional[RobotsManager] = None
        self.rate_limiter: Optional[RateLimiter] = None
        self.html_parser: Optional[HTMLParser] = None
        self.metadata_extractor: Optional[MetadataExtractor] = None
        self.keyword_analyzer: Optional[KeywordAnalyzer] = None
        self.statistics = CrawlerStatistics()
        self.session: Optional[aiohttp.ClientSession] = None
        self.running = False
        self.paused = False

        logger.info("SEOCrawler inicializado")

    async def initialize(self, seed_urls: List[str]) -> None:
        """
        Inicializa todos los componentes del crawler.

        Args:
            seed_urls: URLs iniciales para el crawl
        """
        logger.info(f"Inicializando crawler con {len(seed_urls)} URLs semilla")

        # Base de datos
        self.db = Database(self.config.get('database_path'))
        await self.db.connect()

        # Crear sesión de crawl
        domains = ', '.join(set([get_domain(url) for url in seed_urls]))
        self.session_id = await self.db.create_session(
            seed_url=seed_urls[0],
            domains=domains,
            config=self.config.to_dict()
        )

        logger.info(f"Sesión de crawl creada: {self.session_id}")

        # URL Manager
        self.url_manager = URLManager(
            seed_urls=seed_urls,
            max_depth=self.config.get('max_depth'),
            follow_external=self.config.get('follow_external_links'),
            allow_subdomains=self.config.get('allow_subdomains'),
            exclude_patterns=self.config.get('exclude_patterns')
        )
        await self.url_manager.initialize()

        # Robots Manager
        self.robots_manager = RobotsManager(
            user_agent=self.config.get('user_agent'),
            cache_time=self.config.get('robots_cache_time')
        )

        # Rate Limiter
        self.rate_limiter = RateLimiter(
            default_delay=self.config.get('crawl_delay')
        )

        # Extractores
        self.html_parser = HTMLParser()
        self.metadata_extractor = MetadataExtractor()
        self.keyword_analyzer = KeywordAnalyzer(
            min_length=self.config.get('min_keyword_length'),
            max_length=self.config.get('max_keyword_length'),
            stop_words_language=self.config.get('stop_words_language')
        )

        # Sesión HTTP
        timeout = aiohttp.ClientTimeout(total=self.config.get('request_timeout'))
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            headers=self.config.get('custom_headers')
        )

        logger.info("Crawler inicializado correctamente")

    async def cleanup(self) -> None:
        """Limpia recursos y cierra conexiones."""
        logger.info("Limpiando recursos del crawler")

        try:
            # Cerrar sesión HTTP
            if self.session and not self.session.closed:
                await self.session.close()
                # Pequeño delay para permitir que se cierren las conexiones
                await asyncio.sleep(0.25)

            # Cerrar base de datos
            if self.db:
                if self.session_id:
                    try:
                        await self.db.finish_session(self.session_id)
                    except Exception as e:
                        logger.error(f"Error al finalizar sesión: {e}")
                await self.db.close()

            logger.info("Recursos limpiados correctamente")

        except Exception as e:
            logger.error(f"Error durante cleanup: {e}", exc_info=True)

    async def fetch_page(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Descarga una página web.

        Args:
            url: URL a descargar

        Returns:
            Diccionario con datos de la respuesta o None si falla
        """
        start_time = time.time()

        try:
            # Esperar por rate limit
            await self.rate_limiter.acquire(url)

            # Hacer request
            headers = {'User-Agent': self.config.get('user_agent')}
            async with self.session.get(url, headers=headers, allow_redirects=True) as response:
                status_code = response.status
                content_type = response.headers.get('content-type', '')

                # Verificar tipo de contenido
                if 'text/html' not in content_type.lower():
                    logger.warning(f"Tipo de contenido no HTML: {url} ({content_type})")
                    return None

                # Leer contenido
                content = await response.text()
                response_time = time.time() - start_time

                # Actualizar estadísticas
                await self.statistics.add_bytes(len(content.encode('utf-8')))

                logger.info(f"Página descargada: {url} (Status: {status_code}, Tiempo: {response_time:.2f}s)")

                return {
                    'url': str(response.url),  # URL final después de redirects
                    'status_code': status_code,
                    'content_type': content_type,
                    'content': content,
                    'response_time': response_time,
                    'final_url': str(response.url)
                }

        except asyncio.TimeoutError:
            logger.error(f"Timeout al descargar: {url}")
            return {'error': 'timeout', 'url': url}
        except Exception as e:
            logger.error(f"Error al descargar {url}: {str(e)}")
            return {'error': str(e), 'url': url}

    async def process_page(self, url: str, depth: int, parent_url: Optional[str]) -> bool:
        """
        Procesa una página completa: descarga, extracción y almacenamiento.

        Args:
            url: URL a procesar
            depth: Profundidad desde la URL inicial
            parent_url: URL padre

        Returns:
            True si se procesó exitosamente, False en caso contrario
        """
        logger.debug(f"Procesando página: {url} (depth={depth})")

        # Verificar robots.txt
        if self.config.get('respect_robots'):
            try:
                can_fetch = await self.robots_manager.can_fetch(url)
                if not can_fetch:
                    logger.warning(f"❌ BLOQUEADO POR ROBOTS.TXT: {url}")
                    logger.info(f"💡 Sugerencia: Si tienes permiso, puedes desactivar el respeto a robots.txt en la configuración")
                    await self.url_manager.mark_crawled(url, success=False)
                    await self.statistics.increment_failed()

                    # Guardar en BD para registro
                    try:
                        await self.db.insert_page(self.session_id, {
                            'url': url,
                            'domain': get_domain(url),
                            'status_code': 403,
                            'depth': depth,
                            'parent_url': parent_url,
                            'error_message': 'Blocked by robots.txt'
                        })
                    except Exception:
                        pass  # Ignorar errores de BD aquí

                    return False
            except Exception as e:
                logger.error(f"Error al verificar robots.txt para {url}: {e}")
                # Continuar el crawl si hay error verificando robots.txt

        # Descargar página
        response = await self.fetch_page(url)

        if not response or 'error' in response:
            await self.url_manager.mark_crawled(url, success=False)
            await self.statistics.increment_failed()

            # Guardar error en la base de datos
            error_msg = response.get('error', 'Unknown error') if response else 'Failed to fetch'
            await self.db.insert_page(self.session_id, {
                'url': url,
                'domain': get_domain(url),
                'status_code': response.get('status_code') if response else None,
                'depth': depth,
                'parent_url': parent_url,
                'error_message': error_msg
            })

            return False

        # Extraer datos de la página
        try:
            content = response['content']
            final_url = response['final_url']

            # Parsear HTML
            html_data = self.html_parser.parse(content, final_url)

            # Extraer metadata
            metadata = self.metadata_extractor.extract(content, final_url)

            # Analizar keywords
            full_text = html_data.get('body_text', '')
            keywords_data = self.keyword_analyzer.analyze(
                text=full_text,
                title=html_data.get('title', ''),
                headings=html_data.get('headings', [])
            )

            # Calcular hash de contenido
            content_hash = hash_content(full_text)

            # Preparar datos de la página
            page_data = {
                'url': final_url,
                'domain': get_domain(final_url),
                'status_code': response['status_code'],
                'title': html_data.get('title'),
                'h1': html_data.get('h1'),
                'meta_description': metadata.get('description'),
                'word_count': html_data.get('word_count', 0),
                'content_hash': content_hash,
                'response_time': response['response_time'],
                'depth': depth,
                'parent_url': parent_url,
                'content_type': response['content_type'],
                'canonical_url': metadata.get('canonical'),
                'language': metadata.get('language')
            }

            # Guardar en base de datos
            page_id = await self.db.insert_page(self.session_id, page_data)

            # Guardar keywords
            if keywords_data['keywords']:
                await self.db.insert_keywords(page_id, keywords_data['keywords'])
                await self.statistics.add_keywords(len(keywords_data['keywords']))

            # Guardar enlaces
            if html_data.get('links'):
                await self.db.insert_links(page_id, html_data['links'])
                await self.statistics.add_links(len(html_data['links']))

                # Añadir enlaces a la cola (si son internos o follow_external=True)
                new_urls = [link['url'] for link in html_data['links']
                           if link.get('is_internal') or self.config.get('follow_external_links')]

                await self.url_manager.add_urls_batch(
                    urls=new_urls,
                    depth=depth + 1,
                    parent=final_url
                )

            # Guardar imágenes
            if html_data.get('images'):
                await self.db.insert_images(page_id, html_data['images'])
                await self.statistics.add_images(len(html_data['images']))

            # Guardar headings
            if html_data.get('headings'):
                await self.db.insert_headings(page_id, html_data['headings'])

            # Guardar metadata adicional
            if metadata.get('og_data') or metadata.get('twitter_data'):
                meta_list = []
                for key, value in metadata.get('og_data', {}).items():
                    meta_list.append({'key': f'og:{key}', 'value': value, 'type': 'opengraph'})
                for key, value in metadata.get('twitter_data', {}).items():
                    meta_list.append({'key': f'twitter:{key}', 'value': value, 'type': 'twitter'})

                if meta_list:
                    await self.db.insert_metadata(page_id, meta_list)

            # Marcar como crawleada
            await self.url_manager.mark_crawled(final_url, success=True)
            await self.statistics.increment_crawled()

            logger.info(f"Página procesada exitosamente: {final_url}")
            return True

        except Exception as e:
            logger.error(f"Error al procesar página {url}: {str(e)}", exc_info=True)
            await self.url_manager.mark_crawled(url, success=False)
            await self.statistics.increment_failed()
            return False

    async def crawl_worker(self, worker_id: int) -> None:
        """
        Worker que procesa URLs de la cola.

        Args:
            worker_id: ID del worker
        """
        logger.debug(f"Worker {worker_id} iniciado")

        while self.running:
            # Verificar si está pausado
            while self.paused and self.running:
                await asyncio.sleep(0.5)

            if not self.running:
                break

            # Obtener siguiente URL
            item = await self.url_manager.get_next_url()

            if item is None:
                # No hay más URLs, esperar un poco por si se añaden más
                await asyncio.sleep(1)
                continue

            url, depth, parent = item

            # Procesar página
            await self.process_page(url, depth, parent)

        logger.debug(f"Worker {worker_id} finalizado")

    async def start(self, max_pages: Optional[int] = None) -> Dict[str, Any]:
        """
        Inicia el proceso de crawling.

        Args:
            max_pages: Número máximo de páginas a crawlear (None = sin límite)

        Returns:
            Diccionario con estadísticas finales
        """
        if max_pages is None:
            max_pages = self.config.get('max_pages')

        logger.info(f"Iniciando crawl (max_pages={max_pages})")

        self.running = True
        concurrent_requests = self.config.get('concurrent_requests')

        # Crear workers
        workers = [
            asyncio.create_task(self.crawl_worker(i))
            for i in range(concurrent_requests)
        ]

        # Monitorear progreso
        try:
            while self.running:
                stats = await self.statistics.get_stats()

                # Verificar si se alcanzó el límite
                if stats['pages_crawled'] >= max_pages:
                    logger.info(f"Límite de páginas alcanzado: {max_pages}")
                    self.running = False
                    break

                # Verificar si terminó el crawl
                if await self.url_manager.is_finished() and stats['pages_crawled'] > 0:
                    logger.info("No hay más URLs en la cola, finalizando")
                    self.running = False
                    break

                # Log de progreso cada 5 segundos
                await asyncio.sleep(5)

                url_stats = await self.url_manager.get_stats()
                logger.info(
                    f"Progreso: {stats['pages_crawled']}/{max_pages} páginas | "
                    f"Cola: {url_stats['pending']} | "
                    f"Fallidas: {stats['pages_failed']} | "
                    f"Keywords: {stats['total_keywords']} | "
                    f"Velocidad: {stats['pages_per_second']:.2f} pág/s"
                )

        except KeyboardInterrupt:
            logger.warning("Interrupción detectada, deteniendo crawler...")
            self.running = False

        # Esperar a que terminen los workers
        await asyncio.gather(*workers, return_exceptions=True)

        # Obtener estadísticas finales
        final_stats = await self.statistics.get_stats()
        final_stats['session_id'] = self.session_id

        # Actualizar sesión en BD
        await self.db.update_session(
            self.session_id,
            pages_crawled=final_stats['pages_crawled'],
            pages_failed=final_stats['pages_failed'],
            total_keywords=final_stats['total_keywords']
        )

        logger.info(f"Crawl finalizado: {final_stats['pages_crawled']} páginas en {format_time_delta(final_stats['elapsed_time'])}")

        return final_stats

    def pause(self) -> None:
        """Pausa el crawling."""
        self.paused = True
        logger.info("Crawler pausado")

    def resume(self) -> None:
        """Reanuda el crawling."""
        self.paused = False
        logger.info("Crawler reanudado")

    def stop(self) -> None:
        """Detiene el crawling."""
        self.running = False
        logger.info("Deteniendo crawler...")

    async def get_progress(self) -> Dict[str, Any]:
        """
        Obtiene el progreso actual del crawl.

        Returns:
            Diccionario con información de progreso
        """
        stats = await self.statistics.get_stats()
        url_stats = await self.url_manager.get_stats()

        return {
            **stats,
            **url_stats,
            'session_id': self.session_id,
            'running': self.running,
            'paused': self.paused
        }
