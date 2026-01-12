"""
Análisis competitivo de keywords.

Este módulo implementa análisis competitivo avanzado:
- Keyword Gap Analysis (keywords del competidor que no tienes)
- Keyword Overlap Analysis (keywords compartidas)
- Competitive Matrix (comparación de métricas)
- Content Gap Analysis (tópicos sin cubrir)
- Positioning Analysis (fortalezas y debilidades)
"""

import logging
from typing import List, Dict, Any, Set, Tuple, Optional
from collections import defaultdict, Counter
import statistics

logger = logging.getLogger(__name__)


class CompetitiveAnalyzer:
    """
    Analizador competitivo de keywords y contenido.
    """

    def __init__(self):
        """Inicializa el analizador competitivo."""
        pass

    # ==================== KEYWORD GAP ANALYSIS ====================

    def find_keyword_gaps(
        self,
        own_keywords: List[Dict[str, Any]],
        competitor_keywords: List[Dict[str, Any]],
        min_tfidf: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Identifica keywords que tiene el competidor pero tú no.

        Args:
            own_keywords: Tus keywords
            competitor_keywords: Keywords del competidor
            min_tfidf: TF-IDF mínimo para considerar la keyword relevante

        Returns:
            Lista de keyword gaps (oportunidades)
        """
        # Extraer sets de keywords
        own_kw_set = set(kw.get('keyword', '').lower() for kw in own_keywords)

        # Filtrar keywords del competidor por TF-IDF
        competitor_relevant = [
            kw for kw in competitor_keywords
            if kw.get('tf_idf_score', 0.0) >= min_tfidf
        ]

        gaps = []
        for comp_kw in competitor_relevant:
            keyword_text = comp_kw.get('keyword', '').lower()

            # Si no tenemos esta keyword, es un gap
            if keyword_text not in own_kw_set:
                gaps.append({
                    'keyword': keyword_text,
                    'competitor_tfidf': comp_kw.get('tf_idf_score', 0.0),
                    'competitor_frequency': comp_kw.get('frequency', 0),
                    'competitor_pages': 1,  # Ajustar si tienes datos de múltiples páginas
                    'gap_type': 'missing',
                    'priority': self._calculate_gap_priority(comp_kw)
                })

        # Ordenar por prioridad
        gaps.sort(key=lambda x: x['priority'], reverse=True)

        return gaps

    def _calculate_gap_priority(self, keyword: Dict[str, Any]) -> float:
        """
        Calcula la prioridad de un keyword gap.

        Args:
            keyword: Datos de la keyword del competidor

        Returns:
            Score de prioridad (0-100)
        """
        tfidf = keyword.get('tf_idf_score', 0.0)
        frequency = keyword.get('frequency', 0)
        in_title = keyword.get('position_in_title', False)
        in_h1 = keyword.get('position_in_h1', False)

        # Calcular prioridad ponderada
        priority = (
            tfidf * 40 +  # TF-IDF es el factor más importante
            min(frequency / 10, 10) * 20 +  # Frecuencia (normalizada)
            (30 if in_title else 0) +  # Presencia en título
            (10 if in_h1 else 0)  # Presencia en H1
        )

        return min(priority, 100)

    # ==================== KEYWORD OVERLAP ANALYSIS ====================

    def analyze_keyword_overlap(
        self,
        own_keywords: List[Dict[str, Any]],
        competitor_keywords: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analiza el overlap de keywords entre tú y el competidor.

        Args:
            own_keywords: Tus keywords
            competitor_keywords: Keywords del competidor

        Returns:
            Diccionario con análisis de overlap
        """
        # Crear diccionarios keyword -> datos
        own_kw_dict = {
            kw.get('keyword', '').lower(): kw
            for kw in own_keywords
        }

        comp_kw_dict = {
            kw.get('keyword', '').lower(): kw
            for kw in competitor_keywords
        }

        # Keywords compartidas
        shared_keywords = set(own_kw_dict.keys()) & set(comp_kw_dict.keys())

        # Keywords únicas
        own_unique = set(own_kw_dict.keys()) - set(comp_kw_dict.keys())
        comp_unique = set(comp_kw_dict.keys()) - set(own_kw_dict.keys())

        # Analizar keywords compartidas
        shared_analysis = []
        for keyword in shared_keywords:
            own_data = own_kw_dict[keyword]
            comp_data = comp_kw_dict[keyword]

            # Comparar métricas
            own_tfidf = own_data.get('tf_idf_score', 0.0)
            comp_tfidf = comp_data.get('tf_idf_score', 0.0)

            advantage = 'yours' if own_tfidf > comp_tfidf else 'competitor'
            tfidf_diff = abs(own_tfidf - comp_tfidf)

            shared_analysis.append({
                'keyword': keyword,
                'your_tfidf': own_tfidf,
                'competitor_tfidf': comp_tfidf,
                'tfidf_difference': tfidf_diff,
                'advantage': advantage,
                'your_frequency': own_data.get('frequency', 0),
                'competitor_frequency': comp_data.get('frequency', 0)
            })

        # Ordenar por diferencia de TF-IDF (mayores oportunidades primero)
        shared_analysis.sort(key=lambda x: x['tfidf_difference'], reverse=True)

        return {
            'total_own_keywords': len(own_kw_dict),
            'total_competitor_keywords': len(comp_kw_dict),
            'shared_keywords_count': len(shared_keywords),
            'own_unique_count': len(own_unique),
            'competitor_unique_count': len(comp_unique),
            'overlap_percentage': round(len(shared_keywords) / max(len(own_kw_dict), 1) * 100, 2),
            'shared_keywords': shared_analysis[:50],  # Top 50
            'own_unique_keywords': list(own_unique)[:30],
            'competitor_unique_keywords': list(comp_unique)[:30]
        }

    # ==================== COMPETITIVE MATRIX ====================

    def create_competitive_matrix(
        self,
        sessions_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Crea una matriz comparativa entre múltiples sesiones/sitios.

        Args:
            sessions_data: Lista de sesiones con sus keywords

        Returns:
            Matriz competitiva con métricas comparadas
        """
        if not sessions_data:
            return {}

        matrix = {
            'sessions': [],
            'comparison': {
                'total_keywords': [],
                'unique_keywords': [],
                'avg_tfidf': [],
                'avg_frequency': [],
                'keywords_in_title': [],
                'keywords_in_h1': []
            }
        }

        for session in sessions_data:
            session_id = session.get('session_id')
            session_name = session.get('name', f"Session {session_id}")
            keywords = session.get('keywords', [])

            if not keywords:
                continue

            # Calcular métricas
            unique_kw = set(kw.get('keyword', '') for kw in keywords)
            avg_tfidf = statistics.mean(kw.get('tf_idf_score', 0.0) for kw in keywords)
            avg_freq = statistics.mean(kw.get('frequency', 0) for kw in keywords)
            kw_in_title = sum(1 for kw in keywords if kw.get('position_in_title', False))
            kw_in_h1 = sum(1 for kw in keywords if kw.get('position_in_h1', False))

            matrix['sessions'].append(session_name)
            matrix['comparison']['total_keywords'].append(len(keywords))
            matrix['comparison']['unique_keywords'].append(len(unique_kw))
            matrix['comparison']['avg_tfidf'].append(round(avg_tfidf, 3))
            matrix['comparison']['avg_frequency'].append(round(avg_freq, 2))
            matrix['comparison']['keywords_in_title'].append(kw_in_title)
            matrix['comparison']['keywords_in_h1'].append(kw_in_h1)

        return matrix

    # ==================== CONTENT GAP ANALYSIS ====================

    def analyze_content_gaps(
        self,
        own_pages: List[Dict[str, Any]],
        competitor_pages: List[Dict[str, Any]],
        own_topics: List[Dict[str, Any]],
        competitor_topics: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analiza gaps de contenido basándose en tópicos y estructura.

        Args:
            own_pages: Tus páginas
            competitor_pages: Páginas del competidor
            own_topics: Tus tópicos identificados
            competitor_topics: Tópicos del competidor

        Returns:
            Análisis de content gaps
        """
        # Extraer tópicos
        own_topic_names = set(t.get('topic_name', '') for t in own_topics)
        comp_topic_names = set(t.get('topic_name', '') for t in competitor_topics)

        # Tópicos que el competidor cubre y tú no
        missing_topics = comp_topic_names - own_topic_names

        # Analizar estructura de contenido
        own_avg_word_count = statistics.mean(
            p.get('word_count', 0) for p in own_pages
        ) if own_pages else 0

        comp_avg_word_count = statistics.mean(
            p.get('word_count', 0) for p in competitor_pages
        ) if competitor_pages else 0

        # Analizar profundidad de contenido
        own_depth_dist = self._analyze_depth_distribution(own_pages)
        comp_depth_dist = self._analyze_depth_distribution(competitor_pages)

        return {
            'missing_topics': list(missing_topics),
            'missing_topics_count': len(missing_topics),
            'own_avg_word_count': round(own_avg_word_count, 2),
            'competitor_avg_word_count': round(comp_avg_word_count, 2),
            'word_count_gap': round(comp_avg_word_count - own_avg_word_count, 2),
            'own_total_pages': len(own_pages),
            'competitor_total_pages': len(competitor_pages),
            'own_depth_distribution': own_depth_dist,
            'competitor_depth_distribution': comp_depth_dist,
            'recommendations': self._generate_content_recommendations(
                own_avg_word_count,
                comp_avg_word_count,
                len(own_pages),
                len(competitor_pages),
                missing_topics
            )
        }

    def _analyze_depth_distribution(self, pages: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Analiza la distribución de profundidad de páginas.

        Args:
            pages: Lista de páginas

        Returns:
            Distribución por nivel de profundidad
        """
        depth_counts = Counter(p.get('depth', 0) for p in pages)
        return dict(depth_counts)

    def _generate_content_recommendations(
        self,
        own_word_count: float,
        comp_word_count: float,
        own_pages: int,
        comp_pages: int,
        missing_topics: Set[str]
    ) -> List[str]:
        """
        Genera recomendaciones basadas en content gaps.

        Args:
            own_word_count: Tu word count promedio
            comp_word_count: Word count promedio del competidor
            own_pages: Número de tus páginas
            comp_pages: Número de páginas del competidor
            missing_topics: Tópicos que te faltan

        Returns:
            Lista de recomendaciones
        """
        recommendations = []

        # Recomendación por word count
        if comp_word_count > own_word_count * 1.2:
            gap = comp_word_count - own_word_count
            recommendations.append(
                f"Aumenta la profundidad del contenido. El competidor tiene ~{gap:.0f} palabras más por página en promedio."
            )

        # Recomendación por número de páginas
        if comp_pages > own_pages * 1.5:
            recommendations.append(
                f"Crea más contenido. El competidor tiene {comp_pages} páginas vs tus {own_pages}."
            )

        # Recomendación por tópicos
        if missing_topics:
            recommendations.append(
                f"Cubre {len(missing_topics)} tópicos nuevos que el competidor ya tiene."
            )

        return recommendations

    # ==================== POSITIONING ANALYSIS ====================

    def analyze_competitive_position(
        self,
        own_keywords: List[Dict[str, Any]],
        competitor_keywords: List[Dict[str, Any]],
        own_pages: List[Dict[str, Any]],
        competitor_pages: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analiza el posicionamiento competitivo general.

        Args:
            own_keywords: Tus keywords
            competitor_keywords: Keywords del competidor
            own_pages: Tus páginas
            competitor_pages: Páginas del competidor

        Returns:
            Análisis de posicionamiento
        """
        # Métricas propias
        own_metrics = self._calculate_site_metrics(own_keywords, own_pages)

        # Métricas del competidor
        comp_metrics = self._calculate_site_metrics(competitor_keywords, competitor_pages)

        # Comparación
        strengths = []
        weaknesses = []

        # Comparar cada métrica
        if own_metrics['avg_tfidf'] > comp_metrics['avg_tfidf']:
            strengths.append("Mayor relevancia de keywords (TF-IDF superior)")
        else:
            weaknesses.append("Menor relevancia de keywords vs competidor")

        if own_metrics['keyword_optimization'] > comp_metrics['keyword_optimization']:
            strengths.append("Mejor optimización de keywords en títulos/H1")
        else:
            weaknesses.append("Peor optimización de keywords vs competidor")

        if own_metrics['content_depth'] > comp_metrics['content_depth']:
            strengths.append("Mayor profundidad de contenido")
        else:
            weaknesses.append("Menor profundidad de contenido vs competidor")

        if own_metrics['total_keywords'] > comp_metrics['total_keywords']:
            strengths.append("Mayor cobertura de keywords")
        else:
            weaknesses.append("Menor cobertura de keywords vs competidor")

        # Score competitivo general (0-100)
        competitive_score = self._calculate_competitive_score(own_metrics, comp_metrics)

        return {
            'competitive_score': competitive_score,
            'your_metrics': own_metrics,
            'competitor_metrics': comp_metrics,
            'strengths': strengths,
            'weaknesses': weaknesses,
            'overall_position': self._determine_position(competitive_score)
        }

    def _calculate_site_metrics(
        self,
        keywords: List[Dict[str, Any]],
        pages: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calcula métricas agregadas de un sitio.

        Args:
            keywords: Keywords del sitio
            pages: Páginas del sitio

        Returns:
            Diccionario con métricas
        """
        if not keywords:
            return {
                'total_keywords': 0,
                'unique_keywords': 0,
                'avg_tfidf': 0.0,
                'keyword_optimization': 0.0,
                'content_depth': 0.0
            }

        # Total y únicas
        unique_kw = set(kw.get('keyword', '') for kw in keywords)

        # TF-IDF promedio
        avg_tfidf = statistics.mean(kw.get('tf_idf_score', 0.0) for kw in keywords)

        # Optimización (% en títulos/H1)
        in_title = sum(1 for kw in keywords if kw.get('position_in_title', False))
        in_h1 = sum(1 for kw in keywords if kw.get('position_in_h1', False))
        keyword_optimization = (in_title + in_h1) / (len(keywords) * 2) * 100

        # Profundidad de contenido
        content_depth = statistics.mean(
            p.get('word_count', 0) for p in pages
        ) if pages else 0

        return {
            'total_keywords': len(keywords),
            'unique_keywords': len(unique_kw),
            'avg_tfidf': round(avg_tfidf, 3),
            'keyword_optimization': round(keyword_optimization, 2),
            'content_depth': round(content_depth, 2)
        }

    def _calculate_competitive_score(
        self,
        own_metrics: Dict[str, Any],
        comp_metrics: Dict[str, Any]
    ) -> float:
        """
        Calcula un score competitivo comparativo (0-100).

        Args:
            own_metrics: Tus métricas
            comp_metrics: Métricas del competidor

        Returns:
            Score competitivo
        """
        scores = []

        # Comparar TF-IDF
        if comp_metrics['avg_tfidf'] > 0:
            tfidf_ratio = own_metrics['avg_tfidf'] / comp_metrics['avg_tfidf']
            scores.append(min(tfidf_ratio * 50, 100))

        # Comparar optimización
        if comp_metrics['keyword_optimization'] > 0:
            opt_ratio = own_metrics['keyword_optimization'] / comp_metrics['keyword_optimization']
            scores.append(min(opt_ratio * 50, 100))

        # Comparar profundidad
        if comp_metrics['content_depth'] > 0:
            depth_ratio = own_metrics['content_depth'] / comp_metrics['content_depth']
            scores.append(min(depth_ratio * 50, 100))

        # Comparar cobertura
        if comp_metrics['total_keywords'] > 0:
            coverage_ratio = own_metrics['total_keywords'] / comp_metrics['total_keywords']
            scores.append(min(coverage_ratio * 50, 100))

        return round(statistics.mean(scores) if scores else 50, 2)

    def _determine_position(self, competitive_score: float) -> str:
        """
        Determina la posición competitiva basándose en el score.

        Args:
            competitive_score: Score competitivo (0-100)

        Returns:
            Descripción de la posición
        """
        if competitive_score >= 80:
            return "Leader - Superas al competidor en la mayoría de métricas"
        elif competitive_score >= 60:
            return "Strong - Competitivo, con algunas ventajas"
        elif competitive_score >= 40:
            return "Average - A la par con el competidor"
        elif competitive_score >= 20:
            return "Challenger - Por debajo del competidor, requiere mejoras"
        else:
            return "Weak - Significativamente por debajo del competidor"

    # ==================== QUICK WINS ====================

    def identify_quick_wins(
        self,
        keyword_gaps: List[Dict[str, Any]],
        overlap_analysis: Dict[str, Any],
        difficulty_data: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        """
        Identifica quick wins (oportunidades fáciles de implementar).

        Args:
            keyword_gaps: Keywords gaps identificados
            overlap_analysis: Análisis de overlap
            difficulty_data: Datos de dificultad de keywords (opcional)

        Returns:
            Lista de quick wins priorizados
        """
        quick_wins = []

        # Quick win 1: Gaps de alta prioridad y (probablemente) baja dificultad
        high_priority_gaps = [
            gap for gap in keyword_gaps
            if gap.get('priority', 0) > 70
        ][:10]

        for gap in high_priority_gaps:
            quick_wins.append({
                'type': 'keyword_gap',
                'keyword': gap['keyword'],
                'priority': gap['priority'],
                'action': f"Crear contenido para '{gap['keyword']}'",
                'estimated_effort': 'medium',
                'potential_impact': 'high'
            })

        # Quick win 2: Keywords compartidas donde estás perdiendo
        shared_keywords = overlap_analysis.get('shared_keywords', [])
        losing_keywords = [
            kw for kw in shared_keywords
            if kw.get('advantage') == 'competitor' and kw.get('tfidf_difference', 0) > 0.5
        ][:10]

        for kw in losing_keywords:
            quick_wins.append({
                'type': 'optimization_opportunity',
                'keyword': kw['keyword'],
                'priority': 80,
                'action': f"Optimizar contenido para '{kw['keyword']}' (competidor te supera)",
                'estimated_effort': 'low',
                'potential_impact': 'high'
            })

        # Ordenar por prioridad
        quick_wins.sort(key=lambda x: x['priority'], reverse=True)

        return quick_wins[:20]  # Top 20 quick wins
