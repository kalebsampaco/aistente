# 🚀 Inicio Rápido - Pruebas de S3 Local

Esta guía te ayudará a empezar en menos de 5 minutos.

## ⚡ Pasos Rápidos

### 1. Iniciar MinIO

```bash
docker compose up -d
```

Esto inicia:
- ✅ MinIO (S3 local) en http://localhost:9000
- ✅ Consola Web en http://localhost:9001
- ✅ Servicio Ollama
- ✅ Asistente principal

### 2. Verificar que MinIO está funcionando

Abre tu navegador en http://localhost:9001

- **Usuario**: minioadmin
- **Contraseña**: minioadmin

### 3. Ejecutar el Script de Prueba

```bash
# Asegúrate de tener las dependencias instaladas
pip install boto3

# Ejecuta el script de prueba
python scripts/test_s3.py
```

Presiona `s` cuando te pregunte si deseas ejecutar las pruebas.

## 🎯 ¿Qué hace el script?

El script automaticamente:

1. ✅ Lista los buckets existentes
2. ✅ Crea un bucket de prueba llamado `test-bucket-demo`
3. ✅ Crea y sube un archivo de prueba
4. ✅ Lista los objetos en el bucket
5. ✅ Genera una URL pre-firmada (para compartir temporalmente)
6. ✅ Descarga el archivo
7. ✅ Limpia todo (elimina objeto y bucket)

## 📝 Usar en tu Propio Código

```python
from app.services.s3_service import S3Service

# Inicializar (usa las variables de entorno automáticamente)
s3 = S3Service()

# Crear un bucket
s3.create_bucket("mi-bucket")

# Subir un archivo
s3.upload_file("documento.pdf", "mi-bucket", "docs/documento.pdf")

# Listar archivos
archivos = s3.list_objects("mi-bucket")
for archivo in archivos:
    print(f"📄 {archivo['Key']} - {archivo['Size']} bytes")
```

## 🔄 Cambiar a AWS S3 Real

Para usar AWS S3 en lugar de MinIO local, solo cambia las variables de entorno:

```bash
# En tu terminal o .env
export AWS_ACCESS_KEY_ID=tu_access_key_real
export AWS_SECRET_ACCESS_KEY=tu_secret_key_real
# NO establecer AWS_ENDPOINT_URL
export AWS_DEFAULT_REGION=us-east-1
```

**¡El mismo código funciona sin cambios!**

## 🆘 Problemas Comunes

### Error: "Connection refused"

**Solución**: Verifica que los contenedores estén corriendo:
```bash
docker compose ps
```

Si no están corriendo:
```bash
docker compose up -d
```

### Error: "Credentials not found"

**Solución**: Verifica que las variables de entorno estén configuradas.

Para MinIO local, estas son las variables por defecto (ya configuradas en docker-compose.yml):
```bash
AWS_ACCESS_KEY_ID=minioadmin
AWS_SECRET_ACCESS_KEY=minioadmin
AWS_ENDPOINT_URL=http://localhost:9000
AWS_DEFAULT_REGION=us-east-1
```

## 📚 Documentación Completa

Para más información, consulta:
- [Guía Completa de S3](docs/S3_LOCAL_TESTING.md)
- [README del Proyecto](README.md)

## 💡 Próximos Pasos

1. Experimenta con el servicio S3 en la consola web de MinIO
2. Crea tus propios buckets y sube archivos
3. Integra el servicio S3 en tu aplicación
4. Lee la documentación completa para casos de uso avanzados

¡Eso es todo! Ya estás listo para trabajar con S3 localmente. 🎉
