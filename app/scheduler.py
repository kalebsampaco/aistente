import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import os
import dateparser
import re

AGENDA_FILE = "../data/agenda.json"

class Scheduler:
    def __init__(self, agenda_file: str = AGENDA_FILE):
        self.agenda_file = agenda_file
        self.events: List[Dict] = self._load_events()

    def _load_events(self) -> List[Dict]:
        if not os.path.exists(self.agenda_file):
            return []
        try:
            with open(self.agenda_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _save_events(self) -> None:
        with open(self.agenda_file, "w", encoding="utf-8") as f:
            json.dump(self.events, f, ensure_ascii=False, indent=2)

    def add_event(self, fecha: str, hora: str, descripcion: str) -> None:
        with open(self.agenda_file, "r+", encoding="utf-8") as f:
            eventos = json.load(f)
            eventos.append({"fecha": fecha, "hora": hora, "descripcion": descripcion})
            f.seek(0)
            json.dump(eventos, f, indent=2, ensure_ascii=False)
            f.truncate()

    def get_events_for_day(self,  day: Optional[datetime] = None) -> List[Dict]:
        day_str = day.date().isoformat()
        return [
            event for event in self.events
            if event["datetime"].startswith(day_str)
        ]

    def parse_natural_command(self, texto: str) -> Optional[str]:
        """
        Extrae título y fecha/hora aproximada del comando natural para crear un evento.
        Ejemplo: "Recuérdame reunión mañana a las 9 am"
        """
        # Extraer título y fecha usando regex básicos
        # Suponemos formato "recuérdame <titulo> <fecha>"
        # pattern = r"recuérdame\s+(.*?)\s+(mañana|hoy|el\s+\d{1,2}(?: de [a-z]+)?)(?: a las (\d{1,2})(?:[:.]?(\d{2}))?\s*(am|pm)?)?"
        texto = texto.lower()
        if "recuérdame" in texto or "agenda" in texto or "anota" in texto:
            fecha = dateparser.parse(texto, languages=["es"])
            print(fecha)
            if not fecha:
                return "No entendí la fecha del evento. ¿Puedes repetirlo?"
            # Extrae lo que viene después de la palabra clave
            partes = texto.split("recuérdame")[-1].strip()
            descripcion = partes.replace(str(fecha.date()), "").strip()
            return self.add_event(descripcion, fecha)

        if "qué tengo" in texto or "agenda para" in texto or "eventos" in texto:
            fecha = dateparser.parse(texto, languages=["es"]) or datetime.now()
            eventos = self.get_events_for_day(fecha)
            if not eventos:
                return "No tienes eventos programados para ese día."
            respuesta = f"Tienes {len(eventos)} evento(s): " + ", ".join(
                f"{e['descripcion']} a las {datetime.fromisoformat(e['fecha']).strftime('%H:%M')}"
                for e in eventos
            )
            return respuesta
        return "No entendí el comando de agenda. Intenta con 'Recuérdame...' o '¿Qué tengo hoy?'."


    def list_events_today(self) -> List[str]:
        events = self.get_events_for_day(datetime.now())
        if not events:
            return ["No tienes eventos para hoy."]
        return [f"{e['title']} a las {datetime.fromisoformat(e['datetime']).strftime('%H:%M')}" for e in events]

