"""Cliente de embeddings usando OCI Generative AI (Cohere Embed v4) en Chicago."""
import oci

from app.config import (
    OCI_CONFIG_FILE, OCI_CONFIG_PROFILE, OCI_COMPARTMENT_ID,
    GENAI_ENDPOINT, EMBEDDING_MODEL,
)

from app.oci_client import get_genai_client

_client = get_genai_client()


def embed_texts(textos: list[str], input_type: str = "SEARCH_DOCUMENT") -> list[list[float]]:
    """Genera embeddings para una lista de textos.

    input_type: 'SEARCH_DOCUMENT' para indexar, 'SEARCH_QUERY' para consultas.
    Cohere acepta hasta 96 textos por llamada.
    """
    vectores = []
    for i in range(0, len(textos), 96):
        lote = textos[i:i + 96]
        detail = oci.generative_ai_inference.models.EmbedTextDetails(
            inputs=lote,
            serving_mode=oci.generative_ai_inference.models.OnDemandServingMode(
                model_id=EMBEDDING_MODEL
            ),
            compartment_id=OCI_COMPARTMENT_ID,
            input_type=input_type,
            truncate="END",
        )
        response = _client.embed_text(detail)
        vectores.extend(response.data.embeddings)
    return vectores


def embed_query(texto: str) -> list[float]:
    """Genera el embedding de una sola consulta."""
    return embed_texts([texto], input_type="SEARCH_QUERY")[0]
