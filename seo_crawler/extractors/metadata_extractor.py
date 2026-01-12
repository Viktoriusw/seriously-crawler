"""
Extractor de metadatos para el SEO Crawler.

Este módulo extrae metadatos especiales como Open Graph,
Twitter Cards, meta description, y otros datos relevantes para SEO.
"""

from bs4 import BeautifulSoup
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger('SEOCrawler.MetadataExtractor')


class MetadataExtractor:
    """Extractor de metadatos SEO."""

    def __init__(self):
        """Inicializa el extractor."""
        self.parser = 'lxml'

    def extract(self, html: str, base_url: str) -> Dict[str, Any]:
        """
        Extrae todos los metadatos de una página.

        Args:
            html: Contenido HTML
            base_url: URL base de la página

        Returns:
            Diccionario con metadatos
        """
        try:
            soup = BeautifulSoup(html, self.parser)

            metadata = {
                'description': self._extract_meta_description(soup),
                'keywords': self._extract_meta_keywords(soup),
                'author': self._extract_meta_author(soup),
                'robots': self._extract_meta_robots(soup),
                'canonical': self._extract_canonical(soup),
                'language': self._extract_language(soup),
                'og_data': self._extract_open_graph(soup),
                'twitter_data': self._extract_twitter_cards(soup),
                'viewport': self._extract_viewport(soup),
                'charset': self._extract_charset(soup)
            }

            return metadata

        except Exception as e:
            logger.error(f"Error al extraer metadatos: {str(e)}")
            return {}

    def _extract_meta_description(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Extrae la meta description.

        Args:
            soup: Objeto BeautifulSoup

        Returns:
            Meta description o None
        """
        meta = soup.find('meta', attrs={'name': 'description'})
        if meta and meta.get('content'):
            return meta.get('content').strip()
        return None

    def _extract_meta_keywords(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Extrae las meta keywords.

        Args:
            soup: Objeto BeautifulSoup

        Returns:
            Meta keywords o None
        """
        meta = soup.find('meta', attrs={'name': 'keywords'})
        if meta and meta.get('content'):
            return meta.get('content').strip()
        return None

    def _extract_meta_author(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Extrae el meta author.

        Args:
            soup: Objeto BeautifulSoup

        Returns:
            Meta author o None
        """
        meta = soup.find('meta', attrs={'name': 'author'})
        if meta and meta.get('content'):
            return meta.get('content').strip()
        return None

    def _extract_meta_robots(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Extrae las directivas de robots.

        Args:
            soup: Objeto BeautifulSoup

        Returns:
            Directivas de robots o None
        """
        meta = soup.find('meta', attrs={'name': 'robots'})
        if meta and meta.get('content'):
            return meta.get('content').strip()
        return None

    def _extract_canonical(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Extrae la URL canónica.

        Args:
            soup: Objeto BeautifulSoup

        Returns:
            URL canónica o None
        """
        link = soup.find('link', rel='canonical')
        if link and link.get('href'):
            return link.get('href').strip()
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

        # Intentar obtener de meta tag
        meta = soup.find('meta', attrs={'http-equiv': 'content-language'})
        if meta and meta.get('content'):
            return meta.get('content').strip()

        return None

    def _extract_open_graph(self, soup: BeautifulSoup) -> Dict[str, str]:
        """
        Extrae datos de Open Graph.

        Args:
            soup: Objeto BeautifulSoup

        Returns:
            Diccionario con datos de Open Graph
        """
        og_data = {}

        for meta in soup.find_all('meta', property=True):
            prop = meta.get('property', '')
            if prop.startswith('og:'):
                key = prop[3:]  # Remover 'og:' prefix
                content = meta.get('content', '').strip()
                if content:
                    og_data[key] = content

        return og_data

    def _extract_twitter_cards(self, soup: BeautifulSoup) -> Dict[str, str]:
        """
        Extrae datos de Twitter Cards.

        Args:
            soup: Objeto BeautifulSoup

        Returns:
            Diccionario con datos de Twitter Cards
        """
        twitter_data = {}

        for meta in soup.find_all('meta', attrs={'name': True}):
            name = meta.get('name', '')
            if name.startswith('twitter:'):
                key = name[8:]  # Remover 'twitter:' prefix
                content = meta.get('content', '').strip()
                if content:
                    twitter_data[key] = content

        return twitter_data

    def _extract_viewport(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Extrae la configuración del viewport.

        Args:
            soup: Objeto BeautifulSoup

        Returns:
            Configuración del viewport o None
        """
        meta = soup.find('meta', attrs={'name': 'viewport'})
        if meta and meta.get('content'):
            return meta.get('content').strip()
        return None

    def _extract_charset(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Extrae el charset de la página.

        Args:
            soup: Objeto BeautifulSoup

        Returns:
            Charset o None
        """
        # <meta charset="utf-8">
        meta = soup.find('meta', charset=True)
        if meta and meta.get('charset'):
            return meta.get('charset').strip()

        # <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        meta = soup.find('meta', attrs={'http-equiv': 'Content-Type'})
        if meta and meta.get('content'):
            content = meta.get('content')
            if 'charset=' in content:
                charset = content.split('charset=')[-1].strip()
                return charset

        return None

    def extract_schema_org(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Extrae datos estructurados de Schema.org (microdata).

        Args:
            soup: Objeto BeautifulSoup

        Returns:
            Diccionario con datos de Schema.org
        """
        schema_data = {}

        # Buscar elementos con itemscope
        for item in soup.find_all(attrs={'itemscope': True}):
            item_type = item.get('itemtype', '')

            if item_type:
                # Extraer propiedades
                properties = {}
                for prop in item.find_all(attrs={'itemprop': True}):
                    prop_name = prop.get('itemprop')
                    prop_value = prop.get('content') or prop.get_text().strip()

                    if prop_name:
                        properties[prop_name] = prop_value

                if properties:
                    schema_data[item_type] = properties

        return schema_data

    def extract_json_ld(self, soup: BeautifulSoup) -> list:
        """
        Extrae datos estructurados en formato JSON-LD.

        Args:
            soup: Objeto BeautifulSoup

        Returns:
            Lista de objetos JSON-LD
        """
        json_ld_data = []

        for script in soup.find_all('script', type='application/ld+json'):
            try:
                import json
                data = json.loads(script.string)
                json_ld_data.append(data)
            except Exception as e:
                logger.warning(f"Error al parsear JSON-LD: {str(e)}")

        return json_ld_data

    def extract_all_meta_tags(self, soup: BeautifulSoup) -> list:
        """
        Extrae todos los meta tags de la página.

        Args:
            soup: Objeto BeautifulSoup

        Returns:
            Lista de meta tags
        """
        meta_tags = []

        for meta in soup.find_all('meta'):
            tag_data = {}

            # Obtener todos los atributos
            for attr, value in meta.attrs.items():
                tag_data[attr] = value

            if tag_data:
                meta_tags.append(tag_data)

        return meta_tags

    def is_mobile_friendly(self, soup: BeautifulSoup) -> bool:
        """
        Determina si la página es mobile-friendly basado en meta viewport.

        Args:
            soup: Objeto BeautifulSoup

        Returns:
            True si parece ser mobile-friendly, False en caso contrario
        """
        viewport = self._extract_viewport(soup)

        if viewport:
            # Verificar si tiene configuración responsive
            responsive_indicators = [
                'width=device-width',
                'initial-scale=1',
                'responsive'
            ]

            viewport_lower = viewport.lower()
            return any(indicator in viewport_lower for indicator in responsive_indicators)

        return False

    def get_social_links(self, soup: BeautifulSoup) -> Dict[str, str]:
        """
        Extrae enlaces a redes sociales.

        Args:
            soup: Objeto BeautifulSoup

        Returns:
            Diccionario con enlaces sociales
        """
        social_platforms = {
            'facebook': ['facebook.com', 'fb.com'],
            'twitter': ['twitter.com', 'x.com'],
            'instagram': ['instagram.com'],
            'linkedin': ['linkedin.com'],
            'youtube': ['youtube.com', 'youtu.be'],
            'tiktok': ['tiktok.com'],
            'pinterest': ['pinterest.com']
        }

        social_links = {}

        for link in soup.find_all('a', href=True):
            href = link.get('href', '').lower()

            for platform, domains in social_platforms.items():
                if any(domain in href for domain in domains):
                    if platform not in social_links:
                        social_links[platform] = href
                        break

        return social_links
