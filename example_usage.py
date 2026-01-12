#!/usr/bin/env python3
"""
Ejemplo de uso del SEO Crawler de forma programática.

Este script demuestra cómo usar el crawler desde código Python
para integrarlo en tus propias aplicaciones o scripts de automatización.
"""

import asyncio
from seo_crawler.config.settings import Config
from seo_crawler.crawler.core import SEOCrawler
from seo_crawler.storage.database import Database
from seo_crawler.analytics.keyword_metrics import KeywordMetrics
from seo_crawler.analytics.reporter import Reporter
from seo_crawler.utils.helpers import setup_logging


async def example_basic_crawl():
    """Ejemplo básico de crawl."""
    print("\n" + "="*60)
    print("EJEMPLO 1: Crawl Básico")
    print("="*60 + "\n")

    # Configuración personalizada
    custom_config = {
        'max_pages': 50,
        'max_depth': 2,
        'concurrent_requests': 5,
        'crawl_delay': 1.0,
        'log_level': 'INFO'
    }

    config = Config(custom_config)

    # Setup logging
    logger = setup_logging(
        log_level='INFO',
        log_file=config.get('log_file'),
        log_to_console=True
    )

    # Crear crawler
    crawler = SEOCrawler(config)

    try:
        # URL a crawlear (cambia esto por tu sitio)
        url = "https://example.com"

        # Inicializar
        await crawler.initialize([url])

        print(f"🚀 Crawleando: {url}\n")

        # Iniciar crawl
        stats = await crawler.start(max_pages=50)

        # Mostrar resultados
        print("\n" + "="*60)
        print("✅ CRAWL COMPLETADO")
        print("="*60)
        print(f"Session ID: {stats['session_id']}")
        print(f"Páginas crawleadas: {stats['pages_crawled']}")
        print(f"Keywords extraídas: {stats['total_keywords']}")
        print(f"Enlaces encontrados: {stats['total_links']}")
        print(f"Tiempo total: {stats['elapsed_time']:.2f}s")
        print("="*60 + "\n")

        return stats['session_id']

    finally:
        await crawler.cleanup()


async def example_analyze_session(session_id: int):
    """Ejemplo de análisis de una sesión."""
    print("\n" + "="*60)
    print("EJEMPLO 2: Análisis de Sesión")
    print("="*60 + "\n")

    config = Config()
    db = Database(config.get('database_path'))

    try:
        await db.connect()

        # Obtener información de la sesión
        session = await db.get_session(session_id)
        stats = await db.get_session_stats(session_id)

        print(f"📊 Sesión {session_id}: {session['domains']}\n")
        print(f"Total de páginas: {stats['total_pages']}")
        print(f"Keywords únicas: {stats['unique_keywords']}")
        print(f"Total enlaces: {stats['total_links']}\n")

        # Obtener top keywords
        metrics = KeywordMetrics(db)
        top_keywords = await metrics.get_top_keywords(session_id, limit=10)

        print("🔑 TOP 10 KEYWORDS (por TF-IDF):")
        print("-" * 60)

        for i, kw in enumerate(top_keywords, 1):
            print(f"{i:2d}. {kw['keyword']:30s} | "
                  f"TF-IDF: {kw['avg_tfidf']:.4f} | "
                  f"Freq: {kw['total_frequency']:4d}")

        print()

    finally:
        await db.close()


async def example_export_reports(session_id: int):
    """Ejemplo de exportación de reportes."""
    print("\n" + "="*60)
    print("EJEMPLO 3: Exportación de Reportes")
    print("="*60 + "\n")

    config = Config()
    db = Database(config.get('database_path'))

    try:
        await db.connect()

        reporter = Reporter(db)

        # Exportar a diferentes formatos
        print("📥 Exportando reportes...\n")

        # HTML
        html_file = f"reporte_session_{session_id}.html"
        await reporter.generate_html_report(session_id, html_file)
        print(f"✅ HTML generado: {html_file}")

        # Excel
        excel_file = f"datos_session_{session_id}.xlsx"
        await reporter.export_to_excel(session_id, excel_file)
        print(f"✅ Excel generado: {excel_file}")

        # CSV
        csv_file = f"keywords_session_{session_id}.csv"
        await reporter.export_keywords_to_csv(session_id, csv_file)
        print(f"✅ CSV generado: {csv_file}")

        print("\n📊 Todos los reportes generados exitosamente!\n")

    finally:
        await db.close()


