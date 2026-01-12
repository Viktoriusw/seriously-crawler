# 📦 Guía Completa de Instalación - SEO Crawler Professional

## ✅ TODOS LOS ERRORES CORREGIDOS

Esta guía te ayudará a instalar el SEO Crawler correctamente, evitando todos los errores comunes.

---

## 🚨 ERROR COMÚN: "externally-managed-environment"

Si intentas instalar con `pip install` directamente y ves este error:

```
error: externally-managed-environment
× This environment is externally managed
```

**✅ SOLUCIÓN:** DEBES usar un entorno virtual (venv). Es OBLIGATORIO en sistemas modernos de Linux.

---

## 📋 Instalación Paso a Paso (Linux)

### Paso 1: Verificar Python

```bash
python3 --version
# Debe ser 3.8 o superior
```

Si no tienes Python 3.8+:
```bash
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv python3-tk
```

### Paso 2: Navegar al proyecto

```bash
cd /ruta/a/crawlerserio
```

### Paso 3: Crear entorno virtual

```bash
python3 -m venv venv
```

Esto crea una carpeta `venv/` con un Python aislado.

### Paso 4: Activar entorno virtual

```bash
source venv/bin/activate
```

**✅ VERIFICAR:** Deberías ver `(venv)` al inicio de tu línea de comandos:
```
(venv) usuario@pc:~/crawlerserio$
```

### Paso 5: Actualizar pip

```bash
pip install --upgrade pip
```

### Paso 6: Instalar dependencias

```bash
pip install -r requirements.txt
```

Este proceso tarda 1-3 minutos. Verás output como:
```
Collecting aiohttp>=3.9.0
Downloading aiohttp-3.9.1-cp312-cp312-manylinux...
Installing collected packages: aiohttp, aiosqlite...
Successfully installed aiohttp-3.9.1 aiosqlite-0.19.0 ...
```

### Paso 7: Verificar instalación

```bash
python seo_crawler/main.py --help
```

Deberías ver:
```
usage: main.py [-h] {crawl,analyze,report,list,compare,gui} ...

SEO Crawler - Professional SEO Analysis Tool
```

### Paso 8: Lanzar el programa

```bash
# Interfaz gráfica
python seo_crawler/main.py gui

# O usando el script rápido
./run.sh
```

---

## 📋 Instalación Paso a Paso (Windows)

### Paso 1: Verificar Python

Abrir PowerShell o Command Prompt:

```bash
python --version
# Debe ser 3.8 o superior
```

