import os
import oracledb
from dotenv import load_dotenv

load_dotenv()

db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_dsn = os.getenv("DB_DSN")
wallet_dir = os.getenv("WALLET_DIR")
wallet_password = os.getenv("WALLET_PASSWORD")

print("Intentando conectar a Autonomous Database...")

try:
    connection = oracledb.connect(
        user=db_user,
        password=db_password,
        dsn=db_dsn,
        config_dir=wallet_dir,
        wallet_location=wallet_dir,
        wallet_password=wallet_password,
    )
    print("✅ Conexión exitosa!")

    cursor = connection.cursor()
    cursor.execute("SELECT SYSDATE FROM DUAL")
    result = cursor.fetchone()
    print(f"Fecha del servidor: {result[0]}")

    # Verificar versión (importante para saber si tenemos soporte vectorial)
    cursor.execute("SELECT BANNER FROM V$VERSION")
    version = cursor.fetchone()
    print(f"Versión: {version[0]}")

    cursor.close()
    connection.close()
    print("✅ Conexión cerrada correctamente.")

except Exception as e:
    print(f"❌ Error de conexión: {e}")
