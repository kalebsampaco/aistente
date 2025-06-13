FROM python:3.10.14-slim

# Instala dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    libasound-dev \
    portaudio19-dev \
    libportaudio2 \
    libportaudiocpp0 \
    espeak \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /asistente
COPY . .


# Instala dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "-m", "app.main"]
