import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import threading
import subprocess
import os
import sys

class WindowsService(win32serviceutil.ServiceFramework):
    _svc_name_ = "AssistantDaemon"
    _svc_display_name_ = "Viernes Asistente IA Personal"
    _svc_description_ = "Asistente de voz que ejecuta tareas, responde preguntas y agenda eventos con IA"

    def __init__(self, args):
        super().__init__(args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.process = None

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        if self.process:
            self.process.terminate()
            self.process.wait()
        win32event.SetEvent(self.stop_event)
        servicemanager.LogInfoMsg("🛑 Servicio detenido")

    def SvcDoRun(self):
        servicemanager.LogInfoMsg("🚀 Servicio iniciado")
        python_path = sys.executable
        script_path = os.path.abspath("app/main.py")

        self.process = subprocess.Popen(
            [python_path, script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        servicemanager.LogInfoMsg(f"▶️ Ejecutando: {python_path} {script_path}")
        win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE)
