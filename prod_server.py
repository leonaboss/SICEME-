import os
import sys
from waitress import serve
from Registros.wsgi import application

# Asegurar que el directorio raíz esté en el path de Python
sys.path.append(os.getcwd())

if __name__ == "__main__":
    # Mensaje de bienvenida profesional
    print("\n" + "="*50)
    print("   SICEME - SERVIDOR DE PRODUCCIÓN ACTIVO")
    print("="*50)
    print("\n[INFO] Host: 0.0.0.0 (Accesible en la red)")
    print("[INFO] Puerto: 8000")
    print("[INFO] Hilos de procesamiento: 6")
    print("\n>>> El sistema está listo. Abre http://localhost:8000 en tu navegador.")
    print(">>> Presiona Ctrl+C para apagar el servidor de forma segura.\n")
    
    # Iniciar servidor Waitress
    serve(application, host='0.0.0.0', port=8000, threads=6)
