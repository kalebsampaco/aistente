#!/usr/bin/env python3
"""
Script de ejemplo para probar operaciones con S3/MinIO local

Este script demuestra cómo usar el servicio S3 tanto con MinIO local
como con AWS S3 real.
"""

import sys
import os

# Añadir el directorio raíz al path para importar los módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.s3_service import S3Service
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_s3_operations():
    """
    Ejecuta pruebas básicas de operaciones S3
    """
    print("\n" + "="*60)
    print("🚀 PRUEBA DE OPERACIONES S3/MinIO")
    print("="*60 + "\n")
    
    # Inicializar el servicio S3
    # Por defecto usa las variables de entorno configuradas
    s3_service = S3Service()
    
    bucket_name = "test-bucket-demo"
    test_file = "/tmp/test_file.txt"
    downloaded_file = "/tmp/downloaded_file.txt"
    
    try:
        # 1. Listar buckets existentes
        print("📋 1. Listando buckets existentes...")
        buckets = s3_service.list_buckets()
        if buckets:
            print(f"   Buckets encontrados: {', '.join(buckets)}")
        else:
            print("   No se encontraron buckets")
        
        # 2. Crear un bucket de prueba
        print(f"\n🗂️  2. Creando bucket '{bucket_name}'...")
        if s3_service.create_bucket(bucket_name):
            print(f"   ✅ Bucket '{bucket_name}' creado exitosamente")
        else:
            print(f"   ℹ️  El bucket '{bucket_name}' ya existe o hubo un error")
        
        # 3. Crear un archivo de prueba
        print(f"\n📝 3. Creando archivo de prueba...")
        with open(test_file, 'w') as f:
            f.write("¡Hola desde el servicio S3!\n")
            f.write("Este es un archivo de prueba para demostrar la funcionalidad.\n")
            f.write("Funciona tanto con MinIO local como con AWS S3.\n")
        print(f"   ✅ Archivo creado: {test_file}")
        
        # 4. Subir el archivo
        print(f"\n⬆️  4. Subiendo archivo a S3...")
        if s3_service.upload_file(test_file, bucket_name, "prueba/test_file.txt"):
            print(f"   ✅ Archivo subido exitosamente")
        else:
            print(f"   ❌ Error al subir archivo")
            return
        
        # 5. Listar objetos en el bucket
        print(f"\n📂 5. Listando objetos en el bucket '{bucket_name}'...")
        objects = s3_service.list_objects(bucket_name)
        if objects:
            print(f"   Se encontraron {len(objects)} objetos:")
            for obj in objects:
                print(f"     - {obj['Key']} ({obj['Size']} bytes)")
        else:
            print("   No se encontraron objetos")
        
        # 6. Verificar si el objeto existe
        print(f"\n🔍 6. Verificando existencia del objeto...")
        if s3_service.object_exists(bucket_name, "prueba/test_file.txt"):
            print("   ✅ El objeto existe en el bucket")
        else:
            print("   ❌ El objeto no existe")
        
        # 7. Generar URL pre-firmada
        print(f"\n🔗 7. Generando URL pre-firmada...")
        url = s3_service.get_object_url(bucket_name, "prueba/test_file.txt", expiration=3600)
        if url:
            print(f"   ✅ URL generada (válida por 1 hora):")
            print(f"   {url[:100]}..." if len(url) > 100 else f"   {url}")
        else:
            print("   ❌ Error al generar URL")
        
        # 8. Descargar el archivo
        print(f"\n⬇️  8. Descargando archivo desde S3...")
        if s3_service.download_file(bucket_name, "prueba/test_file.txt", downloaded_file):
            print(f"   ✅ Archivo descargado a: {downloaded_file}")
            with open(downloaded_file, 'r') as f:
                print("\n   📄 Contenido del archivo descargado:")
                for line in f:
                    print(f"      {line.rstrip()}")
        else:
            print("   ❌ Error al descargar archivo")
        
        # 9. Eliminar el objeto
        print(f"\n🗑️  9. Eliminando objeto del bucket...")
        if s3_service.delete_object(bucket_name, "prueba/test_file.txt"):
            print("   ✅ Objeto eliminado exitosamente")
        else:
            print("   ❌ Error al eliminar objeto")
        
        # 10. Eliminar el bucket (con force para eliminar contenido si existe)
        print(f"\n🗑️  10. Eliminando bucket '{bucket_name}'...")
        if s3_service.delete_bucket(bucket_name, force=True):
            print(f"   ✅ Bucket '{bucket_name}' eliminado exitosamente")
        else:
            print(f"   ❌ Error al eliminar bucket")
        
        print("\n" + "="*60)
        print("✅ PRUEBAS COMPLETADAS EXITOSAMENTE")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {e}")
        logger.exception("Error en test_s3_operations")
    finally:
        # Limpiar archivos temporales
        for file in [test_file, downloaded_file]:
            if os.path.exists(file):
                os.remove(file)
                print(f"🧹 Archivo temporal eliminado: {file}")


def show_configuration():
    """
    Muestra la configuración actual de S3
    """
    print("\n" + "="*60)
    print("⚙️  CONFIGURACIÓN ACTUAL")
    print("="*60)
    print(f"AWS_ACCESS_KEY_ID: {os.getenv('AWS_ACCESS_KEY_ID', 'minioadmin')}")
    print(f"AWS_SECRET_ACCESS_KEY: {'*' * len(os.getenv('AWS_SECRET_ACCESS_KEY', 'minioadmin'))}")
    print(f"AWS_ENDPOINT_URL: {os.getenv('AWS_ENDPOINT_URL', 'http://localhost:9000')}")
    print(f"AWS_DEFAULT_REGION: {os.getenv('AWS_DEFAULT_REGION', 'us-east-1')}")
    print("="*60 + "\n")


if __name__ == "__main__":
    print("\n🎯 Script de Prueba de S3/MinIO")
    print("="*60)
    
    show_configuration()
    
    print("\n💡 Este script funciona con:")
    print("   • MinIO local (configuración por defecto)")
    print("   • AWS S3 (cambiando las variables de entorno)\n")
    
    response = input("¿Desea ejecutar las pruebas? (s/n): ")
    if response.lower() in ['s', 'si', 'y', 'yes']:
        test_s3_operations()
    else:
        print("Pruebas canceladas.")
