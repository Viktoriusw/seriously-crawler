"""
Configuración centralizada del SEO Crawler.

Este módulo contiene todas las configuraciones por defecto del sistema,
incluyendo parámetros de crawling, análisis de keywords y almacenamiento.
"""

import os
from typing import Dict, Any
from pathlib import Path

# Directorio raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Directorio de datos
DATA_DIR = BASE_DIR / "seo_crawler" / "data"
DATA_DIR.mkdir(exist_ok=True)

# Configuración por defecto del crawler
DEFAULT_CONFIG: Dict[str, Any] = {
    # Parámetros de crawling
    'max_pages': 500,
    'max_depth': 5,
    'concurrent_requests': 10,
    'request_timeout': 15,
    'crawl_delay': 1.0,  # segundos entre requests al mismo dominio
    'max_retries': 3,
    'retry_delay': 2.0,

    # User Agent
    'user_agent': 'SEOCrawler/1.0 (Professional SEO Analysis Tool; +https://github.com/yourusername/seo-crawler)',

    # Respeto de robots.txt
    'respect_robots': True,
    'robots_cache_time': 3600,  # segundos

    # Comportamiento de crawling
    'follow_external_links': False,
    'follow_redirects': True,
    'max_redirects': 5,
    'allow_subdomains': True,

    # Extracción de contenido
    'extract_javascript': False,  # Requiere Selenium/Playwright
    'extract_images': True,
    'extract_links': True,
    'extract_metadata': True,
    'extract_structured_data': True,

    # Análisis de keywords
    'min_keyword_length': 3,
    'max_keyword_length': 50,
    'stop_words_language': 'spanish',
    'extract_ngrams': True,
    'max_ngram_size': 3,
    'min_keyword_frequency': 2,
    'top_keywords_limit': 100,

    # TF-IDF
    'calculate_tfidf': True,
    'tfidf_max_features': 1000,

    # Base de datos
    'database_path': str(DATA_DIR / 'seo_crawler.db'),
    'db_pool_size': 5,

    # Logging
    'log_level': 'INFO',
    'log_file': str(DATA_DIR / 'crawler.log'),
    'log_to_console': True,
    'log_to_file': True,

    # Límites de contenido
    'max_content_size': 10 * 1024 * 1024,  # 10MB
    'max_url_length': 2048,

    # Filtros
    'exclude_patterns': [
        r'.*\.(jpg|jpeg|png|gif|pdf|doc|docx|zip|rar)$',
        r'.*/feed/?$',
        r'.*/wp-admin/.*',
        r'.*/wp-json/.*',
    ],

    # Headers HTTP personalizados
    'custom_headers': {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    },

    # Detección de contenido duplicado
    'detect_duplicates': True,
    'duplicate_threshold': 0.95,  # similitud mínima para considerar duplicado

    # Reportes y exportación
    'export_formats': ['csv', 'excel', 'json', 'html'],
    'chart_dpi': 300,
    'wordcloud_width': 1200,
    'wordcloud_height': 800,
}


class Config:
    """Clase para gestionar la configuración del crawler."""

    def __init__(self, custom_config: Dict[str, Any] = None):
        """
        Inicializa la configuración.

        Args:
            custom_config: Diccionario con configuración personalizada
        """
        self.config = DEFAULT_CONFIG.copy()
        if custom_config:
            self.config.update(custom_config)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Obtiene un valor de configuración.

        Args:
            key: Clave de configuración
            default: Valor por defecto si no existe

        Returns:
            Valor de configuración
        """
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """
        Establece un valor de configuración.

        Args:
            key: Clave de configuración
            value: Valor a establecer
        """
        self.config[key] = value

    def update(self, config_dict: Dict[str, Any]) -> None:
        """
        Actualiza múltiples valores de configuración.

        Args:
            config_dict: Diccionario con valores a actualizar
        """
        self.config.update(config_dict)

    def to_dict(self) -> Dict[str, Any]:
        """
        Retorna la configuración como diccionario.

        Returns:
            Diccionario con toda la configuración
        """
        return self.config.copy()


# Instancia global de configuración
config = Config()
