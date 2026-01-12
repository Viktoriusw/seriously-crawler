"""
Analizador de calidad de contenido.

Este módulo implementa análisis avanzado de calidad de contenido:
- Readability scores (Flesch Reading Ease, Flesch-Kincaid Grade Level)
- Lexical diversity (Type-Token Ratio)
- Sentence and word length analysis
- Thin content detection
- Duplicate content detection con similitud semántica
- Heading structure scoring
- Multimedia scoring (images, videos)
"""

import re
import logging
import hashlib
from typing import List, Dict, Any, Tuple, Optional, Set
from collections import Counter
import statistics

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

logger = logging.getLogger(__name__)


class ContentQualityAnalyzer:
    """
    Analizador de calidad de contenido SEO.
    """

    def __init__(self):
        """Inicializa el analizador de calidad."""
        # Umbrales de calidad
        self.thresholds = {
            'min_word_count': 300,  # Mínimo para no ser thin content
            'optimal_word_count': 1000,  # Óptimo para SEO
            'min_readability': 30,  # Muy difícil de leer
            'optimal_readability': 60,  # Nivel óptimo
            'min_lexical_diversity': 0.3,  # TTR mínimo aceptable
            'optimal_lexical_diversity': 0.5,  # TTR óptimo
            'duplicate_threshold': 0.85  # Similitud para considerar duplicado
        }

    # ==================== READABILITY ANALYSIS ====================

    def calculate_flesch_reading_ease(
        self,
        text: str,
        language: str = 'es'
    ) -> float:
        """
        Calcula el Flesch Reading Ease Score.

        Fórmula (español): 206.835 - 1.015(palabras/frases) - 84.6(sílabas/palabras)
        Fórmula (inglés): 206.835 - 1.015(palabras/frases) - 84.6(sílabas/palabras)

        Score:
        - 90-100: Muy fácil
        - 80-89: Fácil
        - 70-79: Bastante fácil
        - 60-69: Normal
        - 50-59: Bastante difícil
        - 30-49: Difícil
        - 0-29: Muy difícil

        Args:
            text: Texto a analizar
            language: Idioma ('es' o 'en')

        Returns:
            Flesch Reading Ease score (0-100)
        """
        if not text:
            return 0.0

        # Contar frases
        sentences = self._count_sentences(text)
        if sentences == 0:
            return 0.0

        # Contar palabras
        words = self._count_words(text)
        if words == 0:
            return 0.0

        # Contar sílabas
        syllables = self._count_syllables(text, language)

        # Calcular métricas
        words_per_sentence = words / sentences
        syllables_per_word = syllables / words

        # Fórmula de Flesch
        if language == 'es':
            # Fórmula adaptada al español (Fernández Huerta)
            score = 206.84 - (1.02 * words_per_sentence) - (60 * syllables_per_word)
        else:
            # Fórmula original en inglés
            score = 206.835 - (1.015 * words_per_sentence) - (84.6 * syllables_per_word)

        # Limitar a rango 0-100
        return max(0.0, min(100.0, score))

    def calculate_flesch_kincaid_grade(
        self,
        text: str,
        language: str = 'es'
    ) -> float:
        """
        Calcula el Flesch-Kincaid Grade Level.

        Indica el nivel educativo necesario para entender el texto.

        Args:
            text: Texto a analizar
            language: Idioma

        Returns:
            Grade level (nivel educativo)
        """
        if not text:
            return 0.0

        sentences = self._count_sentences(text)
        words = self._count_words(text)

        if sentences == 0 or words == 0:
            return 0.0

        syllables = self._count_syllables(text, language)

        words_per_sentence = words / sentences
        syllables_per_word = syllables / words

        # Fórmula
        grade = (0.39 * words_per_sentence) + (11.8 * syllables_per_word) - 15.59

        return max(0.0, grade)

    def _count_sentences(self, text: str) -> int:
        """Cuenta el número de frases en el texto."""
        # Dividir por puntos, signos de exclamación e interrogación
        sentences = re.split(r'[.!?]+', text)
        # Filtrar vacíos
        sentences = [s for s in sentences if s.strip()]
        return len(sentences)

    def _count_words(self, text: str) -> int:
        """Cuenta el número de palabras en el texto."""
        words = re.findall(r'\b\w+\b', text.lower())
        return len(words)

    def _count_syllables(self, text: str, language: str = 'es') -> int:
        """
        Cuenta el número aproximado de sílabas.

        Implementación simplificada basada en vocales.
        """
        text = text.lower()
        words = re.findall(r'\b\w+\b', text)

        total_syllables = 0

        for word in words:
            if language == 'es':
                # Contar vocales como aproximación de sílabas
                syllables = len(re.findall(r'[aeiouáéíóúü]', word))
                # Ajustar para diptongos comunes
                syllables -= len(re.findall(r'[aeiou][aeiou]', word)) * 0.5
            else:
                # Inglés: algoritmo simplificado
                syllables = len(re.findall(r'[aeiouy]+', word))
                # Ajuste para palabras que terminan en 'e' silenciosa
                if word.endswith('e'):
                    syllables -= 1

            # Mínimo 1 sílaba por palabra
            total_syllables += max(1, int(syllables))

        return total_syllables

    def get_readability_level(self, score: float) -> str:
        """
        Convierte Flesch score a nivel descriptivo.

        Args:
            score: Flesch Reading Ease score

        Returns:
            Nivel descriptivo
        """
        if score >= 90:
            return 'very_easy'
        elif score >= 80:
            return 'easy'
        elif score >= 70:
            return 'fairly_easy'
        elif score >= 60:
            return 'normal'
        elif score >= 50:
            return 'fairly_difficult'
        elif score >= 30:
            return 'difficult'
        else:
            return 'very_difficult'

    # ==================== LEXICAL ANALYSIS ====================

    def calculate_lexical_diversity(self, text: str) -> float:
        """
        Calcula la diversidad léxica (Type-Token Ratio).

        TTR = Palabras únicas / Total palabras

        Args:
            text: Texto a analizar

        Returns:
            Type-Token Ratio (0-1)
        """
        if not text:
            return 0.0

        words = re.findall(r'\b\w+\b', text.lower())

        if not words:
            return 0.0

        unique_words = set(words)
        ttr = len(unique_words) / len(words)

        return ttr

    def calculate_avg_sentence_length(self, text: str) -> float:
        """
        Calcula la longitud promedio de las frases.

        Args:
            text: Texto a analizar

        Returns:
            Promedio de palabras por frase
        """
        if not text:
            return 0.0

        sentences = self._count_sentences(text)
        words = self._count_words(text)

        if sentences == 0:
            return 0.0

        return words / sentences

    def calculate_avg_word_length(self, text: str) -> float:
        """
        Calcula la longitud promedio de las palabras.

        Args:
            text: Texto a analizar

        Returns:
            Promedio de caracteres por palabra
        """
        if not text:
            return 0.0

        words = re.findall(r'\b\w+\b', text)

        if not words:
            return 0.0

        total_chars = sum(len(word) for word in words)
        return total_chars / len(words)

    # ==================== CONTENT QUALITY SCORING ====================

    def calculate_quality_score(
        self,
        page_data: Dict[str, Any],
        content_text: str
    ) -> float:
        """
        Calcula un score general de calidad (0-100).

        Factores:
        - Word count (25%)
        - Readability (20%)
        - Lexical diversity (15%)
        - Heading structure (15%)
        - Multimedia presence (10%)
        - Metadata completeness (10%)
        - Internal links (5%)

        Args:
            page_data: Datos de la página
            content_text: Contenido textual

        Returns:
            Quality score (0-100)
        """
        scores = {}

        # Factor 1: Word count (25%)
        word_count = page_data.get('word_count', 0)
        if word_count >= self.thresholds['optimal_word_count']:
            scores['word_count'] = 100
        elif word_count >= self.thresholds['min_word_count']:
            # Escala lineal entre min y optimal
            ratio = (word_count - self.thresholds['min_word_count']) / \
                    (self.thresholds['optimal_word_count'] - self.thresholds['min_word_count'])
            scores['word_count'] = 50 + (ratio * 50)
        else:
            # Penalizar thin content
            scores['word_count'] = (word_count / self.thresholds['min_word_count']) * 50

        # Factor 2: Readability (20%)
        readability = self.calculate_flesch_reading_ease(content_text)
        if readability >= self.thresholds['optimal_readability']:
            scores['readability'] = 100
        elif readability >= self.thresholds['min_readability']:
            ratio = (readability - self.thresholds['min_readability']) / \
                    (self.thresholds['optimal_readability'] - self.thresholds['min_readability'])
            scores['readability'] = 50 + (ratio * 50)
        else:
            scores['readability'] = (readability / self.thresholds['min_readability']) * 50

        # Factor 3: Lexical diversity (15%)
        lexical_div = self.calculate_lexical_diversity(content_text)
        if lexical_div >= self.thresholds['optimal_lexical_diversity']:
            scores['lexical_diversity'] = 100
        elif lexical_div >= self.thresholds['min_lexical_diversity']:
            ratio = (lexical_div - self.thresholds['min_lexical_diversity']) / \
                    (self.thresholds['optimal_lexical_diversity'] - self.thresholds['min_lexical_diversity'])
            scores['lexical_diversity'] = 50 + (ratio * 50)
        else:
            scores['lexical_diversity'] = (lexical_div / self.thresholds['min_lexical_diversity']) * 50

        # Factor 4: Heading structure (15%) - placeholder
        # Esto se calculará en heading_structure_score
        scores['heading_structure'] = 70  # Placeholder

        # Factor 5: Multimedia (10%) - placeholder
        scores['multimedia'] = 60  # Placeholder

        # Factor 6: Metadata (10%)
        metadata_score = 0
        if page_data.get('title'):
            metadata_score += 35
        if page_data.get('meta_description'):
            metadata_score += 35
        if page_data.get('h1'):
            metadata_score += 30
        scores['metadata'] = metadata_score

        # Factor 7: Internal links (5%) - placeholder
        scores['internal_links'] = 50  # Placeholder

        # Calcular score ponderado
        quality_score = (
            scores['word_count'] * 0.25 +
            scores['readability'] * 0.20 +
            scores['lexical_diversity'] * 0.15 +
            scores['heading_structure'] * 0.15 +
            scores['multimedia'] * 0.10 +
            scores['metadata'] * 0.10 +
            scores['internal_links'] * 0.05
        )

        return round(quality_score, 2)

    # ==================== THIN CONTENT DETECTION ====================

    def is_thin_content(
        self,
        word_count: int,
        has_multimedia: bool = False
    ) -> bool:
        """
        Detecta si el contenido es "thin" (delgado).

        Args:
            word_count: Número de palabras
            has_multimedia: Si tiene imágenes/videos

        Returns:
            True si es thin content
        """
        # Umbral básico
        if word_count < self.thresholds['min_word_count']:
            # Si tiene multimedia, ser más permisivo
            if has_multimedia and word_count >= 150:
                return False
            return True

        return False

    # ==================== DUPLICATE CONTENT DETECTION ====================

    def calculate_content_similarity(
        self,
        text1: str,
        text2: str,
        method: str = 'tfidf'
    ) -> float:
        """
        Calcula la similitud entre dos textos.

        Args:
            text1: Primer texto
            text2: Segundo texto
            method: Método ('tfidf', 'hash')

        Returns:
            Similarity score (0-1)
        """
        if not text1 or not text2:
            return 0.0

        if method == 'hash':
            # Similitud basada en hash (exactitud)
            hash1 = hashlib.md5(text1.encode()).hexdigest()
            hash2 = hashlib.md5(text2.encode()).hexdigest()
            return 1.0 if hash1 == hash2 else 0.0

        elif method == 'tfidf':
            if not SKLEARN_AVAILABLE:
                # Fallback a Jaccard similarity
                return self._jaccard_similarity(text1, text2)

            try:
                vectorizer = TfidfVectorizer(min_df=1, max_df=0.9)
                tfidf_matrix = vectorizer.fit_transform([text1, text2])
                similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
                return float(similarity)
            except Exception as e:
                logger.error(f"Error calculando similitud TF-IDF: {e}")
                return self._jaccard_similarity(text1, text2)

        return 0.0

    def _jaccard_similarity(self, text1: str, text2: str) -> float:
        """
        Calcula similitud de Jaccard entre dos textos.

        Args:
            text1: Primer texto
            text2: Segundo texto

        Returns:
            Jaccard similarity (0-1)
        """
        words1 = set(re.findall(r'\b\w+\b', text1.lower()))
        words2 = set(re.findall(r'\b\w+\b', text2.lower()))

        if not words1 or not words2:
            return 0.0

        intersection = len(words1 & words2)
        union = len(words1 | words2)

        return intersection / union if union > 0 else 0.0

    def find_duplicate_pages(
        self,
        pages: List[Dict[str, Any]],
        threshold: float = 0.85
    ) -> List[Tuple[int, int, float]]:
        """
        Encuentra páginas duplicadas.

        Args:
            pages: Lista de páginas con content_hash
            threshold: Umbral de similitud

        Returns:
            Lista de tuplas (page_id1, page_id2, similarity)
        """
        duplicates = []

        # Crear mapa de hash -> page_ids
        hash_map: Dict[str, List[int]] = {}

        for page in pages:
            content_hash = page.get('content_hash')
            page_id = page.get('page_id')

            if not content_hash or not page_id:
                continue

            if content_hash not in hash_map:
                hash_map[content_hash] = []
            hash_map[content_hash].append(page_id)

        # Páginas con mismo hash son duplicados exactos
        for content_hash, page_ids in hash_map.items():
            if len(page_ids) > 1:
                # Todas las combinaciones son duplicados
                for i in range(len(page_ids)):
                    for j in range(i + 1, len(page_ids)):
                        duplicates.append((page_ids[i], page_ids[j], 1.0))

        return duplicates

    # ==================== HEADING STRUCTURE SCORING ====================

    def calculate_heading_structure_score(
        self,
        headings: List[Dict[str, Any]]
    ) -> float:
        """
        Calcula un score de calidad de estructura de encabezados.

        Criterios:
        - Tiene H1 (30 puntos)
        - Solo 1 H1 (20 puntos)
        - Orden jerárquico correcto (30 puntos)
        - Distribución balanceada (20 puntos)

        Args:
            headings: Lista de encabezados con level y text

        Returns:
            Score (0-100)
        """
        if not headings:
            return 0.0

        score = 0.0

        # Contar por nivel
        level_counts = Counter(h.get('level', 0) for h in headings)

        # Criterio 1: Tiene H1
        if level_counts.get(1, 0) > 0:
            score += 30

        # Criterio 2: Solo 1 H1
        if level_counts.get(1, 0) == 1:
            score += 20

        # Criterio 3: Orden jerárquico
        levels = [h.get('level', 0) for h in headings]
        is_hierarchical = self._check_hierarchical_order(levels)
        if is_hierarchical:
            score += 30

        # Criterio 4: Distribución balanceada
        if len(headings) >= 3:
            # Tiene suficientes encabezados
            score += 20
        elif len(headings) >= 1:
            # Al menos tiene algunos
            score += 10

        return min(score, 100.0)

    def _check_hierarchical_order(self, levels: List[int]) -> bool:
        """
        Verifica si los encabezados siguen orden jerárquico.

        Args:
            levels: Lista de niveles de encabezados

        Returns:
            True si el orden es correcto
        """
        if not levels:
            return True

        # No debe saltar niveles (ej: H1 -> H3 sin H2)
        for i in range(1, len(levels)):
            # Si salta más de 1 nivel, es incorrecto
            if levels[i] > levels[i-1] + 1:
                return False

        return True

    # ==================== MULTIMEDIA SCORING ====================

    def calculate_multimedia_score(
        self,
        images: List[Dict[str, Any]],
        word_count: int
    ) -> float:
        """
        Calcula un score de uso de multimedia.

        Criterios:
        - Número de imágenes vs word count
        - Imágenes con alt text
        - Tamaño apropiado de imágenes

        Args:
            images: Lista de imágenes
            word_count: Número de palabras del contenido

        Returns:
            Score (0-100)
        """
        if word_count == 0:
            return 0.0

        score = 0.0

        # Criterio 1: Ratio de imágenes (50 puntos)
        # Óptimo: 1 imagen cada 300-500 palabras
        optimal_ratio = 1 / 400
        actual_ratio = len(images) / word_count if word_count > 0 else 0

        if 0.002 <= actual_ratio <= 0.005:  # ~1 cada 200-500 palabras
            score += 50
        elif actual_ratio > 0:
            # Penalizar proporcionalmente
            score += min(actual_ratio / optimal_ratio, 1.0) * 50

        # Criterio 2: Alt text presente (30 puntos)
        if images:
            images_with_alt = sum(1 for img in images if img.get('alt_text'))
            alt_ratio = images_with_alt / len(images)
            score += alt_ratio * 30

        # Criterio 3: Al menos 1 imagen (20 puntos)
        if len(images) > 0:
            score += 20

        return min(score, 100.0)

    # ==================== BATCH ANALYSIS ====================

    def analyze_page_quality(
        self,
        page_data: Dict[str, Any],
        content_text: str,
        headings: List[Dict[str, Any]],
        images: List[Dict[str, Any]],
        language: str = 'es'
    ) -> Dict[str, Any]:
        """
        Analiza la calidad completa de una página.

        Args:
            page_data: Datos básicos de la página
            content_text: Contenido textual
            headings: Lista de encabezados
            images: Lista de imágenes
            language: Idioma

        Returns:
            Diccionario con todas las métricas de calidad
        """
        word_count = page_data.get('word_count', 0)

        # Readability
        readability_score = self.calculate_flesch_reading_ease(content_text, language)
        readability_level = self.get_readability_level(readability_score)
        grade_level = self.calculate_flesch_kincaid_grade(content_text, language)

        # Lexical analysis
        lexical_diversity = self.calculate_lexical_diversity(content_text)
        avg_sentence_length = self.calculate_avg_sentence_length(content_text)
        avg_word_length = self.calculate_avg_word_length(content_text)

        # Structure scores
        heading_structure_score = self.calculate_heading_structure_score(headings)
        multimedia_score = self.calculate_multimedia_score(images, word_count)

        # Thin content
        is_thin = self.is_thin_content(word_count, has_multimedia=len(images) > 0)

        # Quality score general
        quality_score = self.calculate_quality_score(page_data, content_text)

        return {
            'quality_score': quality_score,
            'readability_score': round(readability_score, 2),
            'readability_level': readability_level,
            'grade_level': round(grade_level, 2),
            'lexical_diversity': round(lexical_diversity, 3),
            'avg_sentence_length': round(avg_sentence_length, 2),
            'avg_word_length': round(avg_word_length, 2),
            'is_thin_content': is_thin,
            'heading_structure_score': round(heading_structure_score, 2),
            'multimedia_score': round(multimedia_score, 2),
            'duplicate_of_page_id': None,  # Se determina después
            'similarity_score': 0.0
        }

    def analyze_content_quality(
        self,
        pages: List[Dict[str, Any]],
        language: str = 'es'
    ) -> Dict[str, Any]:
        """
        Analiza la calidad de contenido de múltiples páginas.

        Args:
            pages: Lista de páginas con sus datos
            language: Idioma para análisis

        Returns:
            Diccionario con resultados del análisis de todas las páginas
        """
        from bs4 import BeautifulSoup

        pages_with_quality = []
        thin_content_pages = []
        low_quality_pages = []

        for page in pages:
            # Obtener contenido HTML
            html = page.get('html_content', '')
            if not html:
                continue

            try:
                soup = BeautifulSoup(html, 'lxml')
                text = soup.get_text(separator=' ', strip=True)

                # Extraer headings
                headings = []
                for level in range(1, 7):
                    for heading in soup.find_all(f'h{level}'):
                        headings.append({
                            'level': level,
                            'text': heading.get_text(strip=True)
                        })

                # Extraer imágenes (simplificado)
                images = [{'src': img.get('src', ''), 'alt': img.get('alt', '')} for img in soup.find_all('img')]

                # Analizar calidad
                quality_metrics = self.analyze_page_quality(page, text, headings, images, language)

                page_result = {
                    'page_id': page.get('page_id', page.get('id')),
                    'url': page.get('url', ''),
                    'word_count': page.get('word_count', len(text.split())),
                    **quality_metrics
                }

                pages_with_quality.append(page_result)

                # Clasificar problemas
                if quality_metrics['is_thin_content']:
                    thin_content_pages.append(page_result)

                if quality_metrics['quality_score'] < 50:
                    low_quality_pages.append(page_result)

            except Exception as e:
                logger.error(f"Error analizando página {page.get('url')}: {e}")
                continue

        return {
            'pages': pages_with_quality,
            'thin_content': thin_content_pages,
            'low_quality': low_quality_pages,
            'summary': {
                'total_pages': len(pages),
                'analyzed_pages': len(pages_with_quality),
                'thin_content_count': len(thin_content_pages),
                'low_quality_count': len(low_quality_pages),
                'avg_quality_score': sum(p['quality_score'] for p in pages_with_quality) / len(pages_with_quality) if pages_with_quality else 0,
                'avg_readability': sum(p['readability_score'] for p in pages_with_quality) / len(pages_with_quality) if pages_with_quality else 0
            }
        }
