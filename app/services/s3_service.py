"""
Servicio para operaciones con S3 (compatible con AWS S3 y MinIO local)

Este servicio funciona tanto con MinIO local como con AWS S3 real,
simplemente cambiando las variables de entorno.
"""

import os
import boto3
from botocore.exceptions import ClientError
from typing import Optional, List, Dict
import logging

logger = logging.getLogger(__name__)


class S3Service:
    """
    Servicio para gestionar operaciones con S3/MinIO
    
    Configuración mediante variables de entorno:
    - AWS_ACCESS_KEY_ID: Clave de acceso (minioadmin para MinIO local)
    - AWS_SECRET_ACCESS_KEY: Clave secreta (minioadmin para MinIO local)
    - AWS_ENDPOINT_URL: URL del endpoint (http://localhost:9000 para MinIO local, None para AWS)
    - AWS_DEFAULT_REGION: Región (us-east-1 por defecto)
    """
    
    def __init__(
        self,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        endpoint_url: Optional[str] = None,
        region: str = "us-east-1"
    ):
        """
        Inicializa el cliente S3
        
        Args:
            access_key: AWS Access Key (usa env var si no se provee)
            secret_key: AWS Secret Key (usa env var si no se provee)
            endpoint_url: URL del endpoint S3 (usa env var si no se provee, None para AWS real)
            region: Región de AWS
        """
        self.access_key = access_key or os.getenv("AWS_ACCESS_KEY_ID")
        self.secret_key = secret_key or os.getenv("AWS_SECRET_ACCESS_KEY")
        self.endpoint_url = endpoint_url or os.getenv("AWS_ENDPOINT_URL")
        self.region = region or os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        
        # Validar que se proporcionaron credenciales
        if not self.access_key or not self.secret_key:
            raise ValueError(
                "Se requieren credenciales de AWS. "
                "Configura AWS_ACCESS_KEY_ID y AWS_SECRET_ACCESS_KEY en las variables de entorno "
                "o pásalas como parámetros al constructor."
            )
        
        # Advertencia si se usan credenciales por defecto de MinIO
        if self.access_key == "minioadmin" or self.secret_key == "minioadmin":
            logger.warning(
                "⚠️  Usando credenciales por defecto de MinIO. "
                "Esto es aceptable para desarrollo local, pero NO para producción."
            )
        
        # Crear cliente S3
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            endpoint_url=self.endpoint_url,
            region_name=self.region
        )
        
        logger.info(f"Cliente S3 inicializado con endpoint: {self.endpoint_url or 'AWS S3'}")
    
    def create_bucket(self, bucket_name: str) -> bool:
        """
        Crea un nuevo bucket
        
        Args:
            bucket_name: Nombre del bucket a crear
            
        Returns:
            True si se creó exitosamente, False en caso contrario
        """
        try:
            self.s3_client.create_bucket(Bucket=bucket_name)
            logger.info(f"Bucket '{bucket_name}' creado exitosamente")
            return True
        except ClientError as e:
            logger.error(f"Error al crear bucket '{bucket_name}': {e}")
            return False
    
    def list_buckets(self) -> List[str]:
        """
        Lista todos los buckets disponibles
        
        Returns:
            Lista de nombres de buckets
        """
        try:
            response = self.s3_client.list_buckets()
            buckets = [bucket['Name'] for bucket in response.get('Buckets', [])]
            logger.info(f"Se encontraron {len(buckets)} buckets")
            return buckets
        except ClientError as e:
            logger.error(f"Error al listar buckets: {e}")
            return []
    
    def upload_file(
        self,
        file_path: str,
        bucket_name: str,
        object_name: Optional[str] = None
    ) -> bool:
        """
        Sube un archivo al bucket
        
        Args:
            file_path: Ruta del archivo local a subir
            bucket_name: Nombre del bucket destino
            object_name: Nombre del objeto en S3 (usa el nombre del archivo si no se provee)
            
        Returns:
            True si se subió exitosamente, False en caso contrario
        """
        if object_name is None:
            object_name = os.path.basename(file_path)
        
        try:
            self.s3_client.upload_file(file_path, bucket_name, object_name)
            logger.info(f"Archivo '{file_path}' subido a '{bucket_name}/{object_name}'")
            return True
        except ClientError as e:
            logger.error(f"Error al subir archivo: {e}")
            return False
    
    def download_file(
        self,
        bucket_name: str,
        object_name: str,
        file_path: str
    ) -> bool:
        """
        Descarga un archivo del bucket
        
        Args:
            bucket_name: Nombre del bucket
            object_name: Nombre del objeto en S3
            file_path: Ruta local donde guardar el archivo
            
        Returns:
            True si se descargó exitosamente, False en caso contrario
        """
        try:
            self.s3_client.download_file(bucket_name, object_name, file_path)
            logger.info(f"Archivo '{bucket_name}/{object_name}' descargado a '{file_path}'")
            return True
        except ClientError as e:
            logger.error(f"Error al descargar archivo: {e}")
            return False
    
    def list_objects(self, bucket_name: str, prefix: str = "") -> List[Dict]:
        """
        Lista objetos en un bucket
        
        Args:
            bucket_name: Nombre del bucket
            prefix: Prefijo para filtrar objetos (opcional)
            
        Returns:
            Lista de diccionarios con información de los objetos
        """
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=bucket_name,
                Prefix=prefix
            )
            objects = response.get('Contents', [])
            logger.info(f"Se encontraron {len(objects)} objetos en '{bucket_name}'")
            return objects
        except ClientError as e:
            logger.error(f"Error al listar objetos: {e}")
            return []
    
    def delete_object(self, bucket_name: str, object_name: str) -> bool:
        """
        Elimina un objeto del bucket
        
        Args:
            bucket_name: Nombre del bucket
            object_name: Nombre del objeto a eliminar
            
        Returns:
            True si se eliminó exitosamente, False en caso contrario
        """
        try:
            self.s3_client.delete_object(Bucket=bucket_name, Key=object_name)
            logger.info(f"Objeto '{bucket_name}/{object_name}' eliminado")
            return True
        except ClientError as e:
            logger.error(f"Error al eliminar objeto: {e}")
            return False
    
    def delete_bucket(self, bucket_name: str, force: bool = False) -> bool:
        """
        Elimina un bucket
        
        Args:
            bucket_name: Nombre del bucket a eliminar
            force: Si es True, elimina todos los objetos antes de eliminar el bucket
            
        Returns:
            True si se eliminó exitosamente, False en caso contrario
        """
        try:
            if force:
                # Eliminar todos los objetos primero
                objects = self.list_objects(bucket_name)
                for obj in objects:
                    self.delete_object(bucket_name, obj['Key'])
            
            self.s3_client.delete_bucket(Bucket=bucket_name)
            logger.info(f"Bucket '{bucket_name}' eliminado")
            return True
        except ClientError as e:
            logger.error(f"Error al eliminar bucket: {e}")
            return False
    
    def object_exists(self, bucket_name: str, object_name: str) -> bool:
        """
        Verifica si un objeto existe en el bucket
        
        Args:
            bucket_name: Nombre del bucket
            object_name: Nombre del objeto
            
        Returns:
            True si el objeto existe, False en caso contrario
        """
        try:
            self.s3_client.head_object(Bucket=bucket_name, Key=object_name)
            return True
        except ClientError:
            return False
    
    def get_object_url(
        self,
        bucket_name: str,
        object_name: str,
        expiration: int = 3600
    ) -> Optional[str]:
        """
        Genera una URL pre-firmada para acceder temporalmente a un objeto
        
        Args:
            bucket_name: Nombre del bucket
            object_name: Nombre del objeto
            expiration: Tiempo de expiración en segundos (por defecto 1 hora)
            
        Returns:
            URL pre-firmada o None si hay error
        """
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket_name, 'Key': object_name},
                ExpiresIn=expiration
            )
            logger.info(f"URL generada para '{bucket_name}/{object_name}'")
            return url
        except ClientError as e:
            logger.error(f"Error al generar URL: {e}")
            return None
