"""Pipeline de ingesta completo: documentos → chunks → embeddings → DB."""
from app.loaders import load_all_documents
from app.chunking import build_chunks
from app.embeddings import embed_texts
from app.vectorstore import crear_tabla, insertar_chunks


def main():
    print("1. Cargando documentos...")
    docs = load_all_documents()

    print("\n2. Generando chunks...")
    chunks = build_chunks(docs)
    print(f"   Total: {len(chunks)} chunks")

    print("\n3. Generando embeddings (puede tardar unos segundos)...")
    textos = [c["texto"] for c in chunks]
    vectores = embed_texts(textos)
    print(f"   {len(vectores)} embeddings generados")

    print("\n4. Creando tabla en Autonomous DB...")
    crear_tabla()

    print("\n5. Insertando chunks...")
    insertar_chunks(chunks, vectores)

    print("\n✅ Ingesta completa.")


if __name__ == "__main__":
    main()