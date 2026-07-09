# Falcon-RAG 🦅

Agente de inteligencia artificial corporativo para **RutaSur Logística**, una empresa ficticia chilena de mensajería y última milla. Falcon-RAG responde preguntas de los colaboradores basándose en los documentos internos de la empresa, usando RAG (Retrieval-Augmented Generation) desplegado sobre Oracle Cloud Infrastructure.

> Proyecto desarrollado para el Challenge de Alura LATAM — Oracle Next Education (ONE).

---

## Demo del agente en la nube

El agente está desplegado y en ejecución sobre una instancia de OCI Compute, accesible públicamente a través de la IP de la instancia.

https://github.com/user-attachments/assets/06f5356e-7a8c-450c-bf97-74cf26386130

---

## ¿Qué hace?

Falcon-RAG es una base de conocimiento conversacional que:

- Procesa documentos internos en **8 formatos**: PDF, Word, Excel, PowerPoint, Markdown, CSV, JSON y HTML.
- Responde preguntas en lenguaje natural **citando siempre la fuente** de donde extrae la información.
- **Reconoce cuándo no tiene la información** y lo indica claramente, en lugar de inventar respuestas (sin alucinaciones).
- Está desplegado en la nube de Oracle (OCI), accesible para cualquier colaborador.

---

## Arquitectura

| Componente | Tecnología | Ubicación |
|---|---|---|
| Backend + Interfaz | FastAPI (Python) | OCI Compute (Santiago) |
| Base de datos vectorial | Oracle Autonomous AI Database 26ai | OCI (Santiago) |
| Embeddings | Cohere Embed v4 (1536 dim) | OCI Generative AI (Chicago) |
| Modelo de lenguaje | Meta Llama 3.3 70B Instruct | OCI Generative AI (Chicago) |
| Almacenamiento de documentos | OCI Object Storage | OCI (Santiago) |

