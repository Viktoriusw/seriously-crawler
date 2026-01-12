#!/usr/bin/env python3
"""
SEO Crawler - Professional SEO Analysis Tool
Punto de entrada principal de la aplicación.

Uso:
    python main.py crawl --url https://ejemplo.com --max-pages 200
    python main.py analyze --session 1 --export results.csv
    python main.py report --session 1 --format html
    python main.py gui  # Lanza la interfaz gráfica
"""

import asyncio
import argparse
import sys
from pathlib import Path

# Añadir el directorio padre al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from seo_crawler.config.settings import Config
from seo_crawler.crawler.core import SEOCrawler
from seo_crawler.storage.database import Database
from seo_crawler.analytics.keyword_metrics import KeywordMetrics
from seo_crawler.analytics.reporter import Reporter
from seo_crawler.utils.helpers import setup_logging

# Módulos profesionales
from seo_crawler.extractors.semantic_analyzer import SemanticAnalyzer
from seo_crawler.analytics.keyword_difficulty import KeywordDifficultyAnalyzer
from seo_crawler.analytics.competitive_analysis import CompetitiveAnalyzer
from seo_crawler.analytics.content_analyzer import ContentQualityAnalyzer
from seo_crawler.analytics.visualizations import SEOVisualizer
from seo_crawler.analytics.interactive_visualizations import InteractiveVisualizer
from seo_crawler.analytics.network_analyzer import NetworkAnalyzer
# Módulos PASO 4: Auditoría Técnica
from seo_crawler.analytics.technical_seo_auditor import TechnicalSEOAuditor
from seo_crawler.analytics.schema_analyzer import SchemaAnalyzer
from seo_crawler.analytics.recommendations_engine import RecommendationsEngine


async def cmd_crawl(args):
    """Ejecuta el crawling de un sitio web."""
    print(f"\n🚀 Iniciando crawler para: {args.url}")
    print(f"Profundidad máxima: {args.max_depth}")
    print(f"Máximo de páginas: {args.max_pages}")
    print(f"Requests concurrentes: {args.concurrent}\n")

    # Configuración personalizada
    custom_config = {
        'max_pages': args.max_pages,
        'max_depth': args.max_depth,
        'concurrent_requests': args.concurrent,
        'crawl_delay': args.delay,
        'respect_robots': not args.ignore_robots,
        'follow_external_links': args.follow_external,
        'log_level': args.log_level
    }

    config = Config(custom_config)

    # Setup logging
    logger = setup_logging(
        log_level=args.log_level,
        log_file=config.get('log_file'),
        log_to_console=True
    )

    # Crear crawler
    crawler = SEOCrawler(config)

    try:
        # Inicializar
        await crawler.initialize([args.url])

        # Iniciar crawling
        stats = await crawler.start(max_pages=args.max_pages)

        # Mostrar resultados
        print("\n" + "="*60)
        print("✅ CRAWLING COMPLETADO")
        print("="*60)
        print(f"Session ID: {stats['session_id']}")
        print(f"Páginas crawleadas: {stats['pages_crawled']}")
        print(f"Páginas fallidas: {stats['pages_failed']}")
        print(f"Keywords extraídas: {stats['total_keywords']}")
        print(f"Enlaces encontrados: {stats['total_links']}")
        print(f"Imágenes encontradas: {stats['total_images']}")
        print(f"Tiempo total: {stats['elapsed_time']:.2f}s")
        print(f"Velocidad: {stats['pages_per_second']:.2f} páginas/s")
        print("="*60)

        # Auto-exportar si se especificó
        if args.auto_export:
            print("\n📊 Generando reporte automático...")
            reporter = Reporter(crawler.db)
            export_path = f"session_{stats['session_id']}_report.html"
            await reporter.generate_html_report(stats['session_id'], export_path)
            print(f"✅ Reporte generado: {export_path}")

    except KeyboardInterrupt:
        print("\n⚠️  Crawling interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error durante el crawling: {str(e)}")
        logger.error(f"Error en crawl: {str(e)}", exc_info=True)
    finally:
        await crawler.cleanup()


async def cmd_analyze(args):
    """Analiza los resultados de una sesión."""
    print(f"\n📊 Analizando sesión {args.session}...")

    db = Database(Config().get('database_path'))
    await db.connect()

    try:
        # Verificar que la sesión existe
        session = await db.get_session(args.session)
        if not session:
            print(f"❌ No se encontró la sesión {args.session}")
            return

        # Obtener estadísticas
        stats = await db.get_session_stats(args.session)
        metrics = KeywordMetrics(db)

        print("\n" + "="*60)
        print("ESTADÍSTICAS DE LA SESIÓN")
        print("="*60)
        print(f"Dominio: {session['domains']}")
        print(f"Total de páginas: {stats['total_pages']}")
        print(f"Páginas exitosas: {stats['success_pages']}")
        print(f"Páginas fallidas: {stats['failed_pages']}")
        print(f"Total keywords: {stats['total_keywords']}")
        print(f"Keywords únicas: {stats['unique_keywords']}")
        print(f"Total enlaces: {stats['total_links']}")
        print(f"Enlaces internos: {stats['internal_links']}")
        print(f"Enlaces externos: {stats['external_links']}")
        print("="*60)

        # Top keywords
        print("\n🔑 TOP 20 KEYWORDS:")
        top_keywords = await metrics.get_top_keywords(args.session, limit=20)

        for i, kw in enumerate(top_keywords, 1):
            print(f"{i:2d}. {kw['keyword']:30s} | TF-IDF: {kw['avg_tfidf']:.4f} | Freq: {kw['total_frequency']:4d}")

        # Distribución de keywords
        print("\n📈 DISTRIBUCIÓN DE KEYWORDS:")
        distribution = await metrics.get_keyword_distribution(args.session)
        print(f"Promedio por página: {distribution['avg_keywords_per_page']:.2f}")
        print(f"Mínimo: {distribution['min_keywords']}")
        print(f"Máximo: {distribution['max_keywords']}")

        # Exportar si se especificó
        if args.export:
            print(f"\n💾 Exportando a {args.export}...")
            reporter = Reporter(db)

            if args.export.endswith('.csv'):
                await reporter.export_keywords_to_csv(args.session, args.export)
            elif args.export.endswith('.xlsx'):
                await reporter.export_to_excel(args.session, args.export)
            elif args.export.endswith('.json'):
                await reporter.export_to_json(args.session, args.export)

            print(f"✅ Exportado correctamente")

    finally:
        await db.close()


async def cmd_report(args):
    """Genera un reporte de una sesión."""
    print(f"\n📄 Generando reporte para sesión {args.session}...")

    db = Database(Config().get('database_path'))
    await db.connect()

    try:
        reporter = Reporter(db)

        if args.format == 'html':
            output = args.output or f"session_{args.session}_report.html"
            await reporter.generate_html_report(args.session, output)
        elif args.format == 'excel':
            output = args.output or f"session_{args.session}_report.xlsx"
            await reporter.export_to_excel(args.session, output)
        elif args.format == 'csv':
            output = args.output or f"session_{args.session}_keywords.csv"
            await reporter.export_keywords_to_csv(args.session, output)
        elif args.format == 'json':
            output = args.output or f"session_{args.session}_data.json"
            await reporter.export_to_json(args.session, output)

        print(f"✅ Reporte generado: {output}")

    finally:
        await db.close()


