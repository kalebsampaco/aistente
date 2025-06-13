import pyttsx3

class VoiceOutput:
    def __init__(self, rate: int = 170, gender: str = "female") -> None:
        self.engine = pyttsx3.init()
        self.rate = rate
        self.gender = gender
        self._configure_voice()

    def _configure_voice(self) -> None:
        self.engine.setProperty("rate", self.rate)
        voices = self.engine.getProperty("voices")
        for voice in voices:
            if self.gender.lower() in voice.name.lower() or "spanish" in voice.name.lower():
                self.engine.setProperty("voice", voice.id)
                break

    def speak(self, text: str) -> None:
        self.engine.say(text)
        self.engine.runAndWait()
