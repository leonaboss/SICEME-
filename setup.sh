#!/bin/bash
# ============================================================
#  SICEME - Script de Configuración Automática
#  Ejecutar una sola vez al desplegar en un nuevo servidor
# ============================================================

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # Sin color

echo ""
echo "============================================"
echo "   SICEME - Configuración Automática"
echo "============================================"
echo ""

# --- Paso 1: Crear entorno virtual si no existe ---
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}[1/4] Creando entorno virtual...${NC}"
    python3 -m venv .venv
else
    echo -e "${GREEN}[1/4] Entorno virtual ya existe. OK${NC}"
fi

# Activar entorno virtual
source .venv/bin/activate

# --- Paso 2: Instalar dependencias ---
echo -e "${YELLOW}[2/4] Instalando dependencias...${NC}"
pip install -r requirements.txt -q
echo -e "${GREEN}[2/4] Dependencias instaladas. OK${NC}"

# --- Paso 3: Crear .env si no existe ---
if [ ! -f ".env" ]; then
    echo ""
    echo -e "${YELLOW}[3/4] Configurando base de datos...${NC}"
    echo "      (Deja en blanco para usar los valores por defecto)"
    echo ""

    read -p "  Nombre de la BD       [siceme]: " DB_NAME
    DB_NAME=${DB_NAME:-siceme}

    read -p "  Usuario de MySQL       [root]: " DB_USER
    DB_USER=${DB_USER:-root}

    read -s -p "  Contraseña de MySQL       []: " DB_PASSWORD
    echo ""
    DB_PASSWORD=${DB_PASSWORD:-}

    read -p "  Host de MySQL  [127.0.0.1]: " DB_HOST
    DB_HOST=${DB_HOST:-127.0.0.1}

    read -p "  Puerto de MySQL     [3306]: " DB_PORT
    DB_PORT=${DB_PORT:-3306}

    # Generar SECRET_KEY segura
    SECRET_KEY=$(python3 -c "import secrets, string; print(''.join(secrets.choice(string.ascii_letters + string.digits + '!@#\$%^&*') for _ in range(50)))")

    # Crear el archivo .env
    cat > .env << EOF
SECRET_KEY=${SECRET_KEY}
DEBUG=False

# Base de Datos
DB_NAME=${DB_NAME}
DB_USER=${DB_USER}
DB_PASSWORD=${DB_PASSWORD}
DB_HOST=${DB_HOST}
DB_PORT=${DB_PORT}
EOF

    echo -e "${GREEN}[3/4] Archivo .env creado correctamente. OK${NC}"
else
    echo -e "${GREEN}[3/4] Archivo .env ya existe. OK${NC}"
fi

# --- Paso 4: Crear base de datos y ejecutar migraciones ---
echo -e "${YELLOW}[4/4] Ejecutando migraciones...${NC}"

# Cargar variables del .env
export $(grep -v '^#' .env | xargs)

# Crear la base de datos si no existe
python3 -c "
import MySQLdb
try:
    conn = MySQLdb.connect(
        host='${DB_HOST:-127.0.0.1}',
        user='${DB_USER:-root}',
        password='${DB_PASSWORD:-}',
        port=int('${DB_PORT:-3306}')
    )
    conn.query('CREATE DATABASE IF NOT EXISTS \`${DB_NAME:-siceme}\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;')
    conn.close()
    print('  Base de datos lista.')
except Exception as e:
    print(f'  Aviso: {e}')
" 2>/dev/null

python3 manage.py migrate --run-syncdb
echo -e "${GREEN}[4/4] Migraciones completadas. OK${NC}"

echo ""
echo "============================================"
echo -e "${GREEN}  SICEME configurado exitosamente!${NC}"
echo "  Ejecuta: python3 manage.py runserver"
echo "============================================"
echo ""
