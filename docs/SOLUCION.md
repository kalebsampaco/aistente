# Respuesta: Herramientas para Pruebas de S3 Local

## 🎯 Tu Pregunta

> "quiero realizar pruebas de almacenamiento en buckets de s3 de aws en mi equipo local, que herramientas podría usar para hacer este trabajo y que luego sea aplicable para aws"

## ✅ La Solución

He implementado una solución completa usando **MinIO** y **boto3** que te permite probar S3 localmente y luego usar el mismo código en AWS.

## 🛠️ Herramientas Recomendadas

### 1. MinIO (Principal - Ya Implementado) ⭐

**¿Qué es?**
MinIO es un servidor de almacenamiento de objetos compatible al 100% con la API de Amazon S3.

**¿Por qué MinIO?**
- ✅ **Compatible al 100% con AWS S3** - La misma API
- ✅ **El mismo código funciona en AWS** - Sin cambios
- ✅ **Gratis y de código abierto**
- ✅ **Rápido y ligero**
- ✅ **Incluye interfaz web**
- ✅ **Funciona sin internet**

**¿Cómo lo uso?**
```bash
# 1. Iniciar MinIO
docker compose up -d

# 2. Acceder a la consola web
# Abre http://localhost:9001
# Usuario: minioadmin
# Contraseña: minioadmin

# 3. Usar en tu código Python
from app.services.s3_service import S3Service

s3 = S3Service()
s3.create_bucket("mi-bucket")
s3.upload_file("archivo.pdf", "mi-bucket")
```

### 2. LocalStack (Alternativa)

**¿Qué es?**
LocalStack emula múltiples servicios de AWS (S3, DynamoDB, Lambda, etc.)

**¿Cuándo usarlo?**
- Si necesitas probar múltiples servicios de AWS
- Si necesitas S3, SQS, SNS, Lambda, etc. al mismo tiempo

**Desventajas:**
- ⚠️ Más pesado que MinIO
- ⚠️ Algunas características requieren versión de pago

## 📦 ¿Qué hay en el Proyecto?

### 1. Servicio S3 (app/services/s3_service.py)

Clase Python lista para usar con métodos para:
- `create_bucket()` - Crear buckets
- `upload_file()` - Subir archivos
- `download_file()` - Descargar archivos
- `list_objects()` - Listar objetos
- `delete_object()` - Eliminar objetos
- `get_object_url()` - Generar URLs temporales

### 2. Script de Prueba (scripts/test_s3.py)

Script interactivo que demuestra todas las operaciones:
```bash
python scripts/test_s3.py
```

### 3. Configuración (docker-compose.yml)

MinIO ya está configurado y listo para usar:
- Puerto API: 9000
- Puerto Web: 9001

## 🚀 Cómo Empezar (3 Pasos)

### Paso 1: Iniciar MinIO
```bash
docker compose up -d
```

### Paso 2: Verificar (Opcional)
Abre http://localhost:9001 en tu navegador
- Usuario: minioadmin
- Contraseña: minioadmin

### Paso 3: Probar
```bash
python scripts/test_s3.py
```

## 🔄 ¿Cómo Cambio a AWS S3 Real?

**¡MUY FÁCIL!** Solo cambias las variables de entorno:

### Para MinIO Local:
```bash
export AWS_ACCESS_KEY_ID=minioadmin
export AWS_SECRET_ACCESS_KEY=minioadmin
export AWS_ENDPOINT_URL=http://localhost:9000
```

### Para AWS S3 Real:
```bash
export AWS_ACCESS_KEY_ID=tu_access_key_de_aws
export AWS_SECRET_ACCESS_KEY=tu_secret_key_de_aws
# NO establecer AWS_ENDPOINT_URL
```

**¡El código no cambia!** Solo las variables de entorno. 🎉

## 💡 Ejemplo Completo

```python
from app.services.s3_service import S3Service

# Inicializar (usa las variables de entorno automáticamente)
s3 = S3Service()

# Crear un bucket
s3.create_bucket("mi-proyecto")

# Subir un archivo
s3.upload_file("/home/usuario/documento.pdf", "mi-proyecto", "docs/documento.pdf")

# Listar archivos en el bucket
archivos = s3.list_objects("mi-proyecto")
for archivo in archivos:
    print(f"📄 {archivo['Key']} - {archivo['Size']} bytes")

# Descargar un archivo
s3.download_file("mi-proyecto", "docs/documento.pdf", "/tmp/documento.pdf")

# Generar URL temporal (válida por 1 hora)
url = s3.get_object_url("mi-proyecto", "docs/documento.pdf", expiration=3600)
print(f"Enlace temporal: {url}")

# Eliminar archivo
s3.delete_object("mi-proyecto", "docs/documento.pdf")

# Eliminar bucket
s3.delete_bucket("mi-proyecto", force=True)
```

## 📊 Comparación: Local vs AWS

| Característica | MinIO (Local) | AWS S3 (Producción) |
|---------------|---------------|---------------------|
| **Velocidad** | ⚡ Instantáneo | 🌐 Depende de red |
| **Costo** | 💰 Gratis | 💳 $0.023/GB/mes |
| **Internet** | ❌ No necesario | ✅ Requerido |
| **Desarrollo** | ✅ Perfecto | ❌ Caro/lento |
| **Producción** | ❌ No apto | ✅ Ideal |
| **Código** | 💻 Mismo código | 💻 Mismo código |

## 🎯 Ventajas de Esta Solución

1. **💰 Ahorra dinero** - No gastas en AWS durante desarrollo
2. **⚡ Más rápido** - No hay latencia de red
3. **🔒 Más seguro** - Datos no salen de tu computadora
4. **📴 Offline** - Funciona sin internet
5. **🔄 Transición fácil** - Solo cambias variables de entorno
6. **✅ Producción-ready** - El mismo código en AWS

## 📚 Documentación Completa

- [Inicio Rápido](QUICK_START.md) - 5 minutos
- [Guía Completa](S3_LOCAL_TESTING.md) - Todo lo que necesitas saber
- [Arquitectura](ARCHITECTURE.md) - Cómo funciona

## 🆘 ¿Necesitas Ayuda?

### MinIO no inicia
```bash
docker compose down
docker compose up -d
docker compose logs minio
```

### Error de conexión
```bash
# Verifica que MinIO esté corriendo
docker compose ps

# Debe mostrar minio-s3 como "Up"
```

### Error de credenciales
Las variables de entorno deben estar configuradas. Para desarrollo local:
```bash
export AWS_ACCESS_KEY_ID=minioadmin
export AWS_SECRET_ACCESS_KEY=minioadmin
export AWS_ENDPOINT_URL=http://localhost:9000
export AWS_DEFAULT_REGION=us-east-1
```

## 🎉 Conclusión

Ya tienes todo lo necesario para:

1. ✅ Probar S3 localmente sin costos
2. ✅ Desarrollar más rápido
3. ✅ Usar el mismo código en AWS
4. ✅ Ahorrar tiempo y dinero

**¡Empieza ahora con `docker compose up -d`!** 🚀
