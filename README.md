# 🤖 AIstente - Asistente Virtual con IA

Un asistente virtual inteligente construido con Python que integra múltiples servicios y funcionalidades.

## 🚀 Características

- 🎤 Reconocimiento de voz
- 🔊 Síntesis de voz
- 🤖 Integración con Ollama para procesamiento de lenguaje natural
- 📅 Gestión de calendario con Google Calendar
- 📋 Sistema de tareas
- ☁️ **Almacenamiento en S3** (local con MinIO o AWS S3)

## 📋 Requisitos

- Python 3.10+
- Docker y Docker Compose
- Dependencias del sistema (instaladas automáticamente con Docker)

## 🛠️ Instalación

### Con Docker (Recomendado)

1. Clona el repositorio:
```bash
git clone https://github.com/kalebsampaco/aistente.git
cd aistente
```

2. Inicia los servicios:
```bash
docker-compose up -d
```

Esto iniciará:
- El asistente principal
- Ollama (servidor de IA)
- MinIO (almacenamiento S3 local)

### Sin Docker

1. Instala las dependencias:
```bash
pip install -r requirements.txt
```

2. Configura las variables de entorno (ver `.env.example`)

3. Ejecuta el asistente:
```bash
python -m app.main
```

## ⚙️ Configuración

### Variables de Entorno

Copia el archivo `.env.example` a `.env` y configura las variables:

```bash
cp .env.example .env
```

Variables disponibles:
- `OLLAMA_HOST`: URL del servidor Ollama
- `AWS_ACCESS_KEY_ID`: Credenciales de S3/MinIO
- `AWS_SECRET_ACCESS_KEY`: Credenciales de S3/MinIO
- `AWS_ENDPOINT_URL`: Endpoint de S3 (usa http://localhost:9000 para MinIO local)
- `AWS_DEFAULT_REGION`: Región de AWS

## 💾 Almacenamiento S3

El proyecto incluye soporte completo para almacenamiento de objetos compatible con S3.

### Uso Local con MinIO

MinIO viene preconfigurado y se inicia automáticamente con Docker Compose:

- **API**: http://localhost:9000
- **Consola Web**: http://localhost:9001
- **Usuario**: minioadmin
- **Contraseña**: minioadmin

### Documentación Completa

Lee la [Guía de Pruebas de Almacenamiento S3](docs/S3_LOCAL_TESTING.md) para:
- Configuración detallada
- Ejemplos de código
- Transición a AWS S3 real
- Solución de problemas

### Ejemplo Rápido

```python
from app.services.s3_service import S3Service

# Inicializar servicio
s3 = S3Service()

# Crear bucket y subir archivo
s3.create_bucket("mi-bucket")
s3.upload_file("/ruta/archivo.txt", "mi-bucket")

# Listar y descargar
objetos = s3.list_objects("mi-bucket")
s3.download_file("mi-bucket", "archivo.txt", "/destino/archivo.txt")
```

### Script de Prueba

Ejecuta el script de prueba incluido:

```bash
python scripts/test_s3.py
```

## 📚 Documentación

- [Guía de Almacenamiento S3](docs/S3_LOCAL_TESTING.md)

## 🤝 Contribución

Las contribuciones son bienvenidas. Por favor:

1. Haz fork del proyecto
2. Crea una rama para tu característica (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la licencia especificada en el archivo LICENSE.

## 🙏 Agradecimientos

- [Ollama](https://ollama.ai/) - Modelos de IA local
- [MinIO](https://min.io/) - Almacenamiento de objetos compatible con S3
- [FastAPI](https://fastapi.tiangolo.com/) - Framework web
- [boto3](https://boto3.amazonaws.com/) - AWS SDK para Python
