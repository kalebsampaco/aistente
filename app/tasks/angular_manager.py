import subprocess
import os

ANGULAR_CLI = "ng"

def crear_proyecto(nombre, ruta="./"):
    os.chdir(ruta)
    comando = [ANGULAR_CLI, "new", nombre, "--routing", "--style=scss"]
    try:
        subprocess.run(comando, check=True)
        return f"Proyecto Angular '{nombre}' creado en {ruta}."
    except subprocess.CalledProcessError as e:
        return f"Error al crear el proyecto: {e}"

def generar_componente(nombre, ruta_proyecto):
    os.chdir(ruta_proyecto)
    comando = [ANGULAR_CLI, "generate", "component", nombre]
    try:
        subprocess.run(comando, check=True)
        return f"Componente '{nombre}' creado."
    except subprocess.CalledProcessError as e:
        return f"Error al generar componente: {e}"

def generar_servicio(nombre, ruta_proyecto):
    os.chdir(ruta_proyecto)
    comando = [ANGULAR_CLI, "generate", "service", nombre]
    try:
        subprocess.run(comando, check=True)
        return f"Servicio '{nombre}' creado."
    except subprocess.CalledProcessError as e:
        return f"Error al generar servicio: {e}"

def agregar_ruta(nombre_componente, ruta_archivo_routing):
    try:
        with open(ruta_archivo_routing, 'a') as f:
            ruta = f"\n  {{ path: '{nombre_componente}', component: {nombre_componente.capitalize()}Component }},"
            f.write(ruta)
        return f"Ruta agregada al routing para {nombre_componente}."
    except Exception as e:
        return f"Error al agregar la ruta: {e}"
