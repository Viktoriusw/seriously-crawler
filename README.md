# 🚀 SEO Crawler Professional

**Herramienta profesional de análisis SEO y extracción de keywords** diseñada para especialistas en SEO, marketers digitales y analistas de contenido que necesitan realizar análisis competitivo, auditorías SEO y research de keywords a escala.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-production-success.svg)

## ✨ Características Principales

### 🔍 Crawling Avanzado
- ⚡ **Crawling asíncrono** con aiohttp (10+ requests concurrentes)
- 🤖 **Respeto automático de robots.txt** con caché por dominio
- 🎯 **Rate limiting configurable** para evitar sobrecarga de servidores
- 🔄 **Manejo inteligente de redirects** y errores HTTP
- 📊 **Deduplicación de URLs** y detección de contenido duplicado
- 🌐 **Soporte multi-dominio** con control de subdominios

### 📈 Análisis de Keywords
- 🧮 **Cálculo de TF-IDF** (Term Frequency-Inverse Document Frequency)
- 📝 **Extracción de n-gramas** (1-gram, 2-gram, 3-gram)
- 🎯 **Análisis de posicionamiento** (title, h1, primeras 100 palabras)
- 📊 **Densidad de keywords** y detección de keyword stuffing
- 🔍 **Keyword gaps** (comparación competitiva)
- 📉 **Stop words** configurables (español e inglés)

### 💾 Almacenamiento
- 🗄️ **Base de datos SQLite** con esquema optimizado
- 📑 **Almacenamiento estructurado** de páginas, keywords, enlaces e imágenes
- 🔗 **Relaciones normalizadas** para consultas eficientes
- 📊 **Histórico de sesiones** para análisis temporal

### 📊 Reportes y Exportación
- 📄 **Reportes HTML** visuales y profesionales
- 📈 **Exportación a Excel** con múltiples hojas
- 💾 **Exportación CSV** de keywords
- 📦 **Exportación JSON** completa
- 📊 **Comparación entre dominios** y análisis competitivo

### 🖥️ Interfaces
- 💻 **CLI completa** con múltiples comandos
- 🎨 **GUI profesional con Tkinter** para uso visual
- 📊 **Visualización en tiempo real** del progreso
- 📈 **Estadísticas live** durante el crawl

---

## 📦 Instalación Completa con Entorno Virtual

### ⚠️ ¿Por qué usar un entorno virtual (venv)?

Un entorno virtual es **altamente recomendado** porque:
- ✅ Aísla las dependencias del proyecto de tu sistema Python global
- ✅ Evita conflictos entre versiones de librerías
- ✅ Permite tener diferentes versiones de paquetes en diferentes proyectos
- ✅ Facilita la gestión de dependencias
- ✅ Es una best practice en desarrollo Python

### 📋 Requisitos Previos

Antes de comenzar, asegúrate de tener:

1. **Python 3.8 o superior**
2. **pip** (gestor de paquetes, viene con Python)
3. **venv** (módulo para entornos virtuales, incluido en Python 3.3+)
4. **tkinter** (para la interfaz gráfica, generalmente incluido con Python)

#### Verificar Python y pip

```bash
# Verificar versión de Python (debe ser 3.8 o superior)
python --version
# o en algunos sistemas:
python3 --version

# Verificar pip
pip --version
# o
pip3 --version
```

