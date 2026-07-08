# Falcon-RAG 🦅

Agente de inteligencia artificial corporativo para **RutaSur Logística**, una empresa ficticia chilena de mensajería y última milla. Falcon-RAG responde preguntas de los colaboradores basándose en los documentos internos de la empresa, usando RAG (Retrieval-Augmented Generation) sobre Oracle Cloud Infrastructure.

> Proyecto desarrollado para el Challenge de Alura LATAM — Oracle Next Education (ONE).

---

## ¿Qué hace?

Falcon-RAG es una base de conocimiento conversacional que:

- Procesa documentos internos en **8 formatos**: PDF, Word, Excel, PowerPoint, Markdown, CSV, JSON y HTML.
- Responde preguntas en lenguaje natural **citando siempre la fuente** de donde extrae la información.
- **Reconoce cuándo no tiene la información** y lo indica claramente, en lugar de inventar respuestas.
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

Arquitectura multi-región: los datos residen en Santiago, la inferencia de IA se realiza en Chicago mediante llamadas cross-region.

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

- **OCI Compute** — instancia Ampere A1 (Ubuntu 24.04) que hospeda la aplicación.
- **Oracle Autonomous AI Database 26ai** — almacenamiento y búsqueda vectorial nativa.
- **OCI Generative AI** — modelos de embeddings y lenguaje (Cohere + Llama).
- **OCI Object Storage** — almacenamiento de los documentos originales.

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

## Instalación local

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
# Editar .env con tus credenciales de OCI

# Colocar el wallet de Autonomous Database en ./wallet/

# Ejecutar la ingesta de documentos
python -m app.ingest

# Levantar el servidor
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## Requisitos previos

- Python 3.11+
- Cuenta de OCI con acceso a Generative AI (región Chicago) y Autonomous Database
- Wallet de conexión de Autonomous Database

---

## Demo del agente en la nube

> ⏳ _Pendiente: imagen/video del agente ejecutándose en OCI._

---

## Estructura del proyecto

```
falcon-rag/
├── app/
│   ├── main.py            # FastAPI: API + interfaz de chat
│   ├── config.py          # Configuración y variables de entorno
│   ├── loaders.py         # Extracción de texto (8 formatos)
│   ├── chunking.py        # División en fragmentos + metadatos
│   ├── embeddings.py      # Cliente de embeddings (Cohere)
│   ├── vectorstore.py     # Conexión y búsqueda en Autonomous DB
│   ├── rag.py             # Orquestación del pipeline RAG
│   └── ingest.py          # Script de ingesta de documentos
├── static/                # Interfaz web (HTML/JS)
├── documents/             # Documentos de RutaSur Logística
├── evaluation/            # Banco de preguntas de prueba
├── .env.example           # Plantilla de variables de entorno
├── requirements.txt
└── README.md
```

---

## Licencia

Proyecto educativo desarrollado para el programa Oracle Next Education (ONE) de Alura LATAM.