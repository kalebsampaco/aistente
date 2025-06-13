from fastapi import APIRouter,  UploadFile, File, HTTPException
import speech_recognition as sr
from app.llm.ollama_client import OllamaClient
from app.sst.voice_output import VoiceOutput
from pydantic import BaseModel
import httpx
import tempfile
import os

router = APIRouter()

class AskRequest(BaseModel):
    question: str

@router.post("/")
async def ask_ollama(req: AskRequest):
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post("http://localhost:11434/api/chat", json={
            "model": "llama3.2",
            # "prompt": req.question,
            "messages": [
                {
                "role": "user",
                "content": req.question
                }
            ],
            "stream": False
        })
        data = response.json()
        data = data.get("message", {})
        print(data)
        return {"answer": data.get("content", "").strip()}

ollama_client = OllamaClient()
voice_output = VoiceOutput()


@router.post("/voice")
async def process_voice(audio_file: UploadFile = File(...)):
    # Guardar temporalmente archivo de audio recibido (wav, mp3, etc)
    suffix = os.path.splitext(audio_file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await audio_file.read())
        tmp_path = tmp.name

    # Procesar audio con speech_recognition
    recognizer = sr.Recognizer()
    with sr.AudioFile(tmp_path) as source:
        audio_data = recognizer.record(source)
    os.unlink(tmp_path)

    try:
        prompt = recognizer.recognize_google(audio_data, language="es-ES")
    except sr.UnknownValueError:
        raise HTTPException(status_code=400, detail="No se entendió el audio")
    except sr.RequestError:
        raise HTTPException(status_code=503, detail="Error en servicio de reconocimiento")

    # Consultar Ollama
    try:
        response_text = await ollama_client.chat(prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en modelo Ollama: {e}")

    # Opcional: generar respuesta TTS en el servidor (no recomendado en API, mejor cliente)
    voice_output.speak(response_text)

    return {"prompt": prompt, "response": response_text}