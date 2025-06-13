import asyncio
import json
from app.core.constants import ASSISTANT_NAME, USER_NAME
from app.sst.voice_input import VoiceInput
from app.sst.voice_output import VoiceOutput
from app.llm.ollama_client import OllamaClient
from app.services import task_service
from app.services.calendar_service import GoogleCalendar
from app.services.command_parser import parse_llm_response
from app.services.ollama_prompt_builder import build_prompt
from app.core.utils import validar_fecha_hora, is_exit_command, limpiar_comando_asistente
from datetime import datetime
from dateutil import parser

class AssistantRunner:
    def __init__(self):
        self.running = True
        self.voice_input = VoiceInput(language="es-ES")
        self.voice_output = VoiceOutput(rate=170, gender="female")
        self.ollama_client = OllamaClient(model="llama3.2", host="http://localhost:11434", max_history=80)
        self.calendar = GoogleCalendar()
        self.fecha_actual = datetime.now().date().isoformat()

    async def run(self):
        self.voice_output.speak(f"Asistente iniciado. Di salir o presiona Ctrl+C para finalizar. Di {ASSISTANT_NAME} para activar.")
        while self.running:
            texto = self.voice_input.capture()
            if not texto:
                continue

            texto_lc = texto.lower().strip()
            if is_exit_command(texto_lc):
                self.voice_output.speak(f"Bye '{USER_NAME}', nos vemos pronto.")
                break

            if ASSISTANT_NAME in texto_lc:
                texto = limpiar_comando_asistente(texto_lc)
                self.voice_output.speak(f"Hola {USER_NAME}, procesando...")

                prompt = build_prompt(texto)
                respuesta = await self.ollama_client.chat(prompt)
                print(f"Respuesta del modelo: {respuesta}")
                try:
                    data = parse_llm_response(respuesta)
                    await self._manejar_respuesta(data)
                except json.JSONDecodeError:
                    self.voice_output.speak("Respuesta inválida del modelo.")

    async def _manejar_respuesta(self, data):
        tipo = data.get("tipo")

        if tipo == "general":
            self.voice_output.speak(data["respuesta"])

        elif tipo == "tarea":
            await task_service.procesar_tarea(data["respuesta"], self.voice_output)

        elif tipo == "calendario":
            await self._crear_evento(data["respuesta"])

        elif tipo == "consulta_agenda":
            await self._consultar_agenda(data["respuesta"])

    async def _crear_evento(self, data):
        fecha, hora, descripcion = data["fecha"], data["hora"], data["descripcion"]
        dt_evento = validar_fecha_hora(fecha)
        if not descripcion or not dt_evento or dt_evento.date() < datetime.now().date():
            self.voice_output.speak("No puedo agendar el evento. Revisa los datos.")
            return

        evento = self.calendar.crear_evento(dt_evento.date().isoformat(), dt_evento.time().strftime("%H:%M"), descripcion)
        self.voice_output.speak(f"Evento creado con ID {evento.get('id')}")

    async def _consultar_agenda(self, data):
        fecha = data.get("fecha")
        eventos = self.calendar.obtener_eventos(fecha)
        if not eventos:
            self.voice_output.speak(f"No hay eventos el {fecha}.")
        else:
            respuesta = f"{len(eventos)} evento(s): "
            for e in eventos:
                resumen = e.get("summary", "Sin título")
                hora = parser.parse(e["start"].get("dateTime", e["start"].get("date"))).strftime("%H:%M")
                respuesta += f"{resumen} a las {hora}. "
            self.voice_output.speak(respuesta)