async def cmd_list_sessions(args):
    """Lista todas las sesiones de crawling."""
    db = Database(Config().get('database_path'))
    await db.connect()

    try:
        sessions = await db.get_all_sessions()

        if not sessions:
            print("No hay sesiones de crawling guardadas.")
            return

        print("\n" + "="*80)
        print("SESIONES DE CRAWLING")
        print("="*80)
        print(f"{'ID':>4} | {'Dominios':30s} | {'Páginas':>8} | {'Keywords':>8} | {'Fecha':20s}")
        print("-"*80)

        for session in sessions:
            print(f"{session['session_id']:>4} | "
                  f"{session['domains'][:30]:30s} | "
                  f"{session.get('pages_crawled', 0):>8} | "
                  f"{session.get('total_keywords', 0):>8} | "
                  f"{session['start_time'][:19]:20s}")

        print("="*80)

    finally:
        await db.close()


async def cmd_compare(args):
    """Compara keywords entre sesiones."""
    print(f"\n🔍 Comparando sesiones: {', '.join(map(str, args.sessions))}...")

    db = Database(Config().get('database_path'))
    await db.connect()

    try:
        metrics = KeywordMetrics(db)

        if len(args.sessions) == 2:
            # Comparación detallada entre dos sesiones
            comparison = await metrics.get_session_comparison(args.sessions[0], args.sessions[1])

            print("\n" + "="*60)
            print("COMPARACIÓN DE SESIONES")
            print("="*60)
            print(f"\nSesión {args.sessions[0]}:")
            print(f"  - Total keywords: {comparison['session_1']['total_keywords']}")
            print(f"  - Keywords únicas: {comparison['session_1']['unique_keywords']}")
            print(f"  - Páginas: {comparison['session_1']['pages']}")

            print(f"\nSesión {args.sessions[1]}:")
            print(f"  - Total keywords: {comparison['session_2']['total_keywords']}")
            print(f"  - Keywords únicas: {comparison['session_2']['unique_keywords']}")
            print(f"  - Páginas: {comparison['session_2']['pages']}")

            print(f"\nAnálisis:")
            print(f"  - Keywords comunes: {comparison['common_keywords']}")
            print(f"  - Solo en sesión {args.sessions[0]}: {comparison['unique_to_session_1']}")
            print(f"  - Solo en sesión {args.sessions[1]}: {comparison['unique_to_session_2']}")
            print(f"  - Similitud: {comparison['similarity_score']*100:.2f}%")

            # Mostrar keyword gaps
            print(f"\n🎯 KEYWORD GAPS para sesión {args.sessions[0]}:")
            for i, kw in enumerate(comparison['gaps_for_session_1'][:10], 1):
                print(f"{i:2d}. {kw}")

        else:
            # Comparación múltiple
            common = await metrics.find_common_keywords(args.sessions, min_sessions=2, limit=20)

            print(f"\n🔑 KEYWORDS COMUNES (presentes en al menos 2 sesiones):")
            for i, kw in enumerate(common, 1):
                print(f"{i:2d}. {kw['keyword']:30s} | "
                      f"Sesiones: {kw['session_count']}/{len(args.sessions)} | "
                      f"TF-IDF: {kw['avg_tfidf']:.4f}")

        # Exportar comparación si se especificó
        if args.export:
            reporter = Reporter(db)
            await reporter.generate_comparison_report(args.sessions, args.export)
            print(f"\n✅ Comparación exportada: {args.export}")

    finally:
        await db.close()


def cmd_gui(args):
    """Lanza la interfaz gráfica."""
    print("\n🖥️  Lanzando interfaz gráfica...")

    try:
        from seo_crawler.gui.main_window import SEOCrawlerGUI
        import tkinter as tk

        root = tk.Tk()
        app = SEOCrawlerGUI(root)
        root.mainloop()

    except ImportError as e:
        print(f"❌ Error al cargar la interfaz gráfica: {str(e)}")
        print("Asegúrate de tener tkinter instalado.")


# ==================== COMANDOS PROFESIONALES ====================


async def cmd_analyze_semantic(args):
    """Análisis semántico y clustering de keywords."""
    print(f"\n🧠 Análisis semántico para sesión {args.session}...")

    db = Database(Config().get('database_path'))
    await db.connect()

    try:
        # Obtener keywords de la sesión
        pages = await db.get_pages_by_session(args.session)
        if not pages:
            print(f"❌ No se encontraron páginas en la sesión {args.session}")
            return

        # Obtener todas las keywords
        all_keywords = []
        for page in pages:
            keywords = await db.get_keywords_by_page(page['page_id'])
            all_keywords.extend(keywords)

        if not all_keywords:
            print("❌ No se encontraron keywords en la sesión")
            return

        print(f"Total keywords a analizar: {len(all_keywords)}")

        # Inicializar analizador semántico
        analyzer = SemanticAnalyzer(language=args.language)

        # Clustering de keywords
        print("\n🔍 Realizando clustering de keywords...")
        clusters = analyzer.cluster_keywords(
            all_keywords,
            method=args.method,
            n_clusters=args.n_clusters,
            use_embeddings=args.use_embeddings
        )

        print(f"✅ {len(clusters)} clusters identificados")

        # Guardar clusters en base de datos
        print("\n💾 Guardando clusters en base de datos...")
        for cluster in clusters:
            cluster_id = await db.create_keyword_cluster(
                session_id=args.session,
                cluster_name=cluster['cluster_name'],
                main_keyword=cluster['main_keyword'],
                num_keywords=cluster['num_keywords'],
                avg_tfidf=cluster['avg_tfidf']
            )

            # Añadir keywords al cluster
            for kw in cluster['keywords']:
                if 'keyword_id' in kw:
                    await db.add_keyword_to_cluster(
                        cluster_id=cluster_id,
                        keyword_id=kw['keyword_id'],
                        similarity_score=0.8  # Placeholder
                    )

        # Mostrar resultados
        print("\n" + "="*60)
        print("CLUSTERS IDENTIFICADOS")
        print("="*60)
        for i, cluster in enumerate(clusters[:10], 1):
            print(f"\n{i}. {cluster['cluster_name']}")
            print(f"   Keyword principal: {cluster['main_keyword']}")
            print(f"   Número de keywords: {cluster['num_keywords']}")
            print(f"   TF-IDF promedio: {cluster['avg_tfidf']:.4f}")

        # Clasificar intención de búsqueda
        if args.classify_intent:
            print("\n🎯 Clasificando intención de búsqueda...")
            intent_results = analyzer.classify_keywords_intent(all_keywords)

            # Guardar en base de datos
            for result in intent_results:
                if 'keyword_id' in result:
                    await db.set_search_intent(
                        keyword_id=result['keyword_id'],
                        intent_type=result['intent_type'],
                        confidence=result['confidence']
                    )

            # Mostrar distribución de intenciones
            intent_counts = {}
            for result in intent_results:
                intent = result['intent_type']
                intent_counts[intent] = intent_counts.get(intent, 0) + 1

            print("\n📊 Distribución de intenciones:")
            for intent, count in sorted(intent_counts.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / len(intent_results)) * 100
                print(f"  {intent:15s}: {count:4d} ({percentage:5.2f}%)")

        print("\n✅ Análisis semántico completado")

    finally:
        await db.close()


