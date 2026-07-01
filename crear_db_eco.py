import sqlite3
import os

if os.path.exists("ecoruta.db"):
    os.remove("ecoruta.db")

conexion = sqlite3.connect("ecoruta.db")

with open("crear_db_eco.sql", "r", encoding="utf-8") as archivo:
    script_sql = archivo.read()

conexion.executescript(script_sql)

conexion.close()

print("✅ Base de datos y tablas creadas correctamente.")