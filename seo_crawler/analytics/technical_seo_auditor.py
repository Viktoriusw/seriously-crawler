"""
Auditoría Técnica SEO - PASO 4
Análisis técnico profesional comparable a herramientas enterprise como Sistrix/Ahrefs

Características:
- Análisis completo de meta tags (title, description, duplicados)
- Detección de errores HTTP y redirects
- Validación de canonical tags y estructura de URLs
- Análisis de indexabilidad y robots meta tags
- Detección de mixed content (HTTP/HTTPS)
- Análisis de imágenes (alt tags, optimización)
- Detección de contenido duplicado técnico
- Puntuación global de salud técnica SEO
"""

from typing import Dict, List, Tuple, Optional, Set
from collections import defaultdict
from urllib.parse import urlparse, parse_qs
import re
from bs4 import BeautifulSoup


class TechnicalSEOAuditor:
    """
    Auditor técnico SEO profesional
    Detecta problemas técnicos que afectan el rendimiento SEO
    """

    def __init__(self):
        self.issues = []
        self.warnings = []
        self.passed = []

    # ==================== ANÁLISIS DE META TAGS ====================

    def analyze_meta_tags(self, pages: List[Dict]) -> Dict:
        """
        Analiza meta tags en todas las páginas
        Detecta: duplicados, faltantes, longitud incorrecta

        Returns:
            Dict con análisis completo de meta tags
        """
        results = {
            'title': self._analyze_titles(pages),
            'description': self._analyze_descriptions(pages),
            'duplicates': self._find_duplicate_metas(pages),
            'missing': self._find_missing_metas(pages),
            'length_issues': self._check_meta_lengths(pages),
            'total_issues': 0,
            'total_warnings': 0,
            'health_score': 0.0
        }

        # Calcular totales
        results['total_issues'] = (
            results['duplicates']['duplicate_titles_count'] +
            results['duplicates']['duplicate_descriptions_count'] +
            results['missing']['missing_titles_count'] +
            results['missing']['missing_descriptions_count']
        )

        results['total_warnings'] = (
            results['length_issues']['titles_too_short'] +
            results['length_issues']['titles_too_long'] +
            results['length_issues']['descriptions_too_short'] +
            results['length_issues']['descriptions_too_long']
        )

        # Health score (0-100)
        total_pages = len(pages)
        if total_pages > 0:
            issues_ratio = results['total_issues'] / total_pages
            warnings_ratio = results['total_warnings'] / total_pages
            results['health_score'] = max(0, 100 - (issues_ratio * 50) - (warnings_ratio * 20))

        return results

    def _analyze_titles(self, pages: List[Dict]) -> Dict:
        """Analiza títulos de páginas"""
        titles = []
        for page in pages:
            title = (page.get('title') or '').strip()
            if title:
                titles.append({
                    'page_id': page.get('page_id'),
                    'url': page.get('url'),
                    'title': title,
                    'length': len(title)
                })

        return {
            'total': len(titles),
            'avg_length': sum(t['length'] for t in titles) / len(titles) if titles else 0,
            'titles': titles
        }

    def _analyze_descriptions(self, pages: List[Dict]) -> Dict:
        """Analiza meta descriptions"""
        descriptions = []
        for page in pages:
            desc = (page.get('meta_description') or '').strip()
            if desc:
                descriptions.append({
                    'page_id': page.get('page_id'),
                    'url': page.get('url'),
                    'description': desc,
                    'length': len(desc)
                })

        return {
            'total': len(descriptions),
            'avg_length': sum(d['length'] for d in descriptions) / len(descriptions) if descriptions else 0,
            'descriptions': descriptions
        }

    def _find_duplicate_metas(self, pages: List[Dict]) -> Dict:
        """Encuentra meta tags duplicados"""
        title_map = defaultdict(list)
        desc_map = defaultdict(list)

        for page in pages:
            title = (page.get('title') or '').strip()
            desc = (page.get('meta_description') or '').strip()

            if title:
                title_map[title].append({
                    'page_id': page.get('page_id'),
                    'url': page.get('url')
                })

            if desc:
                desc_map[desc].append({
                    'page_id': page.get('page_id'),
                    'url': page.get('url')
                })

        # Filtrar solo duplicados
        duplicate_titles = {k: v for k, v in title_map.items() if len(v) > 1}
        duplicate_descriptions = {k: v for k, v in desc_map.items() if len(v) > 1}

        return {
            'duplicate_titles': duplicate_titles,
            'duplicate_titles_count': sum(len(v) for v in duplicate_titles.values()),
            'duplicate_descriptions': duplicate_descriptions,
            'duplicate_descriptions_count': sum(len(v) for v in duplicate_descriptions.values())
        }

    def _find_missing_metas(self, pages: List[Dict]) -> Dict:
        """Encuentra páginas sin meta tags esenciales"""
        missing_titles = []
        missing_descriptions = []

        for page in pages:
            url = page.get('url', '')
            page_id = page.get('page_id')

            if not (page.get('title') or '').strip():
                missing_titles.append({'page_id': page_id, 'url': url})

            if not (page.get('meta_description') or '').strip():
                missing_descriptions.append({'page_id': page_id, 'url': url})

        return {
            'missing_titles': missing_titles,
            'missing_titles_count': len(missing_titles),
            'missing_descriptions': missing_descriptions,
            'missing_descriptions_count': len(missing_descriptions)
        }

    def _check_meta_lengths(self, pages: List[Dict]) -> Dict:
        """Verifica longitudes óptimas de meta tags"""
        # Rangos óptimos
        TITLE_MIN = 30
        TITLE_MAX = 60
        DESC_MIN = 120
        DESC_MAX = 160

        titles_too_short = []
        titles_too_long = []
        descriptions_too_short = []
        descriptions_too_long = []

        for page in pages:
            page_id = page.get('page_id')
            url = page.get('url', '')
            title = (page.get('title') or '').strip()
            desc = (page.get('meta_description') or '').strip()

            if title:
                title_len = len(title)
                if title_len < TITLE_MIN:
                    titles_too_short.append({
                        'page_id': page_id,
                        'url': url,
                        'length': title_len,
                        'title': title
                    })
                elif title_len > TITLE_MAX:
                    titles_too_long.append({
                        'page_id': page_id,
                        'url': url,
                        'length': title_len,
                        'title': title
                    })

            if desc:
                desc_len = len(desc)
                if desc_len < DESC_MIN:
                    descriptions_too_short.append({
                        'page_id': page_id,
                        'url': url,
                        'length': desc_len,
                        'description': desc
                    })
                elif desc_len > DESC_MAX:
                    descriptions_too_long.append({
                        'page_id': page_id,
                        'url': url,
                        'length': desc_len,
                        'description': desc
                    })

        return {
            'titles_too_short': len(titles_too_short),
            'titles_too_long': len(titles_too_long),
            'descriptions_too_short': len(descriptions_too_short),
            'descriptions_too_long': len(descriptions_too_long),
            'details': {
                'titles_short': titles_too_short,
                'titles_long': titles_too_long,
                'descriptions_short': descriptions_too_short,
                'descriptions_long': descriptions_too_long
            }
        }

    # ==================== ANÁLISIS DE ERRORES HTTP ====================

    def analyze_http_errors(self, pages: List[Dict]) -> Dict:
        """
        Analiza errores HTTP en las páginas crawleadas

        Returns:
            Dict con desglose de códigos HTTP
        """
        status_codes = defaultdict(list)

        for page in pages:
            status = page.get('status_code', 200)
            status_codes[status].append({
                'page_id': page.get('page_id'),
                'url': page.get('url'),
                'status_code': status
            })

        # Clasificar por tipo
        success = []  # 2xx
        redirects = []  # 3xx
        client_errors = []  # 4xx
        server_errors = []  # 5xx

        for status, pages_list in status_codes.items():
            if 200 <= status < 300:
                success.extend(pages_list)
            elif 300 <= status < 400:
                redirects.extend(pages_list)
            elif 400 <= status < 500:
                client_errors.extend(pages_list)
            elif 500 <= status < 600:
                server_errors.extend(pages_list)

        return {
            'status_codes': dict(status_codes),
            'success': success,
            'success_count': len(success),
            'redirects': redirects,
            'redirect_count': len(redirects),
            'client_errors': client_errors,
            'client_error_count': len(client_errors),
            'server_errors': server_errors,
            'server_error_count': len(server_errors),
            'total_errors': len(client_errors) + len(server_errors),
            'error_rate': (len(client_errors) + len(server_errors)) / len(pages) if pages else 0
        }

    # ==================== ANÁLISIS DE CANONICAL ====================

    def analyze_canonical_tags(self, pages: List[Dict]) -> Dict:
        """
        Analiza canonical tags
        Detecta: faltantes, self-canonical, cadenas de canonical
        """
        missing_canonical = []
        has_canonical = []
        self_canonical = []
        external_canonical = []

        for page in pages:
            page_id = page.get('page_id')
            url = page.get('url', '')
            canonical = (page.get('canonical') or '').strip()

            if not canonical:
                missing_canonical.append({'page_id': page_id, 'url': url})
            else:
                has_canonical.append({
                    'page_id': page_id,
                    'url': url,
                    'canonical': canonical
                })

                # Verificar si es self-canonical
                if self._normalize_url(canonical) == self._normalize_url(url):
                    self_canonical.append({
                        'page_id': page_id,
                        'url': url,
                        'canonical': canonical
                    })
                else:
                    # Verificar si apunta a otro dominio
                    url_domain = urlparse(url).netloc
                    canonical_domain = urlparse(canonical).netloc

                    if url_domain != canonical_domain:
                        external_canonical.append({
                            'page_id': page_id,
                            'url': url,
                            'canonical': canonical,
                            'external_domain': canonical_domain
                        })

        return {
            'total_pages': len(pages),
            'missing_canonical': missing_canonical,
            'missing_count': len(missing_canonical),
            'has_canonical': has_canonical,
            'has_canonical_count': len(has_canonical),
            'self_canonical': self_canonical,
            'self_canonical_count': len(self_canonical),
            'external_canonical': external_canonical,
            'external_canonical_count': len(external_canonical),
            'canonical_coverage': len(has_canonical) / len(pages) if pages else 0
        }

    def _normalize_url(self, url: str) -> str:
        """Normaliza URL para comparación (quita trailing slash, parámetros, etc.)"""
        parsed = urlparse(url)
        normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path.rstrip('/')}"
        return normalized.lower()

    # ==================== ANÁLISIS DE INDEXABILIDAD ====================

    def analyze_indexability(self, pages: List[Dict]) -> Dict:
        """
        Analiza problemas de indexabilidad
        Detecta: noindex, nofollow, canonical a otra página, robots bloqueado
        """
        indexable = []
        non_indexable = []
        noindex_pages = []
        nofollow_pages = []

        for page in pages:
            page_id = page.get('page_id')
            url = page.get('url', '')
            robots_meta = page.get('robots_meta', '').lower()

            is_indexable = True
            reasons = []

            # Verificar robots meta tag
            if 'noindex' in robots_meta:
                is_indexable = False
                reasons.append('noindex')
                noindex_pages.append({'page_id': page_id, 'url': url, 'robots': robots_meta})

            if 'nofollow' in robots_meta:
                nofollow_pages.append({'page_id': page_id, 'url': url, 'robots': robots_meta})

            # Verificar canonical a otra página
            canonical = (page.get('canonical') or '').strip()
            if canonical and self._normalize_url(canonical) != self._normalize_url(url):
                is_indexable = False
                reasons.append('canonical_to_different_url')

            # Verificar si está bloqueado por robots.txt (si tenemos esa info)
            if page.get('blocked_by_robots', False):
                is_indexable = False
                reasons.append('blocked_by_robots')

            page_data = {
                'page_id': page_id,
                'url': url,
                'reasons': reasons
            }

            if is_indexable:
                indexable.append(page_data)
            else:
                non_indexable.append(page_data)

        return {
            'total_pages': len(pages),
            'indexable': indexable,
            'indexable_count': len(indexable),
            'non_indexable': non_indexable,
            'non_indexable_count': len(non_indexable),
            'noindex_pages': noindex_pages,
            'noindex_count': len(noindex_pages),
            'nofollow_pages': nofollow_pages,
            'nofollow_count': len(nofollow_pages),
            'indexability_rate': len(indexable) / len(pages) if pages else 0
        }

    # ==================== ANÁLISIS DE IMÁGENES ====================

    def analyze_images(self, pages: List[Dict], images: List[Dict]) -> Dict:
        """
        Analiza optimización de imágenes
        Detecta: falta de alt tags, imágenes grandes, formatos no optimizados
        """
        missing_alt = []
        has_alt = []
        empty_alt = []

        # Agrupar imágenes por página
        images_by_page = defaultdict(list)
        for img in images:
            page_id = img.get('page_id')
            if page_id:
                images_by_page[page_id].append(img)

        for page in pages:
            page_id = page.get('page_id')
            url = page.get('url', '')
            page_images = images_by_page.get(page_id, [])

            for img in page_images:
                img_src = img.get('src', '')
                alt = (img.get('alt') or '').strip()

                if not alt:
                    if alt == '':
                        empty_alt.append({
                            'page_id': page_id,
                            'page_url': url,
                            'img_src': img_src
                        })
                    else:
                        missing_alt.append({
                            'page_id': page_id,
                            'page_url': url,
                            'img_src': img_src
                        })
                else:
                    has_alt.append({
                        'page_id': page_id,
                        'page_url': url,
                        'img_src': img_src,
                        'alt': alt
                    })

        total_images = len(images)

        return {
            'total_images': total_images,
            'missing_alt': missing_alt,
            'missing_alt_count': len(missing_alt),
            'empty_alt': empty_alt,
            'empty_alt_count': len(empty_alt),
            'has_alt': has_alt,
            'has_alt_count': len(has_alt),
            'alt_coverage': len(has_alt) / total_images if total_images else 0,
            'pages_analyzed': len(pages)
        }

    # ==================== ANÁLISIS DE ESTRUCTURA DE URLs ====================

    def analyze_url_structure(self, pages: List[Dict]) -> Dict:
        """
        Analiza la estructura de URLs
        Detecta: URLs largas, parámetros excesivos, caracteres especiales, profundidad
        """
        long_urls = []
        with_parameters = []
        with_special_chars = []
        depth_distribution = defaultdict(int)

        MAX_URL_LENGTH = 100  # Caracteres recomendados

        for page in pages:
            page_id = page.get('page_id')
            url = page.get('url', '')
            depth = page.get('depth', 0)

            parsed = urlparse(url)
            path = parsed.path
            query = parsed.query

            # Longitud de URL
            if len(url) > MAX_URL_LENGTH:
                long_urls.append({
                    'page_id': page_id,
                    'url': url,
                    'length': len(url)
                })

            # Parámetros en URL
            if query:
                params = parse_qs(query)
                with_parameters.append({
                    'page_id': page_id,
                    'url': url,
                    'param_count': len(params),
                    'params': list(params.keys())
                })

            # Caracteres especiales (no SEO-friendly)
            if re.search(r'[^a-zA-Z0-9\-_/.]', path):
                with_special_chars.append({
                    'page_id': page_id,
                    'url': url,
                    'path': path
                })

            # Distribución de profundidad
            depth_distribution[depth] += 1

        # Calcular profundidad promedio
        total_pages = len(pages)
        avg_depth = sum(depth * count for depth, count in depth_distribution.items()) / total_pages if total_pages else 0

        return {
            'total_pages': total_pages,
            'long_urls': long_urls,
            'long_urls_count': len(long_urls),
            'with_parameters': with_parameters,
            'with_parameters_count': len(with_parameters),
            'with_special_chars': with_special_chars,
            'with_special_chars_count': len(with_special_chars),
            'depth_distribution': dict(depth_distribution),
            'avg_depth': avg_depth,
            'max_depth': max(depth_distribution.keys()) if depth_distribution else 0
        }

    # ==================== ANÁLISIS COMPLETO ====================

    def run_complete_audit(self, pages: List[Dict], images: List[Dict]) -> Dict:
        """
        Ejecuta una auditoría técnica completa

        Returns:
            Dict con todos los análisis y puntuación global
        """
        results = {
            'meta_tags': self.analyze_meta_tags(pages),
            'http_errors': self.analyze_http_errors(pages),
            'canonical': self.analyze_canonical_tags(pages),
            'indexability': self.analyze_indexability(pages),
            'images': self.analyze_images(pages, images),
            'url_structure': self.analyze_url_structure(pages),
            'overall_health_score': 0.0,
            'critical_issues': 0,
            'warnings': 0,
            'passed_checks': 0
        }

        # Calcular puntuación global (promedio ponderado)
        weights = {
            'meta_tags': 0.25,
            'http_errors': 0.20,
            'canonical': 0.15,
            'indexability': 0.20,
            'images': 0.10,
            'url_structure': 0.10
        }

        overall_score = 0.0

        # Meta tags health
        meta_health = results['meta_tags']['health_score']
        overall_score += meta_health * weights['meta_tags']

        # HTTP errors health (100 - error_rate)
        error_rate = results['http_errors']['error_rate']
        http_health = max(0, 100 - (error_rate * 100))
        overall_score += http_health * weights['http_errors']

        # Canonical health
        canonical_coverage = results['canonical']['canonical_coverage']
        canonical_health = canonical_coverage * 100
        overall_score += canonical_health * weights['canonical']

        # Indexability health
        indexability_rate = results['indexability']['indexability_rate']
        indexability_health = indexability_rate * 100
        overall_score += indexability_health * weights['indexability']

        # Images health
        alt_coverage = results['images']['alt_coverage']
        images_health = alt_coverage * 100
        overall_score += images_health * weights['images']

        # URL structure health
        url_issues = (
            results['url_structure']['long_urls_count'] +
            results['url_structure']['with_special_chars_count']
        )
        url_health = max(0, 100 - (url_issues / len(pages) * 50)) if pages else 100
        overall_score += url_health * weights['url_structure']

        results['overall_health_score'] = round(overall_score, 2)

        # Contar issues críticos y warnings
        results['critical_issues'] = (
            results['meta_tags']['total_issues'] +
            results['http_errors']['total_errors'] +
            results['indexability']['non_indexable_count']
        )

        results['warnings'] = (
            results['meta_tags']['total_warnings'] +
            results['canonical']['missing_count'] +
            results['images']['missing_alt_count']
        )

        results['passed_checks'] = (
            results['http_errors']['success_count'] +
            results['indexability']['indexable_count']
        )

        return results

    def generate_audit_summary(self, audit_results: Dict) -> str:
        """
        Genera un resumen legible de la auditoría

        Returns:
            String formateado con resumen ejecutivo
        """
        summary = []
        summary.append("=" * 80)
        summary.append("AUDITORÍA TÉCNICA SEO - RESUMEN EJECUTIVO")
        summary.append("=" * 80)
        summary.append(f"\n📊 PUNTUACIÓN GLOBAL DE SALUD: {audit_results['overall_health_score']}/100")
        summary.append(f"🔴 Issues Críticos: {audit_results['critical_issues']}")
        summary.append(f"⚠️  Warnings: {audit_results['warnings']}")
        summary.append(f"✅ Checks Pasados: {audit_results['passed_checks']}")

        # Meta Tags
        summary.append("\n" + "-" * 80)
        summary.append("📝 META TAGS")
        summary.append("-" * 80)
        meta = audit_results['meta_tags']
        summary.append(f"Health Score: {meta['health_score']:.2f}/100")
        summary.append(f"  - Títulos duplicados: {meta['duplicates']['duplicate_titles_count']}")
        summary.append(f"  - Descriptions duplicadas: {meta['duplicates']['duplicate_descriptions_count']}")
        summary.append(f"  - Títulos faltantes: {meta['missing']['missing_titles_count']}")
        summary.append(f"  - Descriptions faltantes: {meta['missing']['missing_descriptions_count']}")

        # HTTP Errors
        summary.append("\n" + "-" * 80)
        summary.append("🌐 ERRORES HTTP")
        summary.append("-" * 80)
        http = audit_results['http_errors']
        summary.append(f"Error Rate: {http['error_rate']*100:.2f}%")
        summary.append(f"  - Páginas exitosas (2xx): {http['success_count']}")
        summary.append(f"  - Redirects (3xx): {http['redirect_count']}")
        summary.append(f"  - Errores de cliente (4xx): {http['client_error_count']}")
        summary.append(f"  - Errores de servidor (5xx): {http['server_error_count']}")

        # Canonical
        summary.append("\n" + "-" * 80)
        summary.append("🔗 CANONICAL TAGS")
        summary.append("-" * 80)
        canonical = audit_results['canonical']
        summary.append(f"Cobertura: {canonical['canonical_coverage']*100:.2f}%")
        summary.append(f"  - Páginas con canonical: {canonical['has_canonical_count']}")
        summary.append(f"  - Self-canonical: {canonical['self_canonical_count']}")
        summary.append(f"  - Canonical externo: {canonical['external_canonical_count']}")
        summary.append(f"  - Sin canonical: {canonical['missing_count']}")

        # Indexability
        summary.append("\n" + "-" * 80)
        summary.append("🔍 INDEXABILIDAD")
        summary.append("-" * 80)
        index = audit_results['indexability']
        summary.append(f"Tasa de indexabilidad: {index['indexability_rate']*100:.2f}%")
        summary.append(f"  - Páginas indexables: {index['indexable_count']}")
        summary.append(f"  - Páginas no indexables: {index['non_indexable_count']}")
        summary.append(f"  - Páginas con noindex: {index['noindex_count']}")
        summary.append(f"  - Páginas con nofollow: {index['nofollow_count']}")

        # Images
        summary.append("\n" + "-" * 80)
        summary.append("🖼️  IMÁGENES")
        summary.append("-" * 80)
        images = audit_results['images']
        summary.append(f"Cobertura de alt tags: {images['alt_coverage']*100:.2f}%")
        summary.append(f"  - Total de imágenes: {images['total_images']}")
        summary.append(f"  - Con alt tag: {images['has_alt_count']}")
        summary.append(f"  - Sin alt tag: {images['missing_alt_count']}")
        summary.append(f"  - Alt tag vacío: {images['empty_alt_count']}")

        # URL Structure
        summary.append("\n" + "-" * 80)
        summary.append("🔧 ESTRUCTURA DE URLs")
        summary.append("-" * 80)
        urls = audit_results['url_structure']
        summary.append(f"Profundidad promedio: {urls['avg_depth']:.2f}")
        summary.append(f"  - URLs largas (>{100} chars): {urls['long_urls_count']}")
        summary.append(f"  - URLs con parámetros: {urls['with_parameters_count']}")
        summary.append(f"  - URLs con caracteres especiales: {urls['with_special_chars_count']}")

        summary.append("\n" + "=" * 80)

        return "\n".join(summary)
