import speech_recognition as sr

class VoiceInput:
    def __init__(self, language: str = "es-ES") -> None:
        self.recognizer = sr.Recognizer()
        self.language = language
        # Ajusta los tiempos de espera para permitir pausas más largas
        self.recognizer.pause_threshold = 2.0  # espera más tiempo antes de cortar
        self.recognizer.energy_threshold = 300  # nivel mínimo de energía para detectar voz
        self.recognizer.dynamic_energy_threshold = True

    def capture(self) -> str:
        with sr.Microphone() as source:
            print("🎙️ Escuchando...")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)  # ajusta al ruido ambiente
            audio = self.recognizer.listen(source, timeout=None, phrase_time_limit=18)

        try:
            text = self.recognizer.recognize_google(audio, language=self.language)
            print(f"📝 Texto detectado: {text}")
            return text
        except sr.UnknownValueError:
            print("❌ No se entendió el audio.")
            return ""
        except sr.RequestError as e:
            print(f"⚠️ Error de conexión con el servicio STT: {e}")
            return ""