async def cmd_calculate_difficulty(args):
    """Calcula difficulty y opportunity scores para keywords."""
    print(f"\n📊 Calculando métricas de difficulty para sesión {args.session}...")

    db = Database(Config().get('database_path'))
    await db.connect()

    try:
        # Obtener datos
        pages = await db.get_pages_by_session(args.session)
        if not pages:
            print(f"❌ No se encontraron páginas en la sesión {args.session}")
            return

        all_keywords = []
        for page in pages:
            keywords = await db.get_keywords_by_page(page['page_id'])
            all_keywords.extend(keywords)

        if not all_keywords:
            print("❌ No se encontraron keywords")
            return

        print(f"Analizando {len(all_keywords)} keywords...")

        # Inicializar analizador
        analyzer = KeywordDifficultyAnalyzer()

        # Analizar todas las keywords
        print("\n🔍 Calculando difficulty, opportunity y canibalización...")
        results = analyzer.analyze_all_keywords(all_keywords, pages)

        # Guardar en base de datos
        print("\n💾 Guardando métricas en base de datos...")
        for result in results:
            await db.set_keyword_metrics(
                keyword_id=result['keyword_id'],
                difficulty_score=result['difficulty_score'],
                opportunity_score=result['opportunity_score'],
                competition_level=result['competition_level'],
                cannibalization_score=result['cannibalization_score'],
                cannibalized_pages=result['cannibalized_pages'],
                density_title=result['density_title'],
                density_first_100_words=result['density_first_100_words'],
                density_headings=result['density_headings'],
                is_stuffed=result['is_stuffed'],
                pages_in_title=result['pages_in_title'],
                pages_in_h1=result['pages_in_h1'],
                avg_word_count_pages=result['avg_word_count_pages']
            )

        # Mostrar resumen
        print("\n" + "="*80)
        print("TOP KEYWORDS POR OPORTUNIDAD")
        print("="*80)

        # Obtener top opportunities
        high_opportunities = await db.get_high_opportunity_keywords(args.session, min_opportunity=60.0, limit=20)

        for i, kw in enumerate(high_opportunities, 1):
            print(f"{i:2d}. {kw.get('keyword', '')[:40]:40s} | "
                  f"Opportunity: {kw.get('opportunity_score', 0):5.1f} | "
                  f"Difficulty: {kw.get('difficulty_score', 0):5.1f} | "
                  f"Level: {kw.get('competition_level', 'N/A')}")

        # Keywords cannibalizadas
        cannibalized = await db.get_cannibalized_keywords(args.session)
        if cannibalized:
            print("\n⚠️  KEYWORDS CON CANIBALIZACIÓN DETECTADA:")
            for i, kw in enumerate(cannibalized[:10], 1):
                print(f"{i:2d}. {kw.get('keyword', '')[:40]:40s} | "
                      f"Score: {kw.get('cannibalization_score', 0):.2f}")

        print("\n✅ Análisis de difficulty completado")

    finally:
        await db.close()


async def cmd_find_gaps(args):
    """Encuentra keyword gaps entre dos sesiones."""
    print(f"\n🔍 Buscando keyword gaps entre sesiones {args.own_session} y {args.competitor_session}...")

    db = Database(Config().get('database_path'))
    await db.connect()

    try:
        # Obtener keywords de ambas sesiones
        own_pages = await db.get_pages_by_session(args.own_session)
        comp_pages = await db.get_pages_by_session(args.competitor_session)

        own_keywords = []
        for page in own_pages:
            keywords = await db.get_keywords_by_page(page['page_id'])
            own_keywords.extend(keywords)

        comp_keywords = []
        for page in comp_pages:
            keywords = await db.get_keywords_by_page(page['page_id'])
            comp_keywords.extend(keywords)

        if not own_keywords or not comp_keywords:
            print("❌ Una o ambas sesiones no tienen keywords")
            return

        print(f"Tus keywords: {len(own_keywords)}")
        print(f"Keywords del competidor: {len(comp_keywords)}")

        # Inicializar analizador competitivo
        analyzer = CompetitiveAnalyzer()

        # Encontrar gaps
        print("\n🎯 Analizando keyword gaps...")
        gaps = analyzer.find_keyword_gaps(
            own_keywords=own_keywords,
            competitor_keywords=comp_keywords,
            min_tfidf=args.min_tfidf
        )

        # Analizar overlap
        overlap = analyzer.analyze_keyword_overlap(own_keywords, comp_keywords)

        # Mostrar resultados
        print("\n" + "="*80)
        print("KEYWORD GAP ANALYSIS")
        print("="*80)
        print(f"\nKeywords únicas tuyas: {overlap['own_unique_count']}")
        print(f"Keywords únicas del competidor: {overlap['competitor_unique_count']}")
        print(f"Keywords compartidas: {overlap['shared_keywords_count']}")
        print(f"Overlap: {overlap['overlap_percentage']:.2f}%")

        print(f"\n🎯 TOP {min(20, len(gaps))} KEYWORD GAPS (oportunidades):")
        print("-"*80)
        for i, gap in enumerate(gaps[:20], 1):
            print(f"{i:2d}. {gap['keyword'][:50]:50s} | "
                  f"Priority: {gap['priority']:5.1f} | "
                  f"TF-IDF: {gap['competitor_tfidf']:.4f}")

        # Exportar si se especificó
        if args.export:
            import json
            output = {
                'gap_analysis': {
                    'gaps': gaps,
                    'overlap': overlap
                }
            }
            with open(args.export, 'w', encoding='utf-8') as f:
                json.dump(output, f, ensure_ascii=False, indent=2)
            print(f"\n✅ Resultados exportados a: {args.export}")

        print("\n✅ Análisis de gaps completado")

    finally:
        await db.close()


