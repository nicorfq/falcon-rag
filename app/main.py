"""FastAPI: expone la API del agente RAG y sirve la interfaz de chat."""
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.rag import responder

app = FastAPI(title="Falcon-RAG", description="Agente corporativo de RutaSur Logística")

STATIC_DIR = Path(__file__).parent.parent / "static"


class PreguntaRequest(BaseModel):
    pregunta: str


class RespuestaResponse(BaseModel):
    respuesta: str
    fuentes: list[str]


@app.post("/api/chat", response_model=RespuestaResponse)
def chat(req: PreguntaRequest):
    """Recibe una pregunta y devuelve la respuesta del agente con sus fuentes."""
    resultado = responder(req.pregunta)
    return RespuestaResponse(
        respuesta=resultado["respuesta"],
        fuentes=resultado["fuentes"],
    )


@app.get("/api/health")
def health():
    """Endpoint de salud para verificar que el servicio está activo."""
    return {"status": "ok", "servicio": "Falcon-RAG"}


@app.get("/")
def index():
    """Sirve la interfaz de chat."""
    return FileResponse(STATIC_DIR / "index.html")


# Servir archivos estáticos (por si agregamos CSS/JS externos después)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")