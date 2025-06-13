from app.tasks import system_tasks

async def procesar_tarea(data, voice_output):
    accion = data.get("accion", "").lower()
    parametros = data.get("parametros", "")

    if "abrir" in accion:
        voice_output.speak(system_tasks.abrir_aplicacion(parametros))

    if "cerrar" in accion:
        voice_output.speak(system_tasks.cerrar_ventana(parametros))

    if "escribir" in accion:
        import pathlib
        ruta = pathlib.Path.cwd()
        voice_output.speak(system_tasks.escribir_en_archivo(ruta, parametros))

    if "crear" in accion:
        voice_output.speak(system_tasks.ejecutar_comando_angular(parametros))

    elif "apagar" in accion:
        minutos = "".join([c for c in parametros if c.isdigit()])
        voice_output.speak(system_tasks.apagar_equipo_en(int(minutos)))

    elif "ejecutar script" in accion:
        voice_output.speak(system_tasks.ejecutar_script(parametros))

    else:
        voice_output.speak("Acción no reconocida.")