async def cmd_competitive_analysis(args):
    """Análisis competitivo completo."""
    print(f"\n🏆 Análisis competitivo entre sesiones {args.own_session} y {args.competitor_session}...")

    db = Database(Config().get('database_path'))
    await db.connect()

    try:
        # Obtener datos
        own_pages = await db.get_pages_by_session(args.own_session)
        comp_pages = await db.get_pages_by_session(args.competitor_session)

        own_keywords = []
        for page in own_pages:
            keywords = await db.get_keywords_by_page(page['page_id'])
            own_keywords.extend(keywords)

        comp_keywords = []
        for page in comp_pages:
            keywords = await db.get_keywords_by_page(page['page_id'])
            comp_keywords.extend(keywords)

        if not own_keywords or not comp_keywords:
            print("❌ Una o ambas sesiones no tienen keywords")
            return

        # Inicializar analizador
        analyzer = CompetitiveAnalyzer()

        # Análisis de posicionamiento
        print("\n📊 Analizando posicionamiento competitivo...")
        positioning = analyzer.analyze_competitive_position(
            own_keywords=own_keywords,
            competitor_keywords=comp_keywords,
            own_pages=own_pages,
            competitor_pages=comp_pages
        )

        # Mostrar resultados
        print("\n" + "="*80)
        print("ANÁLISIS DE POSICIONAMIENTO COMPETITIVO")
        print("="*80)
        print(f"\nScore competitivo: {positioning['competitive_score']:.2f}/100")
        print(f"Posición: {positioning['overall_position']}")

        print("\n💪 FORTALEZAS:")
        for strength in positioning['strengths']:
            print(f"  ✓ {strength}")

        print("\n⚠️  DEBILIDADES:")
        for weakness in positioning['weaknesses']:
            print(f"  ✗ {weakness}")

        print("\n📈 TUS MÉTRICAS:")
        your_metrics = positioning['your_metrics']
        print(f"  Total keywords: {your_metrics['total_keywords']}")
        print(f"  Keywords únicas: {your_metrics['unique_keywords']}")
        print(f"  TF-IDF promedio: {your_metrics['avg_tfidf']:.4f}")
        print(f"  Optimización: {your_metrics['keyword_optimization']:.2f}%")
        print(f"  Profundidad contenido: {your_metrics['content_depth']:.0f} palabras")

        print("\n📉 MÉTRICAS DEL COMPETIDOR:")
        comp_metrics = positioning['competitor_metrics']
        print(f"  Total keywords: {comp_metrics['total_keywords']}")
        print(f"  Keywords únicas: {comp_metrics['unique_keywords']}")
        print(f"  TF-IDF promedio: {comp_metrics['avg_tfidf']:.4f}")
        print(f"  Optimización: {comp_metrics['keyword_optimization']:.2f}%")
        print(f"  Profundidad contenido: {comp_metrics['content_depth']:.0f} palabras")

        # Quick wins
        gaps = analyzer.find_keyword_gaps(own_keywords, comp_keywords)
        overlap = analyzer.analyze_keyword_overlap(own_keywords, comp_keywords)
        quick_wins = analyzer.identify_quick_wins(gaps, overlap)

        print(f"\n⚡ TOP {min(10, len(quick_wins))} QUICK WINS:")
        for i, win in enumerate(quick_wins[:10], 1):
            print(f"{i:2d}. [{win['type']}] {win['action']}")
            print(f"    Esfuerzo: {win['estimated_effort']} | Impacto: {win['potential_impact']}")

        print("\n✅ Análisis competitivo completado")

    finally:
        await db.close()


async def cmd_analyze_quality(args):
    """Analiza la calidad del contenido de las páginas."""
    print(f"\n📝 Analizando calidad de contenido para sesión {args.session}...")

    db = Database(Config().get('database_path'))
    await db.connect()

    try:
        # Obtener páginas
        pages = await db.get_pages_by_session(args.session)
        if not pages:
            print(f"❌ No se encontraron páginas en la sesión {args.session}")
            return

        print(f"Analizando {len(pages)} páginas...")

        # Inicializar analizador
        analyzer = ContentQualityAnalyzer()

        # Contador
        analyzed = 0
        thin_content_count = 0
        low_quality_count = 0

        print("\n🔍 Procesando páginas...")

        for page in pages:
            page_id = page['page_id']

            # Obtener contenido (simular con título + descripción por ahora)
            # En producción, aquí cargarías el HTML completo
            content_text = f"{page.get('title', '')} {page.get('meta_description', '')} " * 10

            # Obtener headings e imágenes (simplificado)
            # En producción, obtener de la base de datos
            headings = []  # Placeholder
            images = []  # Placeholder

            # Analizar calidad
            quality_metrics = analyzer.analyze_page_quality(
                page_data=page,
                content_text=content_text,
                headings=headings,
                images=images,
                language=args.language
            )

            # Guardar en base de datos
            await db.set_content_quality(
                page_id=page_id,
                quality_score=quality_metrics['quality_score'],
                readability_score=quality_metrics['readability_score'],
                readability_level=quality_metrics['readability_level'],
                lexical_diversity=quality_metrics['lexical_diversity'],
                avg_sentence_length=quality_metrics['avg_sentence_length'],
                avg_word_length=quality_metrics['avg_word_length'],
                is_thin_content=quality_metrics['is_thin_content'],
                heading_structure_score=quality_metrics['heading_structure_score'],
                multimedia_score=quality_metrics['multimedia_score']
            )

            analyzed += 1
            if quality_metrics['is_thin_content']:
                thin_content_count += 1
            if quality_metrics['quality_score'] < 40:
                low_quality_count += 1

            if analyzed % 10 == 0:
                print(f"  Analizadas: {analyzed}/{len(pages)}")

        # Mostrar resumen
        print("\n" + "="*80)
        print("RESUMEN DE CALIDAD DE CONTENIDO")
        print("="*80)
        print(f"Total páginas analizadas: {analyzed}")
        print(f"Páginas con thin content: {thin_content_count} ({thin_content_count/analyzed*100:.1f}%)")
        print(f"Páginas de baja calidad (<40): {low_quality_count} ({low_quality_count/analyzed*100:.1f}%)")

        # Obtener top y peores páginas
        print("\n🏆 TOP 5 PÁGINAS POR CALIDAD:")
        low_quality_pages = await db.get_low_quality_pages(args.session, max_quality=100)
        top_pages = sorted(low_quality_pages, key=lambda x: x.get('quality_score', 0), reverse=True)[:5]

        for i, page in enumerate(top_pages, 1):
            print(f"{i}. {page.get('url', '')[:60]:60s} | Quality: {page.get('quality_score', 0):5.1f}")

        print("\n⚠️  5 PÁGINAS CON PEOR CALIDAD:")
        worst_pages = sorted(low_quality_pages, key=lambda x: x.get('quality_score', 0))[:5]

        for i, page in enumerate(worst_pages, 1):
            print(f"{i}. {page.get('url', '')[:60]:60s} | Quality: {page.get('quality_score', 0):5.1f}")

        print("\n✅ Análisis de calidad completado")

    finally:
        await db.close()


async def cmd_generate_visuals(args):
    """Genera visualizaciones de la sesión."""
    print(f"\n📊 Generando visualizaciones para sesión {args.session}...")

    db = Database(Config().get('database_path'))
    await db.connect()

    try:
        # Recopilar datos necesarios
        session_data = {}

        # Keywords básicas
        print("Obteniendo keywords...")
        pages = await db.get_pages_by_session(args.session)
        all_keywords = []
        for page in pages:
            keywords = await db.get_keywords_by_page(page['page_id'])
            all_keywords.extend(keywords)

        session_data['keywords'] = all_keywords[:100]  # Top 100 para word cloud

        # Keywords con métricas
        print("Obteniendo keywords con métricas...")
        keywords_with_metrics = await db.get_keywords_with_full_metrics(args.session, limit=100)
        session_data['keywords_with_metrics'] = keywords_with_metrics

        # Top keywords
        top_keywords = await db.get_top_keywords_by_session(args.session, limit=20)
        session_data['top_keywords'] = top_keywords

        # Topics
        print("Obteniendo topics...")
        topics = await db.get_topics_by_session(args.session)
        session_data['topics'] = topics

        # Páginas con calidad
        print("Obteniendo páginas con quality scores...")
        pages_quality = await db.get_low_quality_pages(args.session, max_quality=100)
        session_data['pages_with_quality'] = pages_quality

        # Crear visualizador
        output_dir = args.output or f"visuals_session_{args.session}"
        visualizer = SEOVisualizer(output_dir=output_dir)

        # Generar visualizaciones
        print(f"\n🎨 Generando visualizaciones en: {output_dir}/")

        generated = visualizer.generate_full_report_visuals(session_data, output_dir=output_dir)

        # Mostrar resultados
        print("\n✅ Visualizaciones generadas:")
        for name, path in generated.items():
            print(f"  📈 {name}: {path}")

        if args.format == 'html' and generated:
            print(f"\n📄 Puedes ver las visualizaciones en el directorio: {output_dir}/")

        print(f"\n✅ Total: {len(generated)} visualizaciones generadas")

    finally:
        await db.close()


