# task_runner.py
import os
import subprocess
import platform
import time
import threading
from app.tasks.angular_manager import crear_proyecto, generar_componente

def abrir_aplicacion(nombre):
    sistema = platform.system()
    nombre = nombre.lower()

    if sistema == "Windows":
        apps = {
            "vs code": "code",
            "visual studio code": "code",
            "chrome": "chrome",
            "google chrome": "chrome",
            "explorador": "explorer",
            "spotify": "spotify",
            "word": "winword",
            "excel": "excel",
            "pdf": "AcroRd32",  # Adobe Reader o usa SumatraPDF si está instalado
            "dbeaver": "dbeaver",
            "dbeaver community": "dbeaver",
            "intellij": "idea64",
            "intellij idea": "idea64",
            "docker": "Docker Desktop.exe",
            "mongodbcompass": "MongoDBCompass",
            "mongodb compass": "MongoDBCompass",
            "sourcetree": "sourcetree",
            "bloc de notas": "notepad",
            "texto plano": "notepad",
            "postman": "Postman"
        }
        comando = apps.get(nombre)
        if comando:
            os.system(comando)
            return f"Abrí {nombre}."
        else:
            return f"No sé cómo abrir {nombre} en Windows."

    elif sistema == "Linux":
        apps = {
            "vs code": "code",
            "chrome": "google-chrome",
            "explorador": "nautilus",
            "spotify": "spotify",
            "word": "libreoffice --writer",
            "excel": "libreoffice --calc",
            "pdf": "evince",  # o okular, xreader según entorno
            "dbeaver": "dbeaver",
            "intellij": "intellij-idea-community",
            "docker": "docker",
            "mongodb compass": "mongodb-compass",
            "sourcetree": "sourcetree",
            "gedit": "gedit",
            "texto plano": "gedit",
            "postman": "postman"
        }
        comando = apps.get(nombre)
        if comando:
            subprocess.Popen([comando])
            return f"Abrí {nombre}."
        else:
            return f"No sé cómo abrir {nombre} en Linux."

    elif sistema == "Darwin":  # macOS
        apps = {
            "vs code": "Visual Studio Code",
            "chrome": "Google Chrome",
            "explorador": "Finder",
            "spotify": "Spotify",
            "word": "Microsoft Word",
            "excel": "Microsoft Excel",
            "pdf": "Preview",
            "dbeaver": "DBeaver",
            "intellij": "IntelliJ IDEA CE",
            "docker": "Docker",
            "mongodb compass": "MongoDB Compass",
            "sourcetree": "Sourcetree",
            "textedit": "TextEdit",
            "texto plano": "TextEdit",
            "postman": "Postman"
        }
        comando = apps.get(nombre)
        if comando:
            subprocess.run(["open", "-a", comando])
            return f"Abrí {nombre}."
        else:
            return f"No sé cómo abrir {nombre} en Mac."
    else:
        return "Sistema operativo no soportado."


def ejecutar_script(ruta):
    try:
        resultado = subprocess.run(ruta, shell=True, capture_output=True, text=True)
        return resultado.stdout or "Script ejecutado."
    except Exception as e:
        return f"Error al ejecutar script: {str(e)}"


def apagar_equipo_en(minutos):
    segundos = minutos * 60

    def apagado():
        time.sleep(segundos)
        sistema = platform.system()
        if sistema == "Windows":
            os.system("shutdown /s /t 0")
        elif sistema == "Linux" or sistema == "Darwin":
            os.system("shutdown -h now")

    threading.Thread(target=apagado, daemon=True).start()
    return f"Apagaré el equipo en {minutos} minutos."


def cerrar_ventana(nombre_ventana):
    sistema = platform.system()
    if sistema == "Windows":
        os.system(f'taskkill /FI "WINDOWTITLE eq {nombre_ventana}" /F')
    elif sistema == "Linux":
        os.system(f"pkill -f '{nombre_ventana}'")
    elif sistema == "Darwin":
        os.system(f"osascript -e 'tell application \"{nombre_ventana}\" to quit'")
    return f"Cerré la ventana: {nombre_ventana}."

def escribir_en_archivo(ruta, texto):
    try:
        with open(ruta, 'a', encoding='utf-8') as f:
            f.write(texto + '\n')
        return f"Texto escrito en {ruta}."
    except Exception as e:
        return f"No pude escribir en el archivo: {str(e)}"

def abrir_codigo_en_vscode(ruta_archivo):
    try:
        subprocess.Popen(["code", ruta_archivo])
        return f"Abrí el archivo en VS Code: {ruta_archivo}"
    except Exception as e:
        return f"No pude abrir el archivo en VS Code: {str(e)}"

def ejecutar_comando_angular(texto):
    if "crear proyecto angular" in texto:
        nombre = texto.split("crear proyecto angular")[-1].strip()
        return crear_proyecto(nombre)
    elif "crear componente" in texto:
        nombre = texto.split("crear componente")[-1].strip()
        return generar_componente(nombre, "./mi-proyecto-angular")
    return "No entendí el comando relacionado con Angular."