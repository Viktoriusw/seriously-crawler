# 🚀 Guía de Inicio Rápido - SEO Crawler Professional

## ⚡ Instalación Express (3 minutos)

### 🪟 Windows

```bash
# 1. Navegar al proyecto
cd C:\ruta\a\crawlerserio

# 2. Crear entorno virtual
python -m venv venv

# 3. Activar entorno virtual
venv\Scripts\activate
# (Deberías ver "(venv)" al inicio de tu línea de comandos)

# 4. Actualizar pip
python -m pip install --upgrade pip

# 5. Instalar dependencias
pip install -r requirements.txt

# 6. Lanzar interfaz gráfica
python seo_crawler/main.py gui
```

**💡 Nota:** Si tienes error de permisos en PowerShell, ejecuta como Administrador:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 🐧 Linux

```bash
# 1. Navegar al proyecto
cd /ruta/a/crawlerserio

# 2. Instalar dependencias del sistema (solo primera vez)
sudo apt-get update && sudo apt-get install python3 python3-pip python3-venv python3-tk

# 3. Crear entorno virtual
python3 -m venv venv

# 4. Activar entorno virtual
source venv/bin/activate
# (Deberías ver "(venv)" al inicio de tu terminal)

# 5. Actualizar pip
pip install --upgrade pip

# 6. Instalar dependencias
pip install -r requirements.txt

# 7. Lanzar interfaz gráfica
python seo_crawler/main.py gui
```

**🚀 Atajo con script de instalación:**
```bash
./setup.sh
source venv/bin/activate
python seo_crawler/main.py gui
```

### 🍎 macOS

```bash
# 1. Navegar al proyecto
cd /ruta/a/crawlerserio

# 2. Crear entorno virtual
python3 -m venv venv

# 3. Activar entorno virtual
source venv/bin/activate
# (Deberías ver "(venv)" al inicio de tu terminal)

# 4. Actualizar pip
pip install --upgrade pip

# 5. Instalar dependencias
pip install -r requirements.txt

# 6. Lanzar interfaz gráfica
python seo_crawler/main.py gui
```

---

## 🔄 Uso Diario

### Cada vez que quieras usar el programa:

**Windows:**
```bash
cd C:\ruta\a\crawlerserio
venv\Scripts\activate          # ← Activar entorno
python seo_crawler/main.py gui  # ← Lanzar programa
```

**Linux/Mac:**
```bash
cd /ruta/a/crawlerserio
source venv/bin/activate        # ← Activar entorno
python seo_crawler/main.py gui  # ← Lanzar programa
```

### Al terminar:
```bash
deactivate  # Desactivar entorno virtual
```

### ✅ Verificar si el entorno está activado:
Busca `(venv)` al inicio de tu línea de comandos:
```
(venv) C:\crawlerserio>  ← ✅ Activado
C:\crawlerserio>         ← ❌ Desactivado
```

## Primer Crawl desde CLI

```bash
# Crawl básico de un sitio
python seo_crawler/main.py crawl --url https://ejemplo.com --max-pages 50

# Ver sesiones
python seo_crawler/main.py list

# Analizar resultados
python seo_crawler/main.py analyze --session 1

# Generar reporte HTML
python seo_crawler/main.py report --session 1 --format html
```

## Primer Crawl desde GUI

1. **Lanzar GUI:**
   ```bash
   python seo_crawler/main.py gui
   ```

