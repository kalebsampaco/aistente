# Simulador de Certificados DGII - República Dominicana

Esta guía te ayudará a generar certificados digitales simulados que emulan los emitidos por la Dirección General de Impuestos Internos (DGII) de República Dominicana para pruebas locales.

## 💾 Almacenamiento Local

**Los certificados se guardan en tu sistema de archivos local, NO en la nube ni en S3.**

Todos los archivos generados (claves privadas, certificados, archivos .p12) se guardan en directorios locales que tú especifiques en tu computadora.

## ⚠️ IMPORTANTE

**Estos certificados son ÚNICAMENTE para pruebas y desarrollo local. NO son válidos para:**
- Transacciones reales con la DGII
- Facturación electrónica en producción
- Declaraciones tributarias oficiales
- Cualquier uso oficial con entidades gubernamentales

## 📋 Contenido

- [¿Qué es esto?](#qué-es-esto)
- [Instalación](#instalación)
- [Uso Rápido](#uso-rápido)
- [Ejemplos de Código](#ejemplos-de-código)
- [Casos de Uso](#casos-de-uso)
- [Preguntas Frecuentes](#preguntas-frecuentes)

## 🎯 ¿Qué es esto?

El simulador de certificados DGII genera certificados digitales X.509 que simulan las características de los certificados emitidos por la DGII de República Dominicana. Esto te permite:

- 🧪 **Desarrollar aplicaciones** de facturación electrónica sin certificados reales
- 🔒 **Probar firmas digitales** en un entorno local
- 🏗️ **Construir y validar** flujos de autenticación
- 💻 **Iterar rápidamente** sin depender de procesos oficiales

## 🚀 Instalación

### Paso 1: Instalar dependencias

La dependencia principal es `cryptography`:

```bash
pip install cryptography
```

O si usas el proyecto completo:

```bash
pip install -r requirements.txt
```

### Paso 2: Verificar instalación

```bash
python -c "import cryptography; print(f'✅ cryptography {cryptography.__version__}')"
```

## ⚡ Uso Rápido

### Opción 1: Script Interactivo (Recomendado)

Ejecuta el script interactivo que te guiará paso a paso:

```bash
python scripts/simulate_dgii_certificate.py
```

El script te mostrará un menú con opciones:
1. Generar certificado básico
2. Verificar certificado
3. Generar múltiples certificados
4. Demostración de firma digital
5. Ver información de uso

### Opción 2: Uso Directo en Código

```python
from app.services.dgii_certificate_simulator import DGIICertificateSimulator

# Crear simulador
simulator = DGIICertificateSimulator()

# Generar certificado completo en carpeta local
files = simulator.generate_complete_certificate_set(
    output_dir="./certificados",              # ← Carpeta local en tu directorio actual
    rnc="131257681",                          # RNC del contribuyente
    nombre_contribuyente="MI EMPRESA SRL",     # Nombre o razón social
    email="contacto@miempresa.com.do",        # Email (opcional)
    password="MiPassword123",                  # Contraseña para proteger archivos
    valid_days=365                             # Días de validez
)

print(f"✅ Certificado generado!")
print(f"📄 Clave privada: {files['private_key']}")
print(f"📄 Certificado: {files['certificate']}")
print(f"📄 PKCS#12: {files['pkcs12']}")
```

## 📚 Ejemplos de Código

### Ejemplo 1: Certificado Básico

```python
from app.services.dgii_certificate_simulator import DGIICertificateSimulator

simulator = DGIICertificateSimulator()

# Generar certificado para una empresa - se guarda localmente
files = simulator.generate_complete_certificate_set(
    output_dir="./mis_certificados",        # ← Directorio local relativo
    rnc="131257681",
    nombre_contribuyente="EMPRESA DEMO SRL",
    email="info@empresademo.com.do",
    password="SecurePass2024",
    valid_days=365
)

# Archivos generados en ./mis_certificados/:
# - dgii_rnc_131257681_private.key (clave privada cifrada)
# - dgii_rnc_131257681_cert.pem (certificado público)
# - dgii_rnc_131257681.p12 (archivo PKCS#12 para importar)
```

### Ejemplo 2: Firmar Datos

```python
from app.services.dgii_certificate_simulator import DGIICertificateSimulator
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

simulator = DGIICertificateSimulator()

# Generar clave privada
private_key = simulator.generate_private_key()

# Datos a firmar (por ejemplo, una factura)
factura_data = b"""
NCF: E310000000001
RNC: 131257681
Monto: RD$ 5,000.00
Fecha: 2024-01-15
"""

# Firmar los datos
signature = private_key.sign(
    factura_data,
    padding.PSS(
        mgf=padding.MGF1(hashes.SHA256()),
        salt_length=padding.PSS.MAX_LENGTH
    ),
    hashes.SHA256()
)

print(f"✅ Firma generada: {len(signature)} bytes")

# Verificar la firma
public_key = private_key.public_key()
try:
    public_key.verify(
        signature,
        factura_data,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    print("✅ Firma válida - datos no modificados")
except Exception:
    print("❌ Firma inválida - datos fueron modificados")
```

### Ejemplo 3: Verificar Certificado

```python
from app.services.dgii_certificate_simulator import DGIICertificateSimulator
from cryptography import x509
from cryptography.hazmat.backends import default_backend

# Cargar certificado desde archivo
with open('/tmp/dgii_certs/dgii_rnc_131257681_cert.pem', 'rb') as f:
    cert_data = f.read()

certificate = x509.load_pem_x509_certificate(cert_data, default_backend())

# Verificar con el simulador
simulator = DGIICertificateSimulator()
info = simulator.verify_certificate(certificate)

print("📄 Información del Certificado:")
print(f"   RNC: {info.get('rnc', 'N/A')}")
print(f"   Válido desde: {info['not_valid_before']}")
print(f"   Válido hasta: {info['not_valid_after']}")
print(f"   Estado: {'✅ Válido' if info['is_valid'] else '❌ Expirado'}")
```

### Ejemplo 4: Múltiples Certificados

```python
from app.services.dgii_certificate_simulator import DGIICertificateSimulator

simulator = DGIICertificateSimulator()

# Lista de empresas para generar certificados
empresas = [
    {'rnc': '131257681', 'nombre': 'EMPRESA A SRL'},
    {'rnc': '401000001', 'nombre': 'EMPRESA B SA'},
    {'rnc': '501000002', 'nombre': 'EMPRESA C EIRL'},
]

for empresa in empresas:
    output_dir = f"/tmp/certs/{empresa['rnc']}"
    
    files = simulator.generate_complete_certificate_set(
        output_dir=output_dir,
        rnc=empresa['rnc'],
        nombre_contribuyente=empresa['nombre'],
        email=f"info@{empresa['rnc']}.com.do",
        password="Common2024",
        valid_days=730  # 2 años
    )
    
    print(f"✅ Certificado para {empresa['nombre']} generado en {output_dir}")
```

## 🎯 Casos de Uso

### 1. Desarrollo de Facturación Electrónica

```python
# Simular firma de factura electrónica
simulator = DGIICertificateSimulator()
private_key = simulator.generate_private_key()

# Tu factura en formato XML o JSON
factura_xml = """
<FacturaElectronica>
    <NCF>E310000000001</NCF>
    <RNC>131257681</RNC>
    <Monto>5000.00</Monto>
</FacturaElectronica>
"""

# Firmar la factura
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

signature = private_key.sign(
    factura_xml.encode('utf-8'),
    padding.PSS(
        mgf=padding.MGF1(hashes.SHA256()),
        salt_length=padding.PSS.MAX_LENGTH
    ),
    hashes.SHA256()
)

# Enviar factura + firma a tu sistema
```

### 2. Testing de Autenticación

```python
# Generar certificado para testing de login
simulator = DGIICertificateSimulator()

files = simulator.generate_complete_certificate_set(
    output_dir="/tmp/test_auth",
    rnc="999999999",  # RNC de testing
    nombre_contribuyente="USUARIO DE PRUEBA",
    email="test@testing.local",
    password="TestPass123",
    valid_days=30  # Solo 30 días para testing
)

# Usar el certificado en tus pruebas automatizadas
# import el certificado y usa para autenticación
```

### 3. Desarrollo de Portal Tributario

```python
# Simular múltiples contribuyentes para un portal
simulator = DGIICertificateSimulator()

# Generar certificados para diferentes tipos de contribuyentes
tipos_contribuyentes = [
    {'tipo': 'PF', 'rnc': '001000001', 'nombre': 'JUAN PEREZ'},  # Persona física
    {'tipo': 'PJ', 'rnc': '131000001', 'nombre': 'EMPRESA X SRL'},  # Persona jurídica
    {'tipo': 'EX', 'rnc': '401000001', 'nombre': 'MULTINACIONAL SA'},  # Extranjero
]

for contrib in tipos_contribuyentes:
    files = simulator.generate_complete_certificate_set(
        output_dir=f"/tmp/portal/{contrib['tipo']}",
        rnc=contrib['rnc'],
        nombre_contribuyente=contrib['nombre'],
        password="Portal2024"
    )
```

## 📖 Estructura de Archivos Generados

Cuando generas un certificado completo, obtienes tres archivos:

### 1. Clave Privada (`*_private.key`)
- **Formato:** PEM
- **Cifrado:** Opcional (con contraseña)
- **Uso:** Firmar datos, descifrar información
- **Seguridad:** ⚠️ NUNCA compartir

```
-----BEGIN ENCRYPTED PRIVATE KEY-----
MIIFHzBJBgkqhkiG9w0BBQ0wPDAbBgkqhkiG9w0BBQwwDgQI...
-----END ENCRYPTED PRIVATE KEY-----
```

### 2. Certificado Público (`*_cert.pem`)
- **Formato:** PEM (X.509)
- **Contenido:** Información pública del certificado
- **Uso:** Verificar firmas, cifrar datos
- **Seguridad:** ✅ Puede compartirse públicamente

```
-----BEGIN CERTIFICATE-----
MIIDXTCCAkWgAwIBAgIUFj8qF3kF0zKpv3+EwPm...
-----END CERTIFICATE-----
```

### 3. Archivo PKCS#12 (`*.p12`)
- **Formato:** PKCS#12 (binario)
- **Contenido:** Clave privada + certificado
- **Uso:** Importar en navegadores, sistemas
- **Seguridad:** 🔒 Protegido con contraseña

## 🔒 Seguridad

### Mejores Prácticas

1. **Usa contraseñas fuertes**
   ```python
   # ✅ Buena contraseña
   password = "MyC0mpl3x!P@ssw0rd2024"
   
   # ❌ Mala contraseña
   password = "1234"
   ```

2. **Protege las claves privadas**
   ```bash
   # Establecer permisos restrictivos
   chmod 600 /tmp/certs/*_private.key
   ```

3. **No incluyas en control de versiones**
   ```gitignore
   # .gitignore
   *.key
   *.p12
   *.pfx
   /certificados/
   ```

4. **Rotación de certificados**
   ```python
   # Genera certificados con validez limitada para testing
   valid_days=30  # Solo 30 días
   ```

## ❓ Preguntas Frecuentes

### ¿Puedo usar estos certificados en producción?

**NO.** Estos certificados son solo para desarrollo y pruebas locales. Para producción necesitas:
- Certificados oficiales emitidos por la DGII
- Proceso de validación con autoridades certificadoras
- Cumplimiento con normativas legales

### ¿Cómo importo el archivo .p12 en mi navegador?

**Chrome/Edge:**
1. Configuración → Privacidad y seguridad → Seguridad
2. Administrar certificados
3. Importar → Selecciona el archivo .p12
4. Ingresa la contraseña

**Firefox:**
1. Configuración → Privacidad y seguridad
2. Certificados → Ver certificados
3. Importar → Selecciona el archivo .p12
4. Ingresa la contraseña

### ¿Qué es un RNC?

El **RNC (Registro Nacional de Contribuyentes)** es el número de identificación fiscal único asignado por la DGII a cada contribuyente en República Dominicana.

Formato:
- Persona jurídica: 9 dígitos (ej: 131257681)
- Persona física: 11 dígitos (cédula)

### ¿Cómo puedo verificar una firma digital?

```python
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

# Cargar clave pública desde certificado
public_key = certificate.public_key()

# Verificar firma
try:
    public_key.verify(
        signature,      # Firma a verificar
        data,          # Datos originales
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    print("✅ Firma válida")
except Exception:
    print("❌ Firma inválida")
```

### ¿Puedo usar otros algoritmos de firma?

Sí, el simulador usa RSA con SHA-256 por defecto, pero puedes usar:

```python
# RSA con diferentes hashes
hashes.SHA256()   # Recomendado
hashes.SHA384()
hashes.SHA512()

# Diferentes esquemas de padding
padding.PSS(...)  # Recomendado (más seguro)
padding.PKCS1v15()  # Tradicional (compatible)
```

## 🛠️ Solución de Problemas

### Error: "Module 'cryptography' not found"

```bash
pip install cryptography
```

### Error: "Permission denied" al guardar archivos

```python
# Usa un directorio con permisos de escritura
output_dir = "/tmp/certificados"  # ✅ En Linux/Mac
output_dir = "C:/temp/certificados"  # ✅ En Windows
```

### El archivo .p12 no se importa en el navegador

- Verifica que usaste una contraseña al generar el certificado
- Asegúrate de usar la contraseña correcta al importar
- Prueba con un nombre de archivo sin espacios ni caracteres especiales

## 📚 Referencias

- [Cryptography Documentation](https://cryptography.io/)
- [X.509 Certificate Standard](https://tools.ietf.org/html/rfc5280)
- [PKCS#12 Format](https://tools.ietf.org/html/rfc7292)
- [DGII República Dominicana](https://dgii.gov.do/)

## 📞 Soporte

Para preguntas sobre el simulador, revisa:
1. Esta documentación
2. El código comentado en `app/services/dgii_certificate_simulator.py`
3. Los ejemplos en `scripts/simulate_dgii_certificate.py`

---

**Recuerda:** Estos son certificados de prueba. Para uso oficial con la DGII, debes obtener certificados reales a través de los canales oficiales.