async def example_compare_sessions():
    """Ejemplo de comparación entre sesiones."""
    print("\n" + "="*60)
    print("EJEMPLO 4: Comparación de Sesiones")
    print("="*60 + "\n")

    config = Config()
    db = Database(config.get('database_path'))

    try:
        await db.connect()

        # Obtener las dos últimas sesiones
        sessions = await db.get_all_sessions()

        if len(sessions) < 2:
            print("⚠️  Se necesitan al menos 2 sesiones para comparar")
            return

        session1_id = sessions[0]['session_id']
        session2_id = sessions[1]['session_id']

        print(f"Comparando sesiones {session1_id} y {session2_id}\n")

        metrics = KeywordMetrics(db)
        comparison = await metrics.get_session_comparison(session1_id, session2_id)

        print(f"Sesión {session1_id}: {comparison['session_1']['unique_keywords']} keywords únicas")
        print(f"Sesión {session2_id}: {comparison['session_2']['unique_keywords']} keywords únicas")
        print(f"\nKeywords comunes: {comparison['common_keywords']}")
        print(f"Similitud: {comparison['similarity_score']*100:.2f}%\n")

        # Keyword gaps
        print(f"🎯 KEYWORD GAPS para sesión {session1_id}:")
        print("-" * 60)

        for i, kw in enumerate(comparison['gaps_for_session_1'][:10], 1):
            print(f"{i:2d}. {kw}")

        print()

    finally:
        await db.close()


async def example_custom_analysis():
    """Ejemplo de análisis personalizado."""
    print("\n" + "="*60)
    print("EJEMPLO 5: Análisis Personalizado")
    print("="*60 + "\n")

    config = Config()
    db = Database(config.get('database_path'))

    try:
        await db.connect()

        # Obtener última sesión
        sessions = await db.get_all_sessions()

        if not sessions:
            print("⚠️  No hay sesiones disponibles")
            return

        session_id = sessions[0]['session_id']

        # Análisis de distribución de keywords
        metrics = KeywordMetrics(db)

        print("📊 Análisis de distribución de keywords:\n")

        distribution = await metrics.get_keyword_distribution(session_id)
        print(f"Promedio de keywords por página: {distribution['avg_keywords_per_page']:.2f}")
        print(f"Mínimo: {distribution['min_keywords']}")
        print(f"Máximo: {distribution['max_keywords']}\n")

        # Análisis de posicionamiento
        print("📈 Análisis de posicionamiento de keywords:\n")

        position_analysis = await metrics.get_keyword_position_analysis(session_id)
        print(f"Keywords en título: {position_analysis['in_title_pct']:.2f}%")
        print(f"Keywords en H1: {position_analysis['in_h1_pct']:.2f}%")
        print(f"Keywords en primeras 100 palabras: {position_analysis['in_first_100_pct']:.2f}%\n")

        # Detección de keyword stuffing
        print("⚠️  Análisis de densidad de keywords:\n")

        density_analysis = await metrics.get_keyword_density_analysis(session_id)

        if density_analysis['stuffing']:
            print(f"🚨 Posible keyword stuffing detectado:")
            for kw in density_analysis['stuffing'][:5]:
                print(f"   - {kw}")
        else:
            print("✅ No se detectó keyword stuffing")

        print()

    finally:
        await db.close()


async def main():
    """Función principal que ejecuta todos los ejemplos."""
    print("\n" + "="*70)
    print("🚀 SEO CRAWLER - EJEMPLOS DE USO PROGRAMÁTICO")
    print("="*70)

    # Ejemplo 1: Crawl básico
    # session_id = await example_basic_crawl()

    # Para los siguientes ejemplos, usa un session_id existente
    # o el que se generó en el ejemplo 1

    # Obtener session_id de la última sesión
    config = Config()
    db = Database(config.get('database_path'))
    await db.connect()
    sessions = await db.get_all_sessions()
    await db.close()

    if not sessions:
        print("\n⚠️  No hay sesiones disponibles.")
        print("Primero ejecuta el Ejemplo 1 para crear una sesión.")
        return

    session_id = sessions[0]['session_id']

    # Ejemplo 2: Análisis de sesión
    await example_analyze_session(session_id)

    # Ejemplo 3: Exportación
    await example_export_reports(session_id)

    # Ejemplo 4: Comparación (si hay múltiples sesiones)
    if len(sessions) >= 2:
        await example_compare_sessions()

    # Ejemplo 5: Análisis personalizado
    await example_custom_analysis()

    print("="*70)
    print("✅ TODOS LOS EJEMPLOS COMPLETADOS")
    print("="*70 + "\n")


if __name__ == '__main__':
    # Ejecutar ejemplos
    asyncio.run(main())
