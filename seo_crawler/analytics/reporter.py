"""
Generador de reportes para el SEO Crawler.

Este módulo genera reportes en múltiples formatos (CSV, Excel, JSON, HTML)
con análisis y visualizaciones de los datos crawleados.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import logging

logger = logging.getLogger('SEOCrawler.Reporter')


class Reporter:
    """Generador de reportes en múltiples formatos."""

    def __init__(self, database):
        """
        Inicializa el generador de reportes.

        Args:
            database: Instancia de Database
        """
        self.db = database

    async def export_keywords_to_csv(self,
                                    session_id: int,
                                    output_path: str,
                                    limit: int = 1000) -> str:
        """
        Exporta keywords a CSV.

        Args:
            session_id: ID de la sesión
            output_path: Ruta del archivo de salida
            limit: Límite de keywords

        Returns:
            Ruta del archivo generado
        """
        keywords = await self.db.get_top_keywords_by_session(session_id, limit)

        if not keywords:
            logger.warning(f"No hay keywords para exportar en sesión {session_id}")
            return None

        # Convertir a DataFrame
        df = pd.DataFrame(keywords)

        # Guardar CSV
        df.to_csv(output_path, index=False, encoding='utf-8')

        logger.info(f"Keywords exportadas a CSV: {output_path}")
        return output_path

    async def export_pages_to_csv(self,
                                 session_id: int,
                                 output_path: str) -> str:
        """
        Exporta páginas crawleadas a CSV.

        Args:
            session_id: ID de la sesión
            output_path: Ruta del archivo de salida

        Returns:
            Ruta del archivo generado
        """
        pages = await self.db.get_pages_by_session(session_id)

        if not pages:
            logger.warning(f"No hay páginas para exportar en sesión {session_id}")
            return None

        # Convertir a DataFrame
        df = pd.DataFrame(pages)

        # Seleccionar columnas relevantes
        columns = ['url', 'domain', 'status_code', 'title', 'h1', 'meta_description',
                  'word_count', 'depth', 'crawl_date', 'response_time']

        # Filtrar solo columnas existentes
        available_columns = [col for col in columns if col in df.columns]
        df = df[available_columns]

        # Guardar CSV
        df.to_csv(output_path, index=False, encoding='utf-8')

        logger.info(f"Páginas exportadas a CSV: {output_path}")
        return output_path

    async def export_to_excel(self,
                            session_id: int,
                            output_path: str) -> str:
        """
        Exporta todos los datos a Excel con múltiples hojas.

        Args:
            session_id: ID de la sesión
            output_path: Ruta del archivo de salida

        Returns:
            Ruta del archivo generado
        """
        # Obtener datos
        session_info = await self.db.get_session(session_id)
        pages = await self.db.get_pages_by_session(session_id)
        keywords = await self.db.get_top_keywords_by_session(session_id, 1000)
        stats = await self.db.get_session_stats(session_id)

        # Crear Excel writer
        with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
            # Hoja de información general
            info_df = pd.DataFrame([{
                'Session ID': session_info.get('session_id'),
                'Seed URL': session_info.get('seed_url'),
                'Domains': session_info.get('domains'),
                'Start Time': session_info.get('start_time'),
                'End Time': session_info.get('end_time'),
                'Pages Crawled': stats.get('total_pages'),
                'Success Pages': stats.get('success_pages'),
                'Failed Pages': stats.get('failed_pages'),
                'Total Keywords': stats.get('total_keywords'),
                'Unique Keywords': stats.get('unique_keywords'),
                'Total Links': stats.get('total_links')
            }])
            info_df.to_excel(writer, sheet_name='Session Info', index=False)

            # Hoja de páginas
            if pages:
                pages_df = pd.DataFrame(pages)
                columns = ['url', 'domain', 'status_code', 'title', 'h1', 'meta_description',
                          'word_count', 'depth', 'crawl_date', 'response_time']
                available_columns = [col for col in columns if col in pages_df.columns]
                pages_df[available_columns].to_excel(writer, sheet_name='Pages', index=False)

            # Hoja de keywords
            if keywords:
                keywords_df = pd.DataFrame(keywords)
                keywords_df.to_excel(writer, sheet_name='Keywords', index=False)

        logger.info(f"Datos exportados a Excel: {output_path}")
        return output_path

    async def export_to_json(self,
                           session_id: int,
                           output_path: str,
                           include_pages: bool = True,
                           include_keywords: bool = True) -> str:
        """
        Exporta datos a JSON.

        Args:
            session_id: ID de la sesión
            output_path: Ruta del archivo de salida
            include_pages: Si incluir datos de páginas
            include_keywords: Si incluir keywords

        Returns:
            Ruta del archivo generado
        """
        data = {
            'session': await self.db.get_session(session_id),
            'stats': await self.db.get_session_stats(session_id)
        }

        if include_pages:
            data['pages'] = await self.db.get_pages_by_session(session_id)

        if include_keywords:
            data['keywords'] = await self.db.get_top_keywords_by_session(session_id, 1000)

        # Convertir datetime a string
        def json_serializer(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Type {type(obj)} not serializable")

        # Guardar JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=json_serializer)

        logger.info(f"Datos exportados a JSON: {output_path}")
        return output_path

    async def generate_html_report(self,
                                  session_id: int,
                                  output_path: str) -> str:
        """
        Genera un reporte HTML completo.

        Args:
            session_id: ID de la sesión
            output_path: Ruta del archivo de salida

        Returns:
            Ruta del archivo generado
        """
        # Obtener datos
        session_info = await self.db.get_session(session_id)
        stats = await self.db.get_session_stats(session_id)
        top_keywords = await self.db.get_top_keywords_by_session(session_id, 50)

        # Generar HTML
        html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SEO Crawler Report - Session {session_id}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: #f5f7fa;
            color: #2c3e50;
            line-height: 1.6;
            padding: 20px;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 2px 20px rgba(0,0,0,0.08);
        }}

        h1 {{
            color: #2c3e50;
            margin-bottom: 10px;
            font-size: 32px;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}

        h2 {{
            color: #34495e;
            margin-top: 40px;
            margin-bottom: 20px;
            font-size: 24px;
        }}

        .header {{
            margin-bottom: 40px;
        }}

        .meta {{
            color: #7f8c8d;
            font-size: 14px;
            margin-bottom: 30px;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}

        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }}

        .stat-card.green {{
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        }}

        .stat-card.orange {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }}

        .stat-card.blue {{
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        }}

        .stat-label {{
            font-size: 13px;
            opacity: 0.9;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 8px;
        }}

        .stat-value {{
            font-size: 36px;
            font-weight: bold;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
        }}

        thead {{
            background: #34495e;
            color: white;
        }}

        th {{
            padding: 15px;
            text-align: left;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 12px;
            letter-spacing: 0.5px;
        }}

        td {{
            padding: 12px 15px;
            border-bottom: 1px solid #ecf0f1;
        }}

        tbody tr:hover {{
            background: #f8f9fa;
        }}

        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }}

        .badge.high {{
            background: #e74c3c;
            color: white;
        }}

        .badge.medium {{
            background: #f39c12;
            color: white;
        }}

        .badge.low {{
            background: #27ae60;
            color: white;
        }}

        .info-grid {{
            display: grid;
            grid-template-columns: 200px 1fr;
            gap: 15px;
            margin: 20px 0;
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
        }}

        .info-label {{
            font-weight: 600;
            color: #34495e;
        }}

        .info-value {{
            color: #2c3e50;
        }}

        footer {{
            margin-top: 50px;
            padding-top: 20px;
            border-top: 1px solid #ecf0f1;
            text-align: center;
            color: #7f8c8d;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>SEO Crawler Analysis Report</h1>
            <div class="meta">
                Session ID: {session_id} |
                Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </div>
        </div>

        <h2>Session Information</h2>
        <div class="info-grid">
            <div class="info-label">Seed URL:</div>
            <div class="info-value">{session_info.get('seed_url', 'N/A')}</div>

            <div class="info-label">Domains:</div>
            <div class="info-value">{session_info.get('domains', 'N/A')}</div>

            <div class="info-label">Start Time:</div>
            <div class="info-value">{session_info.get('start_time', 'N/A')}</div>

            <div class="info-label">End Time:</div>
            <div class="info-value">{session_info.get('end_time', 'N/A')}</div>
        </div>

        <h2>Statistics Overview</h2>
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Total Pages</div>
                <div class="stat-value">{stats.get('total_pages', 0)}</div>
            </div>

            <div class="stat-card green">
                <div class="stat-label">Success Pages</div>
                <div class="stat-value">{stats.get('success_pages', 0)}</div>
            </div>

            <div class="stat-card orange">
                <div class="stat-label">Failed Pages</div>
                <div class="stat-value">{stats.get('failed_pages', 0)}</div>
            </div>

            <div class="stat-card blue">
                <div class="stat-label">Total Keywords</div>
                <div class="stat-value">{stats.get('total_keywords', 0)}</div>
            </div>

            <div class="stat-card">
                <div class="stat-label">Unique Keywords</div>
                <div class="stat-value">{stats.get('unique_keywords', 0)}</div>
            </div>

            <div class="stat-card green">
                <div class="stat-label">Total Links</div>
                <div class="stat-value">{stats.get('total_links', 0)}</div>
            </div>
        </div>

        <h2>Top 50 Keywords by TF-IDF</h2>
        <table>
            <thead>
                <tr>
                    <th>#</th>
                    <th>Keyword</th>
                    <th>Total Frequency</th>
                    <th>Avg Density</th>
                    <th>Avg TF-IDF</th>
                    <th>Pages</th>
                    <th>Priority</th>
                </tr>
            </thead>
            <tbody>
"""

        # Añadir keywords a la tabla
        for i, kw in enumerate(top_keywords, 1):
            tfidf = kw.get('avg_tfidf', 0)
            priority_class = 'high' if tfidf > 0.5 else 'medium' if tfidf > 0.2 else 'low'

            html += f"""
                <tr>
                    <td>{i}</td>
                    <td><strong>{kw.get('keyword', '')}</strong></td>
                    <td>{kw.get('total_frequency', 0)}</td>
                    <td>{kw.get('avg_density', 0):.2f}%</td>
                    <td>{tfidf:.4f}</td>
                    <td>{kw.get('page_count', 0)}</td>
                    <td><span class="badge {priority_class}">{priority_class.upper()}</span></td>
                </tr>
"""

        html += """
            </tbody>
        </table>

        <footer>
            <p>Generated by SEO Crawler - Professional SEO Analysis Tool</p>
        </footer>
    </div>
</body>
</html>
"""

        # Guardar HTML
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)

        logger.info(f"Reporte HTML generado: {output_path}")
        return output_path

    async def generate_comparison_report(self,
                                        session_ids: List[int],
                                        output_path: str) -> str:
        """
        Genera un reporte comparativo entre múltiples sesiones.

        Args:
            session_ids: Lista de IDs de sesiones
            output_path: Ruta del archivo de salida

        Returns:
            Ruta del archivo generado
        """
        comparison_data = []

        for session_id in session_ids:
            session_info = await self.db.get_session(session_id)
            stats = await self.db.get_session_stats(session_id)

            comparison_data.append({
                'Session ID': session_id,
                'Domain': session_info.get('domains', ''),
                'Total Pages': stats.get('total_pages', 0),
                'Success Pages': stats.get('success_pages', 0),
                'Failed Pages': stats.get('failed_pages', 0),
                'Total Keywords': stats.get('total_keywords', 0),
                'Unique Keywords': stats.get('unique_keywords', 0),
                'Total Links': stats.get('total_links', 0),
                'Internal Links': stats.get('internal_links', 0),
                'External Links': stats.get('external_links', 0)
            })

        df = pd.DataFrame(comparison_data)
        df.to_excel(output_path, index=False)

        logger.info(f"Reporte comparativo generado: {output_path}")
        return output_path