2. **Configurar crawl:**
   - Pestaña "🚀 Nuevo Crawl"
   - Ingresar URL (ej: https://ejemplo.com)
   - Ajustar parámetros (páginas, profundidad, etc.)
   - Click en "▶ Iniciar Crawl"

3. **Ver progreso:**
   - Observar estadísticas en tiempo real
   - Seguir el log de actividad

4. **Analizar resultados:**
   - Pestaña "📋 Sesiones" - Ver todas las sesiones
   - Pestaña "📈 Análisis" - Explorar keywords
   - Pestaña "💾 Exportar" - Generar reportes

## Uso Programático

```python
import asyncio
from seo_crawler.config.settings import Config
from seo_crawler.crawler.core import SEOCrawler

async def crawl_example():
    # Configuración
    config = Config({'max_pages': 100, 'max_depth': 3})

    # Crear crawler
    crawler = SEOCrawler(config)

    # Inicializar y crawlear
    await crawler.initialize(['https://ejemplo.com'])
    stats = await crawler.start()

    # Ver resultados
    print(f"Páginas: {stats['pages_crawled']}")
    print(f"Keywords: {stats['total_keywords']}")

    # Cleanup
    await crawler.cleanup()

# Ejecutar
asyncio.run(crawl_example())
```

## Ejemplos de Uso

Ver archivo `example_usage.py` para ejemplos completos de:
- Crawling básico
- Análisis de sesiones
- Exportación de reportes
- Comparación de dominios
- Análisis personalizado

```bash
python example_usage.py
```

## Casos de Uso Comunes

### 1. Análisis Competitivo

```bash
# Crawlear tu sitio
python seo_crawler/main.py crawl --url https://miempresa.com --max-pages 200

# Crawlear competidor
python seo_crawler/main.py crawl --url https://competidor.com --max-pages 200

# Comparar keywords
python seo_crawler/main.py compare --sessions 1 2 --export comparacion.xlsx
```

### 2. Auditoría SEO

```bash
# Crawl completo
python seo_crawler/main.py crawl --url https://misite.com --max-depth 5 --max-pages 500

# Generar reporte
python seo_crawler/main.py report --session 1 --format html
```

### 3. Research de Keywords

```bash
# Crawlear múltiples sitios del sector
python seo_crawler/main.py crawl --url https://sitio1.com
python seo_crawler/main.py crawl --url https://sitio2.com
python seo_crawler/main.py crawl --url https://sitio3.com

# Encontrar keywords comunes del sector
python seo_crawler/main.py compare --sessions 1 2 3
```

## Estructura de Datos

Los datos se almacenan en `seo_crawler/data/seo_crawler.db` (SQLite).

**Tablas principales:**
- `crawl_sessions` - Sesiones de crawling
- `pages` - Páginas crawleadas
- `keywords` - Keywords extraídas con TF-IDF
- `links` - Enlaces encontrados
- `images` - Imágenes con alt text
- `metadata` - Meta tags y structured data

## Reportes Generados

### HTML Report
- Reporte visual completo
- Estadísticas de la sesión
- Top keywords con métricas
- Diseño profesional

### Excel Export
- Múltiples hojas (Session Info, Pages, Keywords)
- Datos estructurados
- Fácil de analizar en Excel/LibreOffice

### CSV Export
- Keywords con todas las métricas
- Importable a Google Sheets
- Compatible con análisis en Python/R

### JSON Export
- Datos completos en formato JSON
- Integrable con APIs
- Procesamiento programático

## Configuración Avanzada

Edita `seo_crawler/config/settings.py` para personalizar:

```python
DEFAULT_CONFIG = {
    'max_pages': 500,              # Cambiar límite de páginas
    'concurrent_requests': 10,      # Ajustar concurrencia
    'crawl_delay': 1.0,            # Delay entre requests
    'stop_words_language': 'spanish', # Idioma stop words
    'min_keyword_length': 3,       # Longitud mínima keyword
}
```

## Solución de Problemas

### Error: ModuleNotFoundError
```bash
pip install -r requirements.txt
```

### GUI no se abre
```bash
# Linux: Instalar tkinter
sudo apt-get install python3-tk

# Verificar
python -m tkinter
```

### Crawl muy lento
```bash
# Aumentar concurrencia y reducir delay
python seo_crawler/main.py crawl --url https://ejemplo.com \
    --concurrent 20 --delay 0.3
```

## Soporte

- 📖 Documentación completa: `README.md`
- 💡 Ejemplos de código: `example_usage.py`
- 🐛 Reportar bugs: GitHub Issues

## Próximos Pasos

1. ✅ Ejecutar tu primer crawl
2. 📊 Analizar los resultados
3. 💾 Exportar reportes
4. 🔍 Comparar con competidores
5. 🚀 Automatizar con cron/scheduler

---

**¡Listo para analizar keywords como un profesional!** 🎯