async def cmd_generate_interactive(args):
    """Genera visualizaciones interactivas con Plotly."""
    print(f"\n🎨 Generando visualizaciones interactivas para sesión {args.session}...")

    db = Database(Config().get('database_path'))
    await db.connect()

    try:
        # Recopilar datos necesarios
        session_data = {}

        print("Obteniendo datos...")
        pages = await db.get_pages_by_session(args.session)

        # Keywords con métricas
        keywords_with_metrics = await db.get_keywords_with_full_metrics(args.session, limit=200)
        session_data['keywords_with_metrics'] = keywords_with_metrics

        # Top keywords
        top_keywords = await db.get_top_keywords_by_session(args.session, limit=30)
        session_data['top_keywords'] = top_keywords

        # Clusters
        clusters = await db.get_clusters_by_session(args.session)
        session_data['clusters'] = clusters

        # Topics
        topics = await db.get_topics_by_session(args.session)
        session_data['topics'] = topics

        # Páginas con calidad
        pages_quality = await db.get_low_quality_pages(args.session, max_quality=100)
        session_data['pages_with_quality'] = pages_quality

        # Crear visualizador
        output_dir = args.output or f"interactive_session_{args.session}"
        visualizer = InteractiveVisualizer(output_dir=output_dir)

        # Generar visualizaciones
        print(f"\n🎨 Generando visualizaciones interactivas en: {output_dir}/")

        generated = visualizer.generate_all_interactive_visuals(session_data, output_dir=output_dir)

        # Mostrar resultados
        print("\n✅ Visualizaciones interactivas generadas:")
        for name, path in generated.items():
            print(f"  📊 {name}: {path}")

        print(f"\n🌐 Abre los archivos HTML en tu navegador para explorar interactivamente")
        print(f"✅ Total: {len(generated)} visualizaciones interactivas generadas")

    finally:
        await db.close()


