""" from fastapi import FastAPI
from app.routes import assistant

app = FastAPI()

app.include_router(assistant.router, prefix="/ask") """
import asyncio
import signal
import sys
from dateutil import parser
from datetime import datetime
import json
from app.sst.voice_input import VoiceInput
from app.llm.ollama_client import OllamaClient
from app.sst.voice_output import VoiceOutput
from app import task_runner as tasks
# from app.scheduler import Scheduler
from app.calendar_integration import GoogleCalendar

# Variable global para controlar el loop
running = True
ASSISTANT_NAME = "viernes"
USER_NAME = "William"

fecha_actual = datetime.now().date().isoformat()

def shutdown_handler(signum, frame):
    global running
    print("\n👋 Señal de terminación recibida. Cerrando asistente...")
    running = False

def validar_fecha_hora(fecha_str):
    try:
        # Validar y parsear fecha y hora, combinarlas en datetime
        return parser.isoparse(fecha_str)
    except Exception:
        return None

async def main_loop():
    global running
    voice_input = VoiceInput(language="es-ES")
    voice_output = VoiceOutput(rate=170, gender="female")
    ollama_client = OllamaClient(model="llama3.2", host="http://localhost:11434", max_history=80)
    # scheduler = Scheduler()
    calendar = GoogleCalendar()

    print("🎧 Asistente iniciado. Di 'salir' o presiona Ctrl+C para finalizar.")
    print("🤖 Asistente iniciado. Di 'viernes' para activar...")
    voice_output.speak(f"Asistente iniciado. Di salir o presiona Ctrl+C para finalizar. Di {ASSISTANT_NAME} para activar.")

    while running:
        texto = voice_input.capture()
        if not texto:
            print("⚠️ No se entendió el audio, intenta de nuevo.")
            continue

        texto_lc = texto.lower().strip()

        if texto_lc == "salir":
            print("👋 Comando salir recibido. Cerrando asistente...")
            voice_output.speak(f"Bye '{USER_NAME}', nos vemos pronto.")
            break

        if ASSISTANT_NAME in texto_lc:
            voice_output.speak(f"Hola {USER_NAME}, Voy a procesar tu solicitud")
            print(f"🔵 Comando activado por {ASSISTANT_NAME}. Esperando petición...")

            # Remover nombre del asistente para procesar la consulta
            texto = texto_lc.replace(ASSISTANT_NAME, "").strip()


            prompt = f"""
                Eres una asistente de voz llamada {ASSISTANT_NAME}, con una personalidad femenina, optimista y picarona.
                Siempre hablas con naturalidad y calidez, como si fuera viernes: alegre, cercana y con energía positiva.
                Tu usuario se llama {USER_NAME}. Siempre tratas de hacerlo sonreír.

                La fecha actual es {fecha_actual}.

                Tu misión es entender peticiones habladas y responder en uno de los siguientes formatos JSON:

                1. Si es una consulta general (chistes, preguntas, etc.), responde:
                {{
                "tipo": "general",
                "respuesta": "<respuesta humana, simpática y clara>"
                }}

                2. Si es una solicitud para agendar algo:
                - Usa la fecha actual como referencia para resolver palabras como "hoy", "mañana", "pasado mañana".
                - Nunca devuelvas fechas en el pasado.
                - Si no se menciona una fecha explícita ni relativa, asume que es hoy.

                Responde:
                {{
                "tipo": "calendario",
                "respuesta": {{
                    "fecha": "<fecha en formato ISO yyyy-mm-dd o null>",
                    "hora": "<hora en formato HH:MM 24h o null>",
                    "descripcion": "<descripción del evento>"
                }}
                }}

                3. Si se trata de una acción sobre el sistema (abrir apps, ejecutar tareas, etc.), responde:
                {{
                "tipo": "tarea",
                "respuesta": {{
                    "accion": "<nombre de la acción>",
                    "parametros": "<detalle adicional si lo hay>"
                }}
                }}
                4. Si es una consulta de agenda (qué tengo hoy, mañana, etc.), responde:
                {{
                "tipo": "consulta_agenda",
                "respuesta": {{
                    "fecha": "<fecha en formato ISO yyyy-mm-dd o null>"
                }}
                }}
                Ejemplos válidos:
                - "Recuérdame reunión mañana a las 10" → tipo: calendario
                - "¿Cuál es la capital de Japón?" → tipo: general
                - "Abre Visual Studio Code" → tipo: tarea
                - "¿Tengo algo mañana?" → tipo: consulta_agenda
                - "¿Qué tengo hoy?" → tipo: consulta_agenda
                - "Abre VS Code" → tipo: tarea, accion: "abrir", parametros: "vs code"
                - "Apaga el equipo en 30 minutos" → tipo: tarea, accion: "apagar", parametros: "en 30 minutos"
                - "Ejecuta el script 'limpiar_logs.bat'" → tipo: tarea, accion: "ejecutar script", parametros: "ruta/al/script.bat"


                IMPORTANTE:
                - No expliques tu razonamiento, solo devuelve el JSON correspondiente.
                - Nunca agregues texto fuera del JSON.
                - Siempre responde en español.

                Usuario: "{texto}"
                """


            respuesta = await ollama_client.chat(prompt)
            data = json.loads(respuesta)
            print(f"🤖 Ollama extracción: {data}")
            print("💬 Procesando texto en Ollama...")
            try:

                if data.get("tipo") == "general":
                    respuesta = data.get("respuesta")
                    print(f"🤖 {ASSISTANT_NAME.capitalize()} dice: {respuesta}")
                    voice_output.speak(respuesta)
                elif data.get("tipo") == "tarea":
                    accion = data["respuesta"].get("accion", "").lower()
                    parametros = data["respuesta"].get("parametros", "")

                    if "abrir" in accion:
                        resultado = tasks.abrir_aplicacion(parametros)
                        voice_output.speak(resultado)

                    elif "apagar" in accion and "minuto" in parametros:
                        try:
                            minutos = int("".join([c for c in parametros if c.isdigit()]))
                            resultado = tasks.apagar_equipo_en(minutos)
                            voice_output.speak(resultado)
                        except:
                            voice_output.speak("No entendí en cuántos minutos debo apagar el equipo.")

                    elif "ejecutar script" in accion:
                        resultado = tasks.ejecutar_script(parametros)
                        voice_output.speak(resultado)

                    else:
                        voice_output.speak(f"No reconozco la acción '{accion}'.")
                elif data.get("tipo") == "calendario":

                    fecha = data["respuesta"]["fecha"]
                    hora = data["respuesta"]["hora"]
                    descripcion = data["respuesta"]["descripcion"]
                    if not descripcion or descripcion.strip() == "":
                        voice_output.speak("No entendí la descripción del evento, por favor intenta de nuevo.")
                        continue
                    else:
                        try:
                            dt_evento = validar_fecha_hora(fecha)
                            if dt_evento.date() < datetime.now().date():
                                voice_output.speak("No puedo agendar eventos en el pasado, prueba con otra fecha.")
                                continue
                            # Crear evento en Google Calendar con la fecha y hora validadas
                            evento = calendar.crear_evento(
                                dt_evento.date().isoformat(),
                                dt_evento.time().strftime("%H:%M"),
                                descripcion
                            )
                            print(f"📅 Evento creado: {evento.get('htmlLink')}")
                            # voice_output.speak(f"Evento '{descripcion}' agendado para el {dt_evento.strftime('%d/%m/%Y')} a las {dt_evento.strftime('%H:%M')} en tu calendario.")
                            voice_output.speak(f"Evento cradocon id '{evento.get('id')}' en tu calendario.")
                        except ValueError:
                            voice_output.speak("No entendí la fecha o hora del evento, por favor intenta de nuevo.")
                elif data.get("tipo") == "consulta_agenda":
                    fecha_consulta = data["respuesta"].get("fecha")
                    if not fecha_consulta:
                        voice_output.speak("No entendí qué día quieres consultar.")
                        continue

                    eventos = calendar.obtener_eventos(fecha_consulta)

                    if not eventos:
                        voice_output.speak(f"No tienes eventos programados para el {fecha_consulta}.")
                    else:
                        respuesta = f"Tienes {len(eventos)} evento(s) para el {fecha_consulta}: "
                        for e in eventos:
                            resumen = e.get("summary", "Sin título")
                            hora = parser.parse(e["start"].get("dateTime", e["start"].get("date"))).strftime("%H:%M")
                            respuesta += f"{resumen} a las {hora}. "
                        voice_output.speak(respuesta)

            except json.JSONDecodeError:
                voice_output.speak("No entendí la información proporcionada, por favor intenta de nuevo con un formato claro.")
        else:
            print("⏸️ Modo pasivo. Di el nombre para activar.")

if __name__ == "__main__":
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    try:
        asyncio.run(main_loop())
    except KeyboardInterrupt:
        print("\n👋 Programa terminado por teclado.")
        sys.exit(0)

