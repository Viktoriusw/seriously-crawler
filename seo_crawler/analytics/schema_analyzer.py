"""
Analizador de Schema Markup y Datos Estructurados - PASO 4
Análisis de JSON-LD, Microdata, RDFa para SEO avanzado

Características:
- Detección de schema markup (JSON-LD, Microdata, RDFa)
- Validación de tipos de schema (Article, Product, Organization, etc.)
- Análisis de completitud de datos estructurados
- Detección de errores en schema markup
- Recomendaciones para mejorar rich snippets
"""

from typing import Dict, List, Optional, Set
import json
import re
from bs4 import BeautifulSoup
from collections import defaultdict


class SchemaAnalyzer:
    """
    Analizador profesional de Schema Markup y datos estructurados
    Compatible con Schema.org types
    """

    # Tipos comunes de Schema.org
    COMMON_TYPES = {
        'Article', 'NewsArticle', 'BlogPosting', 'WebPage',
        'Product', 'Organization', 'Person', 'LocalBusiness',
        'BreadcrumbList', 'FAQPage', 'HowTo', 'Recipe',
        'Event', 'VideoObject', 'ImageObject', 'Review'
    }

    # Propiedades requeridas por tipo
    REQUIRED_PROPERTIES = {
        'Article': ['headline', 'image', 'datePublished', 'author'],
        'Product': ['name', 'image', 'description'],
        'Organization': ['name', 'url'],
        'BreadcrumbList': ['itemListElement'],
        'FAQPage': ['mainEntity'],
        'Review': ['reviewRating', 'author'],
    }

    def __init__(self):
        self.schemas_found = []
        self.errors = []
        self.warnings = []

    # ==================== DETECCIÓN DE SCHEMA MARKUP ====================

    def detect_schemas_in_html(self, html_content: str, url: str = '') -> Dict:
        """
        Detecta todos los schemas en un HTML
        Soporta: JSON-LD, Microdata, RDFa

        Returns:
            Dict con schemas encontrados y análisis
        """
        soup = BeautifulSoup(html_content, 'lxml')

        jsonld_schemas = self._extract_jsonld(soup)
        microdata_schemas = self._extract_microdata(soup)
        rdfa_schemas = self._extract_rdfa(soup)

        return {
            'url': url,
            'jsonld': jsonld_schemas,
            'jsonld_count': len(jsonld_schemas),
            'microdata': microdata_schemas,
            'microdata_count': len(microdata_schemas),
            'rdfa': rdfa_schemas,
            'rdfa_count': len(rdfa_schemas),
            'total_schemas': len(jsonld_schemas) + len(microdata_schemas) + len(rdfa_schemas),
            'has_schema': len(jsonld_schemas) > 0 or len(microdata_schemas) > 0 or len(rdfa_schemas) > 0
        }

    def _extract_jsonld(self, soup: BeautifulSoup) -> List[Dict]:
        """Extrae schema markup JSON-LD"""
        schemas = []
        scripts = soup.find_all('script', type='application/ld+json')

        for script in scripts:
            try:
                content = script.string
                if content:
                    data = json.loads(content)
                    # Puede ser un objeto o un array
                    if isinstance(data, list):
                        schemas.extend(data)
                    else:
                        schemas.append(data)
            except json.JSONDecodeError as e:
                self.errors.append({
                    'type': 'jsonld_parse_error',
                    'error': str(e),
                    'content': script.string[:100] if script.string else ''
                })

        return schemas

    def _extract_microdata(self, soup: BeautifulSoup) -> List[Dict]:
        """Extrae schema markup en formato Microdata"""
        schemas = []
        items = soup.find_all(attrs={'itemscope': True})

        for item in items:
            itemtype = item.get('itemtype', '')
            if itemtype:
                schema_type = itemtype.split('/')[-1]
                properties = {}

                # Extraer itemprop
                for prop in item.find_all(attrs={'itemprop': True}):
                    prop_name = prop.get('itemprop')
                    prop_value = prop.get('content') or prop.get_text(strip=True)
                    properties[prop_name] = prop_value

                schemas.append({
                    '@type': schema_type,
                    'properties': properties,
                    'format': 'microdata'
                })

        return schemas

    def _extract_rdfa(self, soup: BeautifulSoup) -> List[Dict]:
        """Extrae schema markup en formato RDFa"""
        schemas = []
        items = soup.find_all(attrs={'typeof': True})

        for item in items:
            typeof = item.get('typeof', '')
            if typeof:
                properties = {}

                # Extraer property
                for prop in item.find_all(attrs={'property': True}):
                    prop_name = prop.get('property')
                    prop_value = prop.get('content') or prop.get_text(strip=True)
                    properties[prop_name] = prop_value

                schemas.append({
                    '@type': typeof,
                    'properties': properties,
                    'format': 'rdfa'
                })

        return schemas

    # ==================== VALIDACIÓN DE SCHEMAS ====================

    def validate_schema(self, schema: Dict) -> Dict:
        """
        Valida un schema individual
        Verifica tipo y propiedades requeridas

        Returns:
            Dict con resultado de validación
        """
        schema_type = schema.get('@type', '')
        is_valid = True
        missing_properties = []
        warnings = []

        # Verificar si es un tipo conocido
        if schema_type not in self.COMMON_TYPES:
            warnings.append(f"Tipo '{schema_type}' no es un tipo común de Schema.org")

        # Verificar propiedades requeridas
        if schema_type in self.REQUIRED_PROPERTIES:
            required = self.REQUIRED_PROPERTIES[schema_type]
            for prop in required:
                if prop not in schema:
                    missing_properties.append(prop)
                    is_valid = False

        return {
            'type': schema_type,
            'is_valid': is_valid,
            'missing_properties': missing_properties,
            'warnings': warnings,
            'completeness': self._calculate_completeness(schema, schema_type)
        }

    def _calculate_completeness(self, schema: Dict, schema_type: str) -> float:
        """Calcula completitud del schema (0-1)"""
        if schema_type not in self.REQUIRED_PROPERTIES:
            return 1.0  # Si no hay propiedades requeridas conocidas, asumimos completo

        required = self.REQUIRED_PROPERTIES[schema_type]
        if not required:
            return 1.0

        present = sum(1 for prop in required if prop in schema)
        return present / len(required)

    # ==================== ANÁLISIS DE PÁGINAS ====================

    def analyze_pages_schemas(self, pages: List[Dict]) -> Dict:
        """
        Analiza schema markup en múltiples páginas

        Returns:
            Dict con análisis agregado
        """
        pages_with_schema = []
        pages_without_schema = []
        schema_types_found = defaultdict(int)
        total_schemas = 0
        validation_results = []

        for page in pages:
            page_id = page.get('page_id')
            url = page.get('url', '')
            html = page.get('html_content', '')

            if not html:
                continue

            schema_data = self.detect_schemas_in_html(html, url)
            has_schema = schema_data['has_schema']

            if has_schema:
                pages_with_schema.append({
                    'page_id': page_id,
                    'url': url,
                    'schema_count': schema_data['total_schemas']
                })

                # Analizar cada schema encontrado
                for schema in schema_data['jsonld']:
                    schema_type = schema.get('@type', 'Unknown')
                    schema_types_found[schema_type] += 1
                    total_schemas += 1

                    validation = self.validate_schema(schema)
                    validation_results.append({
                        'page_id': page_id,
                        'url': url,
                        'validation': validation
                    })

            else:
                pages_without_schema.append({
                    'page_id': page_id,
                    'url': url
                })

        total_pages = len(pages)
        schema_coverage = len(pages_with_schema) / total_pages if total_pages > 0 else 0

        return {
            'total_pages': total_pages,
            'pages_with_schema': pages_with_schema,
            'pages_with_schema_count': len(pages_with_schema),
            'pages_without_schema': pages_without_schema,
            'pages_without_schema_count': len(pages_without_schema),
            'schema_coverage': schema_coverage,
            'schema_types_found': dict(schema_types_found),
            'total_schemas': total_schemas,
            'validation_results': validation_results,
            'avg_schemas_per_page': total_schemas / total_pages if total_pages > 0 else 0
        }

    # ==================== DETECCIÓN DE OPEN GRAPH ====================

    def analyze_open_graph(self, html_content: str) -> Dict:
        """
        Analiza Open Graph meta tags
        Importante para compartir en redes sociales

        Returns:
            Dict con tags OG encontrados
        """
        soup = BeautifulSoup(html_content, 'lxml')
        og_tags = {}
        missing_recommended = []

        # Tags OG recomendados
        recommended_tags = ['og:title', 'og:description', 'og:image', 'og:url', 'og:type']

        # Extraer todos los meta tags OG
        og_metas = soup.find_all('meta', property=re.compile(r'^og:'))
        for meta in og_metas:
            property_name = meta.get('property', '')
            content = meta.get('content', '')
            og_tags[property_name] = content

        # Verificar tags recomendados
        for tag in recommended_tags:
            if tag not in og_tags:
                missing_recommended.append(tag)

        return {
            'og_tags': og_tags,
            'og_tags_count': len(og_tags),
            'has_og': len(og_tags) > 0,
            'missing_recommended': missing_recommended,
            'completeness': (len(recommended_tags) - len(missing_recommended)) / len(recommended_tags)
        }

    # ==================== DETECCIÓN DE TWITTER CARDS ====================

    def analyze_twitter_cards(self, html_content: str) -> Dict:
        """
        Analiza Twitter Card meta tags

        Returns:
            Dict con tags de Twitter Cards encontrados
        """
        soup = BeautifulSoup(html_content, 'lxml')
        twitter_tags = {}
        missing_recommended = []

        # Tags Twitter recomendados
        recommended_tags = ['twitter:card', 'twitter:title', 'twitter:description', 'twitter:image']

        # Extraer todos los meta tags de Twitter
        twitter_metas = soup.find_all('meta', attrs={'name': re.compile(r'^twitter:')})
        for meta in twitter_metas:
            name = meta.get('name', '')
            content = meta.get('content', '')
            twitter_tags[name] = content

        # Verificar tags recomendados
        for tag in recommended_tags:
            if tag not in twitter_tags:
                missing_recommended.append(tag)

        return {
            'twitter_tags': twitter_tags,
            'twitter_tags_count': len(twitter_tags),
            'has_twitter': len(twitter_tags) > 0,
            'missing_recommended': missing_recommended,
            'completeness': (len(recommended_tags) - len(missing_recommended)) / len(recommended_tags) if recommended_tags else 0
        }

    # ==================== ANÁLISIS COMPLETO DE METADATOS SOCIALES ====================

    def analyze_social_metadata(self, pages: List[Dict]) -> Dict:
        """
        Analiza metadatos sociales (OG + Twitter Cards) en todas las páginas

        Returns:
            Dict con análisis completo de metadatos sociales
        """
        pages_with_og = []
        pages_with_twitter = []
        pages_without_social = []

        for page in pages:
            page_id = page.get('page_id')
            url = page.get('url', '')
            html = page.get('html_content', '')

            if not html:
                continue

            og_data = self.analyze_open_graph(html)
            twitter_data = self.analyze_twitter_cards(html)

            has_og = og_data['has_og']
            has_twitter = twitter_data['has_twitter']

            if has_og:
                pages_with_og.append({
                    'page_id': page_id,
                    'url': url,
                    'og_count': og_data['og_tags_count'],
                    'completeness': og_data['completeness']
                })

            if has_twitter:
                pages_with_twitter.append({
                    'page_id': page_id,
                    'url': url,
                    'twitter_count': twitter_data['twitter_tags_count'],
                    'completeness': twitter_data['completeness']
                })

            if not has_og and not has_twitter:
                pages_without_social.append({
                    'page_id': page_id,
                    'url': url
                })

        total_pages = len(pages)

        return {
            'total_pages': total_pages,
            'pages_with_og': pages_with_og,
            'pages_with_og_count': len(pages_with_og),
            'og_coverage': len(pages_with_og) / total_pages if total_pages > 0 else 0,
            'pages_with_twitter': pages_with_twitter,
            'pages_with_twitter_count': len(pages_with_twitter),
            'twitter_coverage': len(pages_with_twitter) / total_pages if total_pages > 0 else 0,
            'pages_without_social': pages_without_social,
            'pages_without_social_count': len(pages_without_social),
            'social_metadata_coverage': (len(pages_with_og) + len(pages_with_twitter)) / (total_pages * 2) if total_pages > 0 else 0
        }

    # ==================== ANÁLISIS COMPLETO ====================

    def run_complete_analysis(self, pages: List[Dict]) -> Dict:
        """
        Ejecuta análisis completo de datos estructurados y metadatos

        Returns:
            Dict con análisis completo y puntuación
        """
        schema_analysis = self.analyze_pages_schemas(pages)
        social_analysis = self.analyze_social_metadata(pages)

        # Calcular puntuación de salud (0-100)
        schema_coverage = schema_analysis['schema_coverage']
        og_coverage = social_analysis['og_coverage']
        twitter_coverage = social_analysis['twitter_coverage']

        # Peso: 50% schema markup, 25% OG, 25% Twitter
        health_score = (
            schema_coverage * 50 +
            og_coverage * 25 +
            twitter_coverage * 25
        )

        return {
            'schema_analysis': schema_analysis,
            'social_metadata': social_analysis,
            'health_score': round(health_score, 2),
            'recommendations': self._generate_recommendations(schema_analysis, social_analysis)
        }

    def _generate_recommendations(self, schema_analysis: Dict, social_analysis: Dict) -> List[str]:
        """Genera recomendaciones basadas en el análisis"""
        recommendations = []

        # Schema markup
        schema_coverage = schema_analysis['schema_coverage']
        if schema_coverage < 0.5:
            recommendations.append(
                f"⚠️ Solo {schema_coverage*100:.1f}% de las páginas tienen schema markup. "
                "Considera agregar JSON-LD para mejorar los rich snippets en Google."
            )

        if schema_analysis['pages_without_schema_count'] > 0:
            recommendations.append(
                f"📄 {schema_analysis['pages_without_schema_count']} páginas sin schema markup. "
                "Prioriza agregar schema a páginas importantes (productos, artículos, etc.)."
            )

        # Open Graph
        og_coverage = social_analysis['og_coverage']
        if og_coverage < 0.8:
            recommendations.append(
                f"📱 Solo {og_coverage*100:.1f}% de las páginas tienen Open Graph tags. "
                "Importante para compartir en Facebook, LinkedIn, etc."
            )

        # Twitter Cards
        twitter_coverage = social_analysis['twitter_coverage']
        if twitter_coverage < 0.8:
            recommendations.append(
                f"🐦 Solo {twitter_coverage*100:.1f}% de las páginas tienen Twitter Cards. "
                "Mejora la apariencia de tus URLs cuando se comparten en Twitter."
            )

        if not recommendations:
            recommendations.append("✅ Excelente implementación de datos estructurados y metadatos sociales.")

        return recommendations

    def generate_summary(self, analysis_results: Dict) -> str:
        """
        Genera resumen legible del análisis

        Returns:
            String formateado con resumen
        """
        summary = []
        summary.append("=" * 80)
        summary.append("ANÁLISIS DE DATOS ESTRUCTURADOS Y METADATOS")
        summary.append("=" * 80)
        summary.append(f"\n📊 PUNTUACIÓN DE SALUD: {analysis_results['health_score']}/100")

        # Schema Markup
        summary.append("\n" + "-" * 80)
        summary.append("🏷️  SCHEMA MARKUP")
        summary.append("-" * 80)
        schema = analysis_results['schema_analysis']
        summary.append(f"Cobertura: {schema['schema_coverage']*100:.2f}%")
        summary.append(f"  - Páginas con schema: {schema['pages_with_schema_count']}/{schema['total_pages']}")
        summary.append(f"  - Total de schemas: {schema['total_schemas']}")
        summary.append(f"  - Promedio por página: {schema['avg_schemas_per_page']:.2f}")

        if schema['schema_types_found']:
            summary.append("\n  Tipos de schema encontrados:")
            for schema_type, count in sorted(schema['schema_types_found'].items(), key=lambda x: -x[1])[:5]:
                summary.append(f"    - {schema_type}: {count}")

        # Open Graph
        summary.append("\n" + "-" * 80)
        summary.append("📱 OPEN GRAPH (Facebook, LinkedIn)")
        summary.append("-" * 80)
        social = analysis_results['social_metadata']
        summary.append(f"Cobertura: {social['og_coverage']*100:.2f}%")
        summary.append(f"  - Páginas con OG: {social['pages_with_og_count']}/{social['total_pages']}")

        # Twitter Cards
        summary.append("\n" + "-" * 80)
        summary.append("🐦 TWITTER CARDS")
        summary.append("-" * 80)
        summary.append(f"Cobertura: {social['twitter_coverage']*100:.2f}%")
        summary.append(f"  - Páginas con Twitter Cards: {social['pages_with_twitter_count']}/{social['total_pages']}")

        # Recomendaciones
        summary.append("\n" + "-" * 80)
        summary.append("💡 RECOMENDACIONES")
        summary.append("-" * 80)
        for rec in analysis_results['recommendations']:
            summary.append(f"  {rec}")

        summary.append("\n" + "=" * 80)

        return "\n".join(summary)
