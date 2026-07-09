"""Orquestación RAG: pregunta → recuperación → LLM → respuesta con fuentes."""
import oci

from app.config import (
    OCI_CONFIG_FILE, OCI_CONFIG_PROFILE, OCI_COMPARTMENT_ID,
    GENAI_ENDPOINT, LLM_MODEL,
)
from app.embeddings import embed_query
from app.vectorstore import buscar_similares

from app.oci_client import get_genai_client

_client = get_genai_client()

# Umbral: si el mejor resultado supera esta distancia, no hay info suficiente
UMBRAL_DISTANCIA = 0.70
UMBRAL_FUENTE = 0.55

PROMPT_SISTEMA = """Eres el asistente virtual de RutaSur Logística, una empresa chilena de mensajería y última milla.

Tu tarea es responder preguntas de los colaboradores basándote ÚNICAMENTE en el contexto proporcionado de los documentos internos de la empresa.

Reglas importantes:
- Responde solo con información que esté en el contexto. No inventes datos.
- Si el contexto no contiene la información necesaria, indícalo claramente diciendo: "No encontré esta información en los documentos disponibles" y sugiere contactar al área correspondiente.
- Cita siempre el documento del que extraes la información.
- Sé claro, directo y profesional.
- Responde en español."""


def construir_contexto(resultados: list[dict]) -> str:
    partes = []
    for r in resultados:
        partes.append(f"[Documento: {r['archivo']} | Categoría: {r['categoria']}]\n{r['texto']}")
    return "\n\n---\n\n".join(partes)


def responder(pregunta: str, top_k: int = 5) -> dict:
    """Ejecuta el pipeline RAG completo y devuelve respuesta + fuentes."""
    # 1. Recuperar
    vector = embed_query(pregunta)
    resultados = buscar_similares(vector, top_k=top_k)

    # 2. Verificar umbral de confianza
    if not resultados or resultados[0]["distancia"] > UMBRAL_DISTANCIA:
        return {
            "respuesta": "No encontré esta información en los documentos disponibles. "
                         "Te sugiero contactar al área correspondiente para obtener ayuda.",
            "fuentes": [],
        }

    # 3. Construir contexto
    contexto = construir_contexto(resultados)

    # 4. Llamar al LLM
    mensaje = f"""Contexto de los documentos internos:

{contexto}

---

Pregunta del colaborador: {pregunta}

Responde basándote únicamente en el contexto anterior."""

# Mensaje de sistema (rol SYSTEM para Llama)
    system_content = oci.generative_ai_inference.models.TextContent(text=PROMPT_SISTEMA)
    system_message = oci.generative_ai_inference.models.Message(
        role="SYSTEM", content=[system_content]
    )

    # Mensaje del usuario
    user_content = oci.generative_ai_inference.models.TextContent(text=mensaje)
    user_message = oci.generative_ai_inference.models.Message(
        role="USER", content=[user_content]
    )

    chat_request = oci.generative_ai_inference.models.GenericChatRequest(
        api_format=oci.generative_ai_inference.models.BaseChatRequest.API_FORMAT_GENERIC,
        messages=[system_message, user_message],
        max_tokens=600,
        temperature=0.2,
    )

    chat_detail = oci.generative_ai_inference.models.ChatDetails(
        compartment_id=OCI_COMPARTMENT_ID,
        serving_mode=oci.generative_ai_inference.models.OnDemandServingMode(model_id=LLM_MODEL),
        chat_request=chat_request,
    )

    response = _client.chat(chat_detail)
    texto_respuesta = response.data.chat_response.choices[0].message.content[0].text

   # 5. Fuentes únicas (solo las realmente relevantes, por debajo del umbral)
    fuentes = list({
        r["archivo"] for r in resultados
        if r["distancia"] <= UMBRAL_FUENTE
    })
    # Respaldo: si el filtro deja todo fuera pero sí hubo respuesta,
    # incluir al menos la fuente más cercana
    if not fuentes and resultados:
        fuentes = [resultados[0]["archivo"]]

    return {
        "respuesta": texto_respuesta,
        "fuentes": fuentes,
    }
