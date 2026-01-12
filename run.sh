#!/bin/bash
# Script de ejecución rápida del SEO Crawler

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  SEO Crawler Professional${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Verificar si existe el entorno virtual
if [ ! -d "venv" ]; then
    echo "⚠️  No se encontró el entorno virtual."
    echo "Ejecutando instalación..."
    ./setup.sh
    exit 0
fi

# Activar entorno virtual y ejecutar
echo -e "${GREEN}✓ Activando entorno virtual...${NC}"
source venv/bin/activate

# Verificar argumentos
if [ "$1" == "gui" ] || [ -z "$1" ]; then
    echo -e "${GREEN}✓ Lanzando interfaz gráfica...${NC}"
    python seo_crawler/main.py gui
elif [ "$1" == "help" ]; then
    python seo_crawler/main.py --help
else
    # Pasar todos los argumentos al programa
    python seo_crawler/main.py "$@"
fi
