"""Chunking simple por tamaño con overlap, más asignación de metadatos."""
from pathlib import Path


# Mapeo de cada documento a su categoría organizacional
CATEGORIAS = {
    "Politica_de_Envios_y_Entregas.pdf": "Operacional",
    "Politica_de_Reembolsos_y_Siniestros.pdf": "Legal y Compliance",
    "Preguntas_Frecuentes_FAQ.pdf": "Comunicación Interna",
    "Procedimiento_de_Rastreo.pdf": "Operacional",
    "Proceso_de_Reclamos.pdf": "Legal y Compliance",
    "Manual_Onboarding_Repartidores.docx": "Recursos Humanos",
    "Tarifas_RutaSur.xlsx": "Financiero",
    "Presentacion_Corporativa_RutaSur.pptx": "Estratégico",
    "API_Rastreo_RutaSur.json": "Datos y Sistemas",
    "README_Sistema_Rastreo.md": "Datos y Sistemas",
    "Newsletter_Interno_RutaSur.html": "Comunicación Interna",
}


def chunk_text(texto: str, chunk_size: int = 800, overlap: int = 150) -> list[str]:
    """Divide el texto en fragmentos de tamaño fijo con solapamiento.

    Intenta cortar en saltos de párrafo cercanos para no partir ideas.
    """
    if len(texto) <= chunk_size:
        return [texto]

    chunks = []
    inicio = 0
    while inicio < len(texto):
        fin = inicio + chunk_size
        # Intentar cortar en un salto de línea cercano al final
        if fin < len(texto):
            corte = texto.rfind("\n", inicio, fin)
            if corte > inicio + chunk_size // 2:
                fin = corte
        chunk = texto[inicio:fin].strip()
        if chunk:
            chunks.append(chunk)
        inicio = fin - overlap
    return chunks


def build_chunks(documentos: dict[str, str]) -> list[dict]:
    """Convierte {nombre: texto} en una lista de chunks con metadatos."""
    todos = []
    for nombre, texto in documentos.items():
        categoria = CATEGORIAS.get(nombre, "General")
        fragmentos = chunk_text(texto)
        for idx, frag in enumerate(fragmentos):
            todos.append({
                "texto": frag,
                "archivo": nombre,
                "categoria": categoria,
                "chunk_index": idx,
            })
    return todos
