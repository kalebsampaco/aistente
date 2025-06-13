import httpx
from typing import List, Dict

class OllamaClient:
    def __init__(self, model: str = "llama3.2", host: str = "http://localhost:11434", max_history: int = 10) -> None:
        self.model = model
        self.url = f"{host}/api/chat"
        self.timeout = 60.0
        self.max_history = max_history
        self.messages: List[Dict[str, str]] = []

    def _trim_history(self) -> None:
        # Mantener solo los últimos max_history mensajes (pares usuario+asistente)
        # Por ejemplo, max_history=10 implica 5 pares, 10 mensajes en total.
        if len(self.messages) > self.max_history:
            # recortar mensajes antiguos, manteniendo los más recientes
            self.messages = self.messages[-self.max_history:]

    async def chat(self, prompt: str) -> str:
        self.messages.append({"role": "user", "content": prompt})
        self._trim_history()

        payload = {
            "model": self.model,
            "messages": self.messages,
            "stream": False
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(self.url, json=payload)
                response.raise_for_status()
                assistant_message = response.json()["message"]["content"]
                self.messages.append({"role": "assistant", "content": assistant_message})
                self._trim_history()
                return assistant_message

            except httpx.HTTPStatusError as e:
                print(f"❌ Error HTTP {e.response.status_code}: {e.response.text}")
            except httpx.RequestError as e:
                print(f"⚠️ Error de conexión con Ollama: {e}")

            return "No se pudo obtener una respuesta del modelo."
