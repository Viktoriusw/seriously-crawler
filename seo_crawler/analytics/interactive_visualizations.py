"""
Visualizaciones interactivas con Plotly.

Este módulo genera visualizaciones interactivas y dashboards:
- Interactive scatter plots (3D, hover info)
- Treemaps de keywords por categoría
- Sunburst charts de estructura de sitio
- Sankey diagrams de flujo de keywords
- Interactive heatmaps
- Timeline charts
- Dashboards HTML completos
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import json

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    import plotly.offline as pyo
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

logger = logging.getLogger(__name__)


class InteractiveVisualizer:
    """
    Generador de visualizaciones interactivas con Plotly.
    """

    def __init__(self, output_dir: str = 'interactive_visuals'):
        """
        Inicializa el visualizador interactivo.

        Args:
            output_dir: Directorio donde guardar las visualizaciones
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Template de color
        self.color_scheme = px.colors.qualitative.Set3

    # ==================== 3D SCATTER PLOT ====================

    def generate_3d_opportunity_scatter(
        self,
        keywords: List[Dict[str, Any]],
        output_path: str,
        title: str = "3D Keyword Opportunity Analysis"
    ) -> bool:
        """
        Genera scatter plot 3D interactivo: Difficulty vs Opportunity vs TF-IDF.

        Args:
            keywords: Lista de keywords con métricas
            output_path: Ruta del archivo de salida
            title: Título del gráfico

        Returns:
            True si se generó correctamente
        """
        if not PLOTLY_AVAILABLE or not PANDAS_AVAILABLE:
            logger.warning("Plotly o Pandas no disponible")
            return False

        try:
            # Preparar datos
            data = []
            for kw in keywords:
                if all(k in kw for k in ['difficulty_score', 'opportunity_score', 'tf_idf_score']):
                    data.append({
                        'keyword': kw.get('keyword', ''),
                        'difficulty': kw.get('difficulty_score', 0),
                        'opportunity': kw.get('opportunity_score', 0),
                        'tfidf': kw.get('tf_idf_score', 0),
                        'competition_level': kw.get('competition_level', 'medium')
                    })

            if not data:
                logger.warning("No hay datos para 3D scatter")
                return False

            df = pd.DataFrame(data)

            # Crear scatter 3D
            fig = px.scatter_3d(
                df,
                x='difficulty',
                y='opportunity',
                z='tfidf',
                color='competition_level',
                hover_name='keyword',
                hover_data={
                    'difficulty': ':.1f',
                    'opportunity': ':.1f',
                    'tfidf': ':.3f',
                    'competition_level': True
                },
                color_discrete_map={
                    'low': '#06A77D',
                    'medium': '#F18F01',
                    'high': '#C73E1D'
                },
                title=title,
                labels={
                    'difficulty': 'Difficulty Score',
                    'opportunity': 'Opportunity Score',
                    'tfidf': 'TF-IDF Score'
                }
            )

            # Configuración
            fig.update_layout(
                scene=dict(
                    xaxis_title='Difficulty',
                    yaxis_title='Opportunity',
                    zaxis_title='TF-IDF'
                ),
                height=700
            )

            # Guardar
            fig.write_html(output_path)
            logger.info(f"3D scatter generado: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error generando 3D scatter: {e}")
            return False

    # ==================== TREEMAP ====================

    def generate_keyword_treemap(
        self,
        clusters: List[Dict[str, Any]],
        output_path: str,
        title: str = "Keyword Clusters Treemap"
    ) -> bool:
        """
        Genera treemap de clusters de keywords.

        Args:
            clusters: Lista de clusters con keywords
            output_path: Ruta del archivo de salida
            title: Título del gráfico

        Returns:
            True si se generó correctamente
        """
        if not PLOTLY_AVAILABLE or not PANDAS_AVAILABLE:
            logger.warning("Plotly o Pandas no disponible")
            return False

        try:
            # Preparar datos jerárquicos
            data = []
            for cluster in clusters:
                cluster_name = cluster.get('cluster_name', 'Unknown')
                num_keywords = cluster.get('num_keywords', 0)
                avg_tfidf = cluster.get('avg_tfidf', 0)

                data.append({
                    'cluster': cluster_name,
                    'parent': '',
                    'value': num_keywords,
                    'tfidf': avg_tfidf
                })

            if not data:
                logger.warning("No hay clusters para treemap")
                return False

            df = pd.DataFrame(data)

            # Crear treemap
            fig = px.treemap(
                df,
                names='cluster',
                parents='parent',
                values='value',
                color='tfidf',
                hover_data=['value', 'tfidf'],
                color_continuous_scale='Viridis',
                title=title
            )

            fig.update_layout(height=600)
            fig.write_html(output_path)

            logger.info(f"Treemap generado: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error generando treemap: {e}")
            return False

    # ==================== SUNBURST CHART ====================

    def generate_topic_sunburst(
        self,
        topics: List[Dict[str, Any]],
        output_path: str,
        title: str = "Topic Distribution Sunburst"
    ) -> bool:
        """
        Genera sunburst chart de distribución de tópicos.

        Args:
            topics: Lista de tópicos
            output_path: Ruta del archivo de salida
            title: Título del gráfico

        Returns:
            True si se generó correctamente
        """
        if not PLOTLY_AVAILABLE or not PANDAS_AVAILABLE:
            logger.warning("Plotly o Pandas no disponible")
            return False

        try:
            # Preparar datos
            data = [{'label': 'All Topics', 'parent': '', 'value': 0}]

            for topic in topics:
                topic_name = topic.get('topic_name', f"Topic {topic.get('topic_id')}")
                pages_count = topic.get('pages_count', 0)
                coherence = topic.get('coherence_score', 0)

                data.append({
                    'label': topic_name,
                    'parent': 'All Topics',
                    'value': pages_count,
                    'coherence': coherence
                })

            if len(data) <= 1:
                logger.warning("No hay tópicos para sunburst")
                return False

            df = pd.DataFrame(data)

            # Crear sunburst
            fig = px.sunburst(
                df,
                names='label',
                parents='parent',
                values='value',
                title=title
            )

            fig.update_layout(height=600)
            fig.write_html(output_path)

            logger.info(f"Sunburst generado: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error generando sunburst: {e}")
            return False

    # ==================== INTERACTIVE HEATMAP ====================

    def generate_interactive_heatmap(
        self,
        keywords: List[Dict[str, Any]],
        output_path: str,
        title: str = "Keyword Position Heatmap",
        top_n: int = 30
    ) -> bool:
        """
        Genera heatmap interactivo de posiciones de keywords.

        Args:
            keywords: Lista de keywords
            output_path: Ruta del archivo de salida
            title: Título del gráfico
            top_n: Número de keywords a mostrar

        Returns:
            True si se generó correctamente
        """
        if not PLOTLY_AVAILABLE or not PANDAS_AVAILABLE:
            logger.warning("Plotly o Pandas no disponible")
            return False

        try:
            # Ordenar por TF-IDF y tomar top N
            keywords_sorted = sorted(keywords, key=lambda x: x.get('tf_idf_score', 0), reverse=True)[:top_n]

            # Preparar matriz
            keyword_names = []
            positions = ['Title', 'H1', 'First 100', 'Density']
            matrix = []

            for kw in keywords_sorted:
                keyword_names.append(kw.get('keyword', '')[:30])
                row = [
                    1 if kw.get('position_in_title', False) else 0,
                    1 if kw.get('position_in_h1', False) else 0,
                    1 if kw.get('position_in_first_100', False) else 0,
                    kw.get('density', 0) * 100  # Convertir a porcentaje
                ]
                matrix.append(row)

            if not matrix:
                logger.warning("No hay datos para heatmap")
                return False

            # Crear heatmap
            fig = go.Figure(data=go.Heatmap(
                z=matrix,
                x=positions,
                y=keyword_names,
                colorscale='YlOrRd',
                hoverongaps=False,
                hovertemplate='<b>%{y}</b><br>%{x}: %{z:.2f}<extra></extra>'
            ))

            fig.update_layout(
                title=title,
                xaxis_title='Position',
                yaxis_title='Keyword',
                height=max(600, len(keyword_names) * 20)
            )

            fig.write_html(output_path)
            logger.info(f"Interactive heatmap generado: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error generando interactive heatmap: {e}")
            return False

    # ==================== TIMELINE ====================

    def generate_quality_timeline(
        self,
        sessions: List[Dict[str, Any]],
        output_path: str,
        title: str = "Quality Score Timeline"
    ) -> bool:
        """
        Genera timeline de evolución de quality scores entre sesiones.

        Args:
            sessions: Lista de sesiones con stats
            output_path: Ruta del archivo de salida
            title: Título del gráfico

        Returns:
            True si se generó correctamente
        """
        if not PLOTLY_AVAILABLE or not PANDAS_AVAILABLE:
            logger.warning("Plotly o Pandas no disponible")
            return False

        try:
            # Preparar datos
            data = []
            for session in sessions:
                data.append({
                    'date': session.get('start_time', ''),
                    'session_id': session.get('session_id'),
                    'avg_quality': session.get('avg_quality_score', 0),
                    'total_pages': session.get('pages_crawled', 0)
                })

            if not data:
                logger.warning("No hay sesiones para timeline")
                return False

            df = pd.DataFrame(data)
            df['date'] = pd.to_datetime(df['date'])

            # Crear línea temporal
            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['avg_quality'],
                mode='lines+markers',
                name='Avg Quality Score',
                line=dict(color='#2E86AB', width=3),
                marker=dict(size=10),
                hovertemplate='<b>Session %{customdata}</b><br>Date: %{x}<br>Quality: %{y:.2f}<extra></extra>',
                customdata=df['session_id']
            ))

            fig.update_layout(
                title=title,
                xaxis_title='Date',
                yaxis_title='Average Quality Score',
                hovermode='x unified',
                height=500
            )

            fig.write_html(output_path)
            logger.info(f"Timeline generado: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error generando timeline: {e}")
            return False

    # ==================== SANKEY DIAGRAM ====================

    def generate_intent_flow_sankey(
        self,
        keywords: List[Dict[str, Any]],
        output_path: str,
        title: str = "Search Intent to Competition Flow"
    ) -> bool:
        """
        Genera diagrama Sankey de flujo intent → competition.

        Args:
            keywords: Lista de keywords con intent y competition
            output_path: Ruta del archivo de salida
            title: Título del gráfico

        Returns:
            True si se generó correctamente
        """
        if not PLOTLY_AVAILABLE:
            logger.warning("Plotly no disponible")
            return False

        try:
            # Contar flujos
            flows = {}
            for kw in keywords:
                intent = kw.get('intent_type', 'unknown')
                competition = kw.get('competition_level', 'unknown')
                key = (intent, competition)
                flows[key] = flows.get(key, 0) + 1

            if not flows:
                logger.warning("No hay datos para Sankey")
                return False

            # Crear nodos
            intent_types = list(set(intent for intent, _ in flows.keys()))
            competition_levels = list(set(comp for _, comp in flows.keys()))

            node_labels = intent_types + competition_levels
            node_colors = ['#A23B72'] * len(intent_types) + ['#06A77D'] * len(competition_levels)

            # Crear links
            source_indices = []
            target_indices = []
            values = []

            for (intent, competition), count in flows.items():
                source_idx = intent_types.index(intent)
                target_idx = len(intent_types) + competition_levels.index(competition)
                source_indices.append(source_idx)
                target_indices.append(target_idx)
                values.append(count)

            # Crear Sankey
            fig = go.Figure(data=[go.Sankey(
                node=dict(
                    pad=15,
                    thickness=20,
                    line=dict(color='black', width=0.5),
                    label=node_labels,
                    color=node_colors
                ),
                link=dict(
                    source=source_indices,
                    target=target_indices,
                    value=values
                )
            )])

            fig.update_layout(
                title=title,
                font_size=12,
                height=600
            )

            fig.write_html(output_path)
            logger.info(f"Sankey diagram generado: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error generando Sankey: {e}")
            return False

    # ==================== DASHBOARD ====================

    def generate_interactive_dashboard(
        self,
        session_data: Dict[str, Any],
        output_path: str
    ) -> bool:
        """
        Genera dashboard HTML interactivo completo.

        Args:
            session_data: Datos de la sesión
            output_path: Ruta del archivo HTML de salida

        Returns:
            True si se generó correctamente
        """
        if not PLOTLY_AVAILABLE or not PANDAS_AVAILABLE:
            logger.warning("Plotly o Pandas no disponible")
            return False

        try:
            # Crear subplots
            fig = make_subplots(
                rows=3, cols=2,
                subplot_titles=(
                    'Opportunity Matrix',
                    'Quality Distribution',
                    'Top Keywords by TF-IDF',
                    'Competition Levels',
                    'Readability Distribution',
                    'Keyword Count by Intent'
                ),
                specs=[
                    [{"type": "scatter"}, {"type": "histogram"}],
                    [{"type": "bar"}, {"type": "pie"}],
                    [{"type": "pie"}, {"type": "bar"}]
                ],
                vertical_spacing=0.12,
                horizontal_spacing=0.1
            )

            keywords_with_metrics = session_data.get('keywords_with_metrics', [])
            pages_quality = session_data.get('pages_with_quality', [])

            # 1. Opportunity Matrix
            if keywords_with_metrics:
                difficulties = [k.get('difficulty_score', 0) for k in keywords_with_metrics]
                opportunities = [k.get('opportunity_score', 0) for k in keywords_with_metrics]
                labels = [k.get('keyword', '')[:20] for k in keywords_with_metrics]

                fig.add_trace(
                    go.Scatter(
                        x=difficulties,
                        y=opportunities,
                        mode='markers',
                        text=labels,
                        marker=dict(size=8, opacity=0.6),
                        hovertemplate='%{text}<br>Diff: %{x:.1f}<br>Opp: %{y:.1f}<extra></extra>'
                    ),
                    row=1, col=1
                )

            # 2. Quality Distribution
            if pages_quality:
                quality_scores = [p.get('quality_score', 0) for p in pages_quality]
                fig.add_trace(
                    go.Histogram(x=quality_scores, nbinsx=20, marker_color='#2E86AB'),
                    row=1, col=2
                )

            # 3. Top Keywords
            if keywords_with_metrics:
                top_kw = sorted(keywords_with_metrics, key=lambda x: x.get('tf_idf_score', 0), reverse=True)[:10]
                kw_names = [k.get('keyword', '')[:20] for k in top_kw]
                tfidf_scores = [k.get('tf_idf_score', 0) for k in top_kw]

                fig.add_trace(
                    go.Bar(x=kw_names, y=tfidf_scores, marker_color='#06A77D'),
                    row=2, col=1
                )

            # 4. Competition Levels
            if keywords_with_metrics:
                comp_levels = [k.get('competition_level', 'unknown') for k in keywords_with_metrics]
                comp_counts = pd.Series(comp_levels).value_counts()

                fig.add_trace(
                    go.Pie(labels=comp_counts.index, values=comp_counts.values),
                    row=2, col=2
                )

            # 5. Readability Distribution
            if pages_quality:
                readability_levels = [p.get('readability_level', 'unknown') for p in pages_quality]
                read_counts = pd.Series(readability_levels).value_counts()

                fig.add_trace(
                    go.Pie(labels=read_counts.index, values=read_counts.values),
                    row=3, col=1
                )

            # 6. Intent Distribution
            if keywords_with_metrics:
                intents = [k.get('intent_type', 'unknown') for k in keywords_with_metrics]
                intent_counts = pd.Series(intents).value_counts()

                fig.add_trace(
                    go.Bar(x=intent_counts.index, y=intent_counts.values, marker_color='#A23B72'),
                    row=3, col=2
                )

            # Layout
            fig.update_layout(
                title_text="SEO Analysis Interactive Dashboard",
                showlegend=False,
                height=1200
            )

            # Actualizar ejes
            fig.update_xaxes(title_text="Difficulty", row=1, col=1)
            fig.update_yaxes(title_text="Opportunity", row=1, col=1)
            fig.update_xaxes(title_text="Quality Score", row=1, col=2)
            fig.update_yaxes(title_text="Count", row=1, col=2)

            # Guardar
            fig.write_html(output_path)
            logger.info(f"Dashboard interactivo generado: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error generando dashboard: {e}")
            return False

    # ==================== BATCH GENERATION ====================

    def generate_all_interactive_visuals(
        self,
        session_data: Dict[str, Any],
        output_dir: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Genera todas las visualizaciones interactivas.

        Args:
            session_data: Datos de la sesión
            output_dir: Directorio de salida (opcional)

        Returns:
            Diccionario con paths de archivos generados
        """
        if output_dir:
            self.output_dir = Path(output_dir)
            self.output_dir.mkdir(parents=True, exist_ok=True)

        generated_files = {}

        # 1. 3D Scatter
        if session_data.get('keywords_with_metrics'):
            path = str(self.output_dir / '3d_opportunity_scatter.html')
            if self.generate_3d_opportunity_scatter(session_data['keywords_with_metrics'], path):
                generated_files['3d_scatter'] = path

        # 2. Treemap
        if session_data.get('clusters'):
            path = str(self.output_dir / 'keyword_treemap.html')
            if self.generate_keyword_treemap(session_data['clusters'], path):
                generated_files['treemap'] = path

        # 3. Sunburst
        if session_data.get('topics'):
            path = str(self.output_dir / 'topic_sunburst.html')
            if self.generate_topic_sunburst(session_data['topics'], path):
                generated_files['sunburst'] = path

        # 4. Interactive Heatmap
        if session_data.get('top_keywords'):
            path = str(self.output_dir / 'interactive_heatmap.html')
            if self.generate_interactive_heatmap(session_data['top_keywords'], path):
                generated_files['heatmap'] = path

        # 5. Sankey
        if session_data.get('keywords_with_metrics'):
            path = str(self.output_dir / 'intent_flow_sankey.html')
            if self.generate_intent_flow_sankey(session_data['keywords_with_metrics'], path):
                generated_files['sankey'] = path

        # 6. Dashboard
        path = str(self.output_dir / 'interactive_dashboard.html')
        if self.generate_interactive_dashboard(session_data, path):
            generated_files['dashboard'] = path

        logger.info(f"Generadas {len(generated_files)} visualizaciones interactivas")
        return generated_files