Si no tienes Python, descárgalo de [python.org](https://www.python.org/downloads/)

### Paso 2: Navegar al proyecto

```bash
cd C:\ruta\a\crawlerserio
```

### Paso 3: Crear entorno virtual

```bash
python -m venv venv
```

### Paso 4: Activar entorno virtual

En PowerShell:
```powershell
venv\Scripts\Activate.ps1
```

En Command Prompt (cmd):
```bash
venv\Scripts\activate.bat
```

**Si tienes error de permisos en PowerShell:**
```powershell
# Ejecutar como Administrador:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# Luego volver a intentar activar
```

**✅ VERIFICAR:** Deberías ver `(venv)` al inicio:
```
(venv) C:\crawlerserio>
```

### Paso 5: Actualizar pip

```bash
python -m pip install --upgrade pip
```

### Paso 6: Instalar dependencias

```bash
pip install -r requirements.txt
```

### Paso 7: Verificar instalación

```bash
python seo_crawler\main.py --help
```

### Paso 8: Lanzar el programa

```bash
# Interfaz gráfica
python seo_crawler\main.py gui

# O usando el script rápido
run.bat
```

---

## 🔧 Uso del Entorno Virtual

### ✅ Activar el entorno (SIEMPRE antes de usar el programa)

**Linux/Mac:**
```bash
cd /ruta/a/crawlerserio
source venv/bin/activate
```

**Windows (PowerShell):**
```powershell
cd C:\ruta\a\crawlerserio
venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```bash
cd C:\ruta\a\crawlerserio
venv\Scripts\activate.bat
```

### ❌ Desactivar el entorno (cuando termines)

```bash
deactivate
```

### 🔍 Verificar si está activado

Mira tu línea de comandos:
```
(venv) ~/crawlerserio$     ← ✅ ACTIVADO (correcto)
~/crawlerserio$            ← ❌ DESACTIVADO (no funcionará)
```

---

## 🚀 Scripts de Ejecución Rápida

Para no tener que activar manualmente cada vez, usa los scripts:

### Linux/Mac:
```bash
./run.sh          # Lanza la GUI automáticamente
./run.sh gui      # Lanza la GUI
./run.sh help     # Muestra ayuda
./run.sh crawl --url https://ejemplo.com  # Crawl desde CLI
```

### Windows:
```bash
run.bat           # Lanza la GUI automáticamente
run.bat gui       # Lanza la GUI
run.bat help      # Muestra ayuda
run.bat crawl --url https://ejemplo.com  # Crawl desde CLI
```

---

## ❌ Solución de Errores Comunes

### Error 1: "No module named 'aiosqlite'"

**Causa:** No has activado el entorno virtual o no instalaste las dependencias.

**Solución:**
```bash
# Activar entorno
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Reinstalar dependencias
pip install -r requirements.txt
```

### Error 2: "NameError: name 'Optional' is not defined"

**Causa:** Error en el código (ya corregido).

**Solución:** Asegúrate de tener la última versión del código.

### Error 3: "externally-managed-environment"

**Causa:** Intentaste instalar sin entorno virtual en Linux moderno.

**Solución:** DEBES usar venv. Sigue los pasos de esta guía.

### Error 4: "python: command not found"

**Causa:** Python no está instalado o no está en el PATH.

**Solución:**
```bash
# Linux
sudo apt-get install python3

# Usa python3 en lugar de python
python3 --version
python3 -m venv venv
```

### Error 5: "No module named 'tkinter'"

**Causa:** tkinter no está instalado.

**Solución:**
```bash
# Linux
sudo apt-get install python3-tk

# Windows: Reinstala Python marcando "tcl/tk and IDLE"
```

### Error 6: "Cannot activate venv on Windows"

**Causa:** Restricciones de PowerShell.

**Solución:**
```powershell
# Como Administrador en PowerShell:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

O usa Command Prompt (cmd) en lugar de PowerShell.

### Error 7: El entorno virtual no funciona

**Solución:** Recrea el entorno:
```bash
# Eliminar venv
rm -rf venv       # Linux/Mac
rmdir /s venv     # Windows

# Recrear
python3 -m venv venv  # Linux/Mac
python -m venv venv   # Windows

# Activar y reinstalar
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

---

## ✅ Checklist de Instalación Exitosa

Marca cada item cuando lo completes:

- [ ] Python 3.8+ instalado y verificado
- [ ] Entorno virtual creado (`venv/` existe)
- [ ] Entorno virtual activado (ves `(venv)` en tu terminal)
- [ ] Dependencias instaladas sin errores
- [ ] `python seo_crawler/main.py --help` funciona
- [ ] La GUI se abre sin errores

Si marcaste todos los items, ¡estás listo para usar el crawler! 🎉

---

## 📊 Verificación Final

Ejecuta estos comandos para verificar todo:

```bash
# 1. Verificar Python
python --version
# Output esperado: Python 3.8.x o superior

# 2. Verificar que venv está activado
# Deberías ver (venv) en tu línea de comandos

# 3. Verificar dependencias clave
pip show aiohttp
pip show beautifulsoup4
pip show pandas
# Cada uno debe mostrar información del paquete

# 4. Verificar programa
python seo_crawler/main.py --help
# Debe mostrar el menú de ayuda

# 5. Probar GUI (debe abrir ventana)
python seo_crawler/main.py gui
```

---

## 🆘 ¿Sigues teniendo problemas?

1. **Verifica que estés en la carpeta correcta:**
   ```bash
   pwd  # Linux/Mac
   cd   # Windows
   # Debes estar en /ruta/a/crawlerserio
   ```

2. **Verifica que el entorno esté activado:**
   ```bash
   which python  # Linux/Mac
   where python  # Windows
   # Debe mostrar la ruta dentro de venv/
   ```

3. **Reinstala todo desde cero:**
   ```bash
   # Eliminar venv
   rm -rf venv

   # Seguir la guía completa desde el Paso 3
   ```

4. **Revisa el README.md** para más detalles

5. **Consulta QUICKSTART.md** para guía rápida

---

## 💡 Consejos Finales

- ✅ **SIEMPRE** activa el entorno virtual antes de usar el programa
- ✅ Usa los scripts `run.sh` (Linux) o `run.bat` (Windows) para facilitar el uso
- ✅ Si actualizas el código, puede que necesites reinstalar dependencias
- ✅ El entorno virtual es específico de este proyecto, no afecta tu Python global
- ✅ Puedes crear diferentes entornos virtuales para diferentes proyectos

---

**¡Ya estás listo para analizar keywords como un profesional!** 🚀
