"""
Interfaz gráfica principal del SEO Crawler usando Tkinter.

Esta es una interfaz profesional diseñada para especialistas en SEO
que necesitan analizar keywords y crawlear sitios web de forma visual.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import asyncio
import threading
from typing import Optional
from pathlib import Path
import sys

# Añadir path para imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

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
from seo_crawler.analytics.technical_seo_auditor import TechnicalSEOAuditor
from seo_crawler.analytics.schema_analyzer import SchemaAnalyzer
from seo_crawler.analytics.recommendations_engine import RecommendationsEngine


class SEOCrawlerGUI:
    """Interfaz gráfica principal del SEO Crawler."""

    def __init__(self, root):
        """
        Inicializa la interfaz gráfica.

        Args:
            root: Ventana raíz de Tkinter
        """
        self.root = root
        self.root.title("SEO Crawler Professional - Keyword Analysis Tool")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 700)

        # Variables
        self.crawler: Optional[SEOCrawler] = None
        self.db: Optional[Database] = None
        self.current_session_id: Optional[int] = None
        self.crawler_thread: Optional[threading.Thread] = None
        self.is_crawling = False

        # Configurar estilo
        self.setup_style()

        # Crear interfaz
        self.create_widgets()

        # Inicializar base de datos
        self.init_database()

        # Protocolo de cierre
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_style(self):
        """Configura el estilo visual de la aplicación."""
        style = ttk.Style()
        style.theme_use('clam')

        # Colores profesionales
        bg_color = '#f0f0f0'
        fg_color = '#2c3e50'
        accent_color = '#3498db'
        success_color = '#27ae60'
        danger_color = '#e74c3c'

        # Configurar estilos
        style.configure('Title.TLabel',
                       font=('Helvetica', 24, 'bold'),
                       foreground=fg_color,
                       background=bg_color)

        style.configure('Subtitle.TLabel',
                       font=('Helvetica', 14, 'bold'),
                       foreground=fg_color,
                       background=bg_color)

        style.configure('Info.TLabel',
                       font=('Helvetica', 10),
                       foreground='#7f8c8d',
                       background=bg_color)

        style.configure('Accent.TButton',
                       font=('Helvetica', 11, 'bold'),
                       background=accent_color,
                       foreground='white')

        style.configure('Success.TButton',
                       background=success_color)

        style.configure('Danger.TButton',
                       background=danger_color)

        self.root.configure(bg=bg_color)

    def create_widgets(self):
        """Crea todos los widgets de la interfaz."""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Header
        self.create_header(main_frame)

        # Notebook (pestañas)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)

        # Crear pestañas
        self.create_crawler_tab()
        self.create_sessions_tab()
        self.create_analysis_tab()
        self.create_export_tab()
        # Pestañas profesionales
        self.create_keywords_pro_tab()
        self.create_content_quality_tab()
        self.create_technical_audit_tab()
        self.create_visualizations_tab()

    def create_header(self, parent):
        """Crea el encabezado de la aplicación."""
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        # Título
        title = ttk.Label(header_frame,
                         text="SEO Crawler Professional",
                         style='Title.TLabel')
        title.grid(row=0, column=0, sticky=tk.W)

        subtitle = ttk.Label(header_frame,
                            text="Advanced Keyword Analysis & SEO Research Tool",
                            style='Info.TLabel')
        subtitle.grid(row=1, column=0, sticky=tk.W)

    def create_crawler_tab(self):
        """Crea la pestaña de crawling."""
        crawler_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(crawler_frame, text="🚀 Nuevo Crawl")

        # Configuración del crawl
        config_frame = ttk.LabelFrame(crawler_frame, text="Configuración del Crawl", padding="15")
        config_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), pady=(0, 10))
        crawler_frame.columnconfigure(0, weight=1)

        # URL
        ttk.Label(config_frame, text="URL inicial:", font=('Helvetica', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.url_entry = ttk.Entry(config_frame, width=60, font=('Helvetica', 10))
        self.url_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=10, pady=5)
        self.url_entry.insert(0, "https://ejemplo.com")

        # Max páginas
        ttk.Label(config_frame, text="Máximo de páginas:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.max_pages_var = tk.IntVar(value=100)
        ttk.Spinbox(config_frame, from_=1, to=10000, textvariable=self.max_pages_var, width=20).grid(row=1, column=1, sticky=tk.W, padx=10, pady=5)

        # Profundidad
        ttk.Label(config_frame, text="Profundidad máxima:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.max_depth_var = tk.IntVar(value=3)
        ttk.Spinbox(config_frame, from_=1, to=10, textvariable=self.max_depth_var, width=20).grid(row=2, column=1, sticky=tk.W, padx=10, pady=5)

        # Requests concurrentes
        ttk.Label(config_frame, text="Requests concurrentes:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.concurrent_var = tk.IntVar(value=10)
        ttk.Spinbox(config_frame, from_=1, to=50, textvariable=self.concurrent_var, width=20).grid(row=3, column=1, sticky=tk.W, padx=10, pady=5)

        # Delay
        ttk.Label(config_frame, text="Delay entre requests (seg):").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.delay_var = tk.DoubleVar(value=1.0)
        ttk.Spinbox(config_frame, from_=0.1, to=10.0, increment=0.1, textvariable=self.delay_var, width=20).grid(row=4, column=1, sticky=tk.W, padx=10, pady=5)

        # Opciones
        self.respect_robots_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(config_frame, text="Respetar robots.txt", variable=self.respect_robots_var).grid(row=5, column=1, sticky=tk.W, padx=10, pady=5)

        self.follow_external_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(config_frame, text="Seguir enlaces externos", variable=self.follow_external_var).grid(row=6, column=1, sticky=tk.W, padx=10, pady=5)

        config_frame.columnconfigure(1, weight=1)

        # Botones de control
        control_frame = ttk.Frame(crawler_frame)
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=10)

        self.start_btn = ttk.Button(control_frame,
                                    text="▶ Iniciar Crawl",
                                    style='Accent.TButton',
                                    command=self.start_crawl,
                                    width=20)
        self.start_btn.grid(row=0, column=0, padx=5)

        self.stop_btn = ttk.Button(control_frame,
                                   text="⬛ Detener",
                                   style='Danger.TButton',
                                   command=self.stop_crawl,
                                   state='disabled',
                                   width=20)
        self.stop_btn.grid(row=0, column=1, padx=5)

        # Progreso
        progress_frame = ttk.LabelFrame(crawler_frame, text="Progreso del Crawl", padding="15")
        progress_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        crawler_frame.rowconfigure(2, weight=1)

        # Barra de progreso
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        progress_frame.columnconfigure(0, weight=1)

        # Estadísticas en tiempo real
        stats_frame = ttk.Frame(progress_frame)
        stats_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=10)

        self.pages_label = ttk.Label(stats_frame, text="Páginas: 0", font=('Helvetica', 10))
        self.pages_label.grid(row=0, column=0, padx=10)

        self.keywords_label = ttk.Label(stats_frame, text="Keywords: 0", font=('Helvetica', 10))
        self.keywords_label.grid(row=0, column=1, padx=10)

        self.links_label = ttk.Label(stats_frame, text="Enlaces: 0", font=('Helvetica', 10))
        self.links_label.grid(row=0, column=2, padx=10)

        self.speed_label = ttk.Label(stats_frame, text="Velocidad: 0 pág/s", font=('Helvetica', 10))
        self.speed_label.grid(row=0, column=3, padx=10)

        # Log
        ttk.Label(progress_frame, text="Log:", font=('Helvetica', 10, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=(10, 5))
        self.log_text = scrolledtext.ScrolledText(progress_frame, height=15, width=80, font=('Courier', 9))
        self.log_text.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        progress_frame.rowconfigure(3, weight=1)

    def create_sessions_tab(self):
        """Crea la pestaña de sesiones."""
        sessions_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(sessions_frame, text="📋 Sesiones")

        # Botones
        btn_frame = ttk.Frame(sessions_frame)
        btn_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Button(btn_frame,
                  text="🔄 Actualizar",
                  command=self.refresh_sessions,
                  width=15).grid(row=0, column=0, padx=5)

        ttk.Button(btn_frame,
                  text="📊 Ver Análisis",
                  command=self.view_session_analysis,
                  width=15).grid(row=0, column=1, padx=5)

        # Treeview para sesiones
        columns = ('ID', 'Dominio', 'Páginas', 'Keywords', 'Fecha', 'Estado')
        self.sessions_tree = ttk.Treeview(sessions_frame, columns=columns, show='tree headings', height=20)

        for col in columns:
            self.sessions_tree.heading(col, text=col)
            width = 100 if col != 'Dominio' else 300
            self.sessions_tree.column(col, width=width)

        self.sessions_tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        sessions_frame.columnconfigure(0, weight=1)
        sessions_frame.rowconfigure(1, weight=1)

        # Scrollbar
        scrollbar = ttk.Scrollbar(sessions_frame, orient=tk.VERTICAL, command=self.sessions_tree.yview)
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.sessions_tree.configure(yscrollcommand=scrollbar.set)

    def create_analysis_tab(self):
        """Crea la pestaña de análisis."""
        analysis_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(analysis_frame, text="📈 Análisis")

        # Selección de sesión
        select_frame = ttk.Frame(analysis_frame)
        select_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))

        ttk.Label(select_frame, text="Sesión:", font=('Helvetica', 10, 'bold')).grid(row=0, column=0, padx=5)
        self.analysis_session_var = tk.StringVar()
        self.analysis_session_combo = ttk.Combobox(select_frame, textvariable=self.analysis_session_var, width=30, state='readonly')
        self.analysis_session_combo.grid(row=0, column=1, padx=5)

        ttk.Button(select_frame,
                  text="Cargar Keywords",
                  command=self.load_keywords,
                  width=15).grid(row=0, column=2, padx=5)

        # Keywords treeview
        columns = ('Keyword', 'Frecuencia', 'Densidad', 'TF-IDF', 'Páginas')
        self.keywords_tree = ttk.Treeview(analysis_frame, columns=columns, show='tree headings', height=25)

        for col in columns:
            self.keywords_tree.heading(col, text=col)
            width = 400 if col == 'Keyword' else 100
            self.keywords_tree.column(col, width=width)

        self.keywords_tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        analysis_frame.columnconfigure(0, weight=1)
        analysis_frame.rowconfigure(1, weight=1)

        # Scrollbar
        scrollbar = ttk.Scrollbar(analysis_frame, orient=tk.VERTICAL, command=self.keywords_tree.yview)
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.keywords_tree.configure(yscrollcommand=scrollbar.set)

    def create_export_tab(self):
        """Crea la pestaña de exportación."""
        export_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(export_frame, text="💾 Exportar")

        # Selección de sesión
        select_frame = ttk.LabelFrame(export_frame, text="Seleccionar Sesión", padding="15")
        select_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))

        ttk.Label(select_frame, text="Sesión:").grid(row=0, column=0, padx=5, sticky=tk.W)
        self.export_session_var = tk.StringVar()
        self.export_session_combo = ttk.Combobox(select_frame, textvariable=self.export_session_var, width=40, state='readonly')
        self.export_session_combo.grid(row=0, column=1, padx=5)
        select_frame.columnconfigure(1, weight=1)

        # Opciones de exportación
        options_frame = ttk.LabelFrame(export_frame, text="Formato de Exportación", padding="15")
        options_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))

        self.export_format_var = tk.StringVar(value='html')

        ttk.Radiobutton(options_frame, text="HTML Report (Reporte completo con gráficos)", variable=self.export_format_var, value='html').grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Radiobutton(options_frame, text="Excel (.xlsx) - Múltiples hojas", variable=self.export_format_var, value='excel').grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Radiobutton(options_frame, text="CSV - Keywords", variable=self.export_format_var, value='csv').grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Radiobutton(options_frame, text="JSON - Datos completos", variable=self.export_format_var, value='json').grid(row=3, column=0, sticky=tk.W, pady=5)

        # Botón de exportación
        export_btn_frame = ttk.Frame(export_frame)
        export_btn_frame.grid(row=2, column=0, pady=10)

        ttk.Button(export_btn_frame,
                  text="📥 Exportar Reporte",
                  command=self.export_report,
                  style='Success.TButton',
                  width=25).pack()

        # Información
        info_text = """
        Formatos disponibles:

        • HTML: Reporte visual completo con estadísticas y top keywords
        • Excel: Datos estructurados en múltiples hojas (sesión, páginas, keywords)
        • CSV: Lista de keywords con todas sus métricas
        • JSON: Exportación completa de todos los datos
        """

        info_label = ttk.Label(export_frame, text=info_text, justify=tk.LEFT, font=('Helvetica', 9))
        info_label.grid(row=3, column=0, sticky=tk.W, pady=10)

    def init_database(self):
        """Inicializa la conexión a la base de datos."""
        try:
            config = Config()
            db_path = config.get('database_path')
            self.log(f"Conectando a base de datos: {db_path}")

            # Cargar sesiones al iniciar
            self.root.after(100, self.refresh_sessions)
            self.root.after(100, self.load_session_lists)

        except Exception as e:
            messagebox.showerror("Error", f"Error al inicializar base de datos: {str(e)}")

    def log(self, message: str):
        """Añade un mensaje al log."""
        if hasattr(self, 'log_text'):
            self.log_text.insert(tk.END, f"{message}\n")
            self.log_text.see(tk.END)

    def start_crawl(self):
        """Inicia el proceso de crawling."""
        url = self.url_entry.get().strip()

        if not url:
            messagebox.showwarning("Advertencia", "Por favor, ingresa una URL")
            return

        if not url.startswith(('http://', 'https://')):
            messagebox.showwarning("Advertencia", "La URL debe comenzar con http:// o https://")
            return

        # Deshabilitar botón de inicio
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.progress_bar.start()

        # Limpiar log
        self.log_text.delete(1.0, tk.END)

        self.log("="*60)
        self.log("INICIANDO CRAWLER")
        self.log("="*60)
        self.log(f"URL: {url}")
        self.log(f"Máximo de páginas: {self.max_pages_var.get()}")
        self.log(f"Profundidad: {self.max_depth_var.get()}")
        self.log("="*60 + "\n")

        # Ejecutar crawl en thread separado
        self.is_crawling = True
        self.crawler_thread = threading.Thread(target=self.run_crawler_thread, args=(url,))
        self.crawler_thread.daemon = True
        self.crawler_thread.start()

        # Actualizar estadísticas periódicamente
        self.update_stats()

    def run_crawler_thread(self, url: str):
        """Ejecuta el crawler en un thread separado."""
        loop = None
        try:
            # Crear nuevo event loop para este thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # Ejecutar crawler
            loop.run_until_complete(self.run_crawler_async(url))

        except Exception as e:
            self.log(f"\n❌ Error: {str(e)}")
            self.root.after(0, lambda: messagebox.showerror("Error", f"Error durante el crawling: {str(e)}"))
        finally:
            # Limpiar crawler
            if self.crawler:
                try:
                    if loop and not loop.is_closed():
                        loop.run_until_complete(self.crawler.cleanup())
                except Exception as e:
                    print(f"Error durante cleanup: {e}")
                finally:
                    self.crawler = None

            # Cerrar event loop
            if loop and not loop.is_closed():
                try:
                    # Cancelar tareas pendientes
                    pending = asyncio.all_tasks(loop)
                    for task in pending:
                        task.cancel()

                    # Esperar a que terminen las tareas canceladas
                    if pending:
                        loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))

                    loop.close()
                except Exception as e:
                    print(f"Error al cerrar loop: {e}")

            self.is_crawling = False
            self.root.after(0, self.crawl_finished)

    async def run_crawler_async(self, url: str):
        """Ejecuta el crawler de forma asíncrona."""
        # Configuración
        custom_config = {
            'max_pages': self.max_pages_var.get(),
            'max_depth': self.max_depth_var.get(),
            'concurrent_requests': self.concurrent_var.get(),
            'crawl_delay': self.delay_var.get(),
            'respect_robots': self.respect_robots_var.get(),
            'follow_external_links': self.follow_external_var.get(),
        }

        config = Config(custom_config)
        self.crawler = SEOCrawler(config)

        # Inicializar
        await self.crawler.initialize([url])
        self.current_session_id = self.crawler.session_id

        # Iniciar crawl
        stats = await self.crawler.start(max_pages=self.max_pages_var.get())

        # Mostrar resultados
        self.root.after(0, lambda: self.show_results(stats))

    def update_stats(self):
        """Actualiza las estadísticas en tiempo real."""
        if self.is_crawling and self.crawler:
            try:
                # Crear un nuevo event loop para obtener stats
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                stats = loop.run_until_complete(self.crawler.get_progress())
                loop.close()

                # Actualizar labels
                self.pages_label.config(text=f"Páginas: {stats.get('pages_crawled', 0)}")
                self.keywords_label.config(text=f"Keywords: {stats.get('total_keywords', 0)}")
                self.links_label.config(text=f"Enlaces: {stats.get('total_links', 0)}")
                self.speed_label.config(text=f"Velocidad: {stats.get('pages_per_second', 0):.2f} pág/s")

            except Exception:
                pass

            # Continuar actualizando
            self.root.after(1000, self.update_stats)

    def stop_crawl(self):
        """Detiene el crawling."""
        if self.crawler:
            self.crawler.stop()
            self.log("\n⚠️  Deteniendo crawler...")

    def crawl_finished(self):
        """Callback cuando el crawl termina."""
        self.progress_bar.stop()
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.log("\n✅ Crawl finalizado")

        # Actualizar lista de sesiones
        self.refresh_sessions()
        self.load_session_lists()

    def show_results(self, stats: dict):
        """Muestra los resultados finales del crawl."""
        self.log("\n" + "="*60)
        self.log("RESULTADOS DEL CRAWL")
        self.log("="*60)
        self.log(f"Session ID: {stats.get('session_id')}")
        self.log(f"Páginas crawleadas: {stats.get('pages_crawled', 0)}")
        self.log(f"Páginas fallidas: {stats.get('pages_failed', 0)}")
        self.log(f"Keywords extraídas: {stats.get('total_keywords', 0)}")
        self.log(f"Enlaces encontrados: {stats.get('total_links', 0)}")
        self.log(f"Tiempo total: {stats.get('elapsed_time', 0):.2f}s")
        self.log("="*60)

        messagebox.showinfo("Crawl Completado",
                          f"Crawl finalizado exitosamente!\n\n"
                          f"Páginas: {stats.get('pages_crawled', 0)}\n"
                          f"Keywords: {stats.get('total_keywords', 0)}\n"
                          f"Session ID: {stats.get('session_id')}")

    def refresh_sessions(self):
        """Actualiza la lista de sesiones."""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            config = Config()
            db = Database(config.get('database_path'))
            loop.run_until_complete(db.connect())

            sessions = loop.run_until_complete(db.get_all_sessions())

            # Limpiar treeview
            for item in self.sessions_tree.get_children():
                self.sessions_tree.delete(item)

            # Añadir sesiones
            for session in sessions:
                values = (
                    session['session_id'],
                    session['domains'],
                    session.get('pages_crawled', 0),
                    session.get('total_keywords', 0),
                    session['start_time'][:19] if session['start_time'] else '',
                    session.get('status', 'completed')
                )
                self.sessions_tree.insert('', tk.END, values=values)

            loop.run_until_complete(db.close())
            loop.close()

        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar sesiones: {str(e)}")

    def load_session_lists(self):
        """Carga las listas de sesiones en los comboboxes."""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            config = Config()
            db = Database(config.get('database_path'))
            loop.run_until_complete(db.connect())

            sessions = loop.run_until_complete(db.get_all_sessions())

            session_list = [f"{s['session_id']} - {s['domains']}" for s in sessions]

            if hasattr(self, 'analysis_session_combo'):
                self.analysis_session_combo['values'] = session_list

            if hasattr(self, 'export_session_combo'):
                self.export_session_combo['values'] = session_list

            loop.run_until_complete(db.close())
            loop.close()

        except Exception as e:
            print(f"Error al cargar listas de sesiones: {str(e)}")

    def view_session_analysis(self):
        """Muestra el análisis de la sesión seleccionada."""
        selection = self.sessions_tree.selection()

        if not selection:
            messagebox.showwarning("Advertencia", "Por favor, selecciona una sesión")
            return

        item = self.sessions_tree.item(selection[0])
        session_id = item['values'][0]

        # Cambiar a pestaña de análisis y cargar datos
        self.notebook.select(2)  # Tab de análisis
        self.analysis_session_var.set(f"{session_id} - {item['values'][1]}")
        self.load_keywords()

    def load_keywords(self):
        """Carga las keywords de la sesión seleccionada."""
        session_text = self.analysis_session_var.get()

        if not session_text:
            messagebox.showwarning("Advertencia", "Por favor, selecciona una sesión")
            return

        session_id = int(session_text.split(' - ')[0])

        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            config = Config()
            db = Database(config.get('database_path'))
            loop.run_until_complete(db.connect())

            keywords = loop.run_until_complete(db.get_top_keywords_by_session(session_id, 500))

            # Limpiar treeview
            for item in self.keywords_tree.get_children():
                self.keywords_tree.delete(item)

            # Añadir keywords
            for kw in keywords:
                values = (
                    kw['keyword'],
                    kw.get('total_frequency', 0),
                    f"{kw.get('avg_density', 0):.2f}%",
                    f"{kw.get('avg_tfidf', 0):.4f}",
                    kw.get('page_count', 0)
                )
                self.keywords_tree.insert('', tk.END, values=values)

            loop.run_until_complete(db.close())
            loop.close()

            messagebox.showinfo("Éxito", f"Se cargaron {len(keywords)} keywords")

        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar keywords: {str(e)}")

    def export_report(self):
        """Exporta el reporte de la sesión seleccionada."""
        session_text = self.export_session_var.get()

        if not session_text:
            messagebox.showwarning("Advertencia", "Por favor, selecciona una sesión")
            return

        session_id = int(session_text.split(' - ')[0])
        format_type = self.export_format_var.get()

        # Extensiones
        extensions = {
            'html': '.html',
            'excel': '.xlsx',
            'csv': '.csv',
            'json': '.json'
        }

        # Pedir ruta de guardado
        filename = filedialog.asksaveasfilename(
            defaultextension=extensions[format_type],
            filetypes=[(format_type.upper(), f"*{extensions[format_type]}")]
        )

        if not filename:
            return

        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            config = Config()
            db = Database(config.get('database_path'))
            loop.run_until_complete(db.connect())

            reporter = Reporter(db)

            if format_type == 'html':
                loop.run_until_complete(reporter.generate_html_report(session_id, filename))
            elif format_type == 'excel':
                loop.run_until_complete(reporter.export_to_excel(session_id, filename))
            elif format_type == 'csv':
                loop.run_until_complete(reporter.export_keywords_to_csv(session_id, filename))
            elif format_type == 'json':
                loop.run_until_complete(reporter.export_to_json(session_id, filename))

            loop.run_until_complete(db.close())
            loop.close()

            messagebox.showinfo("Éxito", f"Reporte exportado exitosamente:\n{filename}")

        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar: {str(e)}")

    # ==================== PESTAÑAS PROFESIONALES ====================

    def create_keywords_pro_tab(self):
        """Crea la pestaña de análisis profesional de keywords (PASO 1)."""
        keywords_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(keywords_frame, text="🎯 Keywords Pro")

        # Descripción
        desc_label = ttk.Label(keywords_frame,
                              text="Análisis profesional de keywords: Semántico, Dificultad, Competencia",
                              style='Info.TLabel')
        desc_label.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 15))

        # Session selector
        session_select_frame = ttk.LabelFrame(keywords_frame, text="Seleccionar Sesión", padding="10")
        session_select_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(session_select_frame, text="Sesión:").grid(row=0, column=0, padx=5, sticky=tk.W)
        self.keywords_pro_session_combo = ttk.Combobox(session_select_frame, width=60, state='readonly')
        self.keywords_pro_session_combo.grid(row=0, column=1, padx=5)
        self.keywords_pro_session_combo.bind('<<ComboboxSelected>>', self.on_keywords_pro_session_selected)

        ttk.Button(session_select_frame, text="🔄 Refrescar",
                  command=lambda: self.refresh_professional_sessions(self.keywords_pro_session_combo)).grid(row=0, column=2, padx=5)

        self.keywords_pro_current_label = ttk.Label(session_select_frame, text="No hay sesión seleccionada", foreground='red')
        self.keywords_pro_current_label.grid(row=0, column=3, padx=10)

        session_select_frame.columnconfigure(1, weight=1)

        # Load sessions
        self.root.after(100, lambda: self.refresh_professional_sessions(self.keywords_pro_session_combo))

        # Frame de análisis
        analysis_frame = ttk.LabelFrame(keywords_frame, text="Análisis Profesional", padding="15")
        analysis_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N), padx=(0, 10))

        # Botones de análisis
        ttk.Button(analysis_frame,
                  text="📊 Análisis Semántico (Clustering + Topics)",
                  command=self.run_semantic_analysis,
                  width=40).grid(row=0, column=0, pady=5, sticky=tk.W)

        ttk.Button(analysis_frame,
                  text="💎 Calcular Dificultad de Keywords",
                  command=self.run_keyword_difficulty,
                  width=40).grid(row=1, column=0, pady=5, sticky=tk.W)

        ttk.Button(analysis_frame,
                  text="🔍 Análisis Competitivo (Gaps + Oportunidades)",
                  command=self.run_competitive_analysis,
                  width=40).grid(row=2, column=0, pady=5, sticky=tk.W)

        # Frame de resultados
        results_frame = ttk.LabelFrame(keywords_frame, text="Resultados", padding="15")
        results_frame.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))
        keywords_frame.columnconfigure(1, weight=1)
        keywords_frame.rowconfigure(2, weight=1)

        # Área de texto para resultados
        self.keywords_pro_text = scrolledtext.ScrolledText(results_frame,
                                                           width=70,
                                                           height=25,
                                                           font=('Courier', 10))
        self.keywords_pro_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)

    def create_content_quality_tab(self):
        """Crea la pestaña de análisis de calidad de contenido (PASO 2)."""
        content_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(content_frame, text="📝 Calidad de Contenido")

        # Descripción
        desc_label = ttk.Label(content_frame,
                              text="Análisis de calidad, legibilidad, thin content y visualizaciones",
                              style='Info.TLabel')
        desc_label.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 15))

        # Session selector
        session_select_frame = ttk.LabelFrame(content_frame, text="Seleccionar Sesión", padding="10")
        session_select_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(session_select_frame, text="Sesión:").grid(row=0, column=0, padx=5, sticky=tk.W)
        self.content_quality_session_combo = ttk.Combobox(session_select_frame, width=60, state='readonly')
        self.content_quality_session_combo.grid(row=0, column=1, padx=5)
        self.content_quality_session_combo.bind('<<ComboboxSelected>>', self.on_content_quality_session_selected)

        ttk.Button(session_select_frame, text="🔄 Refrescar",
                  command=lambda: self.refresh_professional_sessions(self.content_quality_session_combo)).grid(row=0, column=2, padx=5)

        self.content_quality_current_label = ttk.Label(session_select_frame, text="No hay sesión seleccionada", foreground='red')
        self.content_quality_current_label.grid(row=0, column=3, padx=10)

        session_select_frame.columnconfigure(1, weight=1)

        # Load sessions
        self.root.after(100, lambda: self.refresh_professional_sessions(self.content_quality_session_combo))

        # Frame de análisis
        analysis_frame = ttk.LabelFrame(content_frame, text="Análisis de Contenido", padding="15")
        analysis_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N), padx=(0, 10))

        ttk.Button(analysis_frame,
                  text="📊 Analizar Calidad de Contenido",
                  command=self.run_content_quality_analysis,
                  width=40).grid(row=0, column=0, pady=5, sticky=tk.W)

        ttk.Button(analysis_frame,
                  text="📈 Generar Visualizaciones (matplotlib)",
                  command=self.generate_static_visualizations,
                  width=40).grid(row=1, column=0, pady=5, sticky=tk.W)

        # Frame de resultados
        results_frame = ttk.LabelFrame(content_frame, text="Resultados", padding="15")
        results_frame.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))
        content_frame.columnconfigure(1, weight=1)
        content_frame.rowconfigure(2, weight=1)

        self.content_quality_text = scrolledtext.ScrolledText(results_frame,
                                                             width=70,
                                                             height=25,
                                                             font=('Courier', 10))
        self.content_quality_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)

    def create_technical_audit_tab(self):
        """Crea la pestaña de auditoría técnica SEO (PASO 4)."""
        audit_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(audit_frame, text="🔍 Auditoría Técnica")

        # Descripción
        desc_label = ttk.Label(audit_frame,
                              text="Auditoría técnica completa: Meta tags, HTTP, Schema, Recomendaciones",
                              style='Info.TLabel')
        desc_label.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 15))

        # Session selector
        session_select_frame = ttk.LabelFrame(audit_frame, text="Seleccionar Sesión", padding="10")
        session_select_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(session_select_frame, text="Sesión:").grid(row=0, column=0, padx=5, sticky=tk.W)
        self.technical_audit_session_combo = ttk.Combobox(session_select_frame, width=60, state='readonly')
        self.technical_audit_session_combo.grid(row=0, column=1, padx=5)
        self.technical_audit_session_combo.bind('<<ComboboxSelected>>', self.on_technical_audit_session_selected)

        ttk.Button(session_select_frame, text="🔄 Refrescar",
                  command=lambda: self.refresh_professional_sessions(self.technical_audit_session_combo)).grid(row=0, column=2, padx=5)

        self.technical_audit_current_label = ttk.Label(session_select_frame, text="No hay sesión seleccionada", foreground='red')
        self.technical_audit_current_label.grid(row=0, column=3, padx=10)

        session_select_frame.columnconfigure(1, weight=1)

        # Load sessions
        self.root.after(100, lambda: self.refresh_professional_sessions(self.technical_audit_session_combo))

        # Frame de análisis
        analysis_frame = ttk.LabelFrame(audit_frame, text="Análisis Técnico", padding="15")
        analysis_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N), padx=(0, 10))

        ttk.Button(analysis_frame,
                  text="🔍 Auditoría Técnica SEO",
                  command=self.run_technical_audit,
                  width=40).grid(row=0, column=0, pady=5, sticky=tk.W)

        ttk.Button(analysis_frame,
                  text="🏷️  Analizar Schema Markup",
                  command=self.run_schema_analysis,
                  width=40).grid(row=1, column=0, pady=5, sticky=tk.W)

        ttk.Button(analysis_frame,
                  text="💡 Generar Recomendaciones",
                  command=self.run_recommendations,
                  width=40).grid(row=2, column=0, pady=5, sticky=tk.W)

        ttk.Button(analysis_frame,
                  text="🚀 AUDITORÍA COMPLETA",
                  command=self.run_complete_audit,
                  width=40,
                  style='Accent.TButton').grid(row=3, column=0, pady=(15, 5), sticky=tk.W)

        # Frame de resultados
        results_frame = ttk.LabelFrame(audit_frame, text="Resultados", padding="15")
        results_frame.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))
        audit_frame.columnconfigure(1, weight=1)
        audit_frame.rowconfigure(2, weight=1)

        self.technical_audit_text = scrolledtext.ScrolledText(results_frame,
                                                             width=70,
                                                             height=25,
                                                             font=('Courier', 10))
        self.technical_audit_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)

    def create_visualizations_tab(self):
        """Crea la pestaña de visualizaciones interactivas (PASO 3)."""
        viz_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(viz_frame, text="📊 Visualizaciones")

        # Descripción
        desc_label = ttk.Label(viz_frame,
                              text="Visualizaciones interactivas (Plotly) y análisis de red de enlaces",
                              style='Info.TLabel')
        desc_label.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 15))

        # Session selector
        session_select_frame = ttk.LabelFrame(viz_frame, text="Seleccionar Sesión", padding="10")
        session_select_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(session_select_frame, text="Sesión:").grid(row=0, column=0, padx=5, sticky=tk.W)
        self.visualizations_session_combo = ttk.Combobox(session_select_frame, width=60, state='readonly')
        self.visualizations_session_combo.grid(row=0, column=1, padx=5)
        self.visualizations_session_combo.bind('<<ComboboxSelected>>', self.on_visualizations_session_selected)

        ttk.Button(session_select_frame, text="🔄 Refrescar",
                  command=lambda: self.refresh_professional_sessions(self.visualizations_session_combo)).grid(row=0, column=2, padx=5)

        self.visualizations_current_label = ttk.Label(session_select_frame, text="No hay sesión seleccionada", foreground='red')
        self.visualizations_current_label.grid(row=0, column=3, padx=10)

        session_select_frame.columnconfigure(1, weight=1)

        # Load sessions
        self.root.after(100, lambda: self.refresh_professional_sessions(self.visualizations_session_combo))

        # Frame de análisis
        analysis_frame = ttk.LabelFrame(viz_frame, text="Generar Visualizaciones", padding="15")
        analysis_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N), padx=(0, 10))

        ttk.Button(analysis_frame,
                  text="🌐 Visualizaciones Interactivas (Plotly)",
                  command=self.generate_interactive_visualizations,
                  width=40).grid(row=0, column=0, pady=5, sticky=tk.W)

        ttk.Button(analysis_frame,
                  text="🕸️  Análisis de Red de Enlaces",
                  command=self.run_network_analysis,
                  width=40).grid(row=1, column=0, pady=5, sticky=tk.W)

        ttk.Button(analysis_frame,
                  text="📊 Dashboard Interactivo Completo",
                  command=self.generate_dashboard,
                  width=40,
                  style='Accent.TButton').grid(row=2, column=0, pady=(15, 5), sticky=tk.W)

        # Frame de resultados
        results_frame = ttk.LabelFrame(viz_frame, text="Resultados", padding="15")
        results_frame.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))
        viz_frame.columnconfigure(1, weight=1)
        viz_frame.rowconfigure(2, weight=1)

        self.visualizations_text = scrolledtext.ScrolledText(results_frame,
                                                            width=70,
                                                            height=25,
                                                            font=('Courier', 10))
        self.visualizations_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)

    # ==================== FUNCIONES DE ANÁLISIS PROFESIONAL ====================

    def run_semantic_analysis(self):
        """Ejecuta análisis semántico de keywords."""
        if not self.current_session_id:
            messagebox.showwarning("Advertencia", "Primero selecciona una sesión")
            return

        self.keywords_pro_text.delete(1.0, tk.END)
        self.keywords_pro_text.insert(tk.END, "Ejecutando análisis semántico...\n\n")

        def analyze():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                config = Config()
                db = Database(config.get('database_path'))
                loop.run_until_complete(db.connect())

                pages = loop.run_until_complete(db.get_pages_by_session(self.current_session_id))
                keywords = loop.run_until_complete(db.get_top_keywords_by_session(self.current_session_id, limit=1000))

                analyzer = SemanticAnalyzer()

                # Clustering
                self.keywords_pro_text.insert(tk.END, "🔄 Analizando clusters de keywords...\n")
                clusters = analyzer.cluster_keywords(keywords, n_clusters=5)
                self.keywords_pro_text.insert(tk.END, f"✅ {len(clusters)} clusters encontrados\n\n")

                # Topic modeling
                self.keywords_pro_text.insert(tk.END, "🔄 Analizando topics...\n")
                topics = analyzer.extract_topics(keywords, n_topics=5)
                self.keywords_pro_text.insert(tk.END, f"✅ {len(topics)} topics extraídos\n\n")

                # Search intent
                self.keywords_pro_text.insert(tk.END, "🔄 Clasificando search intent...\n")
                for i, kw in enumerate(keywords[:20]):
                    intent = analyzer.classify_search_intent(kw['keyword'])
                    kw['intent'] = intent
                    if i < 10:
                        self.keywords_pro_text.insert(tk.END,
                            f"  • {kw['keyword'][:40]:40} → {intent}\n")

                self.keywords_pro_text.insert(tk.END, f"\n✅ Análisis completado\n")
                self.keywords_pro_text.insert(tk.END, f"\n📊 Resumen:\n")
                self.keywords_pro_text.insert(tk.END, f"  • Total keywords: {len(keywords)}\n")
                self.keywords_pro_text.insert(tk.END, f"  • Clusters: {len(clusters)}\n")
                self.keywords_pro_text.insert(tk.END, f"  • Topics: {len(topics)}\n")

                loop.run_until_complete(db.close())
                loop.close()

            except Exception as e:
                self.keywords_pro_text.insert(tk.END, f"\n❌ Error: {str(e)}\n")

        threading.Thread(target=analyze, daemon=True).start()

    def run_keyword_difficulty(self):
        """Calcula dificultad y oportunidad de keywords."""
        if not self.current_session_id:
            messagebox.showwarning("Advertencia", "Primero selecciona una sesión")
            return

        self.keywords_pro_text.delete(1.0, tk.END)
        self.keywords_pro_text.insert(tk.END, "Calculando dificultad de keywords...\n\n")

        def analyze():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                config = Config()
                db = Database(config.get('database_path'))
                loop.run_until_complete(db.connect())

                keywords = loop.run_until_complete(db.get_top_keywords_by_session(self.current_session_id, limit=1000))
                pages = loop.run_until_complete(db.get_pages_by_session(self.current_session_id))

                analyzer = KeywordDifficultyAnalyzer()

                self.keywords_pro_text.insert(tk.END, "🔄 Calculando métricas de dificultad...\n\n")

                # Usar el método correcto que procesa todas las keywords
                results = analyzer.analyze_all_keywords(keywords, pages)

                # Filtrar quick wins
                quick_wins = [r for r in results if r['opportunity_score'] > 70 and r['difficulty_score'] < 40]

                # Agrupar por keyword text para evitar duplicados
                unique_quick_wins = {}
                for r in quick_wins:
                    kw_text = r['keyword']
                    if kw_text not in unique_quick_wins:
                        unique_quick_wins[kw_text] = r

                quick_wins_list = list(unique_quick_wins.values())

                # Mostrar top 10
                self.keywords_pro_text.insert(tk.END, "🎯 TOP 10 QUICK WINS (Alta oportunidad + Baja dificultad):\n\n")
                for i, kw in enumerate(sorted(quick_wins_list, key=lambda x: x['opportunity_score'], reverse=True)[:10], 1):
                    self.keywords_pro_text.insert(tk.END,
                        f"{i}. {kw['keyword'][:40]:40} | "
                        f"Dificultad: {kw['difficulty_score']:5.1f} | "
                        f"Oportunidad: {kw['opportunity_score']:5.1f}\n")

                self.keywords_pro_text.insert(tk.END, f"\n✅ Análisis completado\n")
                self.keywords_pro_text.insert(tk.END, f"  • Quick wins encontrados: {len(quick_wins_list)}\n")

                loop.run_until_complete(db.close())
                loop.close()

            except Exception as e:
                self.keywords_pro_text.insert(tk.END, f"\n❌ Error: {str(e)}\n")
                import traceback
                self.keywords_pro_text.insert(tk.END, f"{traceback.format_exc()}\n")

        threading.Thread(target=analyze, daemon=True).start()

    def run_competitive_analysis(self):
        """Ejecuta análisis competitivo."""
        if not self.current_session_id:
            messagebox.showwarning("Advertencia", "Primero selecciona una sesión")
            return

        self.keywords_pro_text.delete(1.0, tk.END)
        self.keywords_pro_text.insert(tk.END, "Ejecutando análisis competitivo...\n\n")

        def analyze():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                config = Config()
                db = Database(config.get('database_path'))
                loop.run_until_complete(db.connect())

                # Obtener todas las sesiones para comparar
                sessions = loop.run_until_complete(db.get_all_sessions())

                if len(sessions) < 2:
                    self.keywords_pro_text.insert(tk.END, "ℹ️  ANÁLISIS COMPETITIVO REQUIERE MÚLTIPLES SITIOS\n\n")
                    self.keywords_pro_text.insert(tk.END, "Para usar esta función necesitas:\n")
                    self.keywords_pro_text.insert(tk.END, "1. Crawlear tu sitio web\n")
                    self.keywords_pro_text.insert(tk.END, "2. Crawlear sitios competidores\n")
                    self.keywords_pro_text.insert(tk.END, "3. Comparar keywords entre ellos\n\n")
                    self.keywords_pro_text.insert(tk.END, "📊 ANÁLISIS INTERNO DISPONIBLE:\n\n")

                    # Hacer análisis interno de gaps
                    pages = loop.run_until_complete(db.get_pages_by_session(self.current_session_id))
                    keywords = loop.run_until_complete(db.get_top_keywords_by_session(self.current_session_id, limit=1000))

                    # Agrupar keywords por página
                    pages_with_keywords = defaultdict(list)
                    for kw in keywords:
                        pages_with_keywords[kw.get('page_id')].append(kw)

                    # Encontrar páginas con pocas keywords (oportunidades de mejora)
                    low_keyword_pages = []
                    for page in pages:
                        page_kws = pages_with_keywords.get(page.get('page_id', page.get('id')), [])
                        if len(page_kws) < 10 and page.get('word_count', 0) > 200:
                            low_keyword_pages.append({
                                'url': page.get('url'),
                                'keywords': len(page_kws),
                                'word_count': page.get('word_count')
                            })

                    if low_keyword_pages:
                        self.keywords_pro_text.insert(tk.END, "⚠️  PÁGINAS CON BAJO POTENCIAL DE KEYWORDS:\n\n")
                        for i, page in enumerate(sorted(low_keyword_pages, key=lambda x: x['keywords'])[:10], 1):
                            self.keywords_pro_text.insert(tk.END,
                                f"{i}. {page['url'][:50]:50} | "
                                f"KWs: {page['keywords']:3} | "
                                f"Palabras: {page['word_count']:5}\n")
                        self.keywords_pro_text.insert(tk.END, "\n💡 Estas páginas podrían optimizarse para más keywords\n")
                    else:
                        self.keywords_pro_text.insert(tk.END, "✅ Todas las páginas tienen buen potencial de keywords\n")
                else:
                    self.keywords_pro_text.insert(tk.END, f"📊 COMPARACIÓN CON {len(sessions)-1} OTROS SITIOS\n\n")
                    # Aquí se podría implementar comparación real con otros sitios
                    self.keywords_pro_text.insert(tk.END, "ℹ️  Función de comparación multi-sitio en desarrollo\n")

                loop.run_until_complete(db.close())
                loop.close()

            except Exception as e:
                self.keywords_pro_text.insert(tk.END, f"\n❌ Error: {str(e)}\n")

        threading.Thread(target=analyze, daemon=True).start()

    def run_content_quality_analysis(self):
        """Analiza calidad de contenido."""
        if not self.current_session_id:
            messagebox.showwarning("Advertencia", "Primero selecciona una sesión")
            return

        self.content_quality_text.delete(1.0, tk.END)
        self.content_quality_text.insert(tk.END, "Analizando calidad de contenido...\n\n")

        def analyze():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                config = Config()
                db = Database(config.get('database_path'))
                loop.run_until_complete(db.connect())

                pages = loop.run_until_complete(db.get_pages_by_session(self.current_session_id))

                analyzer = ContentQualityAnalyzer()

                thin_content = []
                low_quality = []

                self.content_quality_text.insert(tk.END, f"🔄 Analizando {len(pages)} páginas...\n\n")

                for page in pages[:50]:
                    html = page.get('html_content', '')
                    if not html:
                        continue

                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(html, 'lxml')
                    text = soup.get_text(separator=' ', strip=True)

                    readability = analyzer.calculate_flesch_reading_ease(text)
                    quality = analyzer.calculate_quality_score(page, text)
                    is_thin = analyzer.is_thin_content(len(text.split()))

                    if is_thin:
                        thin_content.append((page['url'], len(text.split())))
                    if quality < 50:
                        low_quality.append((page['url'], quality))

                self.content_quality_text.insert(tk.END, "📊 RESULTADOS:\n\n")
                self.content_quality_text.insert(tk.END, f"⚠️  Thin Content: {len(thin_content)} páginas\n")
                self.content_quality_text.insert(tk.END, f"⚠️  Baja Calidad: {len(low_quality)} páginas\n\n")

                if thin_content:
                    self.content_quality_text.insert(tk.END, "🔴 TOP 5 PÁGINAS CON THIN CONTENT:\n")
                    for url, words in thin_content[:5]:
                        self.content_quality_text.insert(tk.END, f"  • {url[:60]:60} ({words} palabras)\n")

                self.content_quality_text.insert(tk.END, "\n✅ Análisis completado\n")

                loop.run_until_complete(db.close())
                loop.close()

            except Exception as e:
                self.content_quality_text.insert(tk.END, f"\n❌ Error: {str(e)}\n")

        threading.Thread(target=analyze, daemon=True).start()

    def generate_static_visualizations(self):
        """Genera visualizaciones estáticas con matplotlib."""
        if not self.current_session_id:
            messagebox.showwarning("Advertencia", "Primero selecciona una sesión")
            return

        output_dir = filedialog.askdirectory(title="Selecciona carpeta para guardar visualizaciones")
        if not output_dir:
            return

        self.content_quality_text.delete(1.0, tk.END)
        self.content_quality_text.insert(tk.END, "Generando visualizaciones...\n\n")

        def generate():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                config = Config()
                db = Database(config.get('database_path'))
                loop.run_until_complete(db.connect())

                session_data = {
                    'session_id': self.current_session_id,
                    'pages': loop.run_until_complete(db.get_pages_by_session(self.current_session_id)),
                    'keywords': loop.run_until_complete(db.get_top_keywords_by_session(self.current_session_id, limit=1000))
                }

                visualizer = SEOVisualizer()
                results = visualizer.generate_full_report_visuals(session_data, output_dir)

                self.content_quality_text.insert(tk.END, "✅ Visualizaciones generadas:\n\n")
                for name, path in results.items():
                    if path:
                        self.content_quality_text.insert(tk.END, f"  ✓ {name}: {path}\n")

                self.content_quality_text.insert(tk.END, f"\n📂 Carpeta: {output_dir}\n")

                loop.run_until_complete(db.close())
                loop.close()

                messagebox.showinfo("Éxito", f"Visualizaciones generadas en:\n{output_dir}")

            except Exception as e:
                self.content_quality_text.insert(tk.END, f"\n❌ Error: {str(e)}\n")

        threading.Thread(target=generate, daemon=True).start()

    def run_technical_audit(self):
        """Ejecuta auditoría técnica SEO."""
        if not self.current_session_id:
            messagebox.showwarning("Advertencia", "Primero selecciona una sesión")
            return

        self.technical_audit_text.delete(1.0, tk.END)
        self.technical_audit_text.insert(tk.END, "Ejecutando auditoría técnica...\n\n")

        def audit():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                config = Config()
                db = Database(config.get('database_path'))
                loop.run_until_complete(db.connect())

                pages = loop.run_until_complete(db.get_pages_by_session(self.current_session_id))
                images = loop.run_until_complete(db.get_images_by_session(self.current_session_id))

                auditor = TechnicalSEOAuditor()
                results = auditor.run_complete_audit(pages, images)

                summary = auditor.generate_audit_summary(results)
                self.technical_audit_text.insert(tk.END, summary)

                loop.run_until_complete(db.close())
                loop.close()

            except Exception as e:
                self.technical_audit_text.insert(tk.END, f"\n❌ Error: {str(e)}\n")

        threading.Thread(target=audit, daemon=True).start()

    def run_schema_analysis(self):
        """Analiza schema markup y datos estructurados."""
        if not self.current_session_id:
            messagebox.showwarning("Advertencia", "Primero selecciona una sesión")
            return

        self.technical_audit_text.delete(1.0, tk.END)
        self.technical_audit_text.insert(tk.END, "Analizando schema markup...\n\n")

        def analyze():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                config = Config()
                db = Database(config.get('database_path'))
                loop.run_until_complete(db.connect())

                pages = loop.run_until_complete(db.get_pages_by_session(self.current_session_id))

                analyzer = SchemaAnalyzer()
                results = analyzer.run_complete_analysis(pages)

                summary = analyzer.generate_summary(results)
                self.technical_audit_text.insert(tk.END, summary)

                loop.run_until_complete(db.close())
                loop.close()

            except Exception as e:
                self.technical_audit_text.insert(tk.END, f"\n❌ Error: {str(e)}\n")

        threading.Thread(target=analyze, daemon=True).start()

    def run_recommendations(self):
        """Genera recomendaciones SEO priorizadas."""
        if not self.current_session_id:
            messagebox.showwarning("Advertencia", "Primero selecciona una sesión")
            return

        self.technical_audit_text.delete(1.0, tk.END)
        self.technical_audit_text.insert(tk.END, "Generando recomendaciones SEO...\n\n")

        def generate():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                config = Config()
                db = Database(config.get('database_path'))
                loop.run_until_complete(db.connect())

                pages = loop.run_until_complete(db.get_pages_by_session(self.current_session_id))
                images = loop.run_until_complete(db.get_images_by_session(self.current_session_id))
                links = loop.run_until_complete(db.get_links_by_session(self.current_session_id))

                # Análisis técnico
                auditor = TechnicalSEOAuditor()
                technical_audit = auditor.run_complete_audit(pages, images)

                # Análisis de schema
                schema_analyzer = SchemaAnalyzer()
                schema_analysis = schema_analyzer.run_complete_analysis(pages)

                # Análisis de red
                network_analysis = None
                if links:
                    network_analyzer = NetworkAnalyzer()
                    network_analyzer.build_link_graph(pages, links)
                    network_analysis = network_analyzer.analyze_network(pages, links)

                # Generar recomendaciones
                engine = RecommendationsEngine()
                recommendations = engine.generate_recommendations(
                    technical_audit=technical_audit,
                    schema_analysis=schema_analysis,
                    network_analysis=network_analysis
                )

                # Mostrar top 15
                self.technical_audit_text.insert(tk.END, f"🎯 TOP 15 RECOMENDACIONES:\n\n")
                for i, rec in enumerate(recommendations[:15], 1):
                    roi = rec.impact_score / max(rec.effort_score, 1)
                    self.technical_audit_text.insert(tk.END,
                        f"{i}. [{rec.priority.value.upper()}] {rec.title}\n")
                    self.technical_audit_text.insert(tk.END,
                        f"   ROI: {roi:.2f} | Impacto: {rec.impact_score}/100 | Esfuerzo: {rec.effort_score}/100\n")
                    self.technical_audit_text.insert(tk.END,
                        f"   {rec.description[:80]}...\n\n")

                self.technical_audit_text.insert(tk.END, f"💡 Total: {len(recommendations)} recomendaciones\n")

                loop.run_until_complete(db.close())
                loop.close()

            except Exception as e:
                self.technical_audit_text.insert(tk.END, f"\n❌ Error: {str(e)}\n")

        threading.Thread(target=generate, daemon=True).start()

    def run_complete_audit(self):
        """Ejecuta auditoría completa."""
        if not self.current_session_id:
            messagebox.showwarning("Advertencia", "Primero selecciona una sesión")
            return

        self.technical_audit_text.delete(1.0, tk.END)
        self.technical_audit_text.insert(tk.END, "🚀 EJECUTANDO AUDITORÍA COMPLETA...\n\n")
        self.technical_audit_text.insert(tk.END, "Esto puede tardar varios minutos...\n\n")

        def audit():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                config = Config()
                db = Database(config.get('database_path'))
                loop.run_until_complete(db.connect())

                pages = loop.run_until_complete(db.get_pages_by_session(self.current_session_id))
                images = loop.run_until_complete(db.get_images_by_session(self.current_session_id))
                links = loop.run_until_complete(db.get_links_by_session(self.current_session_id))

                # Auditoría técnica
                self.technical_audit_text.insert(tk.END, "1️⃣  Auditoría técnica...\n")
                auditor = TechnicalSEOAuditor()
                technical_audit = auditor.run_complete_audit(pages, images)
                self.technical_audit_text.insert(tk.END,
                    f"   Health Score: {technical_audit['overall_health_score']}/100\n\n")

                # Schema
                self.technical_audit_text.insert(tk.END, "2️⃣  Análisis de schema...\n")
                schema_analyzer = SchemaAnalyzer()
                schema_analysis = schema_analyzer.run_complete_analysis(pages)
                self.technical_audit_text.insert(tk.END,
                    f"   Health Score: {schema_analysis['health_score']}/100\n\n")

                # Red
                if links:
                    self.technical_audit_text.insert(tk.END, "3️⃣  Análisis de red...\n")
                    network_analyzer = NetworkAnalyzer()
                    network_analyzer.build_link_graph(pages, links)
                    network_analysis = network_analyzer.analyze_network(pages, links)
                    self.technical_audit_text.insert(tk.END,
                        f"   Páginas huérfanas: {len(network_analysis['orphan_pages'])}\n\n")
                else:
                    network_analysis = None

                # Recomendaciones
                self.technical_audit_text.insert(tk.END, "4️⃣  Generando recomendaciones...\n\n")
                engine = RecommendationsEngine()
                recommendations = engine.generate_recommendations(
                    technical_audit=technical_audit,
                    schema_analysis=schema_analysis,
                    network_analysis=network_analysis
                )

                # Resumen
                self.technical_audit_text.insert(tk.END, "=" * 80 + "\n")
                self.technical_audit_text.insert(tk.END, "RESUMEN EJECUTIVO\n")
                self.technical_audit_text.insert(tk.END, "=" * 80 + "\n\n")
                self.technical_audit_text.insert(tk.END,
                    f"📊 Health Score Técnico: {technical_audit['overall_health_score']}/100\n")
                self.technical_audit_text.insert(tk.END,
                    f"🏷️  Health Score Schema: {schema_analysis['health_score']}/100\n")
                self.technical_audit_text.insert(tk.END,
                    f"🔴 Issues Críticos: {technical_audit['critical_issues']}\n")
                self.technical_audit_text.insert(tk.END,
                    f"⚠️  Warnings: {technical_audit['warnings']}\n")
                self.technical_audit_text.insert(tk.END,
                    f"💡 Recomendaciones: {len(recommendations)}\n\n")

                # Top 5 recomendaciones
                self.technical_audit_text.insert(tk.END, "🎯 TOP 5 ACCIONES PRIORITARIAS:\n\n")
                for i, rec in enumerate(recommendations[:5], 1):
                    self.technical_audit_text.insert(tk.END,
                        f"{i}. [{rec.priority.value.upper()}] {rec.title}\n")
                    self.technical_audit_text.insert(tk.END,
                        f"   {rec.description[:100]}...\n\n")

                self.technical_audit_text.insert(tk.END, "\n✅ Auditoría completada\n")

                loop.run_until_complete(db.close())
                loop.close()

                messagebox.showinfo("Éxito", "Auditoría completa finalizada")

            except Exception as e:
                self.technical_audit_text.insert(tk.END, f"\n❌ Error: {str(e)}\n")

        threading.Thread(target=audit, daemon=True).start()

    def generate_interactive_visualizations(self):
        """Genera visualizaciones interactivas con Plotly."""
        if not self.current_session_id:
            messagebox.showwarning("Advertencia", "Primero selecciona una sesión")
            return

        output_dir = filedialog.askdirectory(title="Selecciona carpeta para guardar visualizaciones")
        if not output_dir:
            return

        self.visualizations_text.delete(1.0, tk.END)
        self.visualizations_text.insert(tk.END, "Generando visualizaciones interactivas...\n\n")

        def generate():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                config = Config()
                db = Database(config.get('database_path'))
                loop.run_until_complete(db.connect())

                self.visualizations_text.insert(tk.END, "Cargando datos...\n")

                pages = loop.run_until_complete(db.get_pages_by_session(self.current_session_id))
                keywords = loop.run_until_complete(db.get_top_keywords_by_session(self.current_session_id, limit=1000))

                # Calcular métricas necesarias para visualizaciones
                self.visualizations_text.insert(tk.END, "Calculando métricas de keywords...\n")
                keyword_analyzer = KeywordDifficultyAnalyzer()
                keywords_with_metrics = keyword_analyzer.analyze_all_keywords(keywords, pages)

                self.visualizations_text.insert(tk.END, "Analizando clusters y topics...\n")
                semantic_analyzer = SemanticAnalyzer()
                clusters = semantic_analyzer.cluster_keywords(keywords, n_clusters=5)
                topics = semantic_analyzer.extract_topics(keywords, n_topics=5)

                self.visualizations_text.insert(tk.END, "Analizando calidad de contenido...\n")
                content_analyzer = ContentQualityAnalyzer()
                pages_quality = content_analyzer.analyze_content_quality(pages)

                session_data = {
                    'session_id': self.current_session_id,
                    'pages': pages,
                    'keywords': keywords,
                    'keywords_with_metrics': keywords_with_metrics,
                    'pages_with_quality': pages_quality.get('pages', []),
                    'clusters': clusters,
                    'topics': topics,
                    'top_keywords': keywords[:100]
                }

                self.visualizations_text.insert(tk.END, "Generando visualizaciones HTML...\n")
                visualizer = InteractiveVisualizer()
                results = visualizer.generate_all_interactive_visuals(session_data, output_dir)

                self.visualizations_text.insert(tk.END, "\n✅ Visualizaciones interactivas generadas:\n\n")
                for name, path in results.items():
                    if path:
                        self.visualizations_text.insert(tk.END, f"  ✓ {name}: {path}\n")

                self.visualizations_text.insert(tk.END, f"\n📂 Carpeta: {output_dir}\n")
                self.visualizations_text.insert(tk.END, "\n💡 Abre los archivos HTML en tu navegador\n")

                loop.run_until_complete(db.close())
                loop.close()

                messagebox.showinfo("Éxito", f"Visualizaciones interactivas generadas en:\n{output_dir}")

            except Exception as e:
                self.visualizations_text.insert(tk.END, f"\n❌ Error: {str(e)}\n")

        threading.Thread(target=generate, daemon=True).start()

    def run_network_analysis(self):
        """Ejecuta análisis de red de enlaces."""
        if not self.current_session_id:
            messagebox.showwarning("Advertencia", "Primero selecciona una sesión")
            return

        self.visualizations_text.delete(1.0, tk.END)
        self.visualizations_text.insert(tk.END, "Analizando red de enlaces...\n\n")

        def analyze():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                config = Config()
                db = Database(config.get('database_path'))
                loop.run_until_complete(db.connect())

                pages = loop.run_until_complete(db.get_pages_by_session(self.current_session_id))
                links = loop.run_until_complete(db.get_links_by_session(self.current_session_id))

                if not links:
                    self.visualizations_text.insert(tk.END, "⚠️  No hay enlaces para analizar\n")
                    return

                analyzer = NetworkAnalyzer()
                analyzer.build_link_graph(pages, links)
                results = analyzer.analyze_network(pages, links)

                # Validar que results tiene la estructura esperada
                if not results or not isinstance(results, dict):
                    self.visualizations_text.insert(tk.END, "❌ No se pudo generar el análisis de red\n")
                    return

                self.visualizations_text.insert(tk.END, "📊 ANÁLISIS DE RED:\n\n")

                # Validar y mostrar estadísticas del grafo
                if 'graph_stats' in results:
                    stats = results['graph_stats']
                    self.visualizations_text.insert(tk.END, f"Nodos (páginas): {stats.get('nodes', 0)}\n")
                    self.visualizations_text.insert(tk.END, f"Enlaces: {stats.get('edges', 0)}\n")
                    self.visualizations_text.insert(tk.END, f"Densidad: {stats.get('density', 0.0):.4f}\n\n")

                # Mostrar métricas adicionales con validación
                self.visualizations_text.insert(tk.END, f"🔴 Páginas huérfanas: {len(results.get('orphan_pages', []))}\n")
                self.visualizations_text.insert(tk.END, f"🔗 Enlaces rotos: {len(results.get('broken_links', []))}\n")
                self.visualizations_text.insert(tk.END, f"📦 Clusters: {len(results.get('link_clusters', []))}\n\n")

                # Top PageRank con validación
                if 'top_pagerank' in results and results['top_pagerank']:
                    self.visualizations_text.insert(tk.END, "🏆 TOP 10 PÁGINAS POR PAGERANK:\n\n")
                    for i, (page_id, pr) in enumerate(results['top_pagerank'][:10], 1):
                        page = next((p for p in pages if p.get('id') == page_id or p.get('page_id') == page_id), None)
                        if page:
                            url = page.get('url', 'N/A')
                            self.visualizations_text.insert(tk.END,
                                f"{i}. {url[:60]:60} PR: {pr:.4f}\n")
                else:
                    self.visualizations_text.insert(tk.END, "⚠️  No se pudo calcular PageRank\n")

                loop.run_until_complete(db.close())
                loop.close()

            except Exception as e:
                self.visualizations_text.insert(tk.END, f"\n❌ Error: {str(e)}\n")

        threading.Thread(target=analyze, daemon=True).start()

    def generate_dashboard(self):
        """Genera dashboard interactivo completo."""
        if not self.current_session_id:
            messagebox.showwarning("Advertencia", "Primero selecciona una sesión")
            return

        output_file = filedialog.asksaveasfilename(
            title="Guardar dashboard",
            defaultextension=".html",
            filetypes=[("HTML", "*.html")]
        )
        if not output_file:
            return

        self.visualizations_text.delete(1.0, tk.END)
        self.visualizations_text.insert(tk.END, "Generando dashboard interactivo...\n\n")

        def generate():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                config = Config()
                db = Database(config.get('database_path'))
                loop.run_until_complete(db.connect())

                self.visualizations_text.insert(tk.END, "Cargando datos...\n")

                pages = loop.run_until_complete(db.get_pages_by_session(self.current_session_id))
                keywords = loop.run_until_complete(db.get_top_keywords_by_session(self.current_session_id, limit=1000))

                # Calcular métricas necesarias para el dashboard
                self.visualizations_text.insert(tk.END, "Calculando métricas de keywords...\n")
                keyword_analyzer = KeywordDifficultyAnalyzer()
                keywords_with_metrics = keyword_analyzer.analyze_all_keywords(keywords, pages)

                self.visualizations_text.insert(tk.END, "Analizando calidad de contenido...\n")
                content_analyzer = ContentQualityAnalyzer()
                pages_quality = content_analyzer.analyze_content_quality(pages)

                session_data = {
                    'session_id': self.current_session_id,
                    'pages': pages,
                    'keywords': keywords,
                    'keywords_with_metrics': keywords_with_metrics,
                    'pages_with_quality': pages_quality.get('pages', [])
                }

                self.visualizations_text.insert(tk.END, "Generando dashboard HTML...\n")
                visualizer = InteractiveVisualizer()
                if visualizer.generate_interactive_dashboard(session_data, output_file):
                    self.visualizations_text.insert(tk.END, f"\n✅ Dashboard generado:\n{output_file}\n\n")
                    self.visualizations_text.insert(tk.END, "📊 El dashboard incluye:\n")
                    self.visualizations_text.insert(tk.END, "  • Opportunity Matrix (Scatter)\n")
                    self.visualizations_text.insert(tk.END, "  • Quality Distribution (Histogram)\n")
                    self.visualizations_text.insert(tk.END, "  • Top Keywords (Bar)\n")
                    self.visualizations_text.insert(tk.END, "  • Competition Levels (Pie)\n")
                    self.visualizations_text.insert(tk.END, "  • Readability Distribution (Pie)\n")
                    self.visualizations_text.insert(tk.END, "  • Intent Distribution (Bar)\n")

                    messagebox.showinfo("Éxito", f"Dashboard generado:\n{output_file}")
                else:
                    self.visualizations_text.insert(tk.END, "❌ Error generando dashboard\n")

                loop.run_until_complete(db.close())
                loop.close()

            except Exception as e:
                self.visualizations_text.insert(tk.END, f"\n❌ Error: {str(e)}\n")

        threading.Thread(target=generate, daemon=True).start()

    # ==================== MÉTODOS PARA SESSION SELECTORS ====================

    def refresh_professional_sessions(self, combobox):
        """Actualiza la lista de sesiones en un combobox profesional."""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            config = Config()
            db = Database(config.get('database_path'))
            loop.run_until_complete(db.connect())

            sessions = loop.run_until_complete(db.get_all_sessions())

            # Crear lista de sesiones en formato: "ID - Dominio - Fecha"
            session_list = []
            for s in sessions:
                session_str = f"{s['session_id']} - {s['domains']} - {s['start_time'][:10] if s['start_time'] else 'N/A'}"
                session_list.append(session_str)

            combobox['values'] = session_list

            loop.run_until_complete(db.close())
            loop.close()

        except Exception as e:
            print(f"Error al cargar sesiones profesionales: {str(e)}")

    def on_keywords_pro_session_selected(self, event):
        """Maneja la selección de sesión en Keywords Pro."""
        session_text = self.keywords_pro_session_combo.get()
        if session_text:
            session_id = int(session_text.split(' - ')[0])
            self.current_session_id = session_id
            self.keywords_pro_current_label.config(
                text=f"✓ Sesión {session_id} seleccionada",
                foreground='green'
            )

    def on_content_quality_session_selected(self, event):
        """Maneja la selección de sesión en Calidad de Contenido."""
        session_text = self.content_quality_session_combo.get()
        if session_text:
            session_id = int(session_text.split(' - ')[0])
            self.current_session_id = session_id
            self.content_quality_current_label.config(
                text=f"✓ Sesión {session_id} seleccionada",
                foreground='green'
            )

    def on_technical_audit_session_selected(self, event):
        """Maneja la selección de sesión en Auditoría Técnica."""
        session_text = self.technical_audit_session_combo.get()
        if session_text:
            session_id = int(session_text.split(' - ')[0])
            self.current_session_id = session_id
            self.technical_audit_current_label.config(
                text=f"✓ Sesión {session_id} seleccionada",
                foreground='green'
            )

    def on_visualizations_session_selected(self, event):
        """Maneja la selección de sesión en Visualizaciones."""
        session_text = self.visualizations_session_combo.get()
        if session_text:
            session_id = int(session_text.split(' - ')[0])
            self.current_session_id = session_id
            self.visualizations_current_label.config(
                text=f"✓ Sesión {session_id} seleccionada",
                foreground='green'
            )

    def on_closing(self):
        """Maneja el cierre de la aplicación."""
        if self.is_crawling:
            if messagebox.askokcancel("Salir", "Hay un crawl en progreso. ¿Deseas detenerlo y salir?"):
                if self.crawler:
                    self.crawler.stop()
                self.root.destroy()
        else:
            self.root.destroy()


def main():
    """Punto de entrada de la GUI."""
    root = tk.Tk()
    app = SEOCrawlerGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
