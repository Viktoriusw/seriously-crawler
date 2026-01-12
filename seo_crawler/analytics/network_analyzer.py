"""
Analizador de redes de enlaces (Network Graph Analysis).

Este módulo analiza la estructura de enlaces internos/externos:
- Network graph de enlaces internos
- PageRank interno
- Análisis de hubs y authorities (HITS)
- Detección de enlaces rotos
- Identificación de páginas huérfanas
- Profundidad de crawling visualization
- Link clusters
- Visualización interactiva con NetworkX y Plotly
"""

import logging
from typing import List, Dict, Any, Set, Tuple, Optional
from collections import defaultdict, Counter
import statistics

try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False

try:
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

logger = logging.getLogger(__name__)


class NetworkAnalyzer:
    """
    Analizador de grafos de red de enlaces.
    """

    def __init__(self):
        """Inicializa el analizador de red."""
        self.graph = None

    # ==================== GRAPH CONSTRUCTION ====================

    def build_link_graph(
        self,
        pages: List[Dict[str, Any]],
        links: List[Dict[str, Any]]
    ) -> Optional[nx.DiGraph]:
        """
        Construye grafo dirigido de enlaces internos.

        Args:
            pages: Lista de páginas con page_id y url
            links: Lista de enlaces con source_page_id, target_url, is_internal

        Returns:
            DiGraph de NetworkX o None si no está disponible
        """
        if not NETWORKX_AVAILABLE:
            logger.warning("NetworkX no disponible")
            return None

        try:
            # Crear grafo dirigido
            G = nx.DiGraph()

            # Crear mapeo de URL -> page_id
            url_to_id = {p['url']: p['page_id'] for p in pages}
            id_to_url = {p['page_id']: p['url'] for p in pages}

            # Añadir nodos (páginas)
            for page in pages:
                G.add_node(
                    page['page_id'],
                    url=page['url'],
                    title=page.get('title', ''),
                    word_count=page.get('word_count', 0),
                    depth=page.get('depth', 0)
                )

            # Añadir aristas (enlaces internos)
            for link in links:
                if not link.get('is_internal', False):
                    continue  # Solo enlaces internos

                source_id = link.get('source_page_id')
                target_url = link.get('target_url')

                # Verificar si el target existe en nuestras páginas
                target_id = url_to_id.get(target_url)

                if source_id and target_id:
                    G.add_edge(
                        source_id,
                        target_id,
                        anchor_text=link.get('anchor_text', ''),
                        nofollow=link.get('nofollow', False)
                    )

            self.graph = G
            logger.info(f"Grafo construido: {G.number_of_nodes()} nodos, {G.number_of_edges()} aristas")
            return G

        except Exception as e:
            logger.error(f"Error construyendo grafo: {e}")
            return None

    # ==================== PAGERANK ====================

    def calculate_internal_pagerank(
        self,
        damping: float = 0.85,
        max_iter: int = 100
    ) -> Dict[int, float]:
        """
        Calcula PageRank interno de las páginas.

        Args:
            damping: Factor de amortiguación (default: 0.85)
            max_iter: Iteraciones máximas

        Returns:
            Diccionario {page_id: pagerank_score}
        """
        if not self.graph or not NETWORKX_AVAILABLE:
            logger.warning("Grafo no disponible")
            return {}

        try:
            pagerank = nx.pagerank(self.graph, alpha=damping, max_iter=max_iter)
            return pagerank

        except Exception as e:
            logger.error(f"Error calculando PageRank: {e}")
            return {}

    # ==================== HITS (HUBS AND AUTHORITIES) ====================

    def calculate_hits(self, max_iter: int = 100) -> Tuple[Dict[int, float], Dict[int, float]]:
        """
        Calcula HITS (Hyperlink-Induced Topic Search).

        Returns:
            Tupla (hubs, authorities)
        """
        if not self.graph or not NETWORKX_AVAILABLE:
            logger.warning("Grafo no disponible")
            return ({}, {})

        try:
            hubs, authorities = nx.hits(self.graph, max_iter=max_iter)
            return (hubs, authorities)

        except Exception as e:
            logger.error(f"Error calculando HITS: {e}")
            return ({}, {})

    # ==================== CENTRALITY METRICS ====================

    def calculate_centralities(self) -> Dict[str, Dict[int, float]]:
        """
        Calcula múltiples métricas de centralidad.

        Returns:
            Diccionario con degree, betweenness, closeness, eigenvector
        """
        if not self.graph or not NETWORKX_AVAILABLE:
            logger.warning("Grafo no disponible")
            return {}

        try:
            centralities = {}

            # Degree centrality (in-degree para enlaces entrantes)
            centralities['in_degree'] = dict(self.graph.in_degree())
            centralities['out_degree'] = dict(self.graph.out_degree())

            # Betweenness centrality (páginas que conectan otras)
            centralities['betweenness'] = nx.betweenness_centrality(self.graph)

            # Closeness centrality (cercanía promedio)
            try:
                centralities['closeness'] = nx.closeness_centrality(self.graph)
            except:
                centralities['closeness'] = {}

            # Eigenvector centrality (conectado a páginas importantes)
            try:
                centralities['eigenvector'] = nx.eigenvector_centrality(self.graph, max_iter=100)
            except:
                centralities['eigenvector'] = {}

            return centralities

        except Exception as e:
            logger.error(f"Error calculando centralidades: {e}")
            return {}

    # ==================== ORPHAN PAGES ====================

    def find_orphan_pages(self) -> List[int]:
        """
        Encuentra páginas huérfanas (sin enlaces entrantes).

        Returns:
            Lista de page_ids sin enlaces entrantes
        """
        if not self.graph or not NETWORKX_AVAILABLE:
            logger.warning("Grafo no disponible")
            return []

        try:
            orphans = []
            for node in self.graph.nodes():
                if self.graph.in_degree(node) == 0:
                    orphans.append(node)

            return orphans

        except Exception as e:
            logger.error(f"Error encontrando páginas huérfanas: {e}")
            return []

    # ==================== BROKEN LINKS ====================

    def identify_broken_link_patterns(
        self,
        links: List[Dict[str, Any]],
        pages: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Identifica patrones de enlaces rotos.

        Args:
            links: Lista de enlaces
            pages: Lista de páginas

        Returns:
            Lista de enlaces rotos con información
        """
        try:
            # Crear set de URLs válidas
            valid_urls = set(p['url'] for p in pages)

            broken_links = []

            for link in links:
                if not link.get('is_internal', False):
                    continue

                target_url = link.get('target_url')
                source_page_id = link.get('source_page_id')

                # Si es interno pero no está en nuestras páginas, podría ser roto
                if target_url not in valid_urls:
                    # Encontrar página source
                    source_page = next((p for p in pages if p['page_id'] == source_page_id), None)

                    broken_links.append({
                        'source_url': source_page['url'] if source_page else 'Unknown',
                        'target_url': target_url,
                        'anchor_text': link.get('anchor_text', ''),
                        'type': 'missing_internal'
                    })

            return broken_links

        except Exception as e:
            logger.error(f"Error identificando enlaces rotos: {e}")
            return []

    # ==================== LINK CLUSTERS ====================

    def detect_link_clusters(self) -> List[Set[int]]:
        """
        Detecta clusters de páginas fuertemente conectadas.

        Returns:
            Lista de sets de page_ids en cada cluster
        """
        if not self.graph or not NETWORKX_AVAILABLE:
            logger.warning("Grafo no disponible")
            return []

        try:
            # Usar componentes fuertemente conectados
            clusters = list(nx.strongly_connected_components(self.graph))

            # Filtrar clusters de 1 elemento
            clusters = [c for c in clusters if len(c) > 1]

            # Ordenar por tamaño
            clusters.sort(key=len, reverse=True)

            return clusters

        except Exception as e:
            logger.error(f"Error detectando clusters: {e}")
            return []

    # ==================== DEPTH ANALYSIS ====================

    def analyze_depth_distribution(self) -> Dict[int, int]:
        """
        Analiza la distribución de profundidad de crawling.

        Returns:
            Diccionario {depth: count}
        """
        if not self.graph or not NETWORKX_AVAILABLE:
            logger.warning("Grafo no disponible")
            return {}

        try:
            depth_counts = Counter()

            for node in self.graph.nodes():
                depth = self.graph.nodes[node].get('depth', 0)
                depth_counts[depth] += 1

            return dict(depth_counts)

        except Exception as e:
            logger.error(f"Error analizando profundidad: {e}")
            return {}

    # ==================== VISUALIZATION ====================

    def generate_network_visualization(
        self,
        output_path: str,
        layout: str = 'spring',
        top_n: int = 100,
        color_by: str = 'pagerank'
    ) -> bool:
        """
        Genera visualización interactiva del grafo con Plotly.

        Args:
            output_path: Ruta del archivo HTML de salida
            layout: Tipo de layout ('spring', 'circular', 'kamada_kawai')
            top_n: Número de nodos top a incluir
            color_by: Métrica para colorear ('pagerank', 'in_degree', 'betweenness')

        Returns:
            True si se generó correctamente
        """
        if not self.graph or not NETWORKX_AVAILABLE or not PLOTLY_AVAILABLE:
            logger.warning("Grafo, NetworkX o Plotly no disponible")
            return False

        try:
            # Si hay demasiados nodos, tomar top N por PageRank
            if self.graph.number_of_nodes() > top_n:
                pagerank = self.calculate_internal_pagerank()
                top_nodes = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:top_n]
                top_node_ids = [node_id for node_id, _ in top_nodes]
                subgraph = self.graph.subgraph(top_node_ids)
            else:
                subgraph = self.graph

            # Calcular layout
            if layout == 'spring':
                pos = nx.spring_layout(subgraph, k=0.5, iterations=50)
            elif layout == 'circular':
                pos = nx.circular_layout(subgraph)
            elif layout == 'kamada_kawai':
                pos = nx.kamada_kawai_layout(subgraph)
            else:
                pos = nx.spring_layout(subgraph)

            # Calcular métrica de color
            if color_by == 'pagerank':
                pagerank = self.calculate_internal_pagerank()
                node_colors = [pagerank.get(node, 0) for node in subgraph.nodes()]
                colorbar_title = 'PageRank'
            elif color_by == 'in_degree':
                node_colors = [subgraph.in_degree(node) for node in subgraph.nodes()]
                colorbar_title = 'In-Degree'
            elif color_by == 'betweenness':
                betweenness = nx.betweenness_centrality(subgraph)
                node_colors = [betweenness.get(node, 0) for node in subgraph.nodes()]
                colorbar_title = 'Betweenness'
            else:
                node_colors = [1] * subgraph.number_of_nodes()
                colorbar_title = 'Nodes'

            # Crear traces de aristas
            edge_trace = go.Scatter(
                x=[],
                y=[],
                line=dict(width=0.5, color='#888'),
                hoverinfo='none',
                mode='lines'
            )

            for edge in subgraph.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                edge_trace['x'] += tuple([x0, x1, None])
                edge_trace['y'] += tuple([y0, y1, None])

            # Crear trace de nodos
            node_trace = go.Scatter(
                x=[],
                y=[],
                text=[],
                mode='markers',
                hoverinfo='text',
                marker=dict(
                    showscale=True,
                    colorscale='Viridis',
                    reversescale=False,
                    color=node_colors,
                    size=10,
                    colorbar=dict(
                        thickness=15,
                        title=colorbar_title,
                        xanchor='left',
                        titleside='right'
                    ),
                    line_width=2
                )
            )

            for node in subgraph.nodes():
                x, y = pos[node]
                node_trace['x'] += tuple([x])
                node_trace['y'] += tuple([y])

                # Hover text
                url = subgraph.nodes[node].get('url', '')[:50]
                title = subgraph.nodes[node].get('title', '')[:50]
                in_deg = subgraph.in_degree(node)
                out_deg = subgraph.out_degree(node)

                hover_text = f"<b>{title}</b><br>{url}<br>In: {in_deg} | Out: {out_deg}"
                node_trace['text'] += tuple([hover_text])

            # Crear figura
            fig = go.Figure(
                data=[edge_trace, node_trace],
                layout=go.Layout(
                    title='Internal Link Network Graph',
                    titlefont_size=16,
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20, l=5, r=5, t=40),
                    annotations=[dict(
                        text=f"Network of {subgraph.number_of_nodes()} pages, {subgraph.number_of_edges()} links",
                        showarrow=False,
                        xref="paper", yref="paper",
                        x=0.005, y=-0.002
                    )],
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    height=800
                )
            )

            fig.write_html(output_path)
            logger.info(f"Network visualization generada: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error generando visualización de red: {e}")
            return False

    # ==================== COMPREHENSIVE ANALYSIS ====================

    def analyze_network(
        self,
        pages: List[Dict[str, Any]],
        links: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Realiza análisis completo de la red de enlaces.

        Args:
            pages: Lista de páginas
            links: Lista de enlaces

        Returns:
            Diccionario con resultados del análisis
        """
        if not NETWORKX_AVAILABLE:
            logger.warning("NetworkX no disponible")
            return {}

        try:
            # Construir grafo
            graph = self.build_link_graph(pages, links)
            if not graph:
                return {}

            # Análisis básico
            num_nodes = graph.number_of_nodes()
            num_edges = graph.number_of_edges()
            density = nx.density(graph)

            # PageRank
            pagerank = self.calculate_internal_pagerank()
            top_pagerank = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:10]

            # HITS
            hubs, authorities = self.calculate_hits()
            top_hubs = sorted(hubs.items(), key=lambda x: x[1], reverse=True)[:10]
            top_authorities = sorted(authorities.items(), key=lambda x: x[1], reverse=True)[:10]

            # Centralidades
            centralities = self.calculate_centralities()

            # Páginas huérfanas
            orphans = self.find_orphan_pages()

            # Enlaces rotos
            broken_links = self.identify_broken_link_patterns(links, pages)

            # Clusters
            clusters = self.detect_link_clusters()

            # Profundidad
            depth_distribution = self.analyze_depth_distribution()

            # Compilar resultados
            results = {
                'graph_stats': {
                    'nodes': num_nodes,
                    'edges': num_edges,
                    'density': density,
                    'avg_degree': num_edges / num_nodes if num_nodes > 0 else 0
                },
                'top_pagerank': top_pagerank,
                'top_hubs': top_hubs,
                'top_authorities': top_authorities,
                'centralities': {
                    'avg_in_degree': statistics.mean(centralities.get('in_degree', {}).values()) if centralities.get('in_degree') else 0,
                    'avg_out_degree': statistics.mean(centralities.get('out_degree', {}).values()) if centralities.get('out_degree') else 0
                },
                'orphan_pages': orphans,
                'orphan_count': len(orphans),
                'broken_links': broken_links,
                'broken_links_count': len(broken_links),
                'link_clusters': [list(cluster) for cluster in clusters],
                'cluster_count': len(clusters),
                'depth_distribution': depth_distribution
            }

            return results

        except Exception as e:
            logger.error(f"Error en análisis de red: {e}")
            return {}
