"""
Análisis de dificultad y oportunidad de keywords.

Este módulo calcula métricas profesionales para keywords:
- Keyword Difficulty Score (0-100)
- Keyword Opportunity Score (0-100)
- Detección de canibalización de keywords
- Análisis de competencia
- Métricas de densidad avanzadas
"""

import logging
import json
from typing import List, Dict, Any, Set, Tuple, Optional
from collections import defaultdict
import math

logger = logging.getLogger(__name__)


class KeywordDifficultyAnalyzer:
    """
    Analizador de dificultad y oportunidad de keywords.
    """

    def __init__(self):
        """Inicializa el analizador de dificultad."""
        # Pesos para el cálculo de difficulty score
        self.difficulty_weights = {
            'page_count': 0.30,  # Cuantas más páginas compiten, más difícil
            'avg_word_count': 0.20,  # Contenido más largo = más difícil
            'title_presence': 0.25,  # Presencia en títulos
            'h1_presence': 0.15,  # Presencia en H1
            'density': 0.10  # Densidad promedio
        }

        # Pesos para el cálculo de opportunity score
        self.opportunity_weights = {
            'tfidf_score': 0.35,  # Relevancia de la keyword
            'page_diversity': 0.25,  # Diversidad de páginas que la usan
            'low_competition': 0.20,  # Poca competencia interna
            'optimization_gaps': 0.20  # Oportunidades de mejora
        }

    # ==================== KEYWORD DIFFICULTY ====================

    def calculate_keyword_difficulty(
        self,
        keyword: str,
        keyword_data: List[Dict[str, Any]],
        all_keywords: List[Dict[str, Any]],
        pages_data: List[Dict[str, Any]]
    ) -> Tuple[float, str]:
        """
        Calcula el Keyword Difficulty Score (0-100).

        Args:
            keyword: Keyword a analizar
            keyword_data: Datos de esta keyword en diferentes páginas
            all_keywords: Todas las keywords del sitio
            pages_data: Datos de las páginas

        Returns:
            Tupla (difficulty_score, competition_level)
        """
        if not keyword_data:
            return (0.0, 'low')

        # Factor 1: Número de páginas que usan la keyword
        page_count = len(keyword_data)
        page_count_score = min(page_count / 10.0, 1.0) * 100  # Normalizar a 100

        # Factor 2: Word count promedio de páginas con esta keyword
        avg_word_count = self._calculate_avg_word_count(keyword_data, pages_data)
        # Normalizar: 2000+ palabras = alta dificultad
        word_count_score = min(avg_word_count / 2000.0, 1.0) * 100

        # Factor 3: Presencia en títulos
        pages_in_title = sum(1 for kw in keyword_data if kw.get('position_in_title', False))
        title_score = min(pages_in_title / max(page_count, 1), 1.0) * 100

        # Factor 4: Presencia en H1
        pages_in_h1 = sum(1 for kw in keyword_data if kw.get('position_in_h1', False))
        h1_score = min(pages_in_h1 / max(page_count, 1), 1.0) * 100

        # Factor 5: Densidad promedio
        avg_density = sum(kw.get('density', 0.0) for kw in keyword_data) / max(len(keyword_data), 1)
        # Alta densidad = más optimización = más difícil
        density_score = min(avg_density * 200, 100)  # 0.5 density = 100 score

        # Calcular score ponderado
        difficulty_score = (
            page_count_score * self.difficulty_weights['page_count'] +
            word_count_score * self.difficulty_weights['avg_word_count'] +
            title_score * self.difficulty_weights['title_presence'] +
            h1_score * self.difficulty_weights['h1_presence'] +
            density_score * self.difficulty_weights['density']
        )

        # Determinar nivel de competencia
        if difficulty_score < 30:
            competition_level = 'low'
        elif difficulty_score < 60:
            competition_level = 'medium'
        else:
            competition_level = 'high'

        return (round(difficulty_score, 2), competition_level)

    def _calculate_avg_word_count(
        self,
        keyword_data: List[Dict[str, Any]],
        pages_data: List[Dict[str, Any]]
    ) -> float:
        """
        Calcula el word count promedio de páginas con la keyword.

        Args:
            keyword_data: Datos de la keyword
            pages_data: Datos de páginas

        Returns:
            Word count promedio
        """
        # Crear mapa page_id -> word_count
        page_word_counts = {p['page_id']: p.get('word_count', 0) for p in pages_data}

        total_words = 0
        count = 0

        for kw in keyword_data:
            page_id = kw.get('page_id')
            if page_id in page_word_counts:
                total_words += page_word_counts[page_id]
                count += 1

        return total_words / count if count > 0 else 0.0

    # ==================== KEYWORD OPPORTUNITY ====================

    def calculate_keyword_opportunity(
        self,
        keyword: str,
        keyword_data: List[Dict[str, Any]],
        difficulty_score: float,
        pages_data: List[Dict[str, Any]]
    ) -> float:
        """
        Calcula el Keyword Opportunity Score (0-100).

        Oportunidad alta = relevancia alta + dificultad baja + gaps de optimización.

        Args:
            keyword: Keyword a analizar
            keyword_data: Datos de esta keyword
            difficulty_score: Score de dificultad calculado previamente
            pages_data: Datos de páginas

        Returns:
            Opportunity score (0-100)
        """
        if not keyword_data:
            return 0.0

        # Factor 1: TF-IDF promedio (relevancia)
        avg_tfidf = sum(kw.get('tf_idf_score', 0.0) for kw in keyword_data) / len(keyword_data)
        # Normalizar TF-IDF a 0-100
        tfidf_score = min(avg_tfidf * 20, 100)  # TF-IDF de 5 = score 100

        # Factor 2: Diversidad de páginas
        # Más páginas con la keyword = más contenido relevante = más oportunidad
        page_diversity = len(keyword_data)
        diversity_score = min(page_diversity * 10, 100)  # 10 páginas = score 100

        # Factor 3: Baja competencia (inverso de difficulty)
        low_competition_score = 100 - difficulty_score

        # Factor 4: Gaps de optimización
        # Oportunidad de mejorar títulos, H1, etc.
        optimization_gap_score = self._calculate_optimization_gaps(keyword_data)

        # Calcular opportunity score ponderado
        opportunity_score = (
            tfidf_score * self.opportunity_weights['tfidf_score'] +
            diversity_score * self.opportunity_weights['page_diversity'] +
            low_competition_score * self.opportunity_weights['low_competition'] +
            optimization_gap_score * self.opportunity_weights['optimization_gaps']
        )

        return round(opportunity_score, 2)

    def _calculate_optimization_gaps(self, keyword_data: List[Dict[str, Any]]) -> float:
        """
        Calcula oportunidades de optimización.

        Args:
            keyword_data: Datos de la keyword

        Returns:
            Gap score (0-100), donde 100 = muchas oportunidades
        """
        total_pages = len(keyword_data)
        if total_pages == 0:
            return 0.0

        # Contar páginas sin optimización
        missing_title = sum(1 for kw in keyword_data if not kw.get('position_in_title', False))
        missing_h1 = sum(1 for kw in keyword_data if not kw.get('position_in_h1', False))
        missing_first_100 = sum(1 for kw in keyword_data if not kw.get('position_in_first_100', False))

        # Calcular porcentaje de gaps
        title_gap = (missing_title / total_pages) * 100
        h1_gap = (missing_h1 / total_pages) * 100
        first_100_gap = (missing_first_100 / total_pages) * 100

        # Promedio ponderado (título es más importante)
        gap_score = (title_gap * 0.5 + h1_gap * 0.3 + first_100_gap * 0.2)

        return round(gap_score, 2)

    # ==================== KEYWORD CANNIBALIZATION ====================

    def detect_keyword_cannibalization(
        self,
        keyword: str,
        keyword_data: List[Dict[str, Any]],
        pages_data: List[Dict[str, Any]],
        threshold: float = 0.5
    ) -> Tuple[float, Optional[List[int]]]:
        """
        Detecta canibalización de keywords.

        Canibalización ocurre cuando múltiples páginas compiten por la misma keyword,
        diluyendo la autoridad.

        Args:
            keyword: Keyword a analizar
            keyword_data: Datos de la keyword en diferentes páginas
            pages_data: Datos de las páginas
            threshold: Umbral para detectar canibalización (0-1)

        Returns:
            Tupla (cannibalization_score, cannibalized_page_ids)
        """
        page_count = len(keyword_data)

        # Si solo hay 1 página, no hay canibalización
        if page_count <= 1:
            return (0.0, None)

        # Criterios de canibalización:
        # 1. Múltiples páginas con keyword en título/H1
        # 2. Densidad similar en varias páginas
        # 3. TF-IDF similar

        pages_in_title = [kw for kw in keyword_data if kw.get('position_in_title', False)]
        pages_in_h1 = [kw for kw in keyword_data if kw.get('position_in_h1', False)]

        # Factor 1: Número de páginas con keyword en título
        title_cannibalization = len(pages_in_title) / page_count if page_count > 0 else 0

        # Factor 2: Número de páginas con keyword en H1
        h1_cannibalization = len(pages_in_h1) / page_count if page_count > 0 else 0

        # Factor 3: Uniformidad de TF-IDF (si es muy similar, hay canibalización)
        tfidf_scores = [kw.get('tf_idf_score', 0.0) for kw in keyword_data]
        tfidf_variance = self._calculate_variance(tfidf_scores)
        # Baja varianza = alta canibalización
        tfidf_cannibalization = 1.0 - min(tfidf_variance / 5.0, 1.0)

        # Calcular score de canibalización
        cannibalization_score = (
            title_cannibalization * 0.4 +
            h1_cannibalization * 0.3 +
            tfidf_cannibalization * 0.3
        )

        # Identificar páginas cannibalizadas si supera el umbral
        cannibalized_pages = None
        if cannibalization_score >= threshold:
            # Páginas con keyword en título o H1 son las que cannibalizan
            cannibalized_page_ids = list(set(
                [kw['page_id'] for kw in pages_in_title] +
                [kw['page_id'] for kw in pages_in_h1]
            ))
            cannibalized_pages = cannibalized_page_ids

        return (round(cannibalization_score, 2), cannibalized_pages)

    def _calculate_variance(self, values: List[float]) -> float:
        """
        Calcula la varianza de una lista de valores.

        Args:
            values: Lista de valores numéricos

        Returns:
            Varianza
        """
        if not values:
            return 0.0

        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)

        return variance

    # ==================== DENSITY ANALYSIS ====================

    def calculate_advanced_densities(
        self,
        keyword: str,
        keyword_data: List[Dict[str, Any]],
        pages_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calcula densidades avanzadas de keyword.

        Args:
            keyword: Keyword a analizar
            keyword_data: Datos de la keyword
            pages_data: Datos de páginas

        Returns:
            Diccionario con métricas de densidad
        """
        if not keyword_data:
            return {
                'density_title': 0.0,
                'density_first_100_words': 0.0,
                'density_headings': 0.0,
                'is_stuffed': False,
                'pages_in_title': 0,
                'pages_in_h1': 0
            }

        # Densidad en títulos
        pages_with_title = [kw for kw in keyword_data if kw.get('position_in_title', False)]
        density_title = len(pages_with_title) / len(keyword_data)

        # Densidad en primeras 100 palabras
        pages_with_first_100 = [kw for kw in keyword_data if kw.get('position_in_first_100', False)]
        density_first_100 = len(pages_with_first_100) / len(keyword_data)

        # Densidad en headings (aproximado por H1)
        pages_with_h1 = [kw for kw in keyword_data if kw.get('position_in_h1', False)]
        density_headings = len(pages_with_h1) / len(keyword_data)

        # Detección de keyword stuffing
        # Stuffing si densidad > 5% en alguna página
        max_density = max(kw.get('density', 0.0) for kw in keyword_data)
        is_stuffed = max_density > 0.05

        return {
            'density_title': round(density_title, 3),
            'density_first_100_words': round(density_first_100, 3),
            'density_headings': round(density_headings, 3),
            'is_stuffed': is_stuffed,
            'pages_in_title': len(pages_with_title),
            'pages_in_h1': len(pages_with_h1)
        }

    # ==================== BATCH ANALYSIS ====================

    def analyze_all_keywords(
        self,
        keywords: List[Dict[str, Any]],
        pages_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Analiza todas las keywords de una sesión.

        Args:
            keywords: Lista de todas las keywords
            pages_data: Lista de todas las páginas

        Returns:
            Lista de keywords con métricas completas
        """
        # Agrupar keywords por texto
        keywords_by_text = defaultdict(list)
        for kw in keywords:
            keyword_text = kw.get('keyword', '')
            keywords_by_text[keyword_text].append(kw)

        results = []

        for keyword_text, keyword_instances in keywords_by_text.items():
            # Calcular difficulty
            difficulty_score, competition_level = self.calculate_keyword_difficulty(
                keyword_text,
                keyword_instances,
                keywords,
                pages_data
            )

            # Calcular opportunity
            opportunity_score = self.calculate_keyword_opportunity(
                keyword_text,
                keyword_instances,
                difficulty_score,
                pages_data
            )

            # Detectar canibalización
            cannibalization_score, cannibalized_pages = self.detect_keyword_cannibalization(
                keyword_text,
                keyword_instances,
                pages_data
            )

            # Calcular densidades avanzadas
            densities = self.calculate_advanced_densities(
                keyword_text,
                keyword_instances,
                pages_data
            )

            # Word count promedio
            avg_word_count = self._calculate_avg_word_count(keyword_instances, pages_data)

            # Para cada instancia de la keyword, añadir las métricas
            for kw_instance in keyword_instances:
                results.append({
                    'keyword_id': kw_instance.get('keyword_id'),
                    'keyword': keyword_text,
                    'page_id': kw_instance.get('page_id'),
                    'difficulty_score': difficulty_score,
                    'opportunity_score': opportunity_score,
                    'competition_level': competition_level,
                    'cannibalization_score': cannibalization_score,
                    'cannibalized_pages': json.dumps(cannibalized_pages) if cannibalized_pages else None,
                    'avg_word_count_pages': round(avg_word_count, 2),
                    **densities  # Añadir todas las densidades
                })

        return results

    # ==================== RECOMMENDATIONS ====================

    def generate_keyword_recommendations(
        self,
        keyword_metrics: Dict[str, Any]
    ) -> List[str]:
        """
        Genera recomendaciones basadas en las métricas de una keyword.

        Args:
            keyword_metrics: Métricas calculadas de la keyword

        Returns:
            Lista de recomendaciones
        """
        recommendations = []

        difficulty = keyword_metrics.get('difficulty_score', 0)
        opportunity = keyword_metrics.get('opportunity_score', 0)
        cannibalization = keyword_metrics.get('cannibalization_score', 0)
        is_stuffed = keyword_metrics.get('is_stuffed', False)

        # Recomendaciones por dificultad
        if difficulty > 70:
            recommendations.append(
                "Alta competencia interna. Considera consolidar contenido en una página principal."
            )
        elif difficulty < 30:
            recommendations.append(
                "Baja competencia. Oportunidad de crear más contenido sobre este tema."
            )

        # Recomendaciones por oportunidad
        if opportunity > 70:
            recommendations.append(
                "Alta oportunidad de ranking. Prioriza optimización de esta keyword."
            )
        elif opportunity < 30:
            recommendations.append(
                "Baja oportunidad. Considera keywords alternativas o long-tail."
            )

        # Recomendaciones por canibalización
        if cannibalization > 0.6:
            recommendations.append(
                "Canibalización detectada. Consolida páginas o diferencia su enfoque."
            )

        # Recomendaciones por keyword stuffing
        if is_stuffed:
            recommendations.append(
                "Keyword stuffing detectado. Reduce la densidad para evitar penalizaciones."
            )

        # Recomendaciones por gaps de optimización
        if keyword_metrics.get('pages_in_title', 0) == 0:
            recommendations.append(
                "Añade esta keyword en los títulos de las páginas relevantes."
            )

        if keyword_metrics.get('pages_in_h1', 0) == 0:
            recommendations.append(
                "Incluye esta keyword en los H1 para mejorar relevancia."
            )

        return recommendations
