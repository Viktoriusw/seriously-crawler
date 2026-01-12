"""
Visualizaciones profesionales para análisis SEO.

Este módulo genera gráficos y visualizaciones profesionales:
- Keyword word clouds
- Density heatmaps
- Scatter plots (difficulty vs opportunity)
- Topic distribution charts
- Competitive comparison charts
- Quality score distributions
- Network graphs (opcional)
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import json

try:
    import matplotlib
    matplotlib.use('Agg')  # Backend sin GUI
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    from wordcloud import WordCloud
    WORDCLOUD_AVAILABLE = True
except ImportError:
    WORDCLOUD_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

logger = logging.getLogger(__name__)


class SEOVisualizer:
    """
    Generador de visualizaciones profesionales para análisis SEO.
    """

    def __init__(self, output_dir: str = 'visualizations'):
        """
        Inicializa el visualizador.

        Args:
            output_dir: Directorio donde guardar las visualizaciones
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Configuración de estilo
        if MATPLOTLIB_AVAILABLE:
            plt.style.use('seaborn-v0_8-darkgrid' if hasattr(plt.style, 'available') else 'default')
            self.colors = {
                'primary': '#2E86AB',
                'secondary': '#A23B72',
                'success': '#06A77D',
                'warning': '#F18F01',
                'danger': '#C73E1D',
                'info': '#6C757D'
            }

    # ==================== KEYWORD WORD CLOUD ====================

    def generate_keyword_cloud(
        self,
        keywords: List[Dict[str, Any]],
        output_path: str,
        title: str = "Keyword Cloud",
        max_words: int = 100,
        width: int = 1200,
        height: int = 600
    ) -> bool:
        """
        Genera una nube de palabras de keywords.

        Args:
            keywords: Lista de keywords con frequency o tf_idf_score
            output_path: Ruta del archivo de salida
            title: Título del gráfico
            max_words: Número máximo de palabras
            width: Ancho de la imagen
            height: Alto de la imagen

        Returns:
            True si se generó correctamente
        """
        if not WORDCLOUD_AVAILABLE or not MATPLOTLIB_AVAILABLE:
            logger.warning("wordcloud o matplotlib no disponible")
            return False

        try:
            # Crear diccionario de frecuencias
            word_freq = {}
            for kw in keywords:
                keyword_text = kw.get('keyword', '')
                # Usar TF-IDF si está disponible, sino frequency
                weight = kw.get('tf_idf_score', kw.get('frequency', 1))
                word_freq[keyword_text] = weight

            if not word_freq:
                logger.warning("No hay keywords para generar word cloud")
                return False

            # Generar word cloud
            wordcloud = WordCloud(
                width=width,
                height=height,
                max_words=max_words,
                background_color='white',
                colormap='viridis',
                relative_scaling=0.5,
                min_font_size=10
            ).generate_from_frequencies(word_freq)

            # Crear figura
            fig, ax = plt.subplots(figsize=(width/100, height/100), dpi=100)
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis('off')
            ax.set_title(title, fontsize=20, fontweight='bold', pad=20)

            plt.tight_layout(pad=0)
            plt.savefig(output_path, dpi=100, bbox_inches='tight')
            plt.close()

            logger.info(f"Word cloud generado: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error generando word cloud: {e}")
            return False

    # ==================== DIFFICULTY VS OPPORTUNITY SCATTER ====================

    def generate_opportunity_scatter(
        self,
        keywords: List[Dict[str, Any]],
        output_path: str,
        title: str = "Keyword Opportunity Matrix"
    ) -> bool:
        """
        Genera scatter plot de Difficulty vs Opportunity.

        Args:
            keywords: Lista de keywords con difficulty_score y opportunity_score
            output_path: Ruta del archivo de salida
            title: Título del gráfico

        Returns:
            True si se generó correctamente
        """
        if not MATPLOTLIB_AVAILABLE or not NUMPY_AVAILABLE:
            logger.warning("matplotlib o numpy no disponible")
            return False

        try:
            # Extraer datos
            difficulties = []
            opportunities = []
            labels = []

            for kw in keywords:
                diff = kw.get('difficulty_score')
                opp = kw.get('opportunity_score')

                if diff is not None and opp is not None:
                    difficulties.append(diff)
                    opportunities.append(opp)
                    labels.append(kw.get('keyword', ''))

            if not difficulties:
                logger.warning("No hay datos de difficulty/opportunity")
                return False

            # Crear figura
            fig, ax = plt.subplots(figsize=(12, 8))

            # Crear scatter plot con colores por cuadrante
            colors = []
            for d, o in zip(difficulties, opportunities):
                if o >= 70 and d < 30:
                    colors.append(self.colors['success'])  # Quick wins
                elif o >= 70 and d >= 30:
                    colors.append(self.colors['warning'])  # High value
                elif o < 70 and d < 30:
                    colors.append(self.colors['info'])  # Low priority
                else:
                    colors.append(self.colors['danger'])  # Difficult

            scatter = ax.scatter(
                difficulties,
                opportunities,
                c=colors,
                s=100,
                alpha=0.6,
                edgecolors='black',
                linewidth=0.5
            )

            # Líneas de cuadrantes
            ax.axhline(y=70, color='gray', linestyle='--', alpha=0.5, linewidth=1)
            ax.axvline(x=30, color='gray', linestyle='--', alpha=0.5, linewidth=1)

            # Etiquetas de cuadrantes
            ax.text(15, 85, 'QUICK WINS', fontsize=12, ha='center',
                   bbox=dict(boxstyle='round', facecolor=self.colors['success'], alpha=0.3))
            ax.text(65, 85, 'HIGH VALUE', fontsize=12, ha='center',
                   bbox=dict(boxstyle='round', facecolor=self.colors['warning'], alpha=0.3))
            ax.text(15, 35, 'LOW PRIORITY', fontsize=12, ha='center',
                   bbox=dict(boxstyle='round', facecolor=self.colors['info'], alpha=0.3))
            ax.text(65, 35, 'DIFFICULT', fontsize=12, ha='center',
                   bbox=dict(boxstyle='round', facecolor=self.colors['danger'], alpha=0.3))

            # Etiquetar algunos puntos importantes (top keywords)
            top_opportunities = sorted(zip(opportunities, difficulties, labels), reverse=True)[:10]
            for opp, diff, label in top_opportunities:
                ax.annotate(label[:20], (diff, opp), fontsize=8, alpha=0.7,
                           xytext=(5, 5), textcoords='offset points')

            # Configuración
            ax.set_xlabel('Keyword Difficulty', fontsize=14, fontweight='bold')
            ax.set_ylabel('Keyword Opportunity', fontsize=14, fontweight='bold')
            ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
            ax.grid(True, alpha=0.3)
            ax.set_xlim(-5, 105)
            ax.set_ylim(-5, 105)

            plt.tight_layout()
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()

            logger.info(f"Opportunity scatter generado: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error generando opportunity scatter: {e}")
            return False

    # ==================== TOPIC DISTRIBUTION ====================

    def generate_topic_distribution(
        self,
        topics: List[Dict[str, Any]],
        output_path: str,
        title: str = "Topic Distribution"
    ) -> bool:
        """
        Genera gráfico de barras de distribución de tópicos.

        Args:
            topics: Lista de tópicos con coherence_score y pages_count
            output_path: Ruta del archivo de salida
            title: Título del gráfico

        Returns:
            True si se generó correctamente
        """
        if not MATPLOTLIB_AVAILABLE:
            logger.warning("matplotlib no disponible")
            return False

        try:
            if not topics:
                logger.warning("No hay tópicos para visualizar")
                return False

            # Ordenar por coherence score
            topics_sorted = sorted(topics, key=lambda x: x.get('coherence_score', 0), reverse=True)[:15]

            topic_names = [t.get('topic_name', f"Topic {i+1}")[:40] for i, t in enumerate(topics_sorted)]
            coherence_scores = [t.get('coherence_score', 0) for t in topics_sorted]

            # Crear figura
            fig, ax = plt.subplots(figsize=(12, 8))

            # Barras horizontales
            y_pos = range(len(topic_names))
            bars = ax.barh(y_pos, coherence_scores, color=self.colors['primary'], alpha=0.7)

            # Añadir valores al final de las barras
            for i, (bar, score) in enumerate(zip(bars, coherence_scores)):
                ax.text(score + 0.01, i, f'{score:.3f}', va='center', fontsize=10)

            # Configuración
            ax.set_yticks(y_pos)
            ax.set_yticklabels(topic_names, fontsize=10)
            ax.set_xlabel('Coherence Score', fontsize=12, fontweight='bold')
            ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
            ax.grid(axis='x', alpha=0.3)

            plt.tight_layout()
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()

            logger.info(f"Topic distribution generado: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error generando topic distribution: {e}")
            return False

    # ==================== COMPETITIVE COMPARISON ====================

    def generate_competitive_comparison(
        self,
        your_metrics: Dict[str, Any],
        competitor_metrics: Dict[str, Any],
        output_path: str,
        title: str = "Competitive Comparison"
    ) -> bool:
        """
        Genera gráfico de barras comparativo con competidor.

        Args:
            your_metrics: Tus métricas
            competitor_metrics: Métricas del competidor
            output_path: Ruta del archivo de salida
            title: Título del gráfico

        Returns:
            True si se generó correctamente
        """
        if not MATPLOTLIB_AVAILABLE or not NUMPY_AVAILABLE:
            logger.warning("matplotlib o numpy no disponible")
            return False

        try:
            # Métricas a comparar
            metrics_to_compare = [
                ('total_keywords', 'Total Keywords'),
                ('unique_keywords', 'Unique Keywords'),
                ('avg_tfidf', 'Avg TF-IDF'),
                ('keyword_optimization', 'Optimization %'),
                ('content_depth', 'Avg Word Count')
            ]

            your_values = []
            comp_values = []
            metric_labels = []

            for key, label in metrics_to_compare:
                your_val = your_metrics.get(key, 0)
                comp_val = competitor_metrics.get(key, 0)

                # Normalizar para visualización
                if key == 'avg_tfidf':
                    your_val *= 10  # Escalar para visibilidad
                    comp_val *= 10

                your_values.append(your_val)
                comp_values.append(comp_val)
                metric_labels.append(label)

            # Crear figura
            fig, ax = plt.subplots(figsize=(12, 8))

            x = np.arange(len(metric_labels))
            width = 0.35

            bars1 = ax.bar(x - width/2, your_values, width, label='Your Site',
                          color=self.colors['primary'], alpha=0.8)
            bars2 = ax.bar(x + width/2, comp_values, width, label='Competitor',
                          color=self.colors['secondary'], alpha=0.8)

            # Añadir valores encima de las barras
            for bars in [bars1, bars2]:
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{height:.1f}',
                           ha='center', va='bottom', fontsize=9)

            # Configuración
            ax.set_ylabel('Value', fontsize=12, fontweight='bold')
            ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
            ax.set_xticks(x)
            ax.set_xticklabels(metric_labels, rotation=15, ha='right')
            ax.legend(fontsize=12)
            ax.grid(axis='y', alpha=0.3)

            plt.tight_layout()
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()

            logger.info(f"Competitive comparison generado: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error generando competitive comparison: {e}")
            return False

    # ==================== QUALITY SCORE DISTRIBUTION ====================

    def generate_quality_distribution(
        self,
        pages: List[Dict[str, Any]],
        output_path: str,
        title: str = "Content Quality Distribution"
    ) -> bool:
        """
        Genera histograma de distribución de quality scores.

        Args:
            pages: Lista de páginas con quality_score
            output_path: Ruta del archivo de salida
            title: Título del gráfico

        Returns:
            True si se generó correctamente
        """
        if not MATPLOTLIB_AVAILABLE or not NUMPY_AVAILABLE:
            logger.warning("matplotlib o numpy no disponible")
            return False

        try:
            quality_scores = [p.get('quality_score', 0) for p in pages if p.get('quality_score')]

            if not quality_scores:
                logger.warning("No hay quality scores para visualizar")
                return False

            # Crear figura
            fig, ax = plt.subplots(figsize=(12, 7))

            # Histograma
            n, bins, patches = ax.hist(quality_scores, bins=20, edgecolor='black', alpha=0.7)

            # Colorear barras según rangos
            for i, patch in enumerate(patches):
                bin_center = (bins[i] + bins[i+1]) / 2
                if bin_center >= 80:
                    patch.set_facecolor(self.colors['success'])
                elif bin_center >= 60:
                    patch.set_facecolor(self.colors['info'])
                elif bin_center >= 40:
                    patch.set_facecolor(self.colors['warning'])
                else:
                    patch.set_facecolor(self.colors['danger'])

            # Línea de media
            mean_score = np.mean(quality_scores)
            ax.axvline(mean_score, color='red', linestyle='--', linewidth=2,
                      label=f'Mean: {mean_score:.2f}')

            # Configuración
            ax.set_xlabel('Quality Score', fontsize=12, fontweight='bold')
            ax.set_ylabel('Number of Pages', fontsize=12, fontweight='bold')
            ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
            ax.legend(fontsize=12)
            ax.grid(axis='y', alpha=0.3)

            # Añadir leyenda de colores
            legend_elements = [
                mpatches.Patch(color=self.colors['success'], label='Excellent (80-100)'),
                mpatches.Patch(color=self.colors['info'], label='Good (60-79)'),
                mpatches.Patch(color=self.colors['warning'], label='Fair (40-59)'),
                mpatches.Patch(color=self.colors['danger'], label='Poor (0-39)')
            ]
            ax.legend(handles=legend_elements, loc='upper left', fontsize=10)

            plt.tight_layout()
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()

            logger.info(f"Quality distribution generado: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error generando quality distribution: {e}")
            return False

    # ==================== DENSITY HEATMAP ====================

    def generate_density_heatmap(
        self,
        keywords: List[Dict[str, Any]],
        output_path: str,
        title: str = "Keyword Density Heatmap",
        top_n: int = 20
    ) -> bool:
        """
        Genera heatmap de densidad de keywords en diferentes posiciones.

        Args:
            keywords: Lista de keywords con position metrics
            output_path: Ruta del archivo de salida
            title: Título del gráfico
            top_n: Número de top keywords a mostrar

        Returns:
            True si se generó correctamente
        """
        if not MATPLOTLIB_AVAILABLE or not NUMPY_AVAILABLE:
            logger.warning("matplotlib o numpy no disponible")
            return False

        try:
            # Ordenar por TF-IDF y tomar top N
            keywords_sorted = sorted(keywords, key=lambda x: x.get('tf_idf_score', 0), reverse=True)[:top_n]

            keyword_names = [k.get('keyword', '')[:30] for k in keywords_sorted]
            positions = ['Title', 'H1', 'First 100', 'Body']

            # Crear matriz de datos
            data = []
            for kw in keywords_sorted:
                row = [
                    1 if kw.get('position_in_title', False) else 0,
                    1 if kw.get('position_in_h1', False) else 0,
                    1 if kw.get('position_in_first_100', False) else 0,
                    kw.get('density', 0) * 100  # Convertir a porcentaje
                ]
                data.append(row)

            data_array = np.array(data)

            # Crear figura
            fig, ax = plt.subplots(figsize=(10, max(8, len(keyword_names) * 0.4)))

            # Heatmap
            im = ax.imshow(data_array, cmap='YlOrRd', aspect='auto')

            # Configurar ejes
            ax.set_xticks(np.arange(len(positions)))
            ax.set_yticks(np.arange(len(keyword_names)))
            ax.set_xticklabels(positions, fontsize=11)
            ax.set_yticklabels(keyword_names, fontsize=9)

            # Rotar etiquetas
            plt.setp(ax.get_xticklabels(), rotation=0, ha="center")

            # Añadir valores en las celdas
            for i in range(len(keyword_names)):
                for j in range(len(positions)):
                    if j < 3:  # Title, H1, First 100 (binario)
                        text = '✓' if data_array[i, j] == 1 else ''
                    else:  # Body density
                        text = f'{data_array[i, j]:.1f}%' if data_array[i, j] > 0 else ''

                    ax.text(j, i, text, ha="center", va="center",
                           color="white" if data_array[i, j] > 50 else "black",
                           fontsize=9, fontweight='bold')

            # Colorbar
            cbar = plt.colorbar(im, ax=ax)
            cbar.set_label('Density %', rotation=270, labelpad=20, fontsize=11)

            # Título
            ax.set_title(title, fontsize=14, fontweight='bold', pad=20)

            plt.tight_layout()
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()

            logger.info(f"Density heatmap generado: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error generando density heatmap: {e}")
            return False

    # ==================== READABILITY DISTRIBUTION ====================

    def generate_readability_chart(
        self,
        pages: List[Dict[str, Any]],
        output_path: str,
        title: str = "Readability Score Distribution"
    ) -> bool:
        """
        Genera gráfico de pie de distribución de niveles de readability.

        Args:
            pages: Lista de páginas con readability_level
            output_path: Ruta del archivo de salida
            title: Título del gráfico

        Returns:
            True si se generó correctamente
        """
        if not MATPLOTLIB_AVAILABLE:
            logger.warning("matplotlib no disponible")
            return False

        try:
            # Contar por nivel
            level_counts = {}
            for page in pages:
                level = page.get('readability_level', 'unknown')
                level_counts[level] = level_counts.get(level, 0) + 1

            if not level_counts:
                logger.warning("No hay datos de readability")
                return False

            # Preparar datos
            labels = list(level_counts.keys())
            sizes = list(level_counts.values())

            # Colores por nivel
            colors_map = {
                'very_easy': self.colors['success'],
                'easy': '#7CB342',
                'fairly_easy': self.colors['info'],
                'normal': '#FDD835',
                'fairly_difficult': self.colors['warning'],
                'difficult': '#FB8C00',
                'very_difficult': self.colors['danger']
            }
            colors = [colors_map.get(label, '#CCCCCC') for label in labels]

            # Crear figura
            fig, ax = plt.subplots(figsize=(10, 8))

            wedges, texts, autotexts = ax.pie(
                sizes,
                labels=labels,
                colors=colors,
                autopct='%1.1f%%',
                startangle=90,
                textprops={'fontsize': 11}
            )

            # Mejorar texto
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')

            ax.set_title(title, fontsize=16, fontweight='bold', pad=20)

            plt.tight_layout()
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()

            logger.info(f"Readability chart generado: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error generando readability chart: {e}")
            return False

    # ==================== BATCH GENERATION ====================

    def generate_full_report_visuals(
        self,
        session_data: Dict[str, Any],
        output_dir: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Genera todas las visualizaciones para un reporte completo.

        Args:
            session_data: Datos de la sesión con keywords, topics, pages, etc.
            output_dir: Directorio de salida (opcional)

        Returns:
            Diccionario con paths de archivos generados
        """
        if output_dir:
            self.output_dir = Path(output_dir)
            self.output_dir.mkdir(parents=True, exist_ok=True)

        generated_files = {}

        # 1. Keyword cloud
        if session_data.get('keywords'):
            path = str(self.output_dir / 'keyword_cloud.png')
            if self.generate_keyword_cloud(session_data['keywords'], path):
                generated_files['keyword_cloud'] = path

        # 2. Opportunity scatter
        if session_data.get('keywords_with_metrics'):
            path = str(self.output_dir / 'opportunity_scatter.png')
            if self.generate_opportunity_scatter(session_data['keywords_with_metrics'], path):
                generated_files['opportunity_scatter'] = path

        # 3. Topic distribution
        if session_data.get('topics'):
            path = str(self.output_dir / 'topic_distribution.png')
            if self.generate_topic_distribution(session_data['topics'], path):
                generated_files['topic_distribution'] = path

        # 4. Quality distribution
        if session_data.get('pages_with_quality'):
            path = str(self.output_dir / 'quality_distribution.png')
            if self.generate_quality_distribution(session_data['pages_with_quality'], path):
                generated_files['quality_distribution'] = path

        # 5. Density heatmap
        if session_data.get('top_keywords'):
            path = str(self.output_dir / 'density_heatmap.png')
            if self.generate_density_heatmap(session_data['top_keywords'], path):
                generated_files['density_heatmap'] = path

        # 6. Readability chart
        if session_data.get('pages_with_quality'):
            path = str(self.output_dir / 'readability_chart.png')
            if self.generate_readability_chart(session_data['pages_with_quality'], path):
                generated_files['readability_chart'] = path

        logger.info(f"Generadas {len(generated_files)} visualizaciones")
        return generated_files
