import asyncio
import signal
import sys
from app.services.assistant_loop import AssistantRunner

def shutdown_handler(signum, frame):
    print("\n👋 Señal de terminación recibida. Cerrando asistente...")
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)
    try:
        runner = AssistantRunner()
        asyncio.run(runner.run())
    except KeyboardInterrupt:
        print("\n👋 Programa terminado por teclado.")
        sys.exit(0)
