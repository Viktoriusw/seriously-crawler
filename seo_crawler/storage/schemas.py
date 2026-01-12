"""
Esquemas de base de datos para el SEO Crawler.

Este módulo define las estructuras de todas las tablas SQLite
utilizadas para almacenar los datos del crawling y análisis.
"""

# SQL para crear las tablas

CREATE_CRAWL_SESSIONS_TABLE = """
CREATE TABLE IF NOT EXISTS crawl_sessions (
    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    seed_url TEXT NOT NULL,
    domains TEXT NOT NULL,
    pages_crawled INTEGER DEFAULT 0,
    pages_failed INTEGER DEFAULT 0,
    total_keywords INTEGER DEFAULT 0,
    status TEXT DEFAULT 'running',
    config_snapshot TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_PAGES_TABLE = """
CREATE TABLE IF NOT EXISTS pages (
    page_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    url TEXT NOT NULL UNIQUE,
    domain TEXT NOT NULL,
    status_code INTEGER,
    title TEXT,
    h1 TEXT,
    meta_description TEXT,
    word_count INTEGER DEFAULT 0,
    crawl_date TIMESTAMP NOT NULL,
    content_hash TEXT,
    response_time REAL,
    depth INTEGER DEFAULT 0,
    parent_url TEXT,
    content_type TEXT,
    canonical_url TEXT,
    language TEXT,
    error_message TEXT,
    FOREIGN KEY (session_id) REFERENCES crawl_sessions(session_id) ON DELETE CASCADE
);
"""

CREATE_KEYWORDS_TABLE = """
CREATE TABLE IF NOT EXISTS keywords (
    keyword_id INTEGER PRIMARY KEY AUTOINCREMENT,
    page_id INTEGER NOT NULL,
    keyword TEXT NOT NULL,
    frequency INTEGER DEFAULT 1,
    density REAL DEFAULT 0.0,
    tf_idf_score REAL DEFAULT 0.0,
    position_in_title BOOLEAN DEFAULT 0,
    position_in_h1 BOOLEAN DEFAULT 0,
    position_in_first_100 BOOLEAN DEFAULT 0,
    is_ngram BOOLEAN DEFAULT 0,
    ngram_size INTEGER DEFAULT 1,
    FOREIGN KEY (page_id) REFERENCES pages(page_id) ON DELETE CASCADE
);
"""

CREATE_LINKS_TABLE = """
CREATE TABLE IF NOT EXISTS links (
    link_id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_page_id INTEGER NOT NULL,
    target_url TEXT NOT NULL,
    anchor_text TEXT,
    is_internal BOOLEAN DEFAULT 1,
    nofollow BOOLEAN DEFAULT 0,
    link_type TEXT,
    FOREIGN KEY (source_page_id) REFERENCES pages(page_id) ON DELETE CASCADE
);
"""

CREATE_IMAGES_TABLE = """
CREATE TABLE IF NOT EXISTS images (
    image_id INTEGER PRIMARY KEY AUTOINCREMENT,
    page_id INTEGER NOT NULL,
    url TEXT NOT NULL,
    alt_text TEXT,
    title_text TEXT,
    size_bytes INTEGER,
    width INTEGER,
    height INTEGER,
    FOREIGN KEY (page_id) REFERENCES pages(page_id) ON DELETE CASCADE
);
"""

CREATE_METADATA_TABLE = """
CREATE TABLE IF NOT EXISTS metadata (
    metadata_id INTEGER PRIMARY KEY AUTOINCREMENT,
    page_id INTEGER NOT NULL,
    meta_key TEXT NOT NULL,
    meta_value TEXT,
    meta_type TEXT,
    FOREIGN KEY (page_id) REFERENCES pages(page_id) ON DELETE CASCADE
);
"""

CREATE_STRUCTURED_DATA_TABLE = """
CREATE TABLE IF NOT EXISTS structured_data (
    sd_id INTEGER PRIMARY KEY AUTOINCREMENT,
    page_id INTEGER NOT NULL,
    data_type TEXT NOT NULL,
    json_data TEXT NOT NULL,
    FOREIGN KEY (page_id) REFERENCES pages(page_id) ON DELETE CASCADE
);
"""

CREATE_HEADINGS_TABLE = """
CREATE TABLE IF NOT EXISTS headings (
    heading_id INTEGER PRIMARY KEY AUTOINCREMENT,
    page_id INTEGER NOT NULL,
    level INTEGER NOT NULL,
    text TEXT NOT NULL,
    position INTEGER NOT NULL,
    FOREIGN KEY (page_id) REFERENCES pages(page_id) ON DELETE CASCADE
);
"""

# Índices para mejorar el rendimiento de consultas

CREATE_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_pages_url ON pages(url);",
    "CREATE INDEX IF NOT EXISTS idx_pages_domain ON pages(domain);",
    "CREATE INDEX IF NOT EXISTS idx_pages_session ON pages(session_id);",
    "CREATE INDEX IF NOT EXISTS idx_pages_hash ON pages(content_hash);",
    "CREATE INDEX IF NOT EXISTS idx_keywords_page ON keywords(page_id);",
    "CREATE INDEX IF NOT EXISTS idx_keywords_keyword ON keywords(keyword);",
    "CREATE INDEX IF NOT EXISTS idx_keywords_tfidf ON keywords(tf_idf_score DESC);",
    "CREATE INDEX IF NOT EXISTS idx_keywords_session_composite ON keywords(page_id, keyword);",
    "CREATE INDEX IF NOT EXISTS idx_links_source ON links(source_page_id);",
    "CREATE INDEX IF NOT EXISTS idx_links_target ON links(target_url);",
    "CREATE INDEX IF NOT EXISTS idx_images_page ON images(page_id);",
    "CREATE INDEX IF NOT EXISTS idx_metadata_page ON metadata(page_id);",
    "CREATE INDEX IF NOT EXISTS idx_structured_data_page ON structured_data(page_id);",
    "CREATE INDEX IF NOT EXISTS idx_headings_page ON headings(page_id);",
]

# ==================== TABLAS PROFESIONALES (FASE ENTERPRISE) ====================

CREATE_KEYWORD_CLUSTERS_TABLE = """
CREATE TABLE IF NOT EXISTS keyword_clusters (
    cluster_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    cluster_name TEXT NOT NULL,
    main_keyword TEXT NOT NULL,
    num_keywords INTEGER DEFAULT 0,
    avg_tfidf REAL DEFAULT 0.0,
    topic_distribution TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES crawl_sessions(session_id) ON DELETE CASCADE
);
"""

CREATE_KEYWORD_CLUSTER_MEMBERS_TABLE = """
CREATE TABLE IF NOT EXISTS keyword_cluster_members (
    cluster_id INTEGER NOT NULL,
    keyword_id INTEGER NOT NULL,
    similarity_score REAL DEFAULT 0.0,
    PRIMARY KEY (cluster_id, keyword_id),
    FOREIGN KEY (cluster_id) REFERENCES keyword_clusters(cluster_id) ON DELETE CASCADE,
    FOREIGN KEY (keyword_id) REFERENCES keywords(keyword_id) ON DELETE CASCADE
);
"""

CREATE_TOPICS_TABLE = """
CREATE TABLE IF NOT EXISTS topics (
    topic_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    topic_name TEXT,
    top_keywords TEXT,
    pages_count INTEGER DEFAULT 0,
    coherence_score REAL DEFAULT 0.0,
    FOREIGN KEY (session_id) REFERENCES crawl_sessions(session_id) ON DELETE CASCADE
);
"""

CREATE_SEARCH_INTENT_TABLE = """
CREATE TABLE IF NOT EXISTS search_intent (
    keyword_id INTEGER PRIMARY KEY,
    intent_type TEXT CHECK(intent_type IN ('informational', 'transactional', 'navigational', 'commercial')),
    confidence REAL DEFAULT 0.0,
    FOREIGN KEY (keyword_id) REFERENCES keywords(keyword_id) ON DELETE CASCADE
);
"""

CREATE_KEYWORD_METRICS_TABLE = """
CREATE TABLE IF NOT EXISTS keyword_metrics (
    keyword_id INTEGER PRIMARY KEY,
    difficulty_score REAL DEFAULT 0.0,
    opportunity_score REAL DEFAULT 0.0,
    competition_level TEXT CHECK(competition_level IN ('low', 'medium', 'high')),
    cannibalization_score REAL DEFAULT 0.0,
    cannibalized_pages TEXT,
    density_title REAL DEFAULT 0.0,
    density_first_100_words REAL DEFAULT 0.0,
    density_headings REAL DEFAULT 0.0,
    is_stuffed BOOLEAN DEFAULT 0,
    pages_in_title INTEGER DEFAULT 0,
    pages_in_h1 INTEGER DEFAULT 0,
    avg_word_count_pages REAL DEFAULT 0.0,
    FOREIGN KEY (keyword_id) REFERENCES keywords(keyword_id) ON DELETE CASCADE
);
"""

CREATE_CONTENT_QUALITY_TABLE = """
CREATE TABLE IF NOT EXISTS content_quality (
    page_id INTEGER PRIMARY KEY,
    quality_score REAL DEFAULT 0.0,
    readability_score REAL DEFAULT 0.0,
    readability_level TEXT,
    lexical_diversity REAL DEFAULT 0.0,
    avg_sentence_length REAL DEFAULT 0.0,
    avg_word_length REAL DEFAULT 0.0,
    is_thin_content BOOLEAN DEFAULT 0,
    duplicate_of_page_id INTEGER,
    similarity_score REAL DEFAULT 0.0,
    heading_structure_score REAL DEFAULT 0.0,
    multimedia_score REAL DEFAULT 0.0,
    FOREIGN KEY (page_id) REFERENCES pages(page_id) ON DELETE CASCADE
);
"""

# Índices adicionales para tablas profesionales
CREATE_PROFESSIONAL_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_keyword_clusters_session ON keyword_clusters(session_id);",
    "CREATE INDEX IF NOT EXISTS idx_keyword_cluster_members_keyword ON keyword_cluster_members(keyword_id);",
    "CREATE INDEX IF NOT EXISTS idx_topics_session ON topics(session_id);",
    "CREATE INDEX IF NOT EXISTS idx_search_intent_type ON search_intent(intent_type);",
    "CREATE INDEX IF NOT EXISTS idx_keyword_metrics_difficulty ON keyword_metrics(difficulty_score DESC);",
    "CREATE INDEX IF NOT EXISTS idx_keyword_metrics_opportunity ON keyword_metrics(opportunity_score DESC);",
    "CREATE INDEX IF NOT EXISTS idx_content_quality_score ON content_quality(quality_score DESC);",
    "CREATE INDEX IF NOT EXISTS idx_content_quality_thin ON content_quality(is_thin_content);",
]

# Combinar todos los índices
ALL_INDEXES = CREATE_INDEXES + CREATE_PROFESSIONAL_INDEXES

# Lista de todas las tablas en orden de creación
ALL_TABLES = [
    CREATE_CRAWL_SESSIONS_TABLE,
    CREATE_PAGES_TABLE,
    CREATE_KEYWORDS_TABLE,
    CREATE_LINKS_TABLE,
    CREATE_IMAGES_TABLE,
    CREATE_METADATA_TABLE,
    CREATE_STRUCTURED_DATA_TABLE,
    CREATE_HEADINGS_TABLE,
    # Tablas profesionales
    CREATE_KEYWORD_CLUSTERS_TABLE,
    CREATE_KEYWORD_CLUSTER_MEMBERS_TABLE,
    CREATE_TOPICS_TABLE,
    CREATE_SEARCH_INTENT_TABLE,
    CREATE_KEYWORD_METRICS_TABLE,
    CREATE_CONTENT_QUALITY_TABLE,
]
