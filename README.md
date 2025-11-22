# 🤖 AIstente - Asistente Virtual con IA

Un asistente virtual inteligente construido con Python que integra múltiples servicios y funcionalidades.

## 🚀 Características

- 🎤 Reconocimiento de voz
- 🔊 Síntesis de voz
- 🤖 Integración con Ollama para procesamiento de lenguaje natural
- 📅 Gestión de calendario con Google Calendar
- 📋 Sistema de tareas
- ☁️ **Almacenamiento en S3** (local con MinIO o AWS S3)
- 🏛️ **Simulador de Certificados DGII** (República Dominicana)

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

### 🚀 Inicio Rápido

¿Quieres empezar ya? Lee la [Guía de Inicio Rápido](docs/QUICK_START.md) (5 minutos).

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

## 🏛️ Simulador de Certificados DGII

El proyecto incluye un simulador completo de certificados digitales de la DGII (Dirección General de Impuestos Internos de República Dominicana).

**💾 Los certificados se guardan localmente en tu sistema de archivos, NO en S3/nube.**

### Uso Rápido

```bash
# Script interactivo
python scripts/simulate_dgii_certificate.py
```

### Ejemplo de Código

```python
from app.services.dgii_certificate_simulator import DGIICertificateSimulator

# Crear simulador
simulator = DGIICertificateSimulator()

# Generar certificado completo - se guarda localmente
files = simulator.generate_complete_certificate_set(
    output_dir="./certificados",           # ← Carpeta local
    rnc="131257681",
    nombre_contribuyente="MI EMPRESA SRL",
    email="contacto@miempresa.com.do",
    password="MiPassword123",
    valid_days=365
)

# Archivos generados:
# - Clave privada (cifrada)
# - Certificado X.509
# - Archivo PKCS#12 (.p12) para importar en navegadores
```

### ⚠️ Importante

Los certificados generados son **SOLO para pruebas y desarrollo local**. NO son válidos para:
- Transacciones reales con la DGII
- Facturación electrónica en producción
- Declaraciones tributarias oficiales

### Casos de Uso

- 🧪 Desarrollo de aplicaciones de facturación electrónica
- 🔒 Pruebas de firma digital
- 🏗️ Validación de flujos de autenticación
- 💻 Testing de aplicaciones tributarias

Lee la [Guía Completa del Simulador DGII](docs/DGII_CERTIFICATE_SIMULATOR.md) para más información.

## 📚 Documentación

- [🚀 Guía de Inicio Rápido](docs/QUICK_START.md) - Empieza en 5 minutos
- [📖 Guía de Almacenamiento S3](docs/S3_LOCAL_TESTING.md) - Documentación completa
- [🏗️ Arquitectura de la Solución](docs/ARCHITECTURE.md) - Cómo funciona todo
- [🏛️ Simulador de Certificados DGII](docs/DGII_CERTIFICATE_SIMULATOR.md) - Certificados digitales para pruebas

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
