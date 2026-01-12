"""
Métricas de keywords para el SEO Crawler.

Este módulo calcula métricas avanzadas sobre keywords,
incluyendo distribución, competencia, y análisis comparativo.
"""

from typing import Dict, List, Any, Tuple
from collections import Counter, defaultdict
import logging

logger = logging.getLogger('SEOCrawler.KeywordMetrics')


class KeywordMetrics:
    """Calculador de métricas avanzadas de keywords."""

    def __init__(self, database):
        """
        Inicializa el calculador de métricas.

        Args:
            database: Instancia de Database
        """
        self.db = database

    async def get_top_keywords(self,
                              session_id: int,
                              limit: int = 100,
                              order_by: str = 'tfidf') -> List[Dict[str, Any]]:
        """
        Obtiene las top keywords de una sesión.

        Args:
            session_id: ID de la sesión
            limit: Número de keywords a retornar
            order_by: Campo de ordenamiento (tfidf, frequency, density)

        Returns:
            Lista de keywords ordenadas
        """
        keywords = await self.db.get_top_keywords_by_session(session_id, limit)

        # Ordenar según criterio
        if order_by == 'frequency':
            keywords.sort(key=lambda x: x.get('total_frequency', 0), reverse=True)
        elif order_by == 'density':
            keywords.sort(key=lambda x: x.get('avg_density', 0), reverse=True)
        else:  # Default: tfidf
            keywords.sort(key=lambda x: x.get('avg_tfidf', 0), reverse=True)

        return keywords

    async def get_keyword_distribution(self, session_id: int) -> Dict[str, Any]:
        """
        Calcula la distribución de keywords por página.

        Args:
            session_id: ID de la sesión

        Returns:
            Diccionario con estadísticas de distribución
        """
        pages = await self.db.get_pages_by_session(session_id)

        keywords_per_page = []
        total_keywords = 0

        for page in pages:
            page_keywords = await self.db.get_keywords_by_page(page['page_id'])
            count = len(page_keywords)
            keywords_per_page.append(count)
            total_keywords += count

        if not keywords_per_page:
            return {
                'total_pages': 0,
                'total_keywords': 0,
                'avg_keywords_per_page': 0,
                'min_keywords': 0,
                'max_keywords': 0
            }

        return {
            'total_pages': len(pages),
            'total_keywords': total_keywords,
            'avg_keywords_per_page': round(total_keywords / len(pages), 2),
            'min_keywords': min(keywords_per_page),
            'max_keywords': max(keywords_per_page)
        }

    async def get_ngram_distribution(self, session_id: int) -> Dict[int, int]:
        """
        Obtiene la distribución de keywords por tamaño de n-grama.

        Args:
            session_id: ID de la sesión

        Returns:
            Diccionario con conteo por tamaño
        """
        pages = await self.db.get_pages_by_session(session_id)

        ngram_counts = defaultdict(int)

        for page in pages:
            keywords = await self.db.get_keywords_by_page(page['page_id'])

            for kw in keywords:
                ngram_size = kw.get('ngram_size', 1)
                ngram_counts[ngram_size] += 1

        return dict(ngram_counts)

    async def find_common_keywords(self,
                                  session_ids: List[int],
                                  min_sessions: int = 2,
                                  limit: int = 50) -> List[Dict[str, Any]]:
        """
        Encuentra keywords comunes entre múltiples sesiones.

        Args:
            session_ids: Lista de IDs de sesiones
            min_sessions: Mínimo de sesiones en que debe aparecer
            limit: Límite de resultados

        Returns:
            Lista de keywords comunes
        """
        keyword_sessions = defaultdict(set)
        keyword_metrics = defaultdict(lambda: {'frequency': 0, 'tfidf': 0, 'count': 0})

        # Recopilar keywords de cada sesión
        for session_id in session_ids:
            keywords = await self.db.get_top_keywords_by_session(session_id, 1000)

            for kw in keywords:
                keyword = kw['keyword']
                keyword_sessions[keyword].add(session_id)

                # Acumular métricas
                keyword_metrics[keyword]['frequency'] += kw.get('total_frequency', 0)
                keyword_metrics[keyword]['tfidf'] += kw.get('avg_tfidf', 0)
                keyword_metrics[keyword]['count'] += 1

        # Filtrar por mínimo de sesiones
        common_keywords = []

        for keyword, sessions in keyword_sessions.items():
            if len(sessions) >= min_sessions:
                metrics = keyword_metrics[keyword]

                common_keywords.append({
                    'keyword': keyword,
                    'session_count': len(sessions),
                    'total_frequency': metrics['frequency'],
                    'avg_tfidf': round(metrics['tfidf'] / metrics['count'], 4),
                    'sessions': list(sessions)
                })

        # Ordenar por número de sesiones y luego por TF-IDF
        common_keywords.sort(key=lambda x: (x['session_count'], x['avg_tfidf']), reverse=True)

        return common_keywords[:limit]

    async def find_unique_keywords(self,
                                  target_session_id: int,
                                  comparison_session_ids: List[int],
                                  limit: int = 50) -> List[Dict[str, Any]]:
        """
        Encuentra keywords únicas de una sesión vs otras sesiones.

        Args:
            target_session_id: Sesión objetivo
            comparison_session_ids: Sesiones para comparar
            limit: Límite de resultados

        Returns:
            Lista de keywords únicas
        """
        # Keywords de la sesión objetivo
        target_keywords = await self.db.get_top_keywords_by_session(target_session_id, 1000)
        target_kw_dict = {kw['keyword']: kw for kw in target_keywords}

        # Keywords de sesiones de comparación
        comparison_kw_set = set()
        for session_id in comparison_session_ids:
            keywords = await self.db.get_top_keywords_by_session(session_id, 1000)
            comparison_kw_set.update([kw['keyword'] for kw in keywords])

        # Encontrar únicas
        unique_keywords = []

        for keyword, data in target_kw_dict.items():
            if keyword not in comparison_kw_set:
                unique_keywords.append({
                    'keyword': keyword,
                    'frequency': data.get('total_frequency', 0),
                    'tfidf': data.get('avg_tfidf', 0),
                    'density': data.get('avg_density', 0)
                })

        # Ordenar por TF-IDF
        unique_keywords.sort(key=lambda x: x['tfidf'], reverse=True)

        return unique_keywords[:limit]

    async def find_keyword_gaps(self,
                               target_session_id: int,
                               competitor_session_ids: List[int],
                               limit: int = 50) -> List[Dict[str, Any]]:
        """
        Encuentra keywords que tienen los competidores pero no la sesión objetivo (keyword gaps).

        Args:
            target_session_id: Sesión objetivo
            competitor_session_ids: Sesiones de competidores
            limit: Límite de resultados

        Returns:
            Lista de keyword gaps
        """
        # Keywords de la sesión objetivo
        target_keywords = await self.db.get_top_keywords_by_session(target_session_id, 1000)
        target_kw_set = set([kw['keyword'] for kw in target_keywords])

        # Keywords de competidores con métricas agregadas
        competitor_kw_metrics = defaultdict(lambda: {'frequency': 0, 'tfidf': 0, 'count': 0, 'sessions': 0})

        for session_id in competitor_session_ids:
            keywords = await self.db.get_top_keywords_by_session(session_id, 1000)

            for kw in keywords:
                keyword = kw['keyword']

                if keyword not in target_kw_set:
                    competitor_kw_metrics[keyword]['frequency'] += kw.get('total_frequency', 0)
                    competitor_kw_metrics[keyword]['tfidf'] += kw.get('avg_tfidf', 0)
                    competitor_kw_metrics[keyword]['count'] += 1
                    competitor_kw_metrics[keyword]['sessions'] += 1

        # Crear lista de gaps
        keyword_gaps = []

        for keyword, metrics in competitor_kw_metrics.items():
            keyword_gaps.append({
                'keyword': keyword,
                'competitor_sessions': metrics['sessions'],
                'total_frequency': metrics['frequency'],
                'avg_tfidf': round(metrics['tfidf'] / metrics['count'], 4),
                'opportunity_score': metrics['sessions'] * (metrics['tfidf'] / metrics['count'])
            })

        # Ordenar por opportunity score
        keyword_gaps.sort(key=lambda x: x['opportunity_score'], reverse=True)

        return keyword_gaps[:limit]

    async def get_keyword_position_analysis(self, session_id: int) -> Dict[str, Any]:
        """
        Analiza la posición de keywords en elementos importantes.

        Args:
            session_id: ID de la sesión

        Returns:
            Diccionario con análisis de posiciones
        """
        pages = await self.db.get_pages_by_session(session_id)

        total_keywords = 0
        in_title = 0
        in_h1 = 0
        in_first_100 = 0

        for page in pages:
            keywords = await self.db.get_keywords_by_page(page['page_id'])

            for kw in keywords:
                total_keywords += 1

                if kw.get('position_in_title'):
                    in_title += 1
                if kw.get('position_in_h1'):
                    in_h1 += 1
                if kw.get('position_in_first_100'):
                    in_first_100 += 1

        if total_keywords == 0:
            return {
                'total_keywords': 0,
                'in_title_pct': 0,
                'in_h1_pct': 0,
                'in_first_100_pct': 0
            }

        return {
            'total_keywords': total_keywords,
            'in_title': in_title,
            'in_h1': in_h1,
            'in_first_100': in_first_100,
            'in_title_pct': round((in_title / total_keywords) * 100, 2),
            'in_h1_pct': round((in_h1 / total_keywords) * 100, 2),
            'in_first_100_pct': round((in_first_100 / total_keywords) * 100, 2)
        }

    async def get_keyword_density_analysis(self, session_id: int) -> Dict[str, List[str]]:
        """
        Analiza la densidad de keywords y detecta posible keyword stuffing.

        Args:
            session_id: ID de la sesión

        Returns:
            Diccionario con análisis de densidad
        """
        pages = await self.db.get_pages_by_session(session_id)

        low_density = []  # < 0.5%
        normal_density = []  # 0.5% - 3%
        high_density = []  # 3% - 5%
        stuffing = []  # > 5%

        for page in pages:
            keywords = await self.db.get_keywords_by_page(page['page_id'])

            for kw in keywords:
                keyword = kw['keyword']
                density = kw.get('density', 0)

                if density > 5.0:
                    stuffing.append(f"{keyword} ({density}%)")
                elif density > 3.0:
                    high_density.append(f"{keyword} ({density}%)")
                elif density >= 0.5:
                    normal_density.append(f"{keyword} ({density}%)")
                else:
                    low_density.append(f"{keyword} ({density}%)")

        return {
            'low_density': low_density[:20],
            'normal_density': normal_density[:20],
            'high_density': high_density[:20],
            'stuffing': stuffing
        }

    async def calculate_keyword_competitiveness(self,
                                               session_ids: List[int]) -> Dict[str, Dict[str, Any]]:
        """
        Calcula la competitividad de keywords entre múltiples sesiones.

        Args:
            session_ids: Lista de IDs de sesiones

        Returns:
            Diccionario con análisis de competitividad
        """
        keyword_data = defaultdict(lambda: {
            'sessions': set(),
            'total_frequency': 0,
            'avg_tfidf': [],
            'max_density': 0
        })

        # Recopilar datos de todas las sesiones
        for session_id in session_ids:
            keywords = await self.db.get_top_keywords_by_session(session_id, 1000)

            for kw in keywords:
                keyword = kw['keyword']
                keyword_data[keyword]['sessions'].add(session_id)
                keyword_data[keyword]['total_frequency'] += kw.get('total_frequency', 0)
                keyword_data[keyword]['avg_tfidf'].append(kw.get('avg_tfidf', 0))

        # Calcular competitividad
        competitiveness = {}

        for keyword, data in keyword_data.items():
            num_sessions = len(data['sessions'])
            avg_tfidf = sum(data['avg_tfidf']) / len(data['avg_tfidf']) if data['avg_tfidf'] else 0

            # Score de competitividad (cuantas más sesiones, más competitivo)
            competitiveness_score = num_sessions * avg_tfidf

            competitiveness[keyword] = {
                'keyword': keyword,
                'sessions_count': num_sessions,
                'total_frequency': data['total_frequency'],
                'avg_tfidf': round(avg_tfidf, 4),
                'competitiveness_score': round(competitiveness_score, 4)
            }

        # Ordenar por competitividad
        sorted_keywords = sorted(
            competitiveness.values(),
            key=lambda x: x['competitiveness_score'],
            reverse=True
        )

        return {kw['keyword']: kw for kw in sorted_keywords[:100]}

    async def get_session_comparison(self,
                                    session_id1: int,
                                    session_id2: int) -> Dict[str, Any]:
        """
        Compara dos sesiones de crawling.

        Args:
            session_id1: Primera sesión
            session_id2: Segunda sesión

        Returns:
            Diccionario con comparación detallada
        """
        # Obtener keywords de ambas sesiones
        kw1 = await self.db.get_top_keywords_by_session(session_id1, 1000)
        kw2 = await self.db.get_top_keywords_by_session(session_id2, 1000)

        kw1_set = set([k['keyword'] for k in kw1])
        kw2_set = set([k['keyword'] for k in kw2])

        # Calcular métricas
        common = kw1_set & kw2_set
        unique_to_1 = kw1_set - kw2_set
        unique_to_2 = kw2_set - kw1_set

        # Similitud Jaccard
        union = kw1_set | kw2_set
        similarity = len(common) / len(union) if union else 0

        # Obtener estadísticas
        stats1 = await self.db.get_session_stats(session_id1)
        stats2 = await self.db.get_session_stats(session_id2)

        return {
            'session_1': {
                'session_id': session_id1,
                'total_keywords': stats1['total_keywords'],
                'unique_keywords': stats1['unique_keywords'],
                'pages': stats1['total_pages']
            },
            'session_2': {
                'session_id': session_id2,
                'total_keywords': stats2['total_keywords'],
                'unique_keywords': stats2['unique_keywords'],
                'pages': stats2['total_pages']
            },
            'common_keywords': len(common),
            'unique_to_session_1': len(unique_to_1),
            'unique_to_session_2': len(unique_to_2),
            'similarity_score': round(similarity, 4),
            'common_keywords_list': list(common)[:50],
            'gaps_for_session_1': list(unique_to_2)[:50],
            'gaps_for_session_2': list(unique_to_1)[:50]
        }