async def cmd_analyze_network(args):
    """Analiza la estructura de enlaces internos."""
    print(f"\n🕸️  Analizando red de enlaces para sesión {args.session}...")

    db = Database(Config().get('database_path'))
    await db.connect()

    try:
        # Obtener páginas y enlaces
        print("Obteniendo datos de enlaces...")
        pages = await db.get_pages_by_session(args.session)

        all_links = []
        for page in pages:
            links = await db.get_links_by_page(page['page_id'])
            all_links.extend(links)

        if not pages or not all_links:
            print("❌ No hay suficientes datos de enlaces para analizar")
            return

        print(f"Páginas: {len(pages)} | Enlaces: {len(all_links)}")

        # Inicializar analizador
        analyzer = NetworkAnalyzer()

        # Análisis completo
        print("\n🔍 Analizando estructura de red...")
        results = analyzer.analyze_network(pages, all_links)

        if not results:
            print("❌ Error en análisis de red")
            return

        # Mostrar resultados
        print("\n" + "="*80)
        print("ANÁLISIS DE RED DE ENLACES")
        print("="*80)

        stats = results['graph_stats']
        print(f"\n📊 Estadísticas del Grafo:")
        print(f"  Nodos (páginas): {stats['num_pages']}")
        print(f"  Aristas (enlaces): {stats['num_links']}")
        print(f"  Densidad: {stats['density']:.4f}")
        print(f"  Grado promedio: {stats['avg_degree']:.2f}")

        # Top PageRank
        print(f"\n🏆 TOP 10 PÁGINAS POR PAGERANK:")
        for i, (page_id, score) in enumerate(results['top_pagerank'][:10], 1):
            page = next((p for p in pages if p['page_id'] == page_id), None)
            url = page['url'][:60] if page else 'Unknown'
            print(f"{i:2d}. {url:60s} | PageRank: {score:.6f}")

        # Top Hubs
        print(f"\n🔗 TOP 5 HUBS (páginas que más enlazan):")
        for i, (page_id, score) in enumerate(results['top_hubs'][:5], 1):
            page = next((p for p in pages if p['page_id'] == page_id), None)
            url = page['url'][:60] if page else 'Unknown'
            print(f"{i}. {url:60s} | Hub Score: {score:.6f}")

        # Top Authorities
        print(f"\n⭐ TOP 5 AUTHORITIES (páginas más enlazadas):")
        for i, (page_id, score) in enumerate(results['top_authorities'][:5], 1):
            page = next((p for p in pages if p['page_id'] == page_id), None)
            url = page['url'][:60] if page else 'Unknown'
            print(f"{i}. {url:60s} | Authority Score: {score:.6f}")

        # Páginas huérfanas
        if results['orphan_count'] > 0:
            print(f"\n⚠️  PÁGINAS HUÉRFANAS (sin enlaces entrantes): {results['orphan_count']}")
            for i, page_id in enumerate(results['orphan_pages'][:10], 1):
                page = next((p for p in pages if p['page_id'] == page_id), None)
                if page:
                    print(f"{i:2d}. {page['url'][:70]}")

        # Enlaces rotos
        if results['broken_links_count'] > 0:
            print(f"\n🔴 ENLACES ROTOS DETECTADOS: {results['broken_links_count']}")
            for i, broken in enumerate(results['broken_links'][:5], 1):
                print(f"{i}. {broken['source_url'][:40]} → {broken['target_url'][:40]}")

        # Clusters
        if results['cluster_count'] > 0:
            print(f"\n🎯 LINK CLUSTERS DETECTADOS: {results['cluster_count']}")
            for i, cluster in enumerate(results['link_clusters'][:3], 1):
                print(f"{i}. Cluster con {len(cluster)} páginas fuertemente conectadas")

        # Distribución de profundidad
        print(f"\n📊 DISTRIBUCIÓN POR PROFUNDIDAD:")
        for depth, count in sorted(results['depth_distribution'].items()):
            bar = '█' * (count // 2)
            print(f"  Depth {depth}: {count:4d} páginas {bar}")

        # Generar visualización si se solicita
        if args.visualize:
            print(f"\n🎨 Generando visualización de red...")
            output_path = args.output or f"network_graph_session_{args.session}.html"

            if analyzer.generate_network_visualization(
                output_path=output_path,
                layout=args.layout,
                top_n=args.top_n,
                color_by=args.color_by
            ):
                print(f"✅ Visualización generada: {output_path}")
                print(f"🌐 Abre el archivo HTML en tu navegador para explorar el grafo interactivo")

        print("\n✅ Análisis de red completado")

    finally:
        await db.close()


async def cmd_generate_dashboard(args):
    """Genera dashboard HTML interactivo completo."""
    print(f"\n📊 Generando dashboard interactivo para sesión {args.session}...")

    db = Database(Config().get('database_path'))
    await db.connect()

    try:
        # Recopilar todos los datos necesarios
        print("Recopilando datos...")

        session_data = {}

        # Keywords con métricas
        keywords_with_metrics = await db.get_keywords_with_full_metrics(args.session, limit=200)
        session_data['keywords_with_metrics'] = keywords_with_metrics

        # Top keywords
        top_keywords = await db.get_top_keywords_by_session(args.session, limit=30)
        session_data['top_keywords'] = top_keywords

        # Páginas con calidad
        pages_quality = await db.get_low_quality_pages(args.session, max_quality=100)
        session_data['pages_with_quality'] = pages_quality

        # Topics
        topics = await db.get_topics_by_session(args.session)
        session_data['topics'] = topics

        # Clusters
        clusters = await db.get_clusters_by_session(args.session)
        session_data['clusters'] = clusters

        # Crear visualizador
        visualizer = InteractiveVisualizer()

        # Generar dashboard
        output_path = args.output or f"dashboard_session_{args.session}.html"

        print(f"\n🎨 Generando dashboard en: {output_path}")

        if visualizer.generate_interactive_dashboard(session_data, output_path):
            print(f"\n✅ Dashboard generado exitosamente!")
            print(f"📂 Archivo: {output_path}")
            print(f"🌐 Abre el archivo en tu navegador para explorar el dashboard interactivo")
            print(f"\n📊 El dashboard incluye:")
            print(f"  • Opportunity Matrix (Scatter)")
            print(f"  • Quality Distribution (Histogram)")
            print(f"  • Top Keywords (Bar)")
            print(f"  • Competition Levels (Pie)")
            print(f"  • Readability Distribution (Pie)")
            print(f"  • Intent Distribution (Bar)")
        else:
            print("❌ Error generando dashboard")

    finally:
        await db.close()


# ==================== PASO 4: COMANDOS DE AUDITORÍA TÉCNICA ====================

async def cmd_technical_audit(args):
    """Ejecuta auditoría técnica SEO completa."""
    print(f"\n🔍 Ejecutando auditoría técnica SEO para sesión {args.session}...")

    db = Database()
    await db.initialize()

    try:
        # Cargar datos de la sesión
        session_data = await db.get_session_summary(args.session)
        if not session_data:
            print(f"❌ Sesión {args.session} no encontrada")
            return

        pages = await db.get_pages_by_session(args.session)
        images = await db.get_images_by_session(args.session)

        if not pages:
            print("❌ No hay páginas crawleadas en esta sesión")
            return

        print(f"📄 Analizando {len(pages)} páginas...")

        # Ejecutar auditoría técnica
        auditor = TechnicalSEOAuditor()
        audit_results = auditor.run_complete_audit(pages, images)

        # Generar y mostrar resumen
        summary = auditor.generate_audit_summary(audit_results)
        print("\n" + summary)

        # Guardar a archivo si se especifica
        if args.output:
            import json
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(audit_results, f, indent=2, ensure_ascii=False)

            print(f"\n💾 Resultados guardados en: {output_path}")

    finally:
        await db.close()


async def cmd_analyze_schema(args):
    """Analiza schema markup y datos estructurados."""
    print(f"\n🏷️  Analizando datos estructurados para sesión {args.session}...")

    db = Database()
    await db.initialize()

    try:
        # Cargar páginas
        pages = await db.get_pages_by_session(args.session)

        if not pages:
            print("❌ No hay páginas crawleadas en esta sesión")
            return

        print(f"📄 Analizando {len(pages)} páginas...")

        # Ejecutar análisis de schema
        analyzer = SchemaAnalyzer()
        schema_results = analyzer.run_complete_analysis(pages)

        # Generar y mostrar resumen
        summary = analyzer.generate_summary(schema_results)
        print("\n" + summary)

        # Guardar a archivo si se especifica
        if args.output:
            import json
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(schema_results, f, indent=2, ensure_ascii=False)

            print(f"\n💾 Resultados guardados en: {output_path}")

    finally:
        await db.close()


async def cmd_generate_recommendations(args):
    """Genera recomendaciones SEO accionables y priorizadas."""
    print(f"\n💡 Generando recomendaciones SEO para sesión {args.session}...")

    db = Database()
    await db.initialize()

    try:
        # Cargar todos los datos necesarios
        pages = await db.get_pages_by_session(args.session)
        images = await db.get_images_by_session(args.session)
        links = await db.get_links_by_session(args.session)

        if not pages:
            print("❌ No hay páginas crawleadas en esta sesión")
            return

        print(f"📊 Analizando {len(pages)} páginas para generar recomendaciones...")

        # Ejecutar análisis técnico
        print("  • Auditoría técnica...")
        auditor = TechnicalSEOAuditor()
        technical_audit = auditor.run_complete_audit(pages, images)

        # Ejecutar análisis de schema
        print("  • Análisis de datos estructurados...")
        schema_analyzer = SchemaAnalyzer()
        schema_analysis = schema_analyzer.run_complete_analysis(pages)

        # Ejecutar análisis de red (si hay enlaces)
        network_analysis = None
        if links:
            print("  • Análisis de estructura de enlaces...")
            network_analyzer = NetworkAnalyzer()
            network_analyzer.build_link_graph(pages, links)
            network_analysis = network_analyzer.analyze_network(pages, links)

        # Generar recomendaciones
        print("\n🎯 Generando recomendaciones priorizadas...")
        engine = RecommendationsEngine()
        recommendations = engine.generate_recommendations(
            technical_audit=technical_audit,
            schema_analysis=schema_analysis,
            network_analysis=network_analysis
        )

        # Generar roadmap
        roadmap = engine.generate_roadmap(recommendations)

        # Mostrar reporte
        report = engine.format_recommendations_report(recommendations)
        print("\n" + report)

        # Mostrar roadmap
        print("\n" + "=" * 100)
        print("ROADMAP DE IMPLEMENTACIÓN")
        print("=" * 100)
        for phase_key, phase_data in roadmap.items():
            print(f"\n{phase_data['title']}")
            print(f"  {phase_data['count']} recomendaciones")

        # Guardar a archivo si se especifica
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)
                f.write("\n\n" + "=" * 100)
                f.write("\nROADMAP DE IMPLEMENTACIÓN")
                f.write("\n" + "=" * 100)
                for phase_key, phase_data in roadmap.items():
                    f.write(f"\n\n{phase_data['title']}")
                    f.write(f"\n{phase_data['count']} recomendaciones\n")
                    for i, rec in enumerate(phase_data['recommendations'], 1):
                        f.write(f"\n{i}. {rec.title}")
                        f.write(f"\n   Impacto: {rec.impact_score}/100 | Esfuerzo: {rec.effort_score}/100")
                        f.write(f"\n   {rec.description}\n")

            print(f"\n💾 Reporte completo guardado en: {output_path}")

    finally:
        await db.close()


