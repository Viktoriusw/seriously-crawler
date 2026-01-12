"""
Analizador de keywords para el SEO Crawler.

Este módulo analiza el contenido de las páginas para extraer keywords,
calcular frecuencias, densidades, TF-IDF scores y otras métricas relevantes.
"""

import re
from typing import Dict, List, Any, Set, Optional
from collections import Counter
import math
import logging

logger = logging.getLogger('SEOCrawler.KeywordAnalyzer')


class KeywordAnalyzer:
    """Analizador de keywords con soporte para TF-IDF y n-gramas."""

    def __init__(self,
                 min_length: int = 3,
                 max_length: int = 50,
                 stop_words_language: str = 'spanish'):
        """
        Inicializa el analizador de keywords.

        Args:
            min_length: Longitud mínima de keyword
            max_length: Longitud máxima de keyword
            stop_words_language: Idioma de las stop words
        """
        self.min_length = min_length
        self.max_length = max_length
        self.stop_words = self._load_stop_words(stop_words_language)
        self.document_frequencies: Dict[str, int] = {}  # Para TF-IDF
        self.total_documents = 0

    def _load_stop_words(self, language: str) -> Set[str]:
        """
        Carga las stop words para el idioma especificado.

        Args:
            language: Idioma (spanish, english, etc.)

        Returns:
            Set de stop words
        """
        # Stop words básicas en español
        spanish_stop_words = {
            'el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'ser', 'se', 'no', 'haber',
            'por', 'con', 'su', 'para', 'como', 'estar', 'tener', 'le', 'lo', 'todo',
            'pero', 'más', 'hacer', 'o', 'poder', 'decir', 'este', 'ir', 'otro', 'ese',
            'la', 'si', 'me', 'ya', 'ver', 'porque', 'dar', 'cuando', 'él', 'muy', 'sin',
            'vez', 'mucho', 'saber', 'qué', 'sobre', 'mi', 'alguno', 'mismo', 'yo', 'también',
            'hasta', 'año', 'dos', 'querer', 'entre', 'así', 'primero', 'desde', 'grande',
            'eso', 'ni', 'nos', 'llegar', 'pasar', 'tiempo', 'ella', 'sí', 'día', 'uno',
            'bien', 'poco', 'deber', 'entonces', 'poner', 'cosa', 'tanto', 'hombre', 'parecer',
            'nuestro', 'tan', 'donde', 'ahora', 'parte', 'después', 'vida', 'quedar', 'siempre',
            'creer', 'hablar', 'llevar', 'dejar', 'nada', 'cada', 'seguir', 'menos', 'nuevo',
            'encontrar', 'algo', 'solo', 'decir', 'salir', 'volver', 'tomar', 'conocer', 'vivir',
            'sentir', 'tratar', 'mirar', 'contar', 'empezar', 'esperar', 'buscar', 'existir',
            'entrar', 'trabajar', 'escribir', 'perder', 'producir', 'ocurrir', 'entender',
            'pedir', 'recibir', 'recordar', 'terminar', 'permitir', 'aparecer', 'conseguir',
            'comenzar', 'servir', 'sacar', 'necesitar', 'mantener', 'resultar', 'leer', 'caer',
            'cambiar', 'presentar', 'crear', 'abrir', 'considerar', 'oir', 'acabar', 'mil',
            'tal', 'va', 'fue', 'sido', 'son', 'está', 'estaba', 'he', 'ha', 'han', 'es',
            'era', 'eres', 'soy', 'sea', 'será', 'del', 'las', 'los', 'al', 'una', 'unos', 'unas'
        }

        # Stop words básicas en inglés
        english_stop_words = {
            'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i', 'it', 'for',
            'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at', 'this', 'but', 'his', 'by',
            'from', 'they', 'we', 'say', 'her', 'she', 'or', 'an', 'will', 'my', 'one', 'all',
            'would', 'there', 'their', 'what', 'so', 'up', 'out', 'if', 'about', 'who', 'get',
            'which', 'go', 'me', 'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him',
            'know', 'take', 'people', 'into', 'year', 'your', 'good', 'some', 'could', 'them',
            'see', 'other', 'than', 'then', 'now', 'look', 'only', 'come', 'its', 'over',
            'think', 'also', 'back', 'after', 'use', 'two', 'how', 'our', 'work', 'first',
            'well', 'way', 'even', 'new', 'want', 'because', 'any', 'these', 'give', 'day',
            'most', 'us', 'is', 'was', 'are', 'been', 'has', 'had', 'were', 'said', 'did',
            'having', 'may', 'should', 'am', 'being'
        }

        if language.lower() == 'spanish':
            return spanish_stop_words
        elif language.lower() == 'english':
            return english_stop_words
        else:
            return spanish_stop_words  # Default

    def _extract_words(self, text: str) -> List[str]:
        """
        Extrae palabras individuales del texto.

        Args:
            text: Texto a procesar

        Returns:
            Lista de palabras
        """
        # Convertir a minúsculas
        text = text.lower()

        # Extraer palabras (letras, números, guiones)
        words = re.findall(r'\b[a-záéíóúñü\-]+\b', text)

        # Filtrar por longitud y stop words
        filtered_words = [
            word for word in words
            if self.min_length <= len(word) <= self.max_length
            and word not in self.stop_words
            and not word.isdigit()
        ]

        return filtered_words

    def _extract_ngrams(self, words: List[str], n: int) -> List[str]:
        """
        Extrae n-gramas de una lista de palabras.

        Args:
            words: Lista de palabras
            n: Tamaño del n-grama

        Returns:
            Lista de n-gramas
        """
        if len(words) < n:
            return []

        ngrams = []
        for i in range(len(words) - n + 1):
            ngram = ' '.join(words[i:i+n])
            # Verificar longitud total
            if len(ngram) <= self.max_length:
                ngrams.append(ngram)

        return ngrams

    def _calculate_density(self, keyword: str, text: str, total_words: int) -> float:
        """
        Calcula la densidad de una keyword en el texto.

        Args:
            keyword: Palabra clave
            text: Texto completo
            total_words: Total de palabras

        Returns:
            Densidad como porcentaje
        """
        if total_words == 0:
            return 0.0

        # Contar ocurrencias
        keyword_lower = keyword.lower()
        text_lower = text.lower()

        # Para n-gramas, buscar como frase completa
        if ' ' in keyword:
            count = text_lower.count(keyword_lower)
            # Un n-grama de 2 palabras cuenta como 2 palabras
            words_per_occurrence = len(keyword.split())
            total_keyword_words = count * words_per_occurrence
        else:
            count = len(re.findall(r'\b' + re.escape(keyword_lower) + r'\b', text_lower))
            total_keyword_words = count

        density = (total_keyword_words / total_words) * 100
        return round(density, 2)

    def _calculate_tf(self, keyword: str, text: str) -> float:
        """
        Calcula el Term Frequency (TF) de una keyword.

        Args:
            keyword: Palabra clave
            text: Texto

        Returns:
            TF score
        """
        words = self._extract_words(text)
        total_words = len(words)

        if total_words == 0:
            return 0.0

        keyword_lower = keyword.lower()

        # Contar ocurrencias
        if ' ' in keyword:  # N-grama
            # Crear n-gramas del texto
            ngram_size = len(keyword.split())
            ngrams = self._extract_ngrams(words, ngram_size)
            count = ngrams.count(keyword_lower)
        else:  # Palabra simple
            count = words.count(keyword_lower)

        tf = count / total_words
        return tf

    def _calculate_tfidf(self, tf: float, keyword: str) -> float:
        """
        Calcula el TF-IDF score de una keyword.

        Args:
            tf: Term Frequency
            keyword: Palabra clave

        Returns:
            TF-IDF score
        """
        if self.total_documents == 0:
            return tf  # Si no hay corpus, retornar solo TF

        # Obtener document frequency
        df = self.document_frequencies.get(keyword, 1)

        # Calcular IDF (Inverse Document Frequency)
        idf = math.log((self.total_documents + 1) / (df + 1)) + 1

        # TF-IDF
        tfidf = tf * idf

        return round(tfidf, 4)

    def _is_in_element(self, keyword: str, element_text: Optional[str]) -> bool:
        """
        Verifica si una keyword aparece en un elemento específico.

        Args:
            keyword: Palabra clave
            element_text: Texto del elemento

        Returns:
            True si aparece, False en caso contrario
        """
        if not element_text:
            return False

        keyword_lower = keyword.lower()
        element_lower = element_text.lower()

        return keyword_lower in element_lower

    def _is_in_first_n_words(self, keyword: str, text: str, n: int = 100) -> bool:
        """
        Verifica si una keyword aparece en las primeras N palabras.

        Args:
            keyword: Palabra clave
            text: Texto completo
            n: Número de palabras

        Returns:
            True si aparece, False en caso contrario
        """
        words = text.split()
        first_n_words = ' '.join(words[:n])

        return self._is_in_element(keyword, first_n_words)

    def analyze(self,
                text: str,
                title: str = '',
                headings: List[Dict[str, Any]] = None,
                max_ngram: int = 3,
                min_frequency: int = 2) -> Dict[str, Any]:
        """
        Analiza el texto y extrae keywords con sus métricas.

        Args:
            text: Texto principal a analizar
            title: Título de la página
            headings: Lista de headings (h1-h6)
            max_ngram: Tamaño máximo de n-grama
            min_frequency: Frecuencia mínima para considerar una keyword

        Returns:
            Diccionario con keywords y estadísticas
        """
        if headings is None:
            headings = []

        # Extraer palabras individuales
        words = self._extract_words(text)
        total_words = len(words)

        # Contador de palabras
        word_counter = Counter(words)

        # Extraer h1 text
        h1_text = ''
        for heading in headings:
            if heading.get('level') == 1:
                h1_text = heading.get('text', '')
                break

        # Lista de keywords con sus datos
        keywords_list = []

        # 1. Procesar palabras individuales (1-gramas)
        for word, frequency in word_counter.items():
            if frequency < min_frequency:
                continue

            tf = self._calculate_tf(word, text)
            tfidf = self._calculate_tfidf(tf, word)
            density = self._calculate_density(word, text, total_words)

            keywords_list.append({
                'keyword': word,
                'frequency': frequency,
                'density': density,
                'tf_idf_score': tfidf,
                'position_in_title': self._is_in_element(word, title),
                'position_in_h1': self._is_in_element(word, h1_text),
                'position_in_first_100': self._is_in_first_n_words(word, text, 100),
                'is_ngram': False,
                'ngram_size': 1
            })

        # 2. Procesar n-gramas (2-gramas y 3-gramas)
        for n in range(2, max_ngram + 1):
            ngrams = self._extract_ngrams(words, n)

            if not ngrams:
                continue

            ngram_counter = Counter(ngrams)

            for ngram, frequency in ngram_counter.items():
                if frequency < min_frequency:
                    continue

                tf = frequency / total_words
                tfidf = self._calculate_tfidf(tf, ngram)
                density = self._calculate_density(ngram, text, total_words)

                keywords_list.append({
                    'keyword': ngram,
                    'frequency': frequency,
                    'density': density,
                    'tf_idf_score': tfidf,
                    'position_in_title': self._is_in_element(ngram, title),
                    'position_in_h1': self._is_in_element(ngram, h1_text),
                    'position_in_first_100': self._is_in_first_n_words(ngram, text, 100),
                    'is_ngram': True,
                    'ngram_size': n
                })

        # Ordenar por TF-IDF
        keywords_list.sort(key=lambda x: x['tf_idf_score'], reverse=True)

        # Estadísticas
        stats = {
            'total_words': total_words,
            'unique_words': len(word_counter),
            'total_keywords': len(keywords_list),
            'keywords': keywords_list
        }

        return stats

    def update_corpus(self, keywords: List[str]) -> None:
        """
        Actualiza el corpus de documentos para cálculo de IDF.

        Args:
            keywords: Lista de keywords del documento
        """
        self.total_documents += 1

        # Actualizar document frequencies
        unique_keywords = set(keywords)
        for keyword in unique_keywords:
            self.document_frequencies[keyword] = self.document_frequencies.get(keyword, 0) + 1

    def detect_keyword_stuffing(self, keywords: List[Dict[str, Any]], threshold: float = 5.0) -> List[str]:
        """
        Detecta keyword stuffing basado en densidad.

        Args:
            keywords: Lista de keywords con sus métricas
            threshold: Densidad máxima aceptable (%)

        Returns:
            Lista de keywords con stuffing
        """
        stuffed_keywords = []

        for kw in keywords:
            if kw['density'] > threshold:
                stuffed_keywords.append(kw['keyword'])

        return stuffed_keywords

    def find_keyword_gaps(self,
                         page_keywords: List[str],
                         competitor_keywords: List[str]) -> List[str]:
        """
        Encuentra keywords que tiene el competidor pero no la página.

        Args:
            page_keywords: Keywords de la página analizada
            competitor_keywords: Keywords del competidor

        Returns:
            Lista de keywords faltantes
        """
        page_set = set(page_keywords)
        competitor_set = set(competitor_keywords)

        gaps = competitor_set - page_set

        return list(gaps)

    def calculate_keyword_similarity(self,
                                    keywords1: List[str],
                                    keywords2: List[str]) -> float:
        """
        Calcula la similitud entre dos conjuntos de keywords (Jaccard similarity).

        Args:
            keywords1: Primera lista de keywords
            keywords2: Segunda lista de keywords

        Returns:
            Similitud (0-1)
        """
        set1 = set(keywords1)
        set2 = set(keywords2)

        if not set1 and not set2:
            return 1.0

        if not set1 or not set2:
            return 0.0

        intersection = len(set1 & set2)
        union = len(set1 | set2)

        similarity = intersection / union

        return round(similarity, 4)
