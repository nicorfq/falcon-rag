"""Conexión a Autonomous DB y operaciones con la tabla vectorial."""
import array
import oracledb

from app.config import (
    DB_USER, DB_PASSWORD, DB_DSN, WALLET_DIR, WALLET_PASSWORD,
    EMBEDDING_DIMENSIONS,
)


def get_connection():
    return oracledb.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        dsn=DB_DSN,
        config_dir=WALLET_DIR,
        wallet_location=WALLET_DIR,
        wallet_password=WALLET_PASSWORD,
    )


def crear_tabla():
    """Crea la tabla de chunks vectoriales (borra si existe)."""
    with get_connection() as conn:
        cursor = conn.cursor()
        # Borrar tabla previa si existe
        try:
            cursor.execute("DROP TABLE falcon_chunks")
            print("Tabla previa eliminada.")
        except oracledb.DatabaseError:
            pass  # No existía

        cursor.execute(f"""
            CREATE TABLE falcon_chunks (
                id           NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                texto        CLOB NOT NULL,
                archivo      VARCHAR2(255),
                categoria    VARCHAR2(100),
                chunk_index  NUMBER,
                embedding    VECTOR({EMBEDDING_DIMENSIONS}, FLOAT32)
            )
        """)
        conn.commit()
        print("✅ Tabla falcon_chunks creada.")


def insertar_chunks(chunks: list[dict], vectores: list[list[float]]):
    """Inserta los chunks junto con sus embeddings."""
    with get_connection() as conn:
        cursor = conn.cursor()
        for chunk, vector in zip(chunks, vectores):
            vec = array.array("f", vector)  # FLOAT32
            cursor.execute("""
                INSERT INTO falcon_chunks (texto, archivo, categoria, chunk_index, embedding)
                VALUES (:texto, :archivo, :categoria, :chunk_index, :embedding)
            """, {
                "texto": chunk["texto"],
                "archivo": chunk["archivo"],
                "categoria": chunk["categoria"],
                "chunk_index": chunk["chunk_index"],
                "embedding": vec,
            })
        conn.commit()
        print(f"✅ {len(chunks)} chunks insertados.")


def buscar_similares(vector_consulta: list[float], top_k: int = 5) -> list[dict]:
    """Búsqueda por similitud coseno. Devuelve los top_k chunks más cercanos."""
    with get_connection() as conn:
        cursor = conn.cursor()
        vec = array.array("f", vector_consulta)
        cursor.execute("""
            SELECT texto, archivo, categoria,
                   VECTOR_DISTANCE(embedding, :vec, COSINE) AS distancia
            FROM falcon_chunks
            ORDER BY distancia
            FETCH FIRST :top_k ROWS ONLY
        """, {"vec": vec, "top_k": top_k})

        resultados = []
        for texto, archivo, categoria, distancia in cursor:
            resultados.append({
                "texto": texto.read() if hasattr(texto, "read") else texto,
                "archivo": archivo,
                "categoria": categoria,
                "distancia": distancia,
            })
        return resultados