async def cmd_complete_audit(args):
    """Ejecuta auditoría completa: técnica + schema + recomendaciones."""
    print(f"\n🚀 AUDITORÍA SEO COMPLETA - Sesión {args.session}")
    print("=" * 100)

    db = Database()
    await db.initialize()

    try:
        # Cargar todos los datos
        session_data = await db.get_session_summary(args.session)
        pages = await db.get_pages_by_session(args.session)
        images = await db.get_images_by_session(args.session)
        links = await db.get_links_by_session(args.session)

        if not pages:
            print("❌ No hay páginas crawleadas en esta sesión")
            return

        print(f"\n📊 Datos de la sesión:")
        print(f"  • URL base: {session_data.get('base_url', 'N/A')}")
        print(f"  • Páginas crawleadas: {len(pages)}")
        print(f"  • Imágenes: {len(images)}")
        print(f"  • Enlaces internos: {len(links)}")

        # 1. Auditoría técnica
        print("\n" + "=" * 100)
        print("1. AUDITORÍA TÉCNICA SEO")
        print("=" * 100)
        auditor = TechnicalSEOAuditor()
        technical_audit = auditor.run_complete_audit(pages, images)
        print(auditor.generate_audit_summary(technical_audit))

        # 2. Análisis de Schema
        print("\n" + "=" * 100)
        print("2. ANÁLISIS DE DATOS ESTRUCTURADOS")
        print("=" * 100)
        schema_analyzer = SchemaAnalyzer()
        schema_analysis = schema_analyzer.run_complete_analysis(pages)
        print(schema_analyzer.generate_summary(schema_analysis))

        # 3. Análisis de red
        network_analysis = None
        if links:
            print("\n" + "=" * 100)
            print("3. ANÁLISIS DE ESTRUCTURA DE ENLACES")
            print("=" * 100)
            network_analyzer = NetworkAnalyzer()
            network_analyzer.build_link_graph(pages, links)
            network_analysis = network_analyzer.analyze_network(pages, links)

            print(f"\n📊 Estadísticas de la red:")
            stats = network_analysis['graph_stats']
            print(f"  • Nodos (páginas): {stats['nodes']}")
            print(f"  • Enlaces: {stats['edges']}")
            print(f"  • Densidad: {stats['density']:.4f}")
            print(f"  • Páginas huérfanas: {len(network_analysis['orphan_pages'])}")
            print(f"  • Enlaces rotos: {len(network_analysis['broken_links'])}")

        # 4. Generar recomendaciones
        print("\n" + "=" * 100)
        print("4. RECOMENDACIONES PRIORIZADAS")
        print("=" * 100)
        engine = RecommendationsEngine()
        recommendations = engine.generate_recommendations(
            technical_audit=technical_audit,
            schema_analysis=schema_analysis,
            network_analysis=network_analysis
        )

        # Mostrar solo top 10 recomendaciones
        print(f"\n🎯 Top 10 Recomendaciones por Impacto/Esfuerzo:\n")
        for i, rec in enumerate(recommendations[:10], 1):
            roi = rec.impact_score / max(rec.effort_score, 1)
            print(f"{i}. [{rec.priority.value.upper()}] {rec.title}")
            print(f"   ROI: {roi:.2f} | Impacto: {rec.impact_score}/100 | Esfuerzo: {rec.effort_score}/100")
            print(f"   {rec.description[:100]}...")
            print()

        print(f"\n💡 Total de {len(recommendations)} recomendaciones generadas")

        # Guardar todo a archivo si se especifica
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            import json
            complete_report = {
                'session_id': args.session,
                'base_url': session_data.get('base_url'),
                'pages_count': len(pages),
                'technical_audit': technical_audit,
                'schema_analysis': schema_analysis,
                'network_analysis': network_analysis,
                'recommendations_count': len(recommendations)
            }

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(complete_report, f, indent=2, ensure_ascii=False)

            print(f"\n💾 Auditoría completa guardada en: {output_path}")

            # También guardar reporte de texto
            txt_output = output_path.with_suffix('.txt')
            with open(txt_output, 'w', encoding='utf-8') as f:
                f.write("=" * 100 + "\n")
                f.write("AUDITORÍA SEO COMPLETA\n")
                f.write("=" * 100 + "\n\n")
                f.write(auditor.generate_audit_summary(technical_audit))
                f.write("\n\n")
                f.write(schema_analyzer.generate_summary(schema_analysis))
                f.write("\n\n")
                f.write(engine.format_recommendations_report(recommendations))

            print(f"📄 Reporte en texto guardado en: {txt_output}")

    finally:
        await db.close()


