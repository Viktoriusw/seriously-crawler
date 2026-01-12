"""
Gestor de base de datos SQLite para el SEO Crawler.

Este módulo maneja todas las operaciones de base de datos de forma asíncrona,
incluyendo creación de tablas, inserción, consultas y actualizaciones.
"""

import aiosqlite
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path

from .schemas import ALL_TABLES, ALL_INDEXES


class Database:
    """Clase para gestionar todas las operaciones de base de datos."""

    def __init__(self, db_path: str):
        """
        Inicializa el gestor de base de datos.

        Args:
            db_path: Ruta al archivo de base de datos SQLite
        """
        self.db_path = db_path
        self.connection: Optional[aiosqlite.Connection] = None

        # Crear directorio si no existe
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    async def connect(self) -> None:
        """Establece conexión con la base de datos."""
        self.connection = await aiosqlite.connect(self.db_path)
        self.connection.row_factory = aiosqlite.Row
        await self.init_database()

    async def close(self) -> None:
        """Cierra la conexión con la base de datos."""
        if self.connection:
            await self.connection.close()
            self.connection = None

    async def init_database(self) -> None:
        """Crea todas las tablas e índices si no existen."""
        async with self.connection.cursor() as cursor:
            # Crear tablas
            for table_sql in ALL_TABLES:
                await cursor.execute(table_sql)

            # Crear índices
            for index_sql in ALL_INDEXES:
                await cursor.execute(index_sql)

            await self.connection.commit()

    # ==================== CRAWL SESSIONS ====================

    async def create_session(self, seed_url: str, domains: str, config: Dict[str, Any]) -> int:
        """
        Crea una nueva sesión de crawling.

        Args:
            seed_url: URL inicial del crawl
            domains: Dominios a crawlear (separados por coma)
            config: Configuración del crawl

        Returns:
            ID de la sesión creada
        """
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                INSERT INTO crawl_sessions (start_time, seed_url, domains, config_snapshot, status)
                VALUES (?, ?, ?, ?, 'running')
            """, (datetime.now(), seed_url, domains, json.dumps(config)))

            await self.connection.commit()
            return cursor.lastrowid

    async def update_session(self, session_id: int, **kwargs) -> None:
        """
        Actualiza una sesión de crawling.

        Args:
            session_id: ID de la sesión
            **kwargs: Campos a actualizar
        """
        if not kwargs:
            return

        fields = ', '.join([f"{key} = ?" for key in kwargs.keys()])
        values = list(kwargs.values()) + [session_id]

        async with self.connection.cursor() as cursor:
            await cursor.execute(f"""
                UPDATE crawl_sessions SET {fields} WHERE session_id = ?
            """, values)
            await self.connection.commit()

    async def finish_session(self, session_id: int) -> None:
        """
        Marca una sesión como finalizada.

        Args:
            session_id: ID de la sesión
        """
        await self.update_session(
            session_id,
            end_time=datetime.now(),
            status='completed'
        )

    async def get_session(self, session_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene información de una sesión.

        Args:
            session_id: ID de la sesión

        Returns:
            Diccionario con datos de la sesión o None
        """
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                SELECT * FROM crawl_sessions WHERE session_id = ?
            """, (session_id,))
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def get_all_sessions(self) -> List[Dict[str, Any]]:
        """
        Obtiene todas las sesiones.

        Returns:
            Lista de sesiones
        """
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                SELECT * FROM crawl_sessions ORDER BY start_time DESC
            """)
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    # ==================== PAGES ====================

    async def insert_page(self, session_id: int, page_data: Dict[str, Any]) -> int:
        """
        Inserta una nueva página en la base de datos.
        Si la URL ya existe, actualiza los datos.

        Args:
            session_id: ID de la sesión
            page_data: Datos de la página

        Returns:
            ID de la página insertada o actualizada
        """
        async with self.connection.cursor() as cursor:
            # Verificar si la URL ya existe
            url = page_data.get('url')
            await cursor.execute("SELECT page_id FROM pages WHERE url = ?", (url,))
            existing = await cursor.fetchone()

            if existing:
                # Actualizar página existente
                page_id = existing['page_id']
                await cursor.execute("""
                    UPDATE pages SET
                        session_id = ?,
                        domain = ?,
                        status_code = ?,
                        title = ?,
                        h1 = ?,
                        meta_description = ?,
                        word_count = ?,
                        crawl_date = ?,
                        content_hash = ?,
                        response_time = ?,
                        depth = ?,
                        parent_url = ?,
                        content_type = ?,
                        canonical_url = ?,
                        language = ?,
                        error_message = ?
                    WHERE page_id = ?
                """, (
                    session_id,
                    page_data.get('domain'),
                    page_data.get('status_code'),
                    page_data.get('title'),
                    page_data.get('h1'),
                    page_data.get('meta_description'),
                    page_data.get('word_count', 0),
                    datetime.now(),
                    page_data.get('content_hash'),
                    page_data.get('response_time'),
                    page_data.get('depth', 0),
                    page_data.get('parent_url'),
                    page_data.get('content_type'),
                    page_data.get('canonical_url'),
                    page_data.get('language'),
                    page_data.get('error_message'),
                    page_id
                ))
                await self.connection.commit()
                return page_id
            else:
                # Insertar nueva página
                await cursor.execute("""
                    INSERT INTO pages (
                        session_id, url, domain, status_code, title, h1, meta_description,
                        word_count, crawl_date, content_hash, response_time, depth,
                        parent_url, content_type, canonical_url, language, error_message
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    session_id,
                    url,
                    page_data.get('domain'),
                    page_data.get('status_code'),
                    page_data.get('title'),
                    page_data.get('h1'),
                    page_data.get('meta_description'),
                    page_data.get('word_count', 0),
                    datetime.now(),
                    page_data.get('content_hash'),
                    page_data.get('response_time'),
                    page_data.get('depth', 0),
                    page_data.get('parent_url'),
                    page_data.get('content_type'),
                    page_data.get('canonical_url'),
                    page_data.get('language'),
                    page_data.get('error_message')
                ))

                await self.connection.commit()
                return cursor.lastrowid

    async def get_page_by_url(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene una página por su URL.

        Args:
            url: URL de la página

        Returns:
            Diccionario con datos de la página o None
        """
        async with self.connection.cursor() as cursor:
            await cursor.execute("SELECT * FROM pages WHERE url = ?", (url,))
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def url_exists(self, url: str) -> bool:
        """
        Verifica si una URL ya fue crawleada.

        Args:
            url: URL a verificar

        Returns:
            True si existe, False en caso contrario
        """
        async with self.connection.cursor() as cursor:
            await cursor.execute("SELECT 1 FROM pages WHERE url = ?", (url,))
            return await cursor.fetchone() is not None

    async def get_pages_by_session(self, session_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene todas las páginas de una sesión.

        Args:
            session_id: ID de la sesión

        Returns:
            Lista de páginas
        """
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                SELECT * FROM pages WHERE session_id = ? ORDER BY crawl_date
            """, (session_id,))
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    # ==================== KEYWORDS ====================

    async def insert_keywords(self, page_id: int, keywords: List[Dict[str, Any]]) -> None:
        """
        Inserta múltiples keywords de una página.

        Args:
            page_id: ID de la página
            keywords: Lista de keywords con sus datos
        """
        async with self.connection.cursor() as cursor:
            for kw in keywords:
                await cursor.execute("""
                    INSERT INTO keywords (
                        page_id, keyword, frequency, density, tf_idf_score,
                        position_in_title, position_in_h1, position_in_first_100,
                        is_ngram, ngram_size
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    page_id,
                    kw.get('keyword'),
                    kw.get('frequency', 1),
                    kw.get('density', 0.0),
                    kw.get('tf_idf_score', 0.0),
                    kw.get('position_in_title', False),
                    kw.get('position_in_h1', False),
                    kw.get('position_in_first_100', False),
                    kw.get('is_ngram', False),
                    kw.get('ngram_size', 1)
                ))

            await self.connection.commit()

    async def get_keywords_by_page(self, page_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene todas las keywords de una página.

        Args:
            page_id: ID de la página

        Returns:
            Lista de keywords
        """
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                SELECT * FROM keywords WHERE page_id = ? ORDER BY tf_idf_score DESC
            """, (page_id,))
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def get_top_keywords_by_session(self, session_id: int, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Obtiene las top keywords de una sesión ordenadas por TF-IDF.

        Args:
            session_id: ID de la sesión
            limit: Número máximo de keywords

        Returns:
            Lista de keywords con sus métricas
        """
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                SELECT k.keyword,
                       SUM(k.frequency) as total_frequency,
                       AVG(k.density) as avg_density,
                       AVG(k.tf_idf_score) as avg_tfidf,
                       COUNT(DISTINCT k.page_id) as page_count
                FROM keywords k
                JOIN pages p ON k.page_id = p.page_id
                WHERE p.session_id = ?
                GROUP BY k.keyword
                ORDER BY avg_tfidf DESC
                LIMIT ?
            """, (session_id, limit))
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    # ==================== LINKS ====================

    async def insert_links(self, page_id: int, links: List[Dict[str, Any]]) -> None:
        """
        Inserta múltiples enlaces de una página.

        Args:
            page_id: ID de la página
            links: Lista de enlaces
        """
        async with self.connection.cursor() as cursor:
            for link in links:
                await cursor.execute("""
                    INSERT INTO links (
                        source_page_id, target_url, anchor_text, is_internal, nofollow, link_type
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    page_id,
                    link.get('url'),
                    link.get('anchor_text'),
                    link.get('is_internal', True),
                    link.get('nofollow', False),
                    link.get('type', 'a')
                ))

            await self.connection.commit()

    async def get_links_by_page(self, page_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene todos los enlaces de una página.

        Args:
            page_id: ID de la página

        Returns:
            Lista de enlaces
        """
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                SELECT * FROM links WHERE source_page_id = ?
            """, (page_id,))
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    # ==================== IMAGES ====================

    async def insert_images(self, page_id: int, images: List[Dict[str, Any]]) -> None:
        """
        Inserta múltiples imágenes de una página.

        Args:
            page_id: ID de la página
            images: Lista de imágenes
        """
        async with self.connection.cursor() as cursor:
            for img in images:
                await cursor.execute("""
                    INSERT INTO images (
                        page_id, url, alt_text, title_text, size_bytes, width, height
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    page_id,
                    img.get('url'),
                    img.get('alt'),
                    img.get('title'),
                    img.get('size'),
                    img.get('width'),
                    img.get('height')
                ))

            await self.connection.commit()

    # ==================== METADATA ====================

    async def insert_metadata(self, page_id: int, metadata: List[Dict[str, Any]]) -> None:
        """
        Inserta múltiples metadatos de una página.

        Args:
            page_id: ID de la página
            metadata: Lista de metadatos
        """
        async with self.connection.cursor() as cursor:
            for meta in metadata:
                await cursor.execute("""
                    INSERT INTO metadata (page_id, meta_key, meta_value, meta_type)
                    VALUES (?, ?, ?, ?)
                """, (
                    page_id,
                    meta.get('key'),
                    meta.get('value'),
                    meta.get('type', 'meta')
                ))

            await self.connection.commit()

    # ==================== HEADINGS ====================

    async def insert_headings(self, page_id: int, headings: List[Dict[str, Any]]) -> None:
        """
        Inserta múltiples encabezados de una página.

        Args:
            page_id: ID de la página
            headings: Lista de encabezados
        """
        async with self.connection.cursor() as cursor:
            for heading in headings:
                await cursor.execute("""
                    INSERT INTO headings (page_id, level, text, position)
                    VALUES (?, ?, ?, ?)
                """, (
                    page_id,
                    heading.get('level'),
                    heading.get('text'),
                    heading.get('position')
                ))

            await self.connection.commit()

    # ==================== STRUCTURED DATA ====================

    async def insert_structured_data(self, page_id: int, structured_data: List[Dict[str, Any]]) -> None:
        """
        Inserta datos estructurados de una página.

        Args:
            page_id: ID de la página
            structured_data: Lista de datos estructurados
        """
        async with self.connection.cursor() as cursor:
            for sd in structured_data:
                await cursor.execute("""
                    INSERT INTO structured_data (page_id, data_type, json_data)
                    VALUES (?, ?, ?)
                """, (
                    page_id,
                    sd.get('type'),
                    json.dumps(sd.get('data', {}))
                ))

            await self.connection.commit()

    # ==================== STATISTICS ====================

    async def get_session_stats(self, session_id: int) -> Dict[str, Any]:
        """
        Obtiene estadísticas de una sesión.

        Args:
            session_id: ID de la sesión

        Returns:
            Diccionario con estadísticas
        """
        async with self.connection.cursor() as cursor:
            # Total de páginas
            await cursor.execute("""
                SELECT COUNT(*) as total FROM pages WHERE session_id = ?
            """, (session_id,))
            total_pages = (await cursor.fetchone())['total']

            # Páginas exitosas
            await cursor.execute("""
                SELECT COUNT(*) as success FROM pages
                WHERE session_id = ? AND status_code >= 200 AND status_code < 300
            """, (session_id,))
            success_pages = (await cursor.fetchone())['success']

            # Total keywords
            await cursor.execute("""
                SELECT COUNT(*) as total FROM keywords k
                JOIN pages p ON k.page_id = p.page_id
                WHERE p.session_id = ?
            """, (session_id,))
            total_keywords = (await cursor.fetchone())['total']

            # Keywords únicas
            await cursor.execute("""
                SELECT COUNT(DISTINCT keyword) as unique_kw FROM keywords k
                JOIN pages p ON k.page_id = p.page_id
                WHERE p.session_id = ?
            """, (session_id,))
            unique_keywords = (await cursor.fetchone())['unique_kw']

            # Total de enlaces
            await cursor.execute("""
                SELECT COUNT(*) as total FROM links l
                JOIN pages p ON l.source_page_id = p.page_id
                WHERE p.session_id = ?
            """, (session_id,))
            total_links = (await cursor.fetchone())['total']

            # Enlaces internos
            await cursor.execute("""
                SELECT COUNT(*) as internal FROM links l
                JOIN pages p ON l.source_page_id = p.page_id
                WHERE p.session_id = ? AND l.is_internal = 1
            """, (session_id,))
            internal_links = (await cursor.fetchone())['internal']

            return {
                'total_pages': total_pages,
                'success_pages': success_pages,
                'failed_pages': total_pages - success_pages,
                'total_keywords': total_keywords,
                'unique_keywords': unique_keywords,
                'total_links': total_links,
                'internal_links': internal_links,
                'external_links': total_links - internal_links
            }

    # ==================== KEYWORD CLUSTERS (PROFESSIONAL) ====================

    async def create_keyword_cluster(
        self,
        session_id: int,
        cluster_name: str,
        main_keyword: str,
        num_keywords: int = 0,
        avg_tfidf: float = 0.0,
        topic_distribution: Optional[str] = None
    ) -> int:
        """
        Crea un nuevo cluster de keywords.

        Args:
            session_id: ID de la sesión
            cluster_name: Nombre del cluster
            main_keyword: Keyword principal del cluster
            num_keywords: Número de keywords en el cluster
            avg_tfidf: TF-IDF promedio del cluster
            topic_distribution: Distribución de tópicos (JSON string)

        Returns:
            ID del cluster creado
        """
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                INSERT INTO keyword_clusters (
                    session_id, cluster_name, main_keyword, num_keywords,
                    avg_tfidf, topic_distribution
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (session_id, cluster_name, main_keyword, num_keywords, avg_tfidf, topic_distribution))

            await self.connection.commit()
            return cursor.lastrowid

    async def add_keyword_to_cluster(
        self,
        cluster_id: int,
        keyword_id: int,
        similarity_score: float = 0.0
    ) -> None:
        """
        Añade una keyword a un cluster.

        Args:
            cluster_id: ID del cluster
            keyword_id: ID de la keyword
            similarity_score: Score de similitud semántica
        """
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                INSERT INTO keyword_cluster_members (cluster_id, keyword_id, similarity_score)
                VALUES (?, ?, ?)
            """, (cluster_id, keyword_id, similarity_score))

            await self.connection.commit()

    async def get_clusters_by_session(self, session_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene todos los clusters de una sesión.

        Args:
            session_id: ID de la sesión

        Returns:
            Lista de clusters con sus datos
        """
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                SELECT * FROM keyword_clusters
                WHERE session_id = ?
                ORDER BY avg_tfidf DESC
            """, (session_id,))
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def get_cluster_members(self, cluster_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene todas las keywords de un cluster con sus scores.

        Args:
            cluster_id: ID del cluster

        Returns:
            Lista de keywords del cluster
        """
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                SELECT k.*, kcm.similarity_score
                FROM keywords k
                JOIN keyword_cluster_members kcm ON k.keyword_id = kcm.keyword_id
                WHERE kcm.cluster_id = ?
                ORDER BY kcm.similarity_score DESC
            """, (cluster_id,))
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    # ==================== TOPICS (PROFESSIONAL) ====================

    async def create_topic(
        self,
        session_id: int,
        topic_name: Optional[str] = None,
        top_keywords: Optional[str] = None,
        pages_count: int = 0,
        coherence_score: float = 0.0
    ) -> int:
        """
        Crea un nuevo tópico identificado por LDA.

        Args:
            session_id: ID de la sesión
            topic_name: Nombre descriptivo del tópico
            top_keywords: Keywords principales (JSON string)
            pages_count: Número de páginas asociadas
            coherence_score: Score de coherencia del tópico

        Returns:
            ID del tópico creado
        """
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                INSERT INTO topics (
                    session_id, topic_name, top_keywords, pages_count, coherence_score
                ) VALUES (?, ?, ?, ?, ?)
            """, (session_id, topic_name, top_keywords, pages_count, coherence_score))

            await self.connection.commit()
            return cursor.lastrowid

    async def get_topics_by_session(self, session_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene todos los tópicos de una sesión.

        Args:
            session_id: ID de la sesión

        Returns:
            Lista de tópicos
        """
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                SELECT * FROM topics
                WHERE session_id = ?
                ORDER BY coherence_score DESC
            """, (session_id,))
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    # ==================== SEARCH INTENT (PROFESSIONAL) ====================

    async def set_search_intent(
        self,
        keyword_id: int,
        intent_type: str,
        confidence: float = 0.0
    ) -> None:
        """
        Establece el tipo de intención de búsqueda para una keyword.

        Args:
            keyword_id: ID de la keyword
            intent_type: Tipo de intención (informational, transactional, navigational, commercial)
            confidence: Confianza de la clasificación (0-1)
        """
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                INSERT OR REPLACE INTO search_intent (keyword_id, intent_type, confidence)
                VALUES (?, ?, ?)
            """, (keyword_id, intent_type, confidence))

            await self.connection.commit()

    async def get_keywords_by_intent(self, session_id: int, intent_type: str) -> List[Dict[str, Any]]:
        """
        Obtiene keywords de una sesión filtradas por tipo de intención.

        Args:
            session_id: ID de la sesión
            intent_type: Tipo de intención

        Returns:
            Lista de keywords con el tipo de intención especificado
        """
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                SELECT k.*, si.intent_type, si.confidence
                FROM keywords k
                JOIN pages p ON k.page_id = p.page_id
                JOIN search_intent si ON k.keyword_id = si.keyword_id
                WHERE p.session_id = ? AND si.intent_type = ?
                ORDER BY si.confidence DESC
            """, (session_id, intent_type))
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    # ==================== KEYWORD METRICS (PROFESSIONAL) ====================

    async def set_keyword_metrics(
        self,
        keyword_id: int,
        difficulty_score: float = 0.0,
        opportunity_score: float = 0.0,
        competition_level: str = 'medium',
        cannibalization_score: float = 0.0,
        cannibalized_pages: Optional[str] = None,
        density_title: float = 0.0,
        density_first_100_words: float = 0.0,
        density_headings: float = 0.0,
        is_stuffed: bool = False,
        pages_in_title: int = 0,
        pages_in_h1: int = 0,
        avg_word_count_pages: float = 0.0
    ) -> None:
        """
        Establece métricas profesionales para una keyword.

        Args:
            keyword_id: ID de la keyword
            difficulty_score: Dificultad de ranking (0-100)
            opportunity_score: Oportunidad de ranking (0-100)
            competition_level: Nivel de competencia (low, medium, high)
            cannibalization_score: Score de canibalización (0-1)
            cannibalized_pages: IDs de páginas cannibalizadas (JSON string)
            density_title: Densidad en títulos
            density_first_100_words: Densidad en primeras 100 palabras
            density_headings: Densidad en encabezados
            is_stuffed: Si hay keyword stuffing
            pages_in_title: Número de páginas con keyword en título
            pages_in_h1: Número de páginas con keyword en H1
            avg_word_count_pages: Promedio de palabras en páginas con esta keyword
        """
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                INSERT OR REPLACE INTO keyword_metrics (
                    keyword_id, difficulty_score, opportunity_score, competition_level,
                    cannibalization_score, cannibalized_pages, density_title,
                    density_first_100_words, density_headings, is_stuffed,
                    pages_in_title, pages_in_h1, avg_word_count_pages
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                keyword_id, difficulty_score, opportunity_score, competition_level,
                cannibalization_score, cannibalized_pages, density_title,
                density_first_100_words, density_headings, is_stuffed,
                pages_in_title, pages_in_h1, avg_word_count_pages
            ))

            await self.connection.commit()

    async def get_keyword_metrics(self, keyword_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene las métricas profesionales de una keyword.

        Args:
            keyword_id: ID de la keyword

        Returns:
            Diccionario con métricas o None
        """
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                SELECT * FROM keyword_metrics WHERE keyword_id = ?
            """, (keyword_id,))
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def get_high_opportunity_keywords(
        self,
        session_id: int,
        min_opportunity: float = 70.0,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Obtiene keywords con alta oportunidad de ranking.

        Args:
            session_id: ID de la sesión
            min_opportunity: Score mínimo de oportunidad
            limit: Número máximo de resultados

        Returns:
            Lista de keywords de alta oportunidad
        """
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                SELECT k.*, km.opportunity_score, km.difficulty_score, km.competition_level
                FROM keywords k
                JOIN pages p ON k.page_id = p.page_id
                JOIN keyword_metrics km ON k.keyword_id = km.keyword_id
                WHERE p.session_id = ? AND km.opportunity_score >= ?
                ORDER BY km.opportunity_score DESC, km.difficulty_score ASC
                LIMIT ?
            """, (session_id, min_opportunity, limit))
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def get_cannibalized_keywords(self, session_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene keywords con canibalización detectada.

        Args:
            session_id: ID de la sesión

        Returns:
            Lista de keywords cannibalizadas
        """
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                SELECT k.*, km.cannibalization_score, km.cannibalized_pages
                FROM keywords k
                JOIN pages p ON k.page_id = p.page_id
                JOIN keyword_metrics km ON k.keyword_id = km.keyword_id
                WHERE p.session_id = ? AND km.cannibalization_score > 0.5
                ORDER BY km.cannibalization_score DESC
            """, (session_id,))
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    # ==================== CONTENT QUALITY (PROFESSIONAL) ====================

    async def set_content_quality(
        self,
        page_id: int,
        quality_score: float = 0.0,
        readability_score: float = 0.0,
        readability_level: Optional[str] = None,
        lexical_diversity: float = 0.0,
        avg_sentence_length: float = 0.0,
        avg_word_length: float = 0.0,
        is_thin_content: bool = False,
        duplicate_of_page_id: Optional[int] = None,
        similarity_score: float = 0.0,
        heading_structure_score: float = 0.0,
        multimedia_score: float = 0.0
    ) -> None:
        """
        Establece métricas de calidad de contenido para una página.

        Args:
            page_id: ID de la página
            quality_score: Score general de calidad (0-100)
            readability_score: Score de legibilidad
            readability_level: Nivel de lectura (elementary, intermediate, advanced)
            lexical_diversity: Diversidad léxica (0-1)
            avg_sentence_length: Longitud promedio de oraciones
            avg_word_length: Longitud promedio de palabras
            is_thin_content: Si es contenido delgado
            duplicate_of_page_id: ID de página duplicada
            similarity_score: Score de similitud con duplicado
            heading_structure_score: Score de estructura de encabezados
            multimedia_score: Score de uso de multimedia
        """
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                INSERT OR REPLACE INTO content_quality (
                    page_id, quality_score, readability_score, readability_level,
                    lexical_diversity, avg_sentence_length, avg_word_length,
                    is_thin_content, duplicate_of_page_id, similarity_score,
                    heading_structure_score, multimedia_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                page_id, quality_score, readability_score, readability_level,
                lexical_diversity, avg_sentence_length, avg_word_length,
                is_thin_content, duplicate_of_page_id, similarity_score,
                heading_structure_score, multimedia_score
            ))

            await self.connection.commit()

    async def get_content_quality(self, page_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene las métricas de calidad de una página.

        Args:
            page_id: ID de la página

        Returns:
            Diccionario con métricas de calidad o None
        """
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                SELECT * FROM content_quality WHERE page_id = ?
            """, (page_id,))
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def get_low_quality_pages(
        self,
        session_id: int,
        max_quality: float = 40.0
    ) -> List[Dict[str, Any]]:
        """
        Obtiene páginas con baja calidad de contenido.

        Args:
            session_id: ID de la sesión
            max_quality: Score máximo de calidad

        Returns:
            Lista de páginas de baja calidad
        """
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                SELECT p.*, cq.quality_score, cq.is_thin_content, cq.readability_level
                FROM pages p
                JOIN content_quality cq ON p.page_id = cq.page_id
                WHERE p.session_id = ? AND cq.quality_score <= ?
                ORDER BY cq.quality_score ASC
            """, (session_id, max_quality))
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def get_duplicate_pages(self, session_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene páginas con contenido duplicado.

        Args:
            session_id: ID de la sesión

        Returns:
            Lista de páginas duplicadas con sus originales
        """
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                SELECT p.url, p.title, cq.duplicate_of_page_id, cq.similarity_score,
                       p2.url as original_url, p2.title as original_title
                FROM pages p
                JOIN content_quality cq ON p.page_id = cq.page_id
                LEFT JOIN pages p2 ON cq.duplicate_of_page_id = p2.page_id
                WHERE p.session_id = ? AND cq.duplicate_of_page_id IS NOT NULL
                ORDER BY cq.similarity_score DESC
            """, (session_id,))
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    # ==================== ADVANCED QUERIES (PROFESSIONAL) ====================

    async def get_keywords_with_full_metrics(
        self,
        session_id: int,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Obtiene keywords con todas sus métricas profesionales combinadas.

        Args:
            session_id: ID de la sesión
            limit: Número máximo de resultados

        Returns:
            Lista de keywords con métricas completas
        """
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                SELECT
                    k.*,
                    km.difficulty_score,
                    km.opportunity_score,
                    km.competition_level,
                    km.cannibalization_score,
                    si.intent_type,
                    si.confidence as intent_confidence,
                    COUNT(DISTINCT p.page_id) as page_count
                FROM keywords k
                JOIN pages p ON k.page_id = p.page_id
                LEFT JOIN keyword_metrics km ON k.keyword_id = km.keyword_id
                LEFT JOIN search_intent si ON k.keyword_id = si.keyword_id
                WHERE p.session_id = ?
                GROUP BY k.keyword
                ORDER BY k.tf_idf_score DESC
                LIMIT ?
            """, (session_id, limit))
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def get_session_professional_stats(self, session_id: int) -> Dict[str, Any]:
        """
        Obtiene estadísticas profesionales avanzadas de una sesión.

        Args:
            session_id: ID de la sesión

        Returns:
            Diccionario con estadísticas profesionales
        """
        async with self.connection.cursor() as cursor:
            # Número de clusters
            await cursor.execute("""
                SELECT COUNT(*) as total FROM keyword_clusters WHERE session_id = ?
            """, (session_id,))
            total_clusters = (await cursor.fetchone())['total']

            # Número de tópicos
            await cursor.execute("""
                SELECT COUNT(*) as total FROM topics WHERE session_id = ?
            """, (session_id,))
            total_topics = (await cursor.fetchone())['total']

            # Promedio de quality score
            await cursor.execute("""
                SELECT AVG(cq.quality_score) as avg_quality
                FROM content_quality cq
                JOIN pages p ON cq.page_id = p.page_id
                WHERE p.session_id = ?
            """, (session_id,))
            avg_quality = (await cursor.fetchone())['avg_quality'] or 0.0

            # Páginas con thin content
            await cursor.execute("""
                SELECT COUNT(*) as total
                FROM content_quality cq
                JOIN pages p ON cq.page_id = p.page_id
                WHERE p.session_id = ? AND cq.is_thin_content = 1
            """, (session_id,))
            thin_content_pages = (await cursor.fetchone())['total']

            # Páginas duplicadas
            await cursor.execute("""
                SELECT COUNT(*) as total
                FROM content_quality cq
                JOIN pages p ON cq.page_id = p.page_id
                WHERE p.session_id = ? AND cq.duplicate_of_page_id IS NOT NULL
            """, (session_id,))
            duplicate_pages = (await cursor.fetchone())['total']

            # Keywords cannibalizadas
            await cursor.execute("""
                SELECT COUNT(*) as total
                FROM keyword_metrics km
                JOIN keywords k ON km.keyword_id = k.keyword_id
                JOIN pages p ON k.page_id = p.page_id
                WHERE p.session_id = ? AND km.cannibalization_score > 0.5
            """, (session_id,))
            cannibalized_keywords = (await cursor.fetchone())['total']

            # Keywords de alta oportunidad
            await cursor.execute("""
                SELECT COUNT(*) as total
                FROM keyword_metrics km
                JOIN keywords k ON km.keyword_id = k.keyword_id
                JOIN pages p ON k.page_id = p.page_id
                WHERE p.session_id = ? AND km.opportunity_score >= 70
            """, (session_id,))
            high_opportunity_keywords = (await cursor.fetchone())['total']

            return {
                'total_clusters': total_clusters,
                'total_topics': total_topics,
                'avg_quality_score': round(avg_quality, 2),
                'thin_content_pages': thin_content_pages,
                'duplicate_pages': duplicate_pages,
                'cannibalized_keywords': cannibalized_keywords,
                'high_opportunity_keywords': high_opportunity_keywords
            }

    async def get_images_by_session(self, session_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene todas las imágenes de una sesión.

        Args:
            session_id: ID de la sesión

        Returns:
            Lista de diccionarios con información de imágenes
        """
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                SELECT i.*
                FROM images i
                JOIN pages p ON i.page_id = p.page_id
                WHERE p.session_id = ?
                ORDER BY i.page_id
            """, (session_id,))
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def get_links_by_session(self, session_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene todos los enlaces de una sesión.

        Args:
            session_id: ID de la sesión

        Returns:
            Lista de diccionarios con información de enlaces
        """
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                SELECT l.*
                FROM links l
                JOIN pages p ON l.source_page_id = p.page_id
                WHERE p.session_id = ?
                ORDER BY l.source_page_id
            """, (session_id,))
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
