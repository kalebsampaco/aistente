import os
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Alcance necesario para crear y administrar eventos en Google Calendar
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

class GoogleCalendar:
    def __init__(self, credentials_path='app/credentials.json', token_path='token.json'):
        self.credentials_path = credentials_path
        self.token_path = token_path
        # Inicializa el servicio de Google Calendar con las credenciales
        self.service = self._obtener_servicio()

    def _obtener_servicio(self):
        creds = None
        # Si ya existe un token guardado, lo usamos
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
        else:
            # Si no hay token, iniciamos el flujo de autenticación de Google
            flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
            # Guardamos el token para futuras ejecuciones
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())
        # Construimos el cliente del API de Google Calendar
        return build('calendar', 'v3', credentials=creds)

    def obtener_eventos(self, fecha_iso):
        """Devuelve los eventos para una fecha específica (yyyy-mm-dd)"""
        fecha = datetime.fromisoformat(fecha_iso)
        start = datetime.combine(fecha, datetime.min.time()).isoformat() + "Z"
        end = datetime.combine(fecha, datetime.max.time()).isoformat() + "Z"

        eventos = self.service.events().list(
            calendarId="primary",
            timeMin=start,
            timeMax=end,
            singleEvents=True,
            orderBy="startTime"
        ).execute()

        return eventos.get("items", [])


    def crear_evento(self, fecha: str, hora: str, descripcion: str, duracion_horas: int = 1):
        # Construimos el objeto datetime para inicio y fin del evento
        inicio = datetime.fromisoformat(f"{fecha}T{hora}:00")
        fin = inicio + timedelta(hours=duracion_horas)

        # Estructura del evento según el formato de la API de Google Calendar
        evento = {
            'summary': descripcion,
            'start': {
                'dateTime': inicio.isoformat(),  # Fecha y hora de inicio en formato ISO
                'timeZone': 'Europe/Madrid',     # Zona horaria ajustada a España
            },
            'end': {
                'dateTime': fin.isoformat(),      # Fecha y hora de fin en formato ISO
                'timeZone': 'Europe/Madrid',     # Zona horaria ajustada a España
            }
        }

        # Creamos el evento en el calendario principal
        evento_creado = self.service.events().insert(calendarId='primary', body=evento).execute()
        print(f"✅ Evento creado: {evento_creado.get('htmlLink')}")  # Mostramos enlace al evento creado
        return evento_creado
