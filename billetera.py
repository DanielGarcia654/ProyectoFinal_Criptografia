import os
import json
import base64
import datetime
import hashlib
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

NOMBRE_ARCHIVO_CLAVES = "keystore.json"

def generar_direccion(bytes_publicos):
    digest=hashlib.sha256(bytes_publicos).digest()
    direccion_bytes=digest[:20]
    return "0x"+direccion_bytes.hex()

def crear_billetera():
    print("*Configuración inicial de sistema de billetera fría")
    contraseña=input("Define una contraseña segura para tu billetera: ")
    if not contraseña:
        print("Se debe generar una contraseña obligatoriamente")
        return

    print("*Generando par de llaves criptográficas (Ed25519)...")

    llave_privada=ed25519.Ed25519PrivateKey.generate()
    llave_publica=llave_privada.public_key()

    bytes_privados=llave_privada.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption()
    )
    bytes_publicos=llave_publica.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )
    direccion=generar_direccion(bytes_publicos)

    print("Derivando clave de encriptación segura...")
    sal=os.urandom(16) 
    
    kdf = Argon2id(
        salt=sal,
        length=32,            
        iterations=2,         
        memory_cost=64 * 1024,
        lanes=1
    )
    llave_maestra_encriptacion=kdf.derive(contraseña.encode('utf-8'))

    print("Encriptando llave privada...")
    aesgcm=AESGCM(llave_maestra_encriptacion)
    nonce=os.urandom(12) 

    datos_cifrados=aesgcm.encrypt(nonce, bytes_privados, None)
    texto_cifrado=datos_cifrados[:-16]
    etiqueta_auth=datos_cifrados[-16:]

    datos_billetera={
        "kdf":"Argon2id",
        "kdf_params":{
            "salt_b64":base64.b64encode(sal).decode('utf-8'),
            "t_cost":2,
            "m_cost":64 * 1024,
            "p":1
        },
        "cipher":"AES-256-GCM",
        "cipher_params":{
            "nonce_b64":base64.b64encode(nonce).decode('utf-8')
        },
        "ciphertext_b64":base64.b64encode(texto_cifrado).decode('utf-8'),
        "tag_b64":base64.b64encode(etiqueta_auth).decode('utf-8'),
        "pubkey_b64":base64.b64encode(bytes_publicos).decode('utf-8'),
        "address":direccion,
        "scheme":"Ed25519",
        "created":datetime.datetime.now(datetime.timezone.utc).isoformat()
    }

    try:
        with open(NOMBRE_ARCHIVO_CLAVES,"w") as archivo:
            json.dump(datos_billetera, archivo, indent=4)
        
        print(f"\nEXITO, billetera creada y guardada en '{NOMBRE_ARCHIVO_CLAVES}'")
        print(f"Dirección: {direccion}")
        print(f"Llave Pública (Base64): {datos_billetera['pubkey_b64']}")
        print("NO PIERDAS TU CONTRASEÑA O PERDERAS ACCESO A TUS FONDOS.")
        
    except IOError as e:
        print(f"Error al guardar el archivo: {e}")

def cargar_billetera():
    print(f"\nCargar billetera ({NOMBRE_ARCHIVO_CLAVES})")
    if not os.path.exists(NOMBRE_ARCHIVO_CLAVES):
        print("Error: No existe el archivo keystore.json.")
        return None

    try:
        with open(NOMBRE_ARCHIVO_CLAVES,"r") as f:
            datos=json.load(f)

        contraseña=input("Ingresa tu contraseña para desbloquear: ")
        
        sal=base64.b64decode(datos["kdf_params"]["salt_b64"])
        nonce=base64.b64decode(datos["cipher_params"]["nonce_b64"])
        texto_cifrado=base64.b64decode(datos["ciphertext_b64"])
        tag=base64.b64decode(datos["tag_b64"])
        
        kdf=Argon2id(
            salt=sal,
            length=32,
            iterations=datos["kdf_params"]["t_cost"],
            memory_cost=datos["kdf_params"]["m_cost"],
            lanes=datos["kdf_params"]["p"]
        )
        llave_maestra=kdf.derive(contraseña.encode('utf-8'))

        aesgcm=AESGCM(llave_maestra)
        
        datos_para_decifrar=texto_cifrado + tag
        bytes_privados=aesgcm.decrypt(nonce, datos_para_decifrar, None)
        
        llave_privada=ed25519.Ed25519PrivateKey.from_private_bytes(bytes_privados)
        
        print("\nEXITO. Contraseña correcta, billetera desbloqueada.")
        
        bytes_publicos=llave_privada.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        direccion=generar_direccion(bytes_publicos)
        print(f"Dirección recuperada: {direccion}")
        
        return llave_privada

    except Exception:
        print("\nFALLO. No se pudo desbloquear la billetera (Contraseña incorrecta).")
        return None

if __name__=="__main__":
    print("1. Crear nueva billetera")
    print("2. Cargar billetera existente")
    opcion=input("Selecciona una opción (1/2): ")
    
    if opcion=="1":
        crear_billetera()
    elif opcion=="2":
        cargar_billetera()
    else:
        print("Opción no válida")