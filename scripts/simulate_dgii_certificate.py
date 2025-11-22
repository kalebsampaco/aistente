#!/usr/bin/env python3
"""
Script de ejemplo para generar certificados DGII simulados

Este script demuestra cómo generar certificados digitales que simulan
los emitidos por la DGII de República Dominicana para pruebas locales.
"""

import sys
import os
import logging

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.dgii_certificate_simulator import DGIICertificateSimulator

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def example_basic_certificate():
    """
    Ejemplo básico: Generar certificado con clave privada
    """
    print("\n" + "="*70)
    print("📋 EJEMPLO 1: Certificado Básico")
    print("="*70)
    
    simulator = DGIICertificateSimulator()
    
    # Configuración del certificado
    output_dir = "/tmp/dgii_certificates"
    rnc = "131257681"
    nombre = "EMPRESA DE PRUEBA SRL"
    email = "empresa@prueba.com.do"
    password = "MiPassword123"  # Contraseña para proteger archivos
    
    # Generar certificado completo
    files = simulator.generate_complete_certificate_set(
        output_dir=output_dir,
        rnc=rnc,
        nombre_contribuyente=nombre,
        email=email,
        password=password,
        valid_days=365
    )
    
    print("\n✅ Certificado generado exitosamente!")
    print(f"\n📁 Archivos creados en: {output_dir}")
    print(f"   • Clave privada: {os.path.basename(files['private_key'])}")
    print(f"   • Certificado: {os.path.basename(files['certificate'])}")
    if files['pkcs12']:
        print(f"   • PKCS#12: {os.path.basename(files['pkcs12'])}")
    
    print(f"\n🔐 Contraseña configurada: {password}")
    print("\n💡 El archivo .p12 puede ser importado en:")
    print("   • Navegadores web (Chrome, Firefox, Edge)")
    print("   • Aplicaciones de correo")
    print("   • Software de firma digital")
    
    return files


def example_verify_certificate(cert_file: str):
    """
    Ejemplo: Verificar un certificado generado
    """
    print("\n" + "="*70)
    print("🔍 EJEMPLO 2: Verificar Certificado")
    print("="*70)
    
    from cryptography import x509
    from cryptography.hazmat.backends import default_backend
    
    # Leer el certificado
    with open(cert_file, 'rb') as f:
        cert_data = f.read()
    
    certificate = x509.load_pem_x509_certificate(cert_data, default_backend())
    
    # Verificar con el simulador
    simulator = DGIICertificateSimulator()
    info = simulator.verify_certificate(certificate)
    
    print("\n📄 Información del Certificado:")
    print(f"   • Subject: {info['subject']}")
    print(f"   • Issuer: {info['issuer']}")
    print(f"   • Serial Number: {info['serial_number']}")
    print(f"   • Válido desde: {info['not_valid_before']}")
    print(f"   • Válido hasta: {info['not_valid_after']}")
    print(f"   • Estado: {'✅ Válido' if info['is_valid'] else '❌ Expirado'}")
    print(f"   • Algoritmo: {info['signature_algorithm']}")
    if 'rnc' in info:
        print(f"   • RNC: {info['rnc']}")


def example_multiple_certificates():
    """
    Ejemplo: Generar certificados para múltiples contribuyentes
    """
    print("\n" + "="*70)
    print("👥 EJEMPLO 3: Múltiples Certificados")
    print("="*70)
    
    simulator = DGIICertificateSimulator()
    
    # Lista de contribuyentes de prueba
    contribuyentes = [
        {
            'rnc': '131257681',
            'nombre': 'EMPRESA ABC SRL',
            'email': 'abc@empresa.com.do'
        },
        {
            'rnc': '401000001',
            'nombre': 'COMERCIAL XYZ SA',
            'email': 'xyz@comercial.com.do'
        },
        {
            'rnc': '501000002',
            'nombre': 'INDUSTRIAS 123 EIRL',
            'email': 'info@industrias123.com.do'
        }
    ]
    
    output_base = "/tmp/dgii_certificates_batch"
    password = "Batch2024"
    
    print(f"\n📦 Generando {len(contribuyentes)} certificados...")
    
    for contrib in contribuyentes:
        output_dir = os.path.join(output_base, f"rnc_{contrib['rnc']}")
        
        files = simulator.generate_complete_certificate_set(
            output_dir=output_dir,
            rnc=contrib['rnc'],
            nombre_contribuyente=contrib['nombre'],
            email=contrib['email'],
            password=password,
            valid_days=730  # 2 años
        )
        
        print(f"\n✅ Certificado para RNC {contrib['rnc']} creado en: {output_dir}")


