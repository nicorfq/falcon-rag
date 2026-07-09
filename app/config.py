import os
from dotenv import load_dotenv

load_dotenv()

# --- Autonomous Database (Santiago) ---
DB_USER = os.getenv("DB_USER", "ADMIN")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DSN = os.getenv("DB_DSN", "sbitzazd39dte22n_high")
WALLET_DIR = os.getenv("WALLET_DIR", "./wallet")
WALLET_PASSWORD = os.getenv("WALLET_PASSWORD")

# --- OCI Generative AI (Chicago) ---
OCI_CONFIG_FILE = os.getenv("OCI_CONFIG_FILE", "~/.oci/config")
OCI_CONFIG_PROFILE = os.getenv("OCI_CONFIG_PROFILE", "DEFAULT")
OCI_COMPARTMENT_ID = os.getenv("OCI_COMPARTMENT_ID")
# Modo de autenticación OCI: "config_file" (local) o "instance_principal" (VM)
OCI_AUTH_MODE = os.getenv("OCI_AUTH_MODE", "config_file")
GENAI_ENDPOINT = os.getenv(
    "GENAI_ENDPOINT",
    "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com",
)

# --- Modelos ---
EMBEDDING_MODEL = "cohere.embed-v4.0"
LLM_MODEL = "meta.llama-3.3-70b-instruct"
EMBEDDING_DIMENSIONS = 1536
