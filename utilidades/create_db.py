import MySQLdb
import os

DB_USER = 'root'
DB_PASSWORD = '123456'
DB_HOST = 'localhost'
DB_PORT = 3306
DB_NAME = 'siceme_db'

try:
    print(f"Conectando a MySQL como {DB_USER}...")
    db = MySQLdb.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASSWORD, port=DB_PORT)
    cursor = db.cursor()
    
    print(f"Recreando base de datos '{DB_NAME}'...")
    cursor.execute(f"DROP DATABASE IF EXISTS {DB_NAME};")
    cursor.execute(f"CREATE DATABASE {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    print("Base de datos creada/verificada correctamente.")
    
    cursor.close()
    db.close()
except Exception as e:
    print(f"Error: {e}")
