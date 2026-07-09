"""Cliente compartido de OCI Generative AI con autenticación flexible.

Detecta automáticamente el modo:
- config_file: usa ~/.oci/config (desarrollo local en el Ryzen)
- instance_principal: usa la identidad de la VM (producción en OCI)
"""
import oci

from app.config import (
    OCI_AUTH_MODE, OCI_CONFIG_FILE, OCI_CONFIG_PROFILE, GENAI_ENDPOINT,
)


def get_genai_client():
    if OCI_AUTH_MODE == "instance_principal":
        # Autenticación por Instance Principals (VM en OCI)
        signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
        return oci.generative_ai_inference.GenerativeAiInferenceClient(
            config={},
            signer=signer,
            service_endpoint=GENAI_ENDPOINT,
        )
    else:
        # Autenticación por archivo de config (desarrollo local)
        config = oci.config.from_file(OCI_CONFIG_FILE, OCI_CONFIG_PROFILE)
        return oci.generative_ai_inference.GenerativeAiInferenceClient(
            config=config,
            service_endpoint=GENAI_ENDPOINT,
        )