**Arquitectura multi-región:** los datos residen en Santiago (\`sa-santiago-1\`), mientras que la inferencia de IA se realiza en Chicago (\`us-chicago-1\`) mediante llamadas cross-region, ya que OCI Generative AI opera desde esa región.

**Autenticación sin llaves:** en producción, la VM se autentica ante OCI Generative AI mediante **Instance Principals**, evitando almacenar credenciales de API en el servidor. En desarrollo local se usa el archivo de configuración de OCI. El código detecta automáticamente el modo según el entorno.

### Pipeline RAG

```
Documentos (8 formatos)
    → Extracción de texto (loaders)
    → Chunking con overlap + metadatos (categoría, archivo)
    → Embeddings (Cohere Embed v4)
    → Almacenamiento vectorial (Autonomous DB 26ai)

Pregunta del colaborador
    → Embedding de la consulta
    → Búsqueda por similitud coseno (top-K)
    → Umbral de confianza + filtrado de fuentes
    → Generación con contexto (Llama 3.3)
    → Respuesta con fuentes citadas
```

---

## Servicios de OCI utilizados

Aunque el challenge exige usar al menos un servicio de OCI, este proyecto integra **cuatro**:

- **OCI Compute** — instancia Ampere A1 (Ubuntu 24.04) que hospeda la aplicación en contenedor Docker.
- **Oracle Autonomous AI Database 26ai** — almacenamiento y búsqueda vectorial nativa (tipo \`VECTOR\`, distancia coseno).
- **OCI Generative AI** — modelos de embeddings (Cohere Embed v4) y lenguaje (Llama 3.3).
- **OCI Object Storage** — almacenamiento de los documentos originales.

Además se emplea **OCI IAM** (Dynamic Groups + Policies) para habilitar la autenticación por Instance Principals.

---

## Categorías de documentos (RutaSur Logística)

Los documentos cubren distintos dominios organizacionales:

| Documento | Formato | Categoría |
|---|---|---|
| Política de Envíos y Entregas | PDF | Operacional |
| Política de Reembolsos y Siniestros | PDF | Legal y Compliance |
| Preguntas Frecuentes (FAQ) | PDF | Comunicación Interna |
| Procedimiento de Rastreo | PDF | Operacional |
| Proceso de Reclamos | PDF | Legal y Compliance |
| Manual de Onboarding de Repartidores | Word | Recursos Humanos |
| Tarifas y Comisiones | Excel | Financiero |
| Presentación Corporativa | PowerPoint | Estratégico |
| API de Rastreo (mock) | JSON | Datos y Sistemas |
| README del Sistema de Rastreo | Markdown | Datos y Sistemas |
| Newsletter Interno | HTML | Comunicación Interna |

---

## Interfaz

La interfaz de chat incluye los elementos recomendados para un agente corporativo:

- Indicación clara de que se conversa con un agente de IA.
- Visualización de las **fuentes citadas** en cada respuesta.
- Botón de **feedback** (👍/👎) por respuesta.
- **Historial de conversación** dentro de la sesión.

---

## Instalación local (desarrollo)

```bash
# Clonar el repositorio
git clone https://github.com/TU_USUARIO/falcon-rag.git
cd falcon-rag

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales de OCI (modo config_file para local)

# Colocar el wallet de Autonomous Database en ./wallet/

# Ejecutar la ingesta de documentos
python -m app.ingest

# Levantar el servidor
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## Despliegue en OCI (producción)

El despliegue se realiza sobre una instancia de OCI Compute mediante Docker:

```bash
# En la VM de OCI (Ubuntu 24.04, Ampere A1)
git clone https://github.com/TU_USUARIO/falcon-rag.git
cd falcon-rag

# Transferir el wallet y el .env de forma segura (scp), fuera del repo
# Configurar OCI_AUTH_MODE=instance_principal en el .env

# Construir la imagen
docker build -t falcon-rag .

# Ejecutar el contenedor (wallet montado como volumen)
docker run -d \\
  --name falcon-rag \\
  -p 8000:8000 \\
  --env-file .env \\
  -v ~/falcon-rag/wallet:/app/wallet \\
  falcon-rag
```

La autenticación ante OCI Generative AI se resuelve automáticamente mediante Instance Principals (sin llaves API en el servidor), gracias a un Dynamic Group y una Policy de IAM que autorizan a la instancia a usar el servicio.

---

## Requisitos previos

- Python 3.11+
- Cuenta de OCI con acceso a Generative AI (región Chicago) y Autonomous Database
- Wallet de conexión de Autonomous Database
- Docker (para el despliegue en la VM)

---

## Estructura del proyecto

```
falcon-rag/
├── app/
│   ├── main.py            # FastAPI: API + interfaz de chat
│   ├── config.py          # Configuración y variables de entorno
│   ├── oci_client.py      # Cliente OCI con autenticación flexible
│   ├── loaders.py         # Extracción de texto (8 formatos)
│   ├── chunking.py        # División en fragmentos + metadatos
│   ├── embeddings.py      # Cliente de embeddings (Cohere)
│   ├── vectorstore.py     # Conexión y búsqueda en Autonomous DB
│   ├── rag.py             # Orquestación del pipeline RAG
│   └── ingest.py          # Script de ingesta de documentos
├── static/                # Interfaz web (HTML/JS)
├── documents/             # Documentos de RutaSur Logística
├── evaluation/            # Banco de preguntas de prueba
├── Dockerfile
├── .dockerignore
├── .env.example           # Plantilla de variables de entorno
├── requirements.txt
└── README.md
```

---

## Stack técnico

- **Python 3.12** · FastAPI · Uvicorn
- **Oracle Autonomous AI Database 26ai** (AI Vector Search nativo)
- **OCI Generative AI** — Cohere Embed v4 + Meta Llama 3.3 70B
- **Docker** para contenerización
- **OCI**: Compute (Ampere A1), Object Storage, IAM (Instance Principals)

---

## Licencia

Proyecto educativo desarrollado para el programa Oracle Next Education (ONE) de Alura LATAM.
