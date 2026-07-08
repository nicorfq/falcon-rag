import oci
from app.config import (
    OCI_CONFIG_FILE, OCI_CONFIG_PROFILE, OCI_COMPARTMENT_ID,
    GENAI_ENDPOINT, EMBEDDING_MODEL,
)

config = oci.config.from_file(OCI_CONFIG_FILE, OCI_CONFIG_PROFILE)

client = oci.generative_ai_inference.GenerativeAiInferenceClient(
    config=config,
    service_endpoint=GENAI_ENDPOINT,
)

print("Probando embeddings con cohere.embed-v4.0 en Chicago...")

embed_detail = oci.generative_ai_inference.models.EmbedTextDetails(
    inputs=["RutaSur entrega paquetes en todo Chile continental."],
    serving_mode=oci.generative_ai_inference.models.OnDemandServingMode(
        model_id=EMBEDDING_MODEL
    ),
    compartment_id=OCI_COMPARTMENT_ID,
    truncate="END",
)

try:
    response = client.embed_text(embed_detail)
    vector = response.data.embeddings[0]
    print(f"✅ Embedding generado correctamente!")
    print(f"Dimensiones: {len(vector)}")
    print(f"Primeros 5 valores: {vector[:5]}")
except Exception as e:
    print(f"❌ Error: {e}")