def example_sign_data():
    """
    Ejemplo: Firmar datos con el certificado (demostración)
    """
    print("\n" + "="*70)
    print("✍️  EJEMPLO 4: Firma Digital")
    print("="*70)
    
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import padding
    
    simulator = DGIICertificateSimulator()
    
    # Generar clave y certificado
    private_key = simulator.generate_private_key()
    
    # Datos a firmar (simulación de factura electrónica)
    data = b"""
    FACTURA ELECTRONICA
    RNC: 131257681
    NCF: E310000000001
    Monto: RD$ 1,000.00
    Fecha: 2024-01-15
    """
    
    print("\n📄 Datos a firmar:")
    print(data.decode('utf-8'))
    
    # Firmar los datos
    signature = private_key.sign(
        data,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    
    print(f"\n✅ Firma digital generada ({len(signature)} bytes)")
    print(f"   Primeros 32 bytes (hex): {signature[:32].hex()}")
    
    # Verificar la firma
    try:
        public_key = private_key.public_key()
        public_key.verify(
            signature,
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        print("\n✅ Firma verificada correctamente")
        print("   Los datos no han sido modificados")
    except Exception as e:
        print(f"\n❌ Error al verificar firma: {e}")


def show_usage_info():
    """
    Muestra información de uso
    """
    print("\n" + "="*70)
    print("📚 INFORMACIÓN DE USO")
    print("="*70)
    
    print("\n🔧 Uso en tu código:")
    print("""
from app.services.dgii_certificate_simulator import DGIICertificateSimulator

# Crear simulador
simulator = DGIICertificateSimulator()

# Generar certificado completo
files = simulator.generate_complete_certificate_set(
    output_dir="/tmp/certificados",
    rnc="131257681",
    nombre_contribuyente="MI EMPRESA SRL",
    email="contacto@miempresa.com.do",
    password="MiPassword123",
    valid_days=365
)

# Los archivos generados están en:
# - files['private_key']: Clave privada (formato PEM)
# - files['certificate']: Certificado (formato PEM)
# - files['pkcs12']: Archivo .p12 (importable en navegadores)
    """)
    
    print("\n⚠️  IMPORTANTE:")
    print("   • Estos certificados son SOLO para pruebas")
    print("   • NO son válidos para uso real con la DGII")
    print("   • Guarda las contraseñas de forma segura")
    print("   • No compartas las claves privadas")
    
    print("\n💡 Casos de uso:")
    print("   • Desarrollo de aplicaciones de facturación electrónica")
    print("   • Pruebas de integración con servicios DGII")
    print("   • Validación de flujos de firma digital")
    print("   • Testing de aplicaciones tributarias")


def main():
    """
    Función principal
    """
    print("\n🏛️  SIMULADOR DE CERTIFICADOS DGII")
    print("   República Dominicana - Pruebas Locales")
    print("="*70)
    
    # Verificar que cryptography está instalado
    try:
        import cryptography
        print(f"✅ Módulo cryptography instalado (versión {cryptography.__version__})")
    except ImportError:
        print("❌ Error: El módulo 'cryptography' no está instalado")
        print("   Instálalo con: pip install cryptography")
        return
    
    # Menú de opciones
    print("\n📋 EJEMPLOS DISPONIBLES:")
    print("   1. Generar certificado básico")
    print("   2. Verificar certificado")
    print("   3. Generar múltiples certificados")
    print("   4. Demostración de firma digital")
    print("   5. Ver información de uso")
    print("   0. Salir")
    
    while True:
        try:
            opcion = input("\n➡️  Selecciona una opción (0-5): ").strip()
            
            if opcion == '0':
                print("\n👋 ¡Hasta luego!")
                break
            elif opcion == '1':
                files = example_basic_certificate()
                # Ofrecer verificar el certificado generado
                verify = input("\n¿Deseas verificar el certificado generado? (s/n): ").lower()
                if verify in ['s', 'si', 'y', 'yes']:
                    example_verify_certificate(files['certificate'])
            elif opcion == '2':
                cert_path = input("Ruta del certificado a verificar: ").strip()
                if os.path.exists(cert_path):
                    example_verify_certificate(cert_path)
                else:
                    print(f"❌ Archivo no encontrado: {cert_path}")
            elif opcion == '3':
                example_multiple_certificates()
            elif opcion == '4':
                example_sign_data()
            elif opcion == '5':
                show_usage_info()
            else:
                print("❌ Opción no válida. Intenta de nuevo.")
        except KeyboardInterrupt:
            print("\n\n👋 Programa interrumpido. ¡Hasta luego!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
