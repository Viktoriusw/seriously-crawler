"""
Parser de HTML para el SEO Crawler.

Este módulo extrae todos los elementos HTML relevantes para SEO:
títulos, encabezados, enlaces, imágenes, texto del body, etc.
"""

from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin
import re
import logging

from ..utils.helpers import clean_text, normalize_url, is_internal_link, get_domain

logger = logging.getLogger('SEOCrawler.HTMLParser')


class HTMLParser:
    """Parser de HTML para extracción de elementos SEO."""

    def __init__(self):
        """Inicializa el parser."""
        self.parser = 'lxml'

    def parse(self, html: str, base_url: str) -> Dict[str, Any]:
        """
        Parsea HTML y extrae todos los elementos relevantes.

        Args:
            html: Contenido HTML
            base_url: URL base para resolver enlaces relativos

        Returns:
            Diccionario con todos los elementos extraídos
        """
        try:
            soup = BeautifulSoup(html, self.parser)

            # Eliminar scripts y styles
            for script in soup(['script', 'style']):
                script.decompose()

            result = {
                'title': self._extract_title(soup),
                'h1': self._extract_h1(soup),
                'headings': self._extract_headings(soup),
                'meta_tags': self._extract_meta_tags(soup),
                'links': self._extract_links(soup, base_url),
                'images': self._extract_images(soup, base_url),
                'body_text': self._extract_body_text(soup),
                'word_count': 0,
                'canonical': self._extract_canonical(soup),
                'lang': self._extract_language(soup)
            }

            # Calcular word count
            result['word_count'] = len(result['body_text'].split())

            return result

        except Exception as e:
            logger.error(f"Error al parsear HTML: {str(e)}")
            return {}

    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Extrae el título de la página.

        Args:
            soup: Objeto BeautifulSoup

        Returns:
            Título de la página o None
        """
        title_tag = soup.find('title')
        if title_tag and title_tag.string:
            return clean_text(title_tag.string)
        return None

    def _extract_h1(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Extrae el primer H1 de la página.

        Args:
            soup: Objeto BeautifulSoup

        Returns:
            Texto del H1 o None
        """
        h1_tag = soup.find('h1')
        if h1_tag:
            return clean_text(h1_tag.get_text())
        return None

    def _extract_headings(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Extrae todos los encabezados (h1-h6) con su nivel y posición.

        Args:
            soup: Objeto BeautifulSoup

        Returns:
            Lista de headings
        """
        headings = []
        position = 0

        for level in range(1, 7):
            for heading in soup.find_all(f'h{level}'):
                text = clean_text(heading.get_text())
                if text:
                    headings.append({
                        'level': level,
                        'text': text,
                        'position': position
                    })
                    position += 1

        return headings

    def _extract_meta_tags(self, soup: BeautifulSoup) -> Dict[str, str]:
        """
        Extrae todos los meta tags.

        Args:
            soup: Objeto BeautifulSoup

        Returns:
            Diccionario con meta tags
        """
        meta_tags = {}

        for meta in soup.find_all('meta'):
            name = meta.get('name') or meta.get('property')
            content = meta.get('content')

            if name and content:
                meta_tags[name] = content

        return meta_tags

    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, Any]]:
        """
        Extrae todos los enlaces de la página.

        Args:
            soup: Objeto BeautifulSoup
            base_url: URL base

        Returns:
            Lista de enlaces con sus atributos
        """
        links = []
        base_domain = get_domain(base_url)

        for link in soup.find_all('a', href=True):
            href = link.get('href', '').strip()

            if not href or href.startswith('#') or href.startswith('javascript:') or href.startswith('mailto:'):
                continue

            # Resolver URL relativa
            try:
                absolute_url = urljoin(base_url, href)
                normalized_url = normalize_url(absolute_url)
            except Exception:
                continue

            # Anchor text
            anchor_text = clean_text(link.get_text())

            # Verificar si es interno
            is_internal = is_internal_link(normalized_url, base_domain, allow_subdomains=True)

            # Verificar nofollow
            rel = link.get('rel', [])
            if isinstance(rel, list):
                nofollow = 'nofollow' in rel
            else:
                nofollow = 'nofollow' in str(rel)

            links.append({
                'url': normalized_url,
                'anchor_text': anchor_text[:500] if anchor_text else '',  # Limitar longitud
                'is_internal': is_internal,
                'nofollow': nofollow,
                'type': 'a'
            })

        return links

    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, Any]]:
        """
        Extrae todas las imágenes de la página.

        Args:
            soup: Objeto BeautifulSoup
            base_url: URL base

        Returns:
            Lista de imágenes con sus atributos
        """
        images = []

        for img in soup.find_all('img'):
            src = img.get('src', '').strip()

            if not src:
                # Intentar con data-src (lazy loading)
                src = img.get('data-src', '').strip()

            if not src:
                continue

            # Resolver URL relativa
            try:
                absolute_url = urljoin(base_url, src)
            except Exception:
                continue

            alt_text = img.get('alt', '').strip()
            title_text = img.get('title', '').strip()
            width = img.get('width')
            height = img.get('height')

            images.append({
                'url': absolute_url,
                'alt': alt_text[:500] if alt_text else '',
                'title': title_text[:500] if title_text else '',
                'width': int(width) if width and width.isdigit() else None,
                'height': int(height) if height and height.isdigit() else None
            })

        return images

    def _extract_body_text(self, soup: BeautifulSoup) -> str:
        """
        Extrae el texto limpio del body.

        Args:
            soup: Objeto BeautifulSoup

        Returns:
            Texto limpio del body
        """
        # Eliminar navegación, footer, sidebar, etc.
        for tag in soup.find_all(['nav', 'footer', 'aside', 'header']):
            tag.decompose()

        # Obtener texto del body
        body = soup.find('body')
        if body:
            text = body.get_text(separator=' ', strip=True)
        else:
            text = soup.get_text(separator=' ', strip=True)

        # Limpiar texto
        text = clean_text(text)

        return text

    def _extract_canonical(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Extrae la URL canónica.

        Args:
            soup: Objeto BeautifulSoup

        Returns:
            URL canónica o None
        """
        canonical = soup.find('link', rel='canonical')
        if canonical and canonical.get('href'):
            return canonical.get('href')
        return None

    def _extract_language(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Extrae el idioma de la página.

        Args:
            soup: Objeto BeautifulSoup

        Returns:
            Código de idioma o None
        """
        html_tag = soup.find('html')
        if html_tag:
            lang = html_tag.get('lang') or html_tag.get('xml:lang')
            if lang:
                return lang.strip()
        return None

    def extract_structured_data(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Extrae datos estructurados (JSON-LD, microdata).

        Args:
            soup: Objeto BeautifulSoup

        Returns:
            Lista de datos estructurados
        """
        structured_data = []

        # JSON-LD
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                import json
                data = json.loads(script.string)
                structured_data.append({
                    'type': 'json-ld',
                    'data': data
                })
            except Exception as e:
                logger.warning(f"Error al parsear JSON-LD: {str(e)}")

        return structured_data

    def extract_hreflang(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """
        Extrae tags hreflang.

        Args:
            soup: Objeto BeautifulSoup

        Returns:
            Lista de hreflang tags
        """
        hreflang_tags = []

        for link in soup.find_all('link', rel='alternate', hreflang=True):
            href = link.get('href')
            hreflang = link.get('hreflang')

            if href and hreflang:
                hreflang_tags.append({
                    'hreflang': hreflang,
                    'href': href
                })

        return hreflang_tags