def main():
    """Punto de entrada principal."""
    parser = argparse.ArgumentParser(
        description='SEO Crawler - Professional SEO Analysis Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='Comandos disponibles')

    # Comando: crawl
    crawl_parser = subparsers.add_parser('crawl', help='Crawlear un sitio web')
    crawl_parser.add_argument('--url', required=True, help='URL inicial del crawl')
    crawl_parser.add_argument('--max-pages', type=int, default=500, help='Máximo de páginas a crawlear')
    crawl_parser.add_argument('--max-depth', type=int, default=5, help='Profundidad máxima')
    crawl_parser.add_argument('--concurrent', type=int, default=10, help='Requests concurrentes')
    crawl_parser.add_argument('--delay', type=float, default=1.0, help='Delay entre requests (segundos)')
    crawl_parser.add_argument('--ignore-robots', action='store_true', help='Ignorar robots.txt')
    crawl_parser.add_argument('--follow-external', action='store_true', help='Seguir enlaces externos')
    crawl_parser.add_argument('--auto-export', action='store_true', help='Generar reporte automáticamente')
    crawl_parser.add_argument('--log-level', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'])

    # Comando: analyze
    analyze_parser = subparsers.add_parser('analyze', help='Analizar resultados de una sesión')
    analyze_parser.add_argument('--session', type=int, required=True, help='ID de la sesión')
    analyze_parser.add_argument('--export', help='Exportar a archivo (CSV, Excel, JSON)')

    # Comando: report
    report_parser = subparsers.add_parser('report', help='Generar reporte de una sesión')
    report_parser.add_argument('--session', type=int, required=True, help='ID de la sesión')
    report_parser.add_argument('--format', choices=['html', 'excel', 'csv', 'json'], default='html')
    report_parser.add_argument('--output', help='Ruta del archivo de salida')

    # Comando: list
    list_parser = subparsers.add_parser('list', help='Listar todas las sesiones')

    # Comando: compare
    compare_parser = subparsers.add_parser('compare', help='Comparar sesiones')
    compare_parser.add_argument('--sessions', type=int, nargs='+', required=True, help='IDs de sesiones a comparar')
    compare_parser.add_argument('--export', help='Exportar comparación a Excel')

    # Comando: gui
    gui_parser = subparsers.add_parser('gui', help='Lanzar interfaz gráfica')

    # ==================== COMANDOS PROFESIONALES ====================

    # Comando: analyze-semantic
    semantic_parser = subparsers.add_parser(
        'analyze-semantic',
        help='Análisis semántico y clustering de keywords'
    )
    semantic_parser.add_argument('--session', type=int, required=True, help='ID de la sesión')
    semantic_parser.add_argument('--method', choices=['kmeans', 'dbscan'], default='kmeans',
                                 help='Método de clustering')
    semantic_parser.add_argument('--n-clusters', type=int, default=10,
                                 help='Número de clusters (para k-means)')
    semantic_parser.add_argument('--use-embeddings', action='store_true',
                                 help='Usar embeddings semánticos (requiere sentence-transformers)')
    semantic_parser.add_argument('--classify-intent', action='store_true',
                                 help='Clasificar intención de búsqueda')
    semantic_parser.add_argument('--language', choices=['es', 'en'], default='es',
                                 help='Idioma para análisis NLP')

    # Comando: calculate-difficulty
    difficulty_parser = subparsers.add_parser(
        'calculate-difficulty',
        help='Calcular difficulty y opportunity scores'
    )
    difficulty_parser.add_argument('--session', type=int, required=True, help='ID de la sesión')

    # Comando: find-gaps
    gaps_parser = subparsers.add_parser(
        'find-gaps',
        help='Encontrar keyword gaps entre dos sesiones'
    )
    gaps_parser.add_argument('--own-session', type=int, required=True,
                            help='ID de tu sesión')
    gaps_parser.add_argument('--competitor-session', type=int, required=True,
                            help='ID de la sesión del competidor')
    gaps_parser.add_argument('--min-tfidf', type=float, default=0.5,
                            help='TF-IDF mínimo para considerar keyword relevante')
    gaps_parser.add_argument('--export', help='Exportar resultados a JSON')

    # Comando: competitive-analysis
    competitive_parser = subparsers.add_parser(
        'competitive-analysis',
        help='Análisis competitivo completo'
    )
    competitive_parser.add_argument('--own-session', type=int, required=True,
                                   help='ID de tu sesión')
    competitive_parser.add_argument('--competitor-session', type=int, required=True,
                                   help='ID de la sesión del competidor')

    # Comando: analyze-quality
    quality_parser = subparsers.add_parser(
        'analyze-quality',
        help='Analizar calidad de contenido (readability, thin content, etc.)'
    )
    quality_parser.add_argument('--session', type=int, required=True, help='ID de la sesión')
    quality_parser.add_argument('--language', choices=['es', 'en'], default='es',
                               help='Idioma para análisis de readability')

    # Comando: generate-visuals
    visuals_parser = subparsers.add_parser(
        'generate-visuals',
        help='Generar visualizaciones (word clouds, scatter plots, etc.)'
    )
    visuals_parser.add_argument('--session', type=int, required=True, help='ID de la sesión')
    visuals_parser.add_argument('--output', help='Directorio de salida')
    visuals_parser.add_argument('--format', choices=['png', 'html'], default='png',
                               help='Formato de salida')

    # ==================== PASO 3: COMANDOS INTERACTIVOS ====================

    # Comando: generate-interactive
    interactive_parser = subparsers.add_parser(
        'generate-interactive',
        help='Generar visualizaciones interactivas con Plotly (HTML)'
    )
    interactive_parser.add_argument('--session', type=int, required=True, help='ID de la sesión')
    interactive_parser.add_argument('--output', help='Directorio de salida')

    # Comando: analyze-network
    network_parser = subparsers.add_parser(
        'analyze-network',
        help='Analizar estructura de enlaces internos con grafos'
    )
    network_parser.add_argument('--session', type=int, required=True, help='ID de la sesión')
    network_parser.add_argument('--visualize', action='store_true',
                               help='Generar visualización interactiva del grafo')
    network_parser.add_argument('--output', help='Ruta del archivo de visualización')
    network_parser.add_argument('--layout', choices=['spring', 'circular', 'kamada_kawai'],
                               default='spring', help='Tipo de layout del grafo')
    network_parser.add_argument('--top-n', type=int, default=100,
                               help='Número de nodos top a visualizar')
    network_parser.add_argument('--color-by', choices=['pagerank', 'in_degree', 'betweenness'],
                               default='pagerank', help='Métrica para colorear nodos')

    # Comando: generate-dashboard
    dashboard_parser = subparsers.add_parser(
        'generate-dashboard',
        help='Generar dashboard HTML interactivo completo'
    )
    dashboard_parser.add_argument('--session', type=int, required=True, help='ID de la sesión')
    dashboard_parser.add_argument('--output', help='Ruta del archivo HTML de salida')

    # ==================== PASO 4: COMANDOS DE AUDITORÍA TÉCNICA ====================

    # Comando: technical-audit
    technical_audit_parser = subparsers.add_parser(
        'technical-audit',
        help='Ejecutar auditoría técnica SEO completa'
    )
    technical_audit_parser.add_argument('--session', type=int, required=True, help='ID de la sesión')
    technical_audit_parser.add_argument('--output', help='Ruta del archivo JSON de salida')

    # Comando: analyze-schema
    schema_parser = subparsers.add_parser(
        'analyze-schema',
        help='Analizar schema markup y datos estructurados (JSON-LD, OG, Twitter)'
    )
    schema_parser.add_argument('--session', type=int, required=True, help='ID de la sesión')
    schema_parser.add_argument('--output', help='Ruta del archivo JSON de salida')

    # Comando: generate-recommendations
    recommendations_parser = subparsers.add_parser(
        'generate-recommendations',
        help='Generar recomendaciones SEO priorizadas con roadmap'
    )
    recommendations_parser.add_argument('--session', type=int, required=True, help='ID de la sesión')
    recommendations_parser.add_argument('--output', help='Ruta del archivo de reporte')

    # Comando: complete-audit
    complete_audit_parser = subparsers.add_parser(
        'complete-audit',
        help='🚀 Auditoría SEO COMPLETA (técnica + schema + recomendaciones)'
    )
    complete_audit_parser.add_argument('--session', type=int, required=True, help='ID de la sesión')
    complete_audit_parser.add_argument('--output', help='Ruta del archivo JSON de salida')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Ejecutar comando
    if args.command == 'crawl':
        asyncio.run(cmd_crawl(args))
    elif args.command == 'analyze':
        asyncio.run(cmd_analyze(args))
    elif args.command == 'report':
        asyncio.run(cmd_report(args))
    elif args.command == 'list':
        asyncio.run(cmd_list_sessions(args))
    elif args.command == 'compare':
        asyncio.run(cmd_compare(args))
    elif args.command == 'gui':
        cmd_gui(args)
    # Comandos profesionales
    elif args.command == 'analyze-semantic':
        asyncio.run(cmd_analyze_semantic(args))
    elif args.command == 'calculate-difficulty':
        asyncio.run(cmd_calculate_difficulty(args))
    elif args.command == 'find-gaps':
        asyncio.run(cmd_find_gaps(args))
    elif args.command == 'competitive-analysis':
        asyncio.run(cmd_competitive_analysis(args))
    elif args.command == 'analyze-quality':
        asyncio.run(cmd_analyze_quality(args))
    elif args.command == 'generate-visuals':
        asyncio.run(cmd_generate_visuals(args))
    # Comandos PASO 3: Visualizaciones interactivas y análisis de redes
    elif args.command == 'generate-interactive':
        asyncio.run(cmd_generate_interactive(args))
    elif args.command == 'analyze-network':
        asyncio.run(cmd_analyze_network(args))
    elif args.command == 'generate-dashboard':
        asyncio.run(cmd_generate_dashboard(args))
    # Comandos PASO 4: Auditoría técnica y recomendaciones
    elif args.command == 'technical-audit':
        asyncio.run(cmd_technical_audit(args))
    elif args.command == 'analyze-schema':
        asyncio.run(cmd_analyze_schema(args))
    elif args.command == 'generate-recommendations':
        asyncio.run(cmd_generate_recommendations(args))
    elif args.command == 'complete-audit':
        asyncio.run(cmd_complete_audit(args))


if __name__ == '__main__':
    main()
