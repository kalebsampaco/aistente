"""
Servicio para simular certificados digitales de la DGII (República Dominicana)

Este servicio genera certificados X.509 para pruebas locales que simulan
los certificados emitidos por la Dirección General de Impuestos Internos
de República Dominicana.

IMPORTANTE: Estos certificados son SOLO para pruebas locales y desarrollo.
NO deben usarse en producción ni para transacciones reales con la DGII.
"""

import os
from datetime import datetime, timedelta
from typing import Optional, Tuple
import logging

try:
    from cryptography import x509
    from cryptography.x509.oid import NameOID, ExtensionOID
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.backends import default_backend
except ImportError:
    raise ImportError(
        "El módulo 'cryptography' es requerido. "
        "Instálalo con: pip install cryptography"
    )

logger = logging.getLogger(__name__)


class DGIICertificateSimulator:
    """
    Simulador de certificados digitales de la DGII
    
    Genera certificados X.509 con características similares a los emitidos
    por la DGII de República Dominicana para pruebas locales.
    """
    
    def __init__(self):
        """Inicializa el simulador de certificados"""
        self.backend = default_backend()
        logger.info("Simulador de certificados DGII inicializado")
    
    def generate_private_key(self, key_size: int = 2048) -> rsa.RSAPrivateKey:
        """
        Genera una clave privada RSA
        
        Args:
            key_size: Tamaño de la clave en bits (por defecto 2048)
            
        Returns:
            Clave privada RSA
        """
        logger.info(f"Generando clave privada RSA de {key_size} bits...")
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=self.backend
        )
        logger.info("✅ Clave privada generada exitosamente")
        return private_key
    
    def create_dgii_certificate(
        self,
        private_key: rsa.RSAPrivateKey,
        rnc: str,
        nombre_contribuyente: str,
        email: Optional[str] = None,
        valid_days: int = 365,
        is_ca: bool = False
    ) -> x509.Certificate:
        """
        Crea un certificado que simula los emitidos por la DGII
        
        Args:
            private_key: Clave privada RSA
            rnc: RNC (Registro Nacional de Contribuyentes) del contribuyente
            nombre_contribuyente: Nombre o razón social del contribuyente
            email: Email del contribuyente (opcional)
            valid_days: Días de validez del certificado (por defecto 365)
            is_ca: Si es un certificado de autoridad certificadora
            
        Returns:
            Certificado X.509 generado
        """
        logger.info(f"Creando certificado DGII para RNC: {rnc}")
        
        # Crear el subject (información del titular del certificado)
        subject_components = [
            x509.NameAttribute(NameOID.COUNTRY_NAME, "DO"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Distrito Nacional"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Santo Domingo"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, nombre_contribuyente),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "DGII - Simulación"),
            x509.NameAttribute(NameOID.COMMON_NAME, f"RNC-{rnc}"),
        ]
        
        if email:
            subject_components.append(
                x509.NameAttribute(NameOID.EMAIL_ADDRESS, email)
            )
        
        subject = issuer = x509.Name(subject_components)
        
        # Fechas de validez
        not_valid_before = datetime.utcnow()
        not_valid_after = not_valid_before + timedelta(days=valid_days)
        
        # Crear el certificado
        builder = x509.CertificateBuilder()
        builder = builder.subject_name(subject)
        builder = builder.issuer_name(issuer)
        builder = builder.public_key(private_key.public_key())
        builder = builder.serial_number(x509.random_serial_number())
        builder = builder.not_valid_before(not_valid_before)
        builder = builder.not_valid_after(not_valid_after)
        
        # Agregar extensiones
        # Subject Alternative Name (SAN) - incluye el RNC
        san_list = [x509.DNSName(f"rnc-{rnc}.dgii.gov.do.local")]
        if email:
            san_list.append(x509.RFC822Name(email))
        
        builder = builder.add_extension(
            x509.SubjectAlternativeName(san_list),
            critical=False
        )
        
        # Key Usage - uso de la clave
        builder = builder.add_extension(
            x509.KeyUsage(
                digital_signature=True,
                key_encipherment=True,
                content_commitment=True,  # Non-repudiation
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=is_ca,
                crl_sign=is_ca,
                encipher_only=False,
                decipher_only=False
            ),
            critical=True
        )
        
        # Extended Key Usage - propósito del certificado
        builder = builder.add_extension(
            x509.ExtendedKeyUsage([
                x509.ExtendedKeyUsageOID.CLIENT_AUTH,
                x509.ExtendedKeyUsageOID.EMAIL_PROTECTION,
                x509.ExtendedKeyUsageOID.CODE_SIGNING,
            ]),
            critical=False
        )
        
        # Basic Constraints
        builder = builder.add_extension(
            x509.BasicConstraints(ca=is_ca, path_length=None),
            critical=True
        )
        
        # Subject Key Identifier
        builder = builder.add_extension(
            x509.SubjectKeyIdentifier.from_public_key(private_key.public_key()),
            critical=False
        )
        
        # Firmar el certificado con la clave privada
        certificate = builder.sign(
            private_key=private_key,
            algorithm=hashes.SHA256(),
            backend=self.backend
        )
        
        logger.info(f"✅ Certificado creado exitosamente")
        logger.info(f"   Serial Number: {certificate.serial_number}")
        logger.info(f"   Valid From: {certificate.not_valid_before}")
        logger.info(f"   Valid Until: {certificate.not_valid_after}")
        
        return certificate
    
    def save_private_key(
        self,
        private_key: rsa.RSAPrivateKey,
        filepath: str,
        password: Optional[bytes] = None
    ) -> None:
        """
        Guarda la clave privada en un archivo
        
        Args:
            private_key: Clave privada a guardar
            filepath: Ruta del archivo donde guardar
            password: Contraseña para cifrar la clave (opcional)
        """
        logger.info(f"Guardando clave privada en: {filepath}")
        
        # Determinar el algoritmo de cifrado
        if password:
            encryption_algorithm = serialization.BestAvailableEncryption(password)
            logger.info("   🔒 Clave privada será cifrada con contraseña")
        else:
            encryption_algorithm = serialization.NoEncryption()
            logger.warning("   ⚠️  Clave privada sin cifrar (no recomendado para producción)")
        
        # Serializar la clave
        pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=encryption_algorithm
        )
        
        # Guardar en archivo
        with open(filepath, 'wb') as f:
            f.write(pem)
        
        logger.info(f"✅ Clave privada guardada exitosamente")
    
    def save_certificate(
        self,
        certificate: x509.Certificate,
        filepath: str
    ) -> None:
        """
        Guarda el certificado en un archivo
        
        Args:
            certificate: Certificado a guardar
            filepath: Ruta del archivo donde guardar
        """
        logger.info(f"Guardando certificado en: {filepath}")
        
        # Serializar el certificado
        pem = certificate.public_bytes(encoding=serialization.Encoding.PEM)
        
        # Guardar en archivo
        with open(filepath, 'wb') as f:
            f.write(pem)
        
        logger.info(f"✅ Certificado guardado exitosamente")
    
    def create_pkcs12(
        self,
        private_key: rsa.RSAPrivateKey,
        certificate: x509.Certificate,
        filepath: str,
        password: bytes,
        friendly_name: Optional[str] = None
    ) -> None:
        """
        Crea un archivo PKCS#12 (.p12/.pfx) con el certificado y clave privada
        
        Args:
            private_key: Clave privada
            certificate: Certificado
            filepath: Ruta del archivo .p12 a crear
            password: Contraseña para proteger el archivo
            friendly_name: Nombre descriptivo (opcional)
        """
        logger.info(f"Creando archivo PKCS#12 en: {filepath}")
        
        from cryptography.hazmat.primitives.serialization import pkcs12
        
        # Crear el contenedor PKCS#12
        p12_data = pkcs12.serialize_key_and_certificates(
            name=friendly_name.encode('utf-8') if friendly_name else b"DGII Certificate",
            key=private_key,
            cert=certificate,
            cas=None,  # No incluimos certificados de CA adicionales
            encryption_algorithm=serialization.BestAvailableEncryption(password)
        )
        
        # Guardar en archivo
        with open(filepath, 'wb') as f:
            f.write(p12_data)
        
        logger.info(f"✅ Archivo PKCS#12 creado exitosamente")
        logger.info(f"   Este archivo puede ser importado en navegadores y aplicaciones")
    
    def generate_complete_certificate_set(
        self,
        output_dir: str,
        rnc: str,
        nombre_contribuyente: str,
        email: Optional[str] = None,
        password: Optional[str] = None,
        valid_days: int = 365
    ) -> dict:
        """
        Genera un set completo de certificado DGII simulado
        
        Args:
            output_dir: Directorio donde guardar los archivos
            rnc: RNC del contribuyente
            nombre_contribuyente: Nombre del contribuyente
            email: Email del contribuyente (opcional)
            password: Contraseña para proteger archivos (opcional)
            valid_days: Días de validez del certificado
            
        Returns:
            Diccionario con las rutas de los archivos generados
        """
        logger.info("="*60)
        logger.info("🏛️  GENERANDO CERTIFICADO DGII SIMULADO")
        logger.info("="*60)
        logger.info(f"RNC: {rnc}")
        logger.info(f"Contribuyente: {nombre_contribuyente}")
        logger.info(f"Email: {email or 'No especificado'}")
        logger.info(f"Validez: {valid_days} días")
        logger.info("="*60)
        
        # Crear directorio si no existe
        os.makedirs(output_dir, exist_ok=True)
        
        # Generar clave privada
        private_key = self.generate_private_key()
        
        # Crear certificado
        certificate = self.create_dgii_certificate(
            private_key=private_key,
            rnc=rnc,
            nombre_contribuyente=nombre_contribuyente,
            email=email,
            valid_days=valid_days
        )
        
        # Preparar rutas de archivos
        base_filename = f"dgii_rnc_{rnc}"
        files = {
            'private_key': os.path.join(output_dir, f"{base_filename}_private.key"),
            'certificate': os.path.join(output_dir, f"{base_filename}_cert.pem"),
            'pkcs12': os.path.join(output_dir, f"{base_filename}.p12")
        }
        
        # Guardar clave privada
        pwd_bytes = password.encode('utf-8') if password else None
        self.save_private_key(private_key, files['private_key'], pwd_bytes)
        
        # Guardar certificado
        self.save_certificate(certificate, files['certificate'])
        
        # Crear archivo PKCS#12 si hay contraseña
        if password:
            self.create_pkcs12(
                private_key=private_key,
                certificate=certificate,
                filepath=files['pkcs12'],
                password=password.encode('utf-8'),
                friendly_name=f"DGII - {nombre_contribuyente} (RNC: {rnc})"
            )
        else:
            logger.warning("⚠️  No se creó archivo PKCS#12 (requiere contraseña)")
            files['pkcs12'] = None
        
        logger.info("="*60)
        logger.info("✅ CERTIFICADO DGII GENERADO EXITOSAMENTE")
        logger.info("="*60)
        logger.info("Archivos generados:")
        for key, path in files.items():
            if path:
                logger.info(f"  📄 {key}: {path}")
        logger.info("="*60)
        
        return files
    
    def verify_certificate(self, certificate: x509.Certificate) -> dict:
        """
        Verifica y muestra información del certificado
        
        Args:
            certificate: Certificado a verificar
            
        Returns:
            Diccionario con información del certificado
        """
        info = {
            'subject': certificate.subject.rfc4514_string(),
            'issuer': certificate.issuer.rfc4514_string(),
            'serial_number': certificate.serial_number,
            'not_valid_before': certificate.not_valid_before,
            'not_valid_after': certificate.not_valid_after,
            'is_valid': datetime.utcnow() < certificate.not_valid_after,
            'signature_algorithm': certificate.signature_algorithm_oid._name,
        }
        
        # Extraer RNC del subject
        for attr in certificate.subject:
            if attr.oid == NameOID.COMMON_NAME:
                cn = attr.value
                if cn.startswith('RNC-'):
                    info['rnc'] = cn.replace('RNC-', '')
        
        return info
