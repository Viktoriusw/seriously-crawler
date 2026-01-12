#!/bin/bash
# Script de instalación para SEO Crawler Professional

echo "=================================================="
echo "  SEO Crawler Professional - Setup"
echo "=================================================="
echo ""

# Verificar Python
echo "🔍 Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no está instalado. Por favor, instala Python 3.8 o superior."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Python $PYTHON_VERSION encontrado"

# Crear entorno virtual
echo ""
echo "📦 Creando entorno virtual..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Entorno virtual creado"
else
    echo "ℹ️  Entorno virtual ya existe"
fi

# Activar entorno virtual
echo ""
echo "🔧 Activando entorno virtual..."
source venv/bin/activate

# Actualizar pip
echo ""
echo "📥 Actualizando pip..."
pip install --upgrade pip

# Instalar dependencias
echo ""
echo "📦 Instalando dependencias..."
pip install -r requirements.txt

# Crear directorios necesarios
echo ""
echo "📁 Creando directorios..."
mkdir -p seo_crawler/data
mkdir -p exports
mkdir -p reports

# Verificar instalación
echo ""
echo "✅ Verificando instalación..."
python3 seo_crawler/main.py --help > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Instalación completada exitosamente!"
else
    echo "⚠️  Hubo un problema durante la instalación"
fi

echo ""
echo "=================================================="
echo "  Instalación completada"
echo "=================================================="
echo ""
echo "Para empezar a usar el crawler:"
echo ""
echo "1. Activa el entorno virtual:"
echo "   source venv/bin/activate"
echo ""
echo "2. Lanza la interfaz gráfica:"
echo "   python seo_crawler/main.py gui"
echo ""
echo "3. O usa la línea de comandos:"
echo "   python seo_crawler/main.py crawl --url https://ejemplo.com"
echo ""
echo "Para más información, consulta README.md"
echo ""
