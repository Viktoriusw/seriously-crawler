"""
Motor de Recomendaciones SEO Inteligente - PASO 4
Sistema profesional de sugerencias accionables priorizadas por impacto

Características:
- Análisis multidimensional (técnico, contenido, keywords, enlaces)
- Priorización por impacto (Quick Wins vs Long Term)
- Recomendaciones accionables con pasos específicos
- Scoring de oportunidades
- Roadmap de optimización sugerido
"""

from typing import Dict, List, Tuple, Optional
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum


class Priority(Enum):
    """Niveles de prioridad de recomendaciones"""
    CRITICAL = "critical"  # Problemas que bloquean indexación
    HIGH = "high"  # Alto impacto, esfuerzo medio
    MEDIUM = "medium"  # Impacto medio
    LOW = "low"  # Mejoras incrementales


class Category(Enum):
    """Categorías de recomendaciones"""
    TECHNICAL = "technical"
    CONTENT = "content"
    KEYWORDS = "keywords"
    LINKS = "links"
    SCHEMA = "schema"
    PERFORMANCE = "performance"


@dataclass
class Recommendation:
    """Estructura de una recomendación"""
    title: str
    description: str
    priority: Priority
    category: Category
    impact_score: float  # 0-100
    effort_score: float  # 0-100 (mayor = más esfuerzo)
    affected_pages: int
    action_items: List[str]
    expected_results: List[str]


