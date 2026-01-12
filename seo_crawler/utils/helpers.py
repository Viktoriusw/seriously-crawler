"""
Funciones auxiliares y utilidades para el SEO Crawler.

Este módulo contiene funciones de uso común en todo el proyecto,
incluyendo validación de URLs, normalización, logging y más.
"""

import re
import hashlib
import logging
from typing import Optional, Set, List
from urllib.parse import urlparse, urljoin, urlunparse
from datetime import datetime


def setup_logging(log_level: str = 'INFO',
                  log_file: Optional[str] = None,
                  log_to_console: bool = True) -> logging.Logger:
    """
    Configura el sistema de logging.

    Args:
        log_level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Ruta al archivo de log (opcional)
        log_to_console: Si True, también muestra logs en consola

    Returns:
        Logger configurado
    """
    logger = logging.getLogger('SEOCrawler')
    logger.setLevel(getattr(logging, log_level.upper()))

    # Evitar duplicar handlers
    logger.handlers.clear()

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    if log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def normalize_url(url: str, base_url: Optional[str] = None) -> str:
    """
    Normaliza una URL eliminando fragmentos y parámetros innecesarios.

    Args:
        url: URL a normalizar
        base_url: URL base para resolver URLs relativas

    Returns:
        URL normalizada
    """
    # Resolver URL relativa si hay base_url
    if base_url:
        url = urljoin(base_url, url)

    parsed = urlparse(url)

    # Reconstruir sin fragmento y normalizando el path
    normalized = urlunparse((
        parsed.scheme.lower(),
        parsed.netloc.lower(),
        parsed.path.rstrip('/') if parsed.path != '/' else '/',
        parsed.params,
        parsed.query,
        ''  # Sin fragmento
    ))

    return normalized


def is_valid_url(url: str) -> bool:
    """
    Valida si una URL tiene un formato correcto.

    Args:
        url: URL a validar

    Returns:
        True si la URL es válida, False en caso contrario
    """
    try:
        result = urlparse(url)
        return all([result.scheme in ('http', 'https'), result.netloc])
    except Exception:
        return False


def get_domain(url: str) -> str:
    """
    Extrae el dominio de una URL.

    Args:
        url: URL de la que extraer el dominio

    Returns:
        Dominio (ej: 'ejemplo.com')
    """
    parsed = urlparse(url)
    return parsed.netloc.lower()


def is_same_domain(url1: str, url2: str, allow_subdomains: bool = True) -> bool:
    """
    Verifica si dos URLs pertenecen al mismo dominio.

    Args:
        url1: Primera URL
        url2: Segunda URL
        allow_subdomains: Si True, considera subdominios como mismo dominio

    Returns:
        True si son del mismo dominio, False en caso contrario
    """
    domain1 = get_domain(url1)
    domain2 = get_domain(url2)

    if allow_subdomains:
        # Obtener dominio principal (ejemplo: blog.site.com -> site.com)
        parts1 = domain1.split('.')
        parts2 = domain2.split('.')
        if len(parts1) >= 2 and len(parts2) >= 2:
            main_domain1 = '.'.join(parts1[-2:])
            main_domain2 = '.'.join(parts2[-2:])
            return main_domain1 == main_domain2

    return domain1 == domain2


def is_internal_link(url: str, base_domain: str, allow_subdomains: bool = True) -> bool:
    """
    Determina si un enlace es interno (mismo dominio que la página base).

    Args:
        url: URL a verificar
        base_domain: Dominio base para comparar
        allow_subdomains: Si True, considera subdominios como internos

    Returns:
        True si es enlace interno, False en caso contrario
    """
    url_domain = get_domain(url)

    if allow_subdomains:
        return base_domain in url_domain or url_domain in base_domain
    else:
        return url_domain == base_domain


def hash_content(content: str) -> str:
    """
    Genera un hash MD5 del contenido para detección de duplicados.

    Args:
        content: Contenido a hashear

    Returns:
        Hash MD5 en formato hexadecimal
    """
    return hashlib.md5(content.encode('utf-8')).hexdigest()


