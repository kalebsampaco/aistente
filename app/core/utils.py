# utils.py
from dateutil import parser

def validar_fecha_hora(fecha_str):
    try:
        return parser.isoparse(fecha_str)
    except Exception:
        return None

def is_exit_command(texto):
    return texto.strip().lower() == "salir"

def limpiar_comando_asistente(texto):
    from app.core.constants import ASSISTANT_NAME
    return texto.replace(ASSISTANT_NAME, "").strip()