class RecommendationsEngine:
    """
    Motor inteligente de recomendaciones SEO
    Analiza múltiples dimensiones y genera sugerencias priorizadas
    """

    def __init__(self):
        self.recommendations = []

    # ==================== GENERACIÓN DE RECOMENDACIONES ====================

    def generate_recommendations(
        self,
        technical_audit: Optional[Dict] = None,
        content_analysis: Optional[Dict] = None,
        keyword_analysis: Optional[Dict] = None,
        network_analysis: Optional[Dict] = None,
        schema_analysis: Optional[Dict] = None
    ) -> List[Recommendation]:
        """
        Genera recomendaciones basadas en múltiples análisis

        Returns:
            Lista de recomendaciones priorizadas
        """
        self.recommendations = []

        # Generar recomendaciones de cada categoría
        if technical_audit:
            self._generate_technical_recommendations(technical_audit)

        if content_analysis:
            self._generate_content_recommendations(content_analysis)

        if keyword_analysis:
            self._generate_keyword_recommendations(keyword_analysis)

        if network_analysis:
            self._generate_link_recommendations(network_analysis)

        if schema_analysis:
            self._generate_schema_recommendations(schema_analysis)

        # Ordenar por impacto/esfuerzo (Quick Wins primero)
        self.recommendations.sort(key=lambda r: (
            r.priority.value,  # Prioridad
            -(r.impact_score / max(r.effort_score, 1))  # Ratio impacto/esfuerzo (descendente)
        ))

        return self.recommendations

    # ==================== RECOMENDACIONES TÉCNICAS ====================

    def _generate_technical_recommendations(self, technical_audit: Dict):
        """Genera recomendaciones técnicas basadas en auditoría"""

        # Errores HTTP
        http_errors = technical_audit.get('http_errors', {})
        client_errors = http_errors.get('client_error_count', 0)
        server_errors = http_errors.get('server_error_count', 0)

        if client_errors > 0:
            self.recommendations.append(Recommendation(
                title=f"Corregir {client_errors} errores 404 y 4xx",
                description=f"Se detectaron {client_errors} páginas con errores de cliente (404, 403, etc.). "
                           "Estos errores perjudican la experiencia del usuario y el crawl budget.",
                priority=Priority.HIGH,
                category=Category.TECHNICAL,
                impact_score=80,
                effort_score=40,
                affected_pages=client_errors,
                action_items=[
                    "Identificar las URLs con error 404",
                    "Implementar redirects 301 a páginas relevantes",
                    "Eliminar enlaces internos a páginas 404",
                    "Crear página 404 personalizada con navegación útil"
                ],
                expected_results=[
                    "Mejor experiencia de usuario",
                    "Reducción de tasa de rebote",
                    "Mejor distribución de PageRank interno"
                ]
            ))

        if server_errors > 0:
            self.recommendations.append(Recommendation(
                title=f"CRÍTICO: Resolver {server_errors} errores 500 de servidor",
                description=f"Se detectaron {server_errors} páginas con errores de servidor. "
                           "Estos errores impiden la indexación y afectan gravemente al SEO.",
                priority=Priority.CRITICAL,
                category=Category.TECHNICAL,
                impact_score=100,
                effort_score=60,
                affected_pages=server_errors,
                action_items=[
                    "Revisar logs del servidor para identificar causa",
                    "Corregir errores de código o configuración",
                    "Implementar monitoring para detectar errores futuros",
                    "Verificar disponibilidad del servidor"
                ],
                expected_results=[
                    "Páginas correctamente indexables",
                    "Mejora drástica en crawl rate",
                    "Recuperación de rankings perdidos"
                ]
            ))

        # Meta tags
        meta_tags = technical_audit.get('meta_tags', {})
        duplicate_titles = meta_tags.get('duplicates', {}).get('duplicate_titles_count', 0)
        duplicate_descriptions = meta_tags.get('duplicates', {}).get('duplicate_descriptions_count', 0)
        missing_titles = meta_tags.get('missing', {}).get('missing_titles_count', 0)
        missing_descriptions = meta_tags.get('missing', {}).get('missing_descriptions_count', 0)

        if missing_titles > 0:
            self.recommendations.append(Recommendation(
                title=f"Agregar títulos faltantes en {missing_titles} páginas",
                description="El title tag es uno de los factores de ranking más importantes. "
                           "Páginas sin título tienen muy baja probabilidad de rankear.",
                priority=Priority.CRITICAL,
                category=Category.TECHNICAL,
                impact_score=100,
                effort_score=20,
                affected_pages=missing_titles,
                action_items=[
                    "Identificar páginas sin title tag",
                    "Crear títulos únicos y descriptivos (30-60 caracteres)",
                    "Incluir keyword objetivo al inicio del título",
                    "Asegurar que sean atractivos para CTR"
                ],
                expected_results=[
                    "Páginas elegibles para rankear",
                    "Mejora significativa en CTR",
                    "Mayor visibilidad en SERPs"
                ]
            ))

        if duplicate_titles > 5:
            self.recommendations.append(Recommendation(
                title=f"Eliminar títulos duplicados en {duplicate_titles} páginas",
                description="Títulos duplicados confunden a Google sobre qué página rankear para cada término.",
                priority=Priority.HIGH,
                category=Category.TECHNICAL,
                impact_score=75,
                effort_score=40,
                affected_pages=duplicate_titles,
                action_items=[
                    "Auditar páginas con títulos duplicados",
                    "Crear títulos únicos para cada página",
                    "Incluir diferenciadores (ubicación, categoría, etc.)",
                    "Priorizar páginas importantes primero"
                ],
                expected_results=[
                    "Reducción de canibalización",
                    "Mejor CTR en SERPs",
                    "Rankings más claros por keyword"
                ]
            ))

        if missing_descriptions > duplicate_descriptions:
            self.recommendations.append(Recommendation(
                title=f"Agregar meta descriptions en {missing_descriptions} páginas",
                description="Aunque no es factor directo de ranking, la meta description afecta el CTR en resultados de búsqueda.",
                priority=Priority.MEDIUM,
                category=Category.TECHNICAL,
                impact_score=60,
                effort_score=30,
                affected_pages=missing_descriptions,
                action_items=[
                    "Escribir descriptions únicas de 120-160 caracteres",
                    "Incluir llamada a la acción",
                    "Incorporar keyword objetivo naturalmente",
                    "Hacer que sean atractivas y relevantes"
                ],
                expected_results=[
                    "Aumento de 5-15% en CTR",
                    "Mejor presentación en SERPs",
                    "Mayor control sobre snippets"
                ]
            ))

        # Indexabilidad
        indexability = technical_audit.get('indexability', {})
        non_indexable = indexability.get('non_indexable_count', 0)
        noindex_count = indexability.get('noindex_count', 0)

        if noindex_count > 0:
            self.recommendations.append(Recommendation(
                title=f"Revisar {noindex_count} páginas con noindex",
                description="Verifica que las páginas con noindex realmente deban estar bloqueadas de indexación.",
                priority=Priority.HIGH,
                category=Category.TECHNICAL,
                impact_score=70,
                effort_score=25,
                affected_pages=noindex_count,
                action_items=[
                    "Auditar páginas con robots noindex",
                    "Verificar si el noindex es intencional",
                    "Remover noindex de páginas importantes",
                    "Confirmar canonical apunta a versión indexable"
                ],
                expected_results=[
                    "Más páginas indexables",
                    "Potencial aumento de tráfico orgánico",
                    "Mejor cobertura en Google"
                ]
            ))

        # Imágenes
        images = technical_audit.get('images', {})
        missing_alt = images.get('missing_alt_count', 0)
        total_images = images.get('total_images', 1)

        if missing_alt > 0 and (missing_alt / total_images) > 0.3:
            self.recommendations.append(Recommendation(
                title=f"Agregar alt text a {missing_alt} imágenes",
                description="Los alt tags son esenciales para accesibilidad y SEO de imágenes.",
                priority=Priority.MEDIUM,
                category=Category.TECHNICAL,
                impact_score=50,
                effort_score=35,
                affected_pages=missing_alt,
                action_items=[
                    "Identificar imágenes sin alt text",
                    "Escribir descripciones descriptivas y concisas",
                    "Incluir keywords cuando sea relevante",
                    "Evitar 'image.jpg' o descripciones genéricas"
                ],
                expected_results=[
                    "Mejor ranking en Google Imágenes",
                    "Accesibilidad mejorada",
                    "Contexto adicional para Google"
                ]
            ))

        # Canonical
        canonical = technical_audit.get('canonical', {})
        missing_canonical = canonical.get('missing_count', 0)

        if missing_canonical > 0:
            self.recommendations.append(Recommendation(
                title=f"Implementar canonical tags en {missing_canonical} páginas",
                description="Los canonical tags ayudan a prevenir contenido duplicado y consolidar señales de ranking.",
                priority=Priority.MEDIUM,
                category=Category.TECHNICAL,
                impact_score=65,
                effort_score=30,
                affected_pages=missing_canonical,
                action_items=[
                    "Agregar self-canonical a todas las páginas",
                    "Verificar que apunten a la versión correcta (HTTP/HTTPS, www/non-www)",
                    "Implementar canónicos dinámicos si hay parámetros URL",
                    "Validar que sean URLs absolutas, no relativas"
                ],
                expected_results=[
                    "Prevención de contenido duplicado",
                    "Consolidación de autoridad de página",
                    "Señales de ranking más fuertes"
                ]
            ))

    # ==================== RECOMENDACIONES DE CONTENIDO ====================

    def _generate_content_recommendations(self, content_analysis: Dict):
        """Genera recomendaciones de calidad de contenido"""

        # Thin content
        thin_content_pages = []
        quality_scores = content_analysis.get('quality_scores', [])

        for page_quality in quality_scores:
            if page_quality.get('is_thin_content', False):
                thin_content_pages.append(page_quality)

        if len(thin_content_pages) > 0:
            self.recommendations.append(Recommendation(
                title=f"Expandir {len(thin_content_pages)} páginas con thin content",
                description="Páginas con menos de 300 palabras suelen tener dificultades para rankear. "
                           "Google prefiere contenido exhaustivo y útil.",
                priority=Priority.HIGH,
                category=Category.CONTENT,
                impact_score=75,
                effort_score=70,
                affected_pages=len(thin_content_pages),
                action_items=[
                    "Expandir contenido a mínimo 500-800 palabras",
                    "Agregar información útil y relevante",
                    "Incluir ejemplos, casos de uso, FAQs",
                    "Considerar consolidar páginas muy similares"
                ],
                expected_results=[
                    "Mayor tiempo en página",
                    "Mejor ranking para long-tail keywords",
                    "Reducción de tasa de rebote"
                ]
            ))

        # Baja legibilidad
        low_readability = [p for p in quality_scores if p.get('readability_score', 100) < 40]

        if len(low_readability) > 5:
            self.recommendations.append(Recommendation(
                title=f"Mejorar legibilidad en {len(low_readability)} páginas",
                description="Contenido difícil de leer aumenta la tasa de rebote y reduce el engagement.",
                priority=Priority.MEDIUM,
                category=Category.CONTENT,
                impact_score=55,
                effort_score=50,
                affected_pages=len(low_readability),
                action_items=[
                    "Acortar oraciones y párrafos",
                    "Usar subtítulos (H2, H3) para organizar contenido",
                    "Agregar listas con viñetas",
                    "Simplificar vocabulario cuando sea posible"
                ],
                expected_results=[
                    "Mayor tiempo en página",
                    "Mejor experiencia de usuario",
                    "Posible mejora en engagement signals"
                ]
            ))

        # Baja calidad general
        low_quality = [p for p in quality_scores if p.get('quality_score', 100) < 50]

        if len(low_quality) > 10:
            self.recommendations.append(Recommendation(
                title=f"Mejorar calidad general en {len(low_quality)} páginas",
                description="Páginas con bajo quality score necesitan optimización integral.",
                priority=Priority.MEDIUM,
                category=Category.CONTENT,
                impact_score=70,
                effort_score=80,
                affected_pages=len(low_quality),
                action_items=[
                    "Revisar y mejorar factores de calidad: extensión, legibilidad, estructura",
                    "Agregar imágenes y multimedia relevante",
                    "Optimizar meta tags y headings",
                    "Aumentar enlaces internos relevantes"
                ],
                expected_results=[
                    "Mejor posicionamiento general",
                    "Mayor autoridad percibida",
                    "Mejores métricas de engagement"
                ]
            ))

    # ==================== RECOMENDACIONES DE KEYWORDS ====================

    def _generate_keyword_recommendations(self, keyword_analysis: Dict):
        """Genera recomendaciones basadas en análisis de keywords"""

        # Quick wins (keywords con alta oportunidad y baja dificultad)
        quick_wins = keyword_analysis.get('quick_wins', [])

        if len(quick_wins) > 0:
            self.recommendations.append(Recommendation(
                title=f"🎯 QUICK WINS: Optimizar para {len(quick_wins)} keywords de oportunidad",
                description="Keywords con alta oportunidad y baja dificultad. Alto ROI potencial.",
                priority=Priority.HIGH,
                category=Category.KEYWORDS,
                impact_score=90,
                effort_score=30,
                affected_pages=len(quick_wins),
                action_items=[
                    "Priorizar estas keywords en creación de contenido",
                    "Optimizar páginas existentes para estos términos",
                    "Crear contenido específico si no existe",
                    "Construir enlaces internos con estos anchor texts"
                ],
                expected_results=[
                    "Rankings rápidos (1-3 meses)",
                    "Tráfico incremental con bajo esfuerzo",
                    "Momentum positivo para SEO"
                ]
            ))

        # Keyword gaps
        gaps = keyword_analysis.get('keyword_gaps', [])

        if len(gaps) > 0:
            self.recommendations.append(Recommendation(
                title=f"Cerrar gaps con competidores en {len(gaps)} keywords",
                description="Keywords donde los competidores rankean pero tu sitio no.",
                priority=Priority.MEDIUM,
                category=Category.KEYWORDS,
                impact_score=75,
                effort_score=60,
                affected_pages=0,
                action_items=[
                    "Analizar contenido de competidores para estos términos",
                    "Crear contenido superior (más completo, actualizado, útil)",
                    "Optimizar on-page SEO para estas keywords",
                    "Construir enlaces a estas páginas nuevas"
                ],
                expected_results=[
                    "Captura de tráfico de competidores",
                    "Expansión de cobertura de keywords",
                    "Mayor share of voice en tu nicho"
                ]
            ))

        # Keyword cannibalization
        cannibalization = keyword_analysis.get('cannibalization', [])

        if len(cannibalization) > 5:
            self.recommendations.append(Recommendation(
                title=f"Resolver canibalización en {len(cannibalization)} keywords",
                description="Múltiples páginas compitiendo por el mismo término reducen el potencial de ranking.",
                priority=Priority.MEDIUM,
                category=Category.KEYWORDS,
                impact_score=70,
                effort_score=55,
                affected_pages=len(cannibalization) * 2,
                action_items=[
                    "Identificar la página principal para cada keyword",
                    "Consolidar contenido similar en una página",
                    "Usar canonical o redirects 301 para duplicados",
                    "Diferenciar páginas con keywords relacionadas pero distintas"
                ],
                expected_results=[
                    "Rankings más fuertes y estables",
                    "Reducción de confusión para Google",
                    "Mejor distribución de autoridad"
                ]
            ))

    # ==================== RECOMENDACIONES DE ENLACES ====================

    def _generate_link_recommendations(self, network_analysis: Dict):
        """Genera recomendaciones de estructura de enlaces"""

        # Páginas huérfanas
        orphan_pages = network_analysis.get('orphan_pages', [])

        if len(orphan_pages) > 0:
            self.recommendations.append(Recommendation(
                title=f"Conectar {len(orphan_pages)} páginas huérfanas",
                description="Páginas sin enlaces internos son difíciles de descubrir para Google y usuarios.",
                priority=Priority.HIGH,
                category=Category.LINKS,
                impact_score=80,
                effort_score=35,
                affected_pages=len(orphan_pages),
                action_items=[
                    "Identificar páginas relevantes para enlazar a huérfanas",
                    "Agregar enlaces contextuales con anchor text descriptivo",
                    "Incluir en navegación o sidebar si son importantes",
                    "Considerar eliminar si no aportan valor"
                ],
                expected_results=[
                    "Mejor crawlability",
                    "Distribución de PageRank interno",
                    "Posible indexación de páginas olvidadas"
                ]
            ))

        # Broken links
        broken_links = network_analysis.get('broken_links', [])

        if len(broken_links) > 0:
            self.recommendations.append(Recommendation(
                title=f"Corregir {len(broken_links)} enlaces rotos",
                description="Enlaces internos rotos crean mala experiencia y desperdician link equity.",
                priority=Priority.HIGH,
                category=Category.LINKS,
                impact_score=65,
                effort_score=25,
                affected_pages=len(broken_links),
                action_items=[
                    "Identificar enlaces que apuntan a 404",
                    "Actualizar URLs o implementar redirects 301",
                    "Verificar enlaces después de modificaciones",
                    "Implementar monitoring de broken links"
                ],
                expected_results=[
                    "Mejor experiencia de usuario",
                    "Preservación de PageRank interno",
                    "Sitio más profesional y mantenido"
                ]
            ))

        # Distribución de PageRank
        pagerank_data = network_analysis.get('pagerank', {})
        top_pages = pagerank_data.get('top_pages', [])

        if len(top_pages) > 0:
            self.recommendations.append(Recommendation(
                title="Optimizar distribución de PageRank interno",
                description="Usa el PageRank interno para potenciar páginas estratégicas.",
                priority=Priority.MEDIUM,
                category=Category.LINKS,
                impact_score=70,
                effort_score=45,
                affected_pages=10,
                action_items=[
                    "Identificar páginas con alto PageRank interno",
                    "Agregar enlaces desde estas páginas a páginas objetivo",
                    "Reducir enlaces salientes en páginas de alto valor",
                    "Crear hub pages que distribuyan autoridad estratégicamente"
                ],
                expected_results=[
                    "Mejor ranking de páginas objetivo",
                    "Uso eficiente de autoridad interna",
                    "Arquitectura de enlaces más efectiva"
                ]
            ))

    # ==================== RECOMENDACIONES DE SCHEMA ====================

    def _generate_schema_recommendations(self, schema_analysis: Dict):
        """Genera recomendaciones de datos estructurados"""

        schema_data = schema_analysis.get('schema_analysis', {})
        social_data = schema_analysis.get('social_metadata', {})

        pages_without_schema = schema_data.get('pages_without_schema_count', 0)
        pages_without_og = social_data.get('pages_without_social_count', 0)

        if pages_without_schema > 0:
            self.recommendations.append(Recommendation(
                title=f"Implementar schema markup en {pages_without_schema} páginas",
                description="Schema markup mejora los rich snippets y la visibilidad en SERPs.",
                priority=Priority.MEDIUM,
                category=Category.SCHEMA,
                impact_score=65,
                effort_score=50,
                affected_pages=pages_without_schema,
                action_items=[
                    "Identificar tipos de schema apropiados (Article, Product, etc.)",
                    "Implementar JSON-LD en páginas clave",
                    "Validar con Google Rich Results Test",
                    "Monitorear aparición de rich snippets en GSC"
                ],
                expected_results=[
                    "Rich snippets en SERPs",
                    "Mayor CTR (hasta 30% más)",
                    "Mejor presentación en resultados de búsqueda"
                ]
            ))

        if pages_without_og > 0:
            self.recommendations.append(Recommendation(
                title=f"Agregar Open Graph tags en {pages_without_og} páginas",
                description="Open Graph mejora la apariencia cuando se comparte en redes sociales.",
                priority=Priority.LOW,
                category=Category.SCHEMA,
                impact_score=45,
                effort_score=30,
                affected_pages=pages_without_og,
                action_items=[
                    "Agregar og:title, og:description, og:image, og:url",
                    "Usar imágenes optimizadas (1200x630px)",
                    "Validar con Facebook Debugger",
                    "Incluir también Twitter Cards"
                ],
                expected_results=[
                    "Mejor apariencia en shares sociales",
                    "Mayor CTR desde redes sociales",
                    "Más compartidos y engagement"
                ]
            ))

    # ==================== ROADMAP Y PRIORIZACIÓN ====================

    def generate_roadmap(self, recommendations: List[Recommendation]) -> Dict:
        """
        Genera roadmap de implementación por fases

        Returns:
            Dict con fases de implementación
        """
        critical = [r for r in recommendations if r.priority == Priority.CRITICAL]
        high = [r for r in recommendations if r.priority == Priority.HIGH]
        medium = [r for r in recommendations if r.priority == Priority.MEDIUM]
        low = [r for r in recommendations if r.priority == Priority.LOW]

        # Quick wins (alto impacto, bajo esfuerzo)
        quick_wins = [r for r in recommendations if r.impact_score > 70 and r.effort_score < 40]

        return {
            'phase_1_critical': {
                'title': 'FASE 1: Issues Críticos (Semana 1)',
                'recommendations': critical,
                'count': len(critical)
            },
            'phase_2_quick_wins': {
                'title': 'FASE 2: Quick Wins (Semanas 2-3)',
                'recommendations': quick_wins,
                'count': len(quick_wins)
            },
            'phase_3_high_priority': {
                'title': 'FASE 3: Alta Prioridad (Mes 1-2)',
                'recommendations': high,
                'count': len(high)
            },
            'phase_4_medium_priority': {
                'title': 'FASE 4: Prioridad Media (Mes 2-3)',
                'recommendations': medium,
                'count': len(medium)
            },
            'phase_5_optimization': {
                'title': 'FASE 5: Optimización Continua (Ongoing)',
                'recommendations': low,
                'count': len(low)
            }
        }

    def format_recommendations_report(self, recommendations: List[Recommendation]) -> str:
        """
        Genera reporte formateado de recomendaciones

        Returns:
            String con reporte completo
        """
        report = []
        report.append("=" * 100)
        report.append("RECOMENDACIONES SEO PRIORIZADAS")
        report.append("=" * 100)
        report.append(f"\nTotal de recomendaciones: {len(recommendations)}\n")

        # Agrupar por prioridad
        by_priority = defaultdict(list)
        for rec in recommendations:
            by_priority[rec.priority].append(rec)

        # Orden de prioridades
        priorities = [Priority.CRITICAL, Priority.HIGH, Priority.MEDIUM, Priority.LOW]

        for priority in priorities:
            recs = by_priority.get(priority, [])
            if not recs:
                continue

            report.append("\n" + "=" * 100)
            report.append(f"{priority.value.upper()} - {len(recs)} recomendaciones")
            report.append("=" * 100)

            for i, rec in enumerate(recs, 1):
                report.append(f"\n{i}. {rec.title}")
                report.append(f"   Categoría: {rec.category.value} | Páginas afectadas: {rec.affected_pages}")
                report.append(f"   Impacto: {rec.impact_score}/100 | Esfuerzo: {rec.effort_score}/100 | ROI: {rec.impact_score/max(rec.effort_score, 1):.2f}")
                report.append(f"\n   {rec.description}")

                report.append("\n   📋 Acciones a tomar:")
                for action in rec.action_items:
                    report.append(f"      • {action}")

                report.append("\n   ✅ Resultados esperados:")
                for result in rec.expected_results:
                    report.append(f"      • {result}")

                report.append("")

        report.append("\n" + "=" * 100)
        return "\n".join(report)
