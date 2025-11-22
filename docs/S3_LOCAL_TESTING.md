# Guía de Pruebas de Almacenamiento S3 Local

Esta guía te ayudará a realizar pruebas de almacenamiento en buckets S3 de AWS en tu equipo local, con herramientas que luego son aplicables directamente a AWS.

## 📋 Contenido

- [Herramientas Disponibles](#herramientas-disponibles)
- [Configuración con MinIO](#configuración-con-minio)
- [Configuración con LocalStack](#configuración-con-localstack-alternativa)
- [Uso del Servicio S3](#uso-del-servicio-s3)
- [Transición a AWS S3 Real](#transición-a-aws-s3-real)
- [Ejemplos de Código](#ejemplos-de-código)

---

## 🛠️ Herramientas Disponibles

### 1. **MinIO** (Recomendado para S3)

MinIO es un servidor de almacenamiento de objetos compatible con S3 que se ejecuta localmente.

**Ventajas:**
- ✅ 100% compatible con la API de AWS S3
- ✅ Ligero y rápido
- ✅ Interfaz web incluida
- ✅ Fácil de configurar con Docker
- ✅ El mismo código funciona en AWS sin cambios

### 2. **LocalStack** (Para múltiples servicios AWS)

LocalStack emula múltiples servicios de AWS, incluyendo S3.

**Ventajas:**
- ✅ Emula S3, DynamoDB, Lambda, SQS, SNS, etc.
- ✅ Útil si necesitas probar múltiples servicios AWS
- ✅ Buena documentación

**Desventajas:**
- ⚠️ Más pesado que MinIO
- ⚠️ Algunas características requieren versión Pro

---

## 🚀 Configuración con MinIO

### Paso 1: Iniciar los Servicios

El proyecto ya incluye MinIO configurado en `docker-compose.yml`. Para iniciar todos los servicios:

```bash
docker-compose up -d
```

Esto iniciará:
- **MinIO Server** en `http://localhost:9000` (API)
- **MinIO Console** en `http://localhost:9001` (Interfaz Web)
- **Ollama** (servicio existente)
- **Assistant** (servicio existente)

### Paso 2: Acceder a la Interfaz Web de MinIO

1. Abre tu navegador en `http://localhost:9001`
2. Credenciales por defecto:
   - **Usuario:** minioadmin
   - **Contraseña:** minioadmin

Desde aquí puedes:
- Crear buckets
- Subir archivos manualmente
- Ver métricas y logs
- Configurar políticas de acceso

### Paso 3: Instalar Dependencias Python

Las dependencias necesarias ya están en `requirements.txt`. Para instalarlas:

```bash
pip install -r requirements.txt
```

La dependencia principal es `boto3`, el SDK oficial de AWS para Python.

---

## 🧪 Uso del Servicio S3

### Opción 1: Script de Prueba Rápido

Ejecuta el script de prueba incluido:

```bash
python scripts/test_s3.py
```

Este script realizará:
1. Listado de buckets existentes
2. Creación de un bucket de prueba
3. Subida de un archivo
4. Listado de objetos
5. Generación de URL pre-firmada
6. Descarga del archivo
7. Eliminación del objeto
8. Eliminación del bucket

### Opción 2: Usar el Servicio en tu Código

```python
from app.services.s3_service import S3Service

# Inicializar el servicio (usa variables de entorno por defecto)
s3 = S3Service()

# Crear un bucket
s3.create_bucket("mi-bucket")

# Subir un archivo
s3.upload_file("/ruta/al/archivo.txt", "mi-bucket", "archivo.txt")

# Listar objetos
objetos = s3.list_objects("mi-bucket")
for obj in objetos:
    print(f"- {obj['Key']} ({obj['Size']} bytes)")

# Descargar un archivo
s3.download_file("mi-bucket", "archivo.txt", "/ruta/destino/archivo.txt")

# Eliminar un objeto
s3.delete_object("mi-bucket", "archivo.txt")

# Eliminar un bucket (forzar eliminación de contenido)
s3.delete_bucket("mi-bucket", force=True)
```

---

## 🔄 Transición a AWS S3 Real

Una de las grandes ventajas de usar MinIO con boto3 es que **el mismo código funciona en AWS S3 sin cambios**. Solo necesitas cambiar las variables de entorno.

### Para MinIO Local:

```bash
export AWS_ACCESS_KEY_ID=minioadmin
export AWS_SECRET_ACCESS_KEY=minioadmin
export AWS_ENDPOINT_URL=http://localhost:9000
export AWS_DEFAULT_REGION=us-east-1
```

O en Docker (ya configurado en `docker-compose.yml`):

```yaml
environment:
  - AWS_ACCESS_KEY_ID=minioadmin
  - AWS_SECRET_ACCESS_KEY=minioadmin
  - AWS_ENDPOINT_URL=http://minio:9000
  - AWS_DEFAULT_REGION=us-east-1
```

### Para AWS S3 Real:

```bash
export AWS_ACCESS_KEY_ID=tu_access_key_real
export AWS_SECRET_ACCESS_KEY=tu_secret_key_real
# NO establecer AWS_ENDPOINT_URL (o dejarlo vacío)
export AWS_DEFAULT_REGION=us-east-1
```

O en Docker:

```yaml
environment:
  - AWS_ACCESS_KEY_ID=tu_access_key_real
  - AWS_SECRET_ACCESS_KEY=tu_secret_key_real
  # NO incluir AWS_ENDPOINT_URL
  - AWS_DEFAULT_REGION=us-east-1
```

### Obtener Credenciales de AWS

1. Inicia sesión en [AWS Console](https://console.aws.amazon.com/)
2. Ve a **IAM** → **Users** → Tu usuario
3. Pestaña **Security credentials**
4. Click en **Create access key**
5. Guarda el Access Key ID y Secret Access Key

**Importante:** Nunca compartas tus credenciales reales de AWS ni las guardes en el código fuente.

---

## 📝 Ejemplos de Código

### Ejemplo 1: Respaldo Automático de Archivos

```python
from app.services.s3_service import S3Service
import os

def backup_files(directory, bucket_name):
    """Respalda todos los archivos de un directorio a S3"""
    s3 = S3Service()
    
    # Crear bucket si no existe
    s3.create_bucket(bucket_name)
    
    # Subir todos los archivos
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            s3.upload_file(file_path, bucket_name, f"backup/{filename}")
            print(f"✅ Respaldado: {filename}")

# Uso
backup_files("/ruta/a/datos", "mi-bucket-backup")
```

### Ejemplo 2: Compartir Archivos Temporalmente

```python
from app.services.s3_service import S3Service

def share_file(bucket_name, object_name, expiration_hours=24):
    """Genera un enlace temporal para compartir un archivo"""
    s3 = S3Service()
    
    url = s3.get_object_url(
        bucket_name,
        object_name,
        expiration=expiration_hours * 3600
    )
    
    if url:
        print(f"🔗 Enlace (válido por {expiration_hours} horas):")
        print(url)
        return url
    else:
        print("❌ Error al generar enlace")
        return None

# Uso
share_file("mi-bucket", "documento.pdf", expiration_hours=48)
```

### Ejemplo 3: Sincronización de Archivos

```python
from app.services.s3_service import S3Service
import os

def sync_directory(local_dir, bucket_name, s3_prefix=""):
    """Sincroniza un directorio local con S3"""
    s3 = S3Service()
    
    # Obtener archivos locales
    local_files = set()
    for root, dirs, files in os.walk(local_dir):
        for file in files:
            rel_path = os.path.relpath(
                os.path.join(root, file),
                local_dir
            )
            local_files.add(rel_path)
    
    # Obtener archivos remotos
    remote_objects = s3.list_objects(bucket_name, s3_prefix)
    remote_files = {obj['Key'].replace(s3_prefix, '', 1).lstrip('/') 
                    for obj in remote_objects}
    
    # Subir archivos nuevos o modificados
    for file in local_files:
        local_path = os.path.join(local_dir, file)
        s3_key = f"{s3_prefix}/{file}".lstrip('/')
        
        if file not in remote_files or \
           not s3.object_exists(bucket_name, s3_key):
            s3.upload_file(local_path, bucket_name, s3_key)
            print(f"⬆️  Subido: {file}")
    
    # Eliminar archivos que ya no existen localmente
    for file in remote_files - local_files:
        s3_key = f"{s3_prefix}/{file}".lstrip('/')
        s3.delete_object(bucket_name, s3_key)
        print(f"🗑️  Eliminado: {file}")

# Uso
sync_directory("/ruta/local", "mi-bucket", "datos/")
```

---

## 🔧 Configuración con LocalStack (Alternativa)

Si prefieres usar LocalStack en lugar de MinIO, puedes agregar este servicio a tu `docker-compose.yml`:

```yaml
localstack:
  image: localstack/localstack:latest
  container_name: localstack
  ports:
    - "4566:4566"  # Edge port para todos los servicios
  environment:
    - SERVICES=s3,dynamodb,lambda,sqs  # Servicios que deseas emular
    - DEBUG=1
    - DATA_DIR=/tmp/localstack/data
  volumes:
    - localstack_data:/tmp/localstack
```

Y cambiar las variables de entorno:

```yaml
environment:
  - AWS_ENDPOINT_URL=http://localstack:4566
  - AWS_ACCESS_KEY_ID=test
  - AWS_SECRET_ACCESS_KEY=test
  - AWS_DEFAULT_REGION=us-east-1
```

---

## 🎯 Mejores Prácticas

1. **Usa MinIO para desarrollo local** - Es más ligero y específico para S3
2. **Usa las mismas variables de entorno** - Facilita la transición entre entornos
3. **Nunca hagas commit de credenciales** - Usa variables de entorno o AWS Secrets Manager
4. **Nombra tus buckets correctamente** - Usa prefijos como `dev-`, `staging-`, `prod-`
5. **Implementa manejo de errores** - Los fallos de red son comunes
6. **Usa URLs pre-firmadas** - Para compartir archivos de forma segura y temporal

---

## 🐛 Solución de Problemas

### Error: "Connection refused" al conectar a MinIO

**Solución:** Verifica que el servicio esté corriendo:
```bash
docker-compose ps
docker-compose logs minio
```

### Error: "Bucket already exists"

**Solución:** Normal si el bucket ya fue creado. Verifica con:
```python
s3.list_buckets()
```

### Error: "Access Denied"

**Solución:** Verifica las credenciales en las variables de entorno.

### Los cambios no se reflejan

**Solución:** Reconstruye los contenedores:
```bash
docker-compose down
docker-compose up --build -d
```

---

## 📚 Recursos Adicionales

- [Documentación de MinIO](https://min.io/docs/minio/linux/index.html)
- [Documentación de boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/)
- [LocalStack Documentation](https://docs.localstack.cloud/)

---

## ✅ Conclusión

Con esta configuración, tienes todo lo necesario para:

1. ✅ Desarrollar y probar funcionalidades de S3 localmente
2. ✅ Usar el mismo código en AWS S3 sin modificaciones
3. ✅ Ahorrar costos de desarrollo al no usar AWS durante el desarrollo
4. ✅ Trabajar sin conexión a internet
5. ✅ Hacer pruebas rápidas e iterativas

¡Feliz desarrollo! 🚀
