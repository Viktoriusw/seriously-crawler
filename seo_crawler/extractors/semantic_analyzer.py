"""
Analizador semántico profesional de keywords.

Este módulo implementa capacidades avanzadas de NLP y análisis semántico:
- Clustering de keywords con K-means y DBSCAN
- Embeddings semánticos con sentence-transformers
- Topic modeling con LDA (Latent Dirichlet Allocation)
- Clasificación de intención de búsqueda (search intent)
- Análisis de similitud semántica
"""

import re
import json
import logging
from typing import List, Dict, Any, Tuple, Optional
from collections import Counter, defaultdict
import numpy as np

# NLP y ML imports (se instalarán en requirements.txt)
try:
    import spacy
    from spacy.lang.es import Spanish
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

try:
    from sklearn.cluster import KMeans, DBSCAN
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.decomposition import LatentDirichletAllocation
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

logger = logging.getLogger(__name__)


class SemanticAnalyzer:
    """
    Analizador semántico de keywords con capacidades profesionales.
    """

    def __init__(self, language: str = 'es'):
        """
        Inicializa el analizador semántico.

        Args:
            language: Idioma para el análisis ('es' o 'en')
        """
        self.language = language
        self.nlp = None
        self.embedding_model = None

        # Verificar disponibilidad de librerías
        if not SKLEARN_AVAILABLE:
            logger.warning("scikit-learn no disponible. Clustering y LDA desactivados.")

        if not TRANSFORMERS_AVAILABLE:
            logger.warning("sentence-transformers no disponible. Embeddings desactivados.")

        # Inicializar spaCy si está disponible
        if SPACY_AVAILABLE:
            try:
                if language == 'es':
                    self.nlp = spacy.load('es_core_news_sm')
                else:
                    self.nlp = spacy.load('en_core_web_sm')
                logger.info(f"spaCy cargado para idioma: {language}")
            except OSError:
                logger.warning(f"Modelo spaCy no encontrado. Ejecuta: python -m spacy download {language}_core_news_sm")
                self.nlp = None

        # Inicializar modelo de embeddings si está disponible
        if TRANSFORMERS_AVAILABLE:
            try:
                # Usar modelo multilingüe ligero
                self.embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
                logger.info("Modelo de embeddings cargado")
            except Exception as e:
                logger.warning(f"Error al cargar modelo de embeddings: {e}")
                self.embedding_model = None

        # Patrones para detección de intención de búsqueda
        self.intent_patterns = {
            'transactional': [
                r'\b(comprar|precio|oferta|descuento|tienda|vender|coste|gratis)\b',
                r'\b(buy|price|sale|discount|shop|cost|free|deal)\b'
            ],
            'navigational': [
                r'\b(login|acceder|sitio|web|página|contacto|ubicación)\b',
                r'\b(login|website|site|contact|location|homepage)\b'
            ],
            'commercial': [
                r'\b(mejor|top|comparar|vs|revisión|opinión|reseña)\b',
                r'\b(best|top|compare|vs|review|rating)\b'
            ]
            # Si no coincide con ninguno, será 'informational' por defecto
        }

    # ==================== CLUSTERING DE KEYWORDS ====================

    def cluster_keywords(
        self,
        keywords: List[Dict[str, Any]],
        method: str = 'kmeans',
        n_clusters: int = 10,
        use_embeddings: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Agrupa keywords en clusters semánticos.

        Args:
            keywords: Lista de keywords con sus datos
            method: Método de clustering ('kmeans' o 'dbscan')
            n_clusters: Número de clusters para k-means
            use_embeddings: Si True usa embeddings semánticos, si False usa TF-IDF

        Returns:
            Lista de clusters con sus keywords
        """
        if not SKLEARN_AVAILABLE:
            logger.error("scikit-learn no disponible")
            return []

        if len(keywords) < n_clusters:
            logger.warning(f"Pocas keywords ({len(keywords)}) para {n_clusters} clusters")
            n_clusters = max(2, len(keywords) // 2)

        # Extraer textos de keywords
        keyword_texts = [kw.get('keyword', '') for kw in keywords]

        if not keyword_texts:
            return []

        # Obtener vectores de características
        if use_embeddings and self.embedding_model:
            logger.info("Usando embeddings semánticos para clustering")
            vectors = self._get_embeddings(keyword_texts)
        else:
            logger.info("Usando TF-IDF para clustering")
            vectors = self._get_tfidf_vectors(keyword_texts)

        # Aplicar clustering
        if method == 'kmeans':
            cluster_labels = self._kmeans_clustering(vectors, n_clusters)
        elif method == 'dbscan':
            cluster_labels = self._dbscan_clustering(vectors)
        else:
            logger.error(f"Método de clustering desconocido: {method}")
            return []

        # Organizar resultados por cluster
        clusters = self._organize_clusters(keywords, cluster_labels, vectors)

        return clusters

    def _get_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Genera embeddings semánticos para textos.

        Args:
            texts: Lista de textos

        Returns:
            Matriz de embeddings
        """
        if not self.embedding_model:
            logger.warning("Modelo de embeddings no disponible, usando TF-IDF")
            return self._get_tfidf_vectors(texts)

        try:
            embeddings = self.embedding_model.encode(texts, show_progress_bar=False)
            return embeddings
        except Exception as e:
            logger.error(f"Error generando embeddings: {e}")
            return self._get_tfidf_vectors(texts)

    def _get_tfidf_vectors(self, texts: List[str]) -> np.ndarray:
        """
        Genera vectores TF-IDF para textos.

        Args:
            texts: Lista de textos

        Returns:
            Matriz TF-IDF
        """
        vectorizer = TfidfVectorizer(
            max_features=100,
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.8
        )

        try:
            vectors = vectorizer.fit_transform(texts).toarray()
            return vectors
        except Exception as e:
            logger.error(f"Error generando vectores TF-IDF: {e}")
            # Devolver vectores cero como fallback
            return np.zeros((len(texts), 10))

    def _kmeans_clustering(self, vectors: np.ndarray, n_clusters: int) -> np.ndarray:
        """
        Aplica K-means clustering.

        Args:
            vectors: Matriz de vectores de características
            n_clusters: Número de clusters

        Returns:
            Array de etiquetas de cluster
        """
        try:
            kmeans = KMeans(
                n_clusters=n_clusters,
                random_state=42,
                n_init=10,
                max_iter=300
            )
            labels = kmeans.fit_predict(vectors)
            return labels
        except Exception as e:
            logger.error(f"Error en K-means clustering: {e}")
            return np.zeros(len(vectors), dtype=int)

    def _dbscan_clustering(self, vectors: np.ndarray, eps: float = 0.3, min_samples: int = 3) -> np.ndarray:
        """
        Aplica DBSCAN clustering (density-based).

        Args:
            vectors: Matriz de vectores de características
            eps: Radio de vecindad
            min_samples: Mínimo de muestras para un cluster

        Returns:
            Array de etiquetas de cluster (-1 para noise)
        """
        try:
            dbscan = DBSCAN(eps=eps, min_samples=min_samples, metric='cosine')
            labels = dbscan.fit_predict(vectors)
            return labels
        except Exception as e:
            logger.error(f"Error en DBSCAN clustering: {e}")
            return np.zeros(len(vectors), dtype=int)

    def _organize_clusters(
        self,
        keywords: List[Dict[str, Any]],
        labels: np.ndarray,
        vectors: np.ndarray
    ) -> List[Dict[str, Any]]:
        """
        Organiza keywords en clusters con metadatos.

        Args:
            keywords: Lista de keywords originales
            labels: Etiquetas de cluster
            vectors: Vectores de características

        Returns:
            Lista de clusters organizados
        """
        clusters_dict = defaultdict(list)

        # Agrupar keywords por cluster
        for idx, (kw, label) in enumerate(zip(keywords, labels)):
            if label == -1:  # Noise en DBSCAN
                continue

            clusters_dict[int(label)].append({
                'keyword_data': kw,
                'vector': vectors[idx],
                'keyword_id': kw.get('keyword_id')
            })

        # Crear lista de clusters con metadatos
        clusters = []
        for cluster_id, cluster_keywords in clusters_dict.items():
            if not cluster_keywords:
                continue

            # Calcular centroide del cluster
            cluster_vectors = np.array([item['vector'] for item in cluster_keywords])
            centroid = np.mean(cluster_vectors, axis=0)

            # Encontrar keyword más representativa (más cercana al centroide)
            similarities = cosine_similarity([centroid], cluster_vectors)[0]
            main_keyword_idx = np.argmax(similarities)
            main_keyword = cluster_keywords[main_keyword_idx]['keyword_data']

            # Calcular TF-IDF promedio
            avg_tfidf = np.mean([kw['keyword_data'].get('tf_idf_score', 0.0)
                                for kw in cluster_keywords])

            clusters.append({
                'cluster_id': cluster_id,
                'cluster_name': f"Cluster {cluster_id + 1}",
                'main_keyword': main_keyword.get('keyword', ''),
                'num_keywords': len(cluster_keywords),
                'avg_tfidf': avg_tfidf,
                'keywords': cluster_keywords
            })

        # Ordenar por TF-IDF promedio
        clusters.sort(key=lambda x: x['avg_tfidf'], reverse=True)

        return clusters

    # ==================== TOPIC MODELING ====================

    def extract_topics(
        self,
        keywords: List[Dict[str, Any]],
        n_topics: int = 5,
        n_top_words: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Extrae tópicos usando LDA (Latent Dirichlet Allocation).

        Args:
            keywords: Lista de keywords
            n_topics: Número de tópicos a extraer
            n_top_words: Número de palabras principales por tópico

        Returns:
            Lista de tópicos con sus palabras principales
        """
        if not SKLEARN_AVAILABLE:
            logger.error("scikit-learn no disponible para LDA")
            return []

        keyword_texts = [kw.get('keyword', '') for kw in keywords]

        if len(keyword_texts) < n_topics:
            logger.warning(f"Pocas keywords para extraer {n_topics} tópicos")
            n_topics = max(2, len(keyword_texts) // 3)

        try:
            # Crear matriz TF para LDA (no TF-IDF)
            vectorizer = TfidfVectorizer(
                max_features=200,
                max_df=0.85,
                min_df=2,
                use_idf=False,  # Solo TF para LDA
                norm=None
            )

            tf_matrix = vectorizer.fit_transform(keyword_texts)
            feature_names = vectorizer.get_feature_names_out()

            # Aplicar LDA
            lda = LatentDirichletAllocation(
                n_components=n_topics,
                random_state=42,
                max_iter=20,
                learning_method='batch'
            )

            lda.fit(tf_matrix)

            # Extraer palabras principales de cada tópico
            topics = []
            for topic_idx, topic in enumerate(lda.components_):
                top_indices = topic.argsort()[-n_top_words:][::-1]
                top_words = [feature_names[i] for i in top_indices]

                # Calcular coherence score aproximado
                coherence = float(np.mean(topic[top_indices]))

                topics.append({
                    'topic_id': topic_idx,
                    'topic_name': f"Topic {topic_idx + 1}: {', '.join(top_words[:3])}",
                    'top_keywords': json.dumps(top_words, ensure_ascii=False),
                    'coherence_score': coherence,
                    'pages_count': 0  # Se calculará después al relacionar con páginas
                })

            return topics

        except Exception as e:
            logger.error(f"Error en extracción de tópicos: {e}")
            return []

    # ==================== SEARCH INTENT CLASSIFICATION ====================

    def classify_search_intent(self, keyword: str) -> Tuple[str, float]:
        """
        Clasifica la intención de búsqueda de una keyword.

        Args:
            keyword: Keyword a clasificar

        Returns:
            Tupla (intent_type, confidence) donde intent_type es
            'informational', 'transactional', 'navigational' o 'commercial'
        """
        keyword_lower = keyword.lower()

        # Contar coincidencias con patrones
        intent_scores = {
            'transactional': 0,
            'navigational': 0,
            'commercial': 0,
            'informational': 0
        }

        for intent_type, patterns in self.intent_patterns.items():
            for pattern in patterns:
                matches = len(re.findall(pattern, keyword_lower))
                intent_scores[intent_type] += matches

        # Si no hay coincidencias, es informational
        if all(score == 0 for score in intent_scores.values()):
            return ('informational', 0.6)

        # Obtener intención con mayor score
        max_intent = max(intent_scores, key=intent_scores.get)
        max_score = intent_scores[max_intent]
        total_score = sum(intent_scores.values())

        # Calcular confianza
        confidence = max_score / total_score if total_score > 0 else 0.5

        return (max_intent, min(confidence, 0.95))

    def classify_keywords_intent(
        self,
        keywords: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Clasifica la intención de búsqueda para múltiples keywords.

        Args:
            keywords: Lista de keywords

        Returns:
            Lista de keywords con intent_type y confidence añadidos
        """
        results = []

        for kw in keywords:
            keyword_text = kw.get('keyword', '')
            intent_type, confidence = self.classify_search_intent(keyword_text)

            results.append({
                'keyword_id': kw.get('keyword_id'),
                'keyword': keyword_text,
                'intent_type': intent_type,
                'confidence': confidence
            })

        return results

    # ==================== SIMILARITY ANALYSIS ====================

    def calculate_keyword_similarity(
        self,
        keyword1: str,
        keyword2: str,
        use_embeddings: bool = True
    ) -> float:
        """
        Calcula similitud semántica entre dos keywords.

        Args:
            keyword1: Primera keyword
            keyword2: Segunda keyword
            use_embeddings: Si True usa embeddings, si False usa TF-IDF

        Returns:
            Score de similitud (0-1)
        """
        if use_embeddings and self.embedding_model:
            try:
                embeddings = self.embedding_model.encode([keyword1, keyword2])
                similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
                return float(similarity)
            except Exception as e:
                logger.error(f"Error calculando similitud con embeddings: {e}")

        # Fallback a similitud de caracteres simple
        set1 = set(keyword1.lower().split())
        set2 = set(keyword2.lower().split())

        if not set1 or not set2:
            return 0.0

        intersection = len(set1 & set2)
        union = len(set1 | set2)

        return intersection / union if union > 0 else 0.0

    def find_similar_keywords(
        self,
        target_keyword: str,
        candidates: List[str],
        threshold: float = 0.6,
        top_n: int = 10
    ) -> List[Tuple[str, float]]:
        """
        Encuentra keywords similares a una keyword objetivo.

        Args:
            target_keyword: Keyword de referencia
            candidates: Lista de keywords candidatas
            threshold: Umbral mínimo de similitud
            top_n: Número máximo de resultados

        Returns:
            Lista de tuplas (keyword, similarity_score)
        """
        similarities = []

        for candidate in candidates:
            if candidate == target_keyword:
                continue

            similarity = self.calculate_keyword_similarity(target_keyword, candidate)

            if similarity >= threshold:
                similarities.append((candidate, similarity))

        # Ordenar por similitud y retornar top N
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_n]

    # ==================== LEMMATIZATION ====================

    def lemmatize_keyword(self, keyword: str) -> str:
        """
        Lematiza una keyword (reduce a forma base).

        Args:
            keyword: Keyword a lematizar

        Returns:
            Keyword lematizada
        """
        if not self.nlp:
            # Fallback simple: lowercase
            return keyword.lower()

        try:
            doc = self.nlp(keyword.lower())
            lemmas = [token.lemma_ for token in doc if not token.is_punct]
            return ' '.join(lemmas)
        except Exception as e:
            logger.error(f"Error en lematización: {e}")
            return keyword.lower()

    def lemmatize_keywords(
        self,
        keywords: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Lematiza múltiples keywords.

        Args:
            keywords: Lista de keywords

        Returns:
            Lista de keywords con campo 'lemma' añadido
        """
        results = []

        for kw in keywords:
            keyword_text = kw.get('keyword', '')
            lemma = self.lemmatize_keyword(keyword_text)

            kw_copy = kw.copy()
            kw_copy['lemma'] = lemma
            results.append(kw_copy)

        return results