Si no tienes Python instalado, descárgalo desde [python.org](https://www.python.org/downloads/)

---

## 🪟 Instalación en Windows

### Paso 1: Descargar el proyecto

```bash
# Navegar a la carpeta del proyecto
cd C:\ruta\a\crawlerserio
```

### Paso 2: Crear entorno virtual

```bash
# Crear entorno virtual llamado 'venv'
python -m venv venv
```

**Nota:** Si tienes tanto Python 2 como 3, usa `python3 -m venv venv`

### Paso 3: Activar entorno virtual

```bash
# Activar el entorno virtual
venv\Scripts\activate
```

**¿Cómo saber si está activado?**
- Verás `(venv)` al inicio de tu línea de comandos
- Ejemplo: `(venv) C:\ruta\a\crawlerserio>`

**Si aparece un error de permisos (PowerShell):**
```powershell
# Ejecutar PowerShell como Administrador y ejecutar:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Luego volver a intentar activar:
venv\Scripts\activate
```

**Alternativa con Command Prompt (cmd):**
```bash
venv\Scripts\activate.bat
```

### Paso 4: Actualizar pip (recomendado)

```bash
# Actualizar pip a la última versión
python -m pip install --upgrade pip
```

### Paso 5: Instalar dependencias

```bash
# Instalar todas las dependencias del proyecto
pip install -r requirements.txt
```

Este proceso puede tardar 1-2 minutos dependiendo de tu conexión a internet.

### Paso 6: Verificar instalación

```bash
# Verificar que todo funciona correctamente
python seo_crawler/main.py --help
```

Si ves el menú de ayuda del programa, ¡la instalación fue exitosa! ✅

### Paso 7: Lanzar el programa

```bash
# Opción 1: Interfaz gráfica
python seo_crawler/main.py gui

# Opción 2: Línea de comandos
python seo_crawler/main.py crawl --url https://ejemplo.com
```

### 🔴 Desactivar entorno virtual (cuando termines)

```bash
deactivate
```

Verás que `(venv)` desaparece de tu línea de comandos.

---

## 🐧 Instalación en Linux

### Paso 1: Descargar el proyecto

```bash
# Navegar a la carpeta del proyecto
cd /ruta/a/crawlerserio
```

### Paso 2: Instalar dependencias del sistema (si es necesario)

```bash
# En Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv python3-tk

# En Fedora/RHEL
sudo dnf install python3 python3-pip python3-tkinter

# En Arch Linux
sudo pacman -S python python-pip tk
```

### Paso 3: Crear entorno virtual

```bash
# Crear entorno virtual
python3 -m venv venv
```

### Paso 4: Activar entorno virtual

```bash
# Activar el entorno virtual
source venv/bin/activate
```

**¿Cómo saber si está activado?**
- Verás `(venv)` al inicio de tu línea de comandos
- Ejemplo: `(venv) usuario@pc:~/crawlerserio$`

### Paso 5: Actualizar pip

```bash
# Actualizar pip
pip install --upgrade pip
```

### Paso 6: Instalar dependencias

```bash
# Instalar todas las dependencias
pip install -r requirements.txt
```

### Paso 7: Verificar instalación

```bash
# Verificar que todo funciona
python seo_crawler/main.py --help
```

### Paso 8: Lanzar el programa

```bash
# Interfaz gráfica
python seo_crawler/main.py gui

# Línea de comandos
python seo_crawler/main.py crawl --url https://ejemplo.com
```

### 🔴 Desactivar entorno virtual

```bash
deactivate
```

### 🚀 Script de instalación automática (Linux)

También puedes usar el script de instalación incluido:

```bash
# Dar permisos de ejecución
chmod +x setup.sh

# Ejecutar instalación
./setup.sh

# Activar entorno virtual
source venv/bin/activate
```

---

## 🍎 Instalación en macOS

### Paso 1: Instalar Python (si no lo tienes)

```bash
# Opción 1: Desde python.org
# Descargar desde https://www.python.org/downloads/macos/

# Opción 2: Con Homebrew (recomendado)
brew install python3
```

### Paso 2: Navegar al proyecto

```bash
cd /ruta/a/crawlerserio
```

### Paso 3: Crear entorno virtual

```bash
# Crear entorno virtual
python3 -m venv venv
```

### Paso 4: Activar entorno virtual

```bash
# Activar el entorno virtual
source venv/bin/activate
```

**Verificación:** Deberías ver `(venv)` al inicio de tu terminal.

### Paso 5: Actualizar pip

```bash
pip install --upgrade pip
```

### Paso 6: Instalar dependencias

```bash
pip install -r requirements.txt
```

### Paso 7: Verificar instalación

```bash
python seo_crawler/main.py --help
```

### Paso 8: Lanzar el programa

```bash
# Interfaz gráfica
python seo_crawler/main.py gui

# Línea de comandos
python seo_crawler/main.py crawl --url https://ejemplo.com
```

### 🔴 Desactivar entorno virtual

```bash
deactivate
```

---

## 🔧 Solución de Problemas Comunes

### ❌ Error: "python: command not found"

**Solución:**
```bash
# Intenta con python3 en lugar de python
python3 --version

# Si funciona, usa python3 en todos los comandos
python3 -m venv venv
python3 seo_crawler/main.py gui
```

### ❌ Error: "No module named 'venv'"

**Solución en Linux:**
```bash
sudo apt-get install python3-venv
```

**Solución en Windows:**
- Reinstala Python desde python.org asegurándote de marcar "Add Python to PATH"

### ❌ Error: "No module named 'tkinter'"

**Solución en Linux:**
```bash
sudo apt-get install python3-tk
```

**Solución en macOS:**
```bash
# Tkinter viene con Python, pero si no funciona:
brew reinstall python-tk
```

**En Windows:** Tkinter viene incluido. Si no funciona, reinstala Python marcando la opción "tcl/tk and IDLE".

### ❌ Error: "Cannot activate venv on Windows"

**Solución:**
```powershell
# En PowerShell (como Administrador):
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# O usa Command Prompt (cmd) en lugar de PowerShell:
venv\Scripts\activate.bat
```

### ❌ Error: "pip: command not found"

**Solución:**
```bash
# Usa python -m pip en lugar de pip
python -m pip install -r requirements.txt
```

### ❌ El entorno virtual no se activa

**Verificar:**
```bash
# Windows
dir venv\Scripts

# Linux/Mac
ls venv/bin
```

Deberías ver archivos como `activate`, `python`, etc. Si no existen, vuelve a crear el entorno:

```bash
# Eliminar carpeta venv
rm -rf venv  # Linux/Mac
rmdir /s venv  # Windows

# Volver a crear
python -m venv venv
```

### ❌ "ModuleNotFoundError" al ejecutar el programa

**Solución:**
```bash
# Asegúrate de que el entorno virtual está activado
# Deberías ver (venv) en tu terminal

# Reinstalar dependencias
pip install -r requirements.txt

# Verificar que las dependencias se instalaron
pip list
```

---

## 📝 Uso del Entorno Virtual - Resumen Rápido

### Cada vez que quieras usar el programa:

**Windows:**
```bash
cd C:\ruta\a\crawlerserio
venv\Scripts\activate
python seo_crawler/main.py gui
```

**Linux/Mac:**
```bash
cd /ruta/a/crawlerserio
source venv/bin/activate
python seo_crawler/main.py gui
```

### Cuando termines:

```bash
deactivate
```

### Verificar si el entorno está activado:

Mira tu línea de comandos. Si ves `(venv)` al inicio, está activado:
```
(venv) C:\crawlerserio>        # ✅ Activado
C:\crawlerserio>               # ❌ Desactivado
```

---

## 🎯 Verificación Final de Instalación

Ejecuta estos comandos para verificar que todo está correcto:

```bash
# 1. Verificar Python
python --version

# 2. Verificar entorno virtual activado
# Deberías ver (venv) en tu terminal

# 3. Verificar dependencias instaladas
pip list | grep aiohttp
pip list | grep beautifulsoup4
pip list | grep pandas

# 4. Verificar que el programa arranca
python seo_crawler/main.py --help

# 5. Verificar GUI (debe abrir una ventana)
python seo_crawler/main.py gui
```

Si todos estos comandos funcionan, ¡estás listo para usar el SEO Crawler! 🎉

---

## 🚀 Guía de Uso

### 1️⃣ Interfaz Gráfica (GUI)

La forma más sencilla de usar el crawler es mediante la interfaz gráfica:

```bash
python seo_crawler/main.py gui
```

**Funcionalidades de la GUI:**
- ✅ Configurar crawls visualmente
- 📊 Ver progreso en tiempo real
- 📋 Explorar sesiones anteriores
- 🔍 Analizar keywords con filtros
- 💾 Exportar reportes con un clic

![GUI Screenshot](docs/gui_screenshot.png)

### 2️⃣ Interfaz de Línea de Comandos (CLI)

Para usuarios avanzados y automatización:

#### Crawlear un sitio web

```bash
# Crawl básico
python seo_crawler/main.py crawl --url https://ejemplo.com

# Crawl con opciones personalizadas
python seo_crawler/main.py crawl \
    --url https://ejemplo.com \
    --max-pages 200 \
    --max-depth 3 \
    --concurrent 15 \
    --delay 0.5 \
    --auto-export
```

**Opciones disponibles:**
- `--url`: URL inicial del crawl (requerido)
- `--max-pages`: Máximo de páginas a crawlear (default: 500)
- `--max-depth`: Profundidad máxima (default: 5)
- `--concurrent`: Requests concurrentes (default: 10)
- `--delay`: Segundos entre requests (default: 1.0)
- `--ignore-robots`: Ignorar robots.txt
- `--follow-external`: Seguir enlaces externos
- `--auto-export`: Generar reporte HTML automáticamente

#### Listar sesiones

```bash
python seo_crawler/main.py list
```

Output:
```
================================================================================
SESIONES DE CRAWLING
================================================================================
  ID | Dominios                       | Páginas | Keywords | Fecha
--------------------------------------------------------------------------------
   1 | ejemplo.com                    |     150 |     2340 | 2024-01-11 10:30:00
   2 | competencia.com                |     200 |     3150 | 2024-01-11 14:15:00
================================================================================
```

#### Analizar una sesión

```bash
# Análisis en consola
python seo_crawler/main.py analyze --session 1

# Análisis con exportación
python seo_crawler/main.py analyze --session 1 --export resultados.xlsx
```

#### Generar reportes

```bash
# Reporte HTML
python seo_crawler/main.py report --session 1 --format html

# Reporte Excel
python seo_crawler/main.py report --session 1 --format excel --output reporte.xlsx

# CSV de keywords
python seo_crawler/main.py report --session 1 --format csv

# JSON completo
python seo_crawler/main.py report --session 1 --format json
```

#### Comparar sesiones

```bash
# Comparar 2 sesiones (análisis detallado)
python seo_crawler/main.py compare --sessions 1 2

# Comparar múltiples sesiones
python seo_crawler/main.py compare --sessions 1 2 3

# Comparar y exportar
python seo_crawler/main.py compare --sessions 1 2 --export comparacion.xlsx
```

---

## 📁 Estructura del Proyecto

```
crawlerserio/
├── seo_crawler/
│   ├── crawler/
│   │   ├── __init__.py
│   │   ├── core.py              # Motor principal del crawler
│   │   ├── robots.py            # Gestor de robots.txt
│   │   ├── url_manager.py       # Cola de URLs y deduplicación
│   │   └── rate_limiter.py      # Control de velocidad por dominio
│   ├── extractors/
│   │   ├── __init__.py
│   │   ├── html_parser.py       # Extracción de elementos HTML
│   │   ├── keyword_analyzer.py  # Análisis de keywords y TF-IDF
│   │   └── metadata_extractor.py # Meta tags, structured data
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── database.py          # Gestión de SQLite
│   │   └── schemas.py           # Esquemas de base de datos
│   ├── analytics/
│   │   ├── __init__.py
│   │   ├── keyword_metrics.py   # Métricas de keywords
│   │   └── reporter.py          # Generador de reportes
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py          # Configuración centralizada
│   ├── utils/
│   │   ├── __init__.py
│   │   └── helpers.py           # Funciones auxiliares
│   ├── gui/
│   │   ├── __init__.py
│   │   └── main_window.py       # Interfaz gráfica Tkinter
│   ├── data/                    # Base de datos y logs (generado)
│   └── main.py                  # Punto de entrada CLI
├── requirements.txt             # Dependencias
└── README.md                    # Este archivo
```

---

## 🎯 Casos de Uso

### 1. Análisis Competitivo

```bash
# Crawlear tu sitio
python seo_crawler/main.py crawl --url https://miempresa.com --max-pages 300

# Crawlear competidor
python seo_crawler/main.py crawl --url https://competencia.com --max-pages 300

# Comparar y encontrar keyword gaps
python seo_crawler/main.py compare --sessions 1 2
```

**Resultado:** Identificarás keywords que usa tu competencia y tú no, permitiéndote optimizar tu estrategia de contenido.

### 2. Auditoría SEO On-Page

```bash
# Crawl profundo del sitio
python seo_crawler/main.py crawl --url https://misite.com --max-depth 5

# Analizar y exportar
python seo_crawler/main.py analyze --session 1 --export auditoria.xlsx
```

**Resultado:** Excel con todas las páginas, sus keywords, densidades, y detección de keyword stuffing.

### 3. Research de Keywords

```bash
# Crawlear múltiples sitios del sector
python seo_crawler/main.py crawl --url https://sitio1.com
python seo_crawler/main.py crawl --url https://sitio2.com
python seo_crawler/main.py crawl --url https://sitio3.com

# Encontrar keywords comunes
python seo_crawler/main.py compare --sessions 1 2 3
```

**Resultado:** Lista de keywords más relevantes del sector con métricas TF-IDF.

### 4. Monitoreo Temporal

```bash
# Crawlear el mismo sitio periódicamente
python seo_crawler/main.py crawl --url https://misite.com

# Comparar con crawl anterior
python seo_crawler/main.py compare --sessions 5 10
```

**Resultado:** Detectar cambios en la estrategia de keywords del sitio a lo largo del tiempo.

---

## ⚙️ Configuración Avanzada

### Personalizar configuración

Puedes modificar `seo_crawler/config/settings.py` para ajustar:

```python
DEFAULT_CONFIG = {
    # Crawling
    'max_pages': 500,
    'max_depth': 5,
    'concurrent_requests': 10,
    'crawl_delay': 1.0,

    # Keywords
    'min_keyword_length': 3,
    'max_keyword_length': 50,
    'stop_words_language': 'spanish',  # 'spanish' o 'english'
    'max_ngram_size': 3,

    # Base de datos
    'database_path': 'data/seo_crawler.db',

    # Exportación
    'export_formats': ['csv', 'excel', 'json', 'html'],
}
```

### Patrones de exclusión

Añade patrones regex para excluir URLs:

```python
'exclude_patterns': [
    r'.*\.(jpg|jpeg|png|gif|pdf|doc|docx|zip|rar)$',
    r'.*/feed/?$',
    r'.*/wp-admin/.*',
    r'.*/wp-json/.*',
    r'.*/tag/.*',
    r'.*/category/.*'
]
```

---

## 📊 Esquema de Base de Datos

### Tablas Principales

**crawl_sessions**
- `session_id`: ID único de la sesión
- `seed_url`: URL inicial
- `domains`: Dominios crawleados
- `start_time`, `end_time`: Timestamps
- `pages_crawled`, `total_keywords`: Estadísticas

**pages**
- `page_id`: ID único
- `url`, `domain`: Identificadores
- `title`, `h1`, `meta_description`: Elementos SEO
- `word_count`, `content_hash`: Métricas
- `status_code`, `response_time`: Info técnica

**keywords**
- `keyword_id`: ID único
- `keyword`: Palabra clave
- `frequency`: Apariciones
- `density`: % de densidad
- `tf_idf_score`: Score TF-IDF
- `position_in_title`, `position_in_h1`: Posicionamiento
- `is_ngram`, `ngram_size`: Tipo de keyword

**links**
- `link_id`: ID único
- `source_page_id`: Página origen
- `target_url`: URL destino
- `anchor_text`: Texto ancla
- `is_internal`, `nofollow`: Atributos

---

## 🔧 Desarrollo y Extensión

### Añadir nuevos extractores

```python
# En extractors/custom_extractor.py
class CustomExtractor:
    def extract(self, html: str) -> dict:
        # Tu lógica personalizada
        return data
```

### Crear nuevas métricas

```python
# En analytics/custom_metrics.py
class CustomMetrics:
    async def calculate_metric(self, session_id: int):
        # Tus cálculos personalizados
        return metric_data
```

### Tests (opcional)

```bash
# Instalar dependencias de testing
pip install pytest pytest-asyncio

# Ejecutar tests
pytest tests/
```

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Haz fork del proyecto
2. Crea una branch para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la branch (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📝 Roadmap

### Próximas funcionalidades
- [ ] Integración con APIs de Google Search Console
- [ ] Exportación a bases de datos externas (MySQL, PostgreSQL)
- [ ] Generación de gráficos y visualizaciones avanzadas
- [ ] Soporte para JavaScript rendering (Playwright/Selenium)
- [ ] Análisis de imágenes (alt text, tamaño, optimización)
- [ ] Detección de errores técnicos SEO (canonical, hreflang, etc.)
- [ ] CLI interactiva con menús
- [ ] API REST para integración con otras herramientas
- [ ] Dashboard web con Flask/Django

---

## ⚠️ Consideraciones Legales y Éticas

### Uso Responsable

Esta herramienta está diseñada para:
- ✅ Análisis de tus propios sitios web
- ✅ Análisis competitivo con fines educativos/investigación
- ✅ Auditorías SEO autorizadas
- ✅ Research de mercado legítimo

**NO debe usarse para:**
- ❌ Sobrecarga de servidores (DoS)
- ❌ Scraping masivo no autorizado
- ❌ Violación de términos de servicio
- ❌ Acceso a contenido protegido

### Respeto de robots.txt

Por defecto, el crawler **respeta robots.txt**. Solo desactiva esta opción si:
- Tienes permiso explícito del propietario del sitio
- Es tu propio sitio
- Estás en un entorno de testing

### Rate Limiting

El crawler incluye rate limiting por defecto (1 req/seg) para evitar sobrecargar servidores. Ajusta este valor responsablemente.

---

## 🐛 Solución de Problemas

### Error: "ModuleNotFoundError"

```bash
# Asegúrate de haber instalado las dependencias
pip install -r requirements.txt
```

### Error: "Database locked"

```bash
# Cierra todas las instancias del programa y elimina locks
rm seo_crawler/data/*.db-wal
rm seo_crawler/data/*.db-shm
```

### Crawl muy lento

```bash
# Aumenta requests concurrentes y reduce delay
python seo_crawler/main.py crawl --url https://ejemplo.com \
    --concurrent 20 --delay 0.3
```

### GUI no se abre

```bash
# Verifica que tkinter esté instalado
python -m tkinter

# En Linux, instalar tkinter si falta
sudo apt-get install python3-tk
```

---

## 📞 Soporte

Para reportar bugs, solicitar features o hacer preguntas:

- 📧 Email: [tu-email@ejemplo.com]
- 🐛 Issues: [GitHub Issues](https://github.com/usuario/seo-crawler/issues)
- 📖 Documentación: [Wiki del proyecto](https://github.com/usuario/seo-crawler/wiki)

---

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver archivo `LICENSE` para más detalles.

---

## 🙏 Agradecimientos

Este proyecto utiliza las siguientes bibliotecas de código abierto:

- [aiohttp](https://github.com/aio-libs/aiohttp) - HTTP asíncrono
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) - Parseo HTML
- [pandas](https://pandas.pydata.org/) - Análisis de datos
- [tkinter](https://docs.python.org/3/library/tkinter.html) - GUI

---

## 🌟 Características Técnicas Destacadas

### Arquitectura
- ✨ **Código asíncrono** con asyncio para máximo rendimiento
- 🎯 **Type hints** en todas las funciones (Python 3.8+)
- 📝 **Docstrings completos** en español
- 🧩 **Diseño modular** fácilmente extensible
- 🔒 **Manejo robusto de excepciones**
- 📊 **Logging estructurado** con múltiples niveles

### Performance
- ⚡ 10+ requests concurrentes por defecto
- 🚀 1-2 páginas/segundo en promedio
- 💾 Base de datos optimizada con índices
- 🔄 Caché de robots.txt por dominio
- 📦 Gestión eficiente de memoria

---

## 📚 Recursos Adicionales

### Tutoriales
- [Cómo hacer un análisis competitivo de keywords](docs/tutorial_analisis_competitivo.md)
- [Detectar keyword stuffing en tu sitio](docs/tutorial_keyword_stuffing.md)
- [Automatizar crawls con cron/Task Scheduler](docs/tutorial_automatizacion.md)

### Ejemplos de scripts
- [Script para crawl masivo de competidores](examples/crawl_competidores.py)
- [Generar reportes automáticos por email](examples/reportes_email.py)
- [Integración con Google Sheets](examples/export_google_sheets.py)

---

**Desarrollado con ❤️ para profesionales del SEO**

_Última actualización: Enero 2024_