def clean_text(text: str) -> str:
    """
    Limpia un texto eliminando espacios extra y caracteres especiales.

    Args:
        text: Texto a limpiar

    Returns:
        Texto limpio
    """
    # Eliminar múltiples espacios, tabs y newlines
    text = re.sub(r'\s+', ' ', text)
    # Eliminar espacios al inicio y final
    text = text.strip()
    return text


def extract_keywords_from_text(text: str, min_length: int = 3, max_length: int = 50) -> List[str]:
    """
    Extrae palabras individuales de un texto (versión básica sin NLP).

    Args:
        text: Texto del que extraer palabras
        min_length: Longitud mínima de palabra
        max_length: Longitud máxima de palabra

    Returns:
        Lista de palabras
    """
    # Convertir a minúsculas
    text = text.lower()
    # Extraer palabras (solo letras y números)
    words = re.findall(r'\b[a-záéíóúñü]+\b', text)
    # Filtrar por longitud
    words = [w for w in words if min_length <= len(w) <= max_length]
    return words


def calculate_density(keyword: str, text: str, total_words: int) -> float:
    """
    Calcula la densidad de una keyword en un texto.

    Args:
        keyword: Palabra clave
        text: Texto completo
        total_words: Total de palabras en el texto

    Returns:
        Densidad como porcentaje (0-100)
    """
    if total_words == 0:
        return 0.0

    keyword_lower = keyword.lower()
    text_lower = text.lower()

    # Contar ocurrencias
    count = text_lower.count(keyword_lower)

    # Calcular densidad
    density = (count / total_words) * 100

    return round(density, 2)


def matches_pattern(url: str, patterns: List[str]) -> bool:
    """
    Verifica si una URL coincide con alguno de los patrones dados.

    Args:
        url: URL a verificar
        patterns: Lista de patrones regex

    Returns:
        True si coincide con algún patrón, False en caso contrario
    """
    for pattern in patterns:
        if re.search(pattern, url, re.IGNORECASE):
            return True
    return False


def format_time_delta(seconds: float) -> str:
    """
    Formatea un delta de tiempo en un string legible.

    Args:
        seconds: Segundos transcurridos

    Returns:
        String formateado (ej: "2h 15m 30s")
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if secs > 0 or not parts:
        parts.append(f"{secs}s")

    return " ".join(parts)


def estimate_remaining_time(processed: int, total: int, elapsed: float) -> str:
    """
    Estima el tiempo restante basado en el progreso actual.

    Args:
        processed: Cantidad de items procesados
        total: Total de items a procesar
        elapsed: Tiempo transcurrido en segundos

    Returns:
        String con tiempo estimado restante
    """
    if processed == 0 or total == 0:
        return "Calculando..."

    avg_time_per_item = elapsed / processed
    remaining_items = total - processed
    remaining_seconds = avg_time_per_item * remaining_items

    return format_time_delta(remaining_seconds)


def truncate_string(text: str, max_length: int = 100, suffix: str = '...') -> str:
    """
    Trunca un string a una longitud máxima.

    Args:
        text: Texto a truncar
        max_length: Longitud máxima
        suffix: Sufijo a añadir si se trunca

    Returns:
        Texto truncado
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def get_file_extension(url: str) -> str:
    """
    Obtiene la extensión de archivo de una URL.

    Args:
        url: URL a analizar

    Returns:
        Extensión del archivo (sin el punto) o cadena vacía
    """
    path = urlparse(url).path
    match = re.search(r'\.([a-zA-Z0-9]+)$', path)
    return match.group(1).lower() if match else ''


def is_crawlable_url(url: str, exclude_patterns: List[str]) -> bool:
    """
    Determina si una URL es crawleable según los patrones de exclusión.

    Args:
        url: URL a verificar
        exclude_patterns: Patrones de exclusión

    Returns:
        True si es crawleable, False en caso contrario
    """
    # Verificar formato válido
    if not is_valid_url(url):
        return False

    # Verificar patrones de exclusión
    if matches_pattern(url, exclude_patterns):
        return False

    return True


def sanitize_filename(filename: str) -> str:
    """
    Sanitiza un nombre de archivo eliminando caracteres no válidos.

    Args:
        filename: Nombre de archivo a sanitizar

    Returns:
        Nombre de archivo sanitizado
    """
    # Reemplazar caracteres no válidos con guión bajo
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Limitar longitud
    sanitized = sanitized[:200]
    return sanitized
