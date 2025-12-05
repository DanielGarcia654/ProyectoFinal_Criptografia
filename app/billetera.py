import os
import json
import base64
import datetime
import hashlib
import secrets
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

NOMBRE_ARCHIVO_CLAVES = "keystore.json"

def generar_direccion(bytes_publicos):
    sha256_hash=hashlib.sha256(bytes_publicos).digest()
    direccion_bytes=sha256_hash[-20:]
    return "0x" + direccion_bytes.hex()

def crear_billetera(contraseña,request=None):
    if not contraseña:
        return {"exito": False, "error": "Se debe generar una contraseña obligatoriamente"}
    resultado = {"exito": False, "mensaje": "", "direccion": "", "pubkey_b64": "", "error": ""}

    try:
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

        sal=os.urandom(16)
        kdf=Argon2id(salt=sal,length=32,iterations=2,memory_cost=64*1024,lanes=1)
        llave_maestra =kdf.derive(contraseña.encode('utf-8'))
        aesgcm=AESGCM(llave_maestra)
        nonce=os.urandom(12)
        datos_cifrados= aesgcm.encrypt(nonce, bytes_privados, None)
        texto_cifrado =datos_cifrados[:-16]
        etiqueta_auth= datos_cifrados[-16:]

        datos_billetera = {
            "kdf": "Argon2id",
            "kdf_params": {
                "salt_b64":base64.b64encode(sal).decode('utf-8'),
                "t_cost":2,
                "m_cost":64*1024,
                "p": 1
            },
            "cipher": "AES-256-GCM",
            "cipher_params": {"nonce_b64": base64.b64encode(nonce).decode('utf-8')},
            "ciphertext_b64": base64.b64encode(texto_cifrado).decode('utf-8'),
            "tag_b64": base64.b64encode(etiqueta_auth).decode('utf-8'),
            "pubkey_b64": base64.b64encode(bytes_publicos).decode('utf-8'),
            "address": direccion,
            "scheme": "Ed25519",
            "created": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }

        # Guardar sin checksum primero
        with open(NOMBRE_ARCHIVO_CLAVES,"w",encoding="utf-8") as f:
            json.dump(datos_billetera, f,indent=4)

        # Calcular checksum del json sin el campo checksum
        checksum=hashlib.sha256(json.dumps(datos_billetera, indent=4).encode('utf-8')).hexdigest()
        datos_billetera["checksum"]=checksum

        # Reescribir con checksum
        with open(NOMBRE_ARCHIVO_CLAVES,"w",encoding="utf-8") as f:
            json.dump(datos_billetera, f, indent=4)
        resultado["exito"]=True
        resultado["direccion"]=direccion
        resultado["pubkey_b64"]=datos_billetera["pubkey_b64"]
        resultado["mensaje"] = f"Exito: billetera creada → {NOMBRE_ARCHIVO_CLAVES}\nDirección: {direccion}"
        if request:
            request.session['billetera_info'] = {'direccion': direccion}

        # Zeroize
        for i in range(len(bytes_privados)):
            bytes_privados = bytes_privados[:i]+ secrets.token_bytes(1) + bytes_privados[i+1:]
        del bytes_privados, llave_maestra, datos_cifrados

    except Exception as e:
        resultado["error"]= f"Error: {str(e)}"
    return resultado

def cargar_billetera(contraseña,request=None):
    resultado = {"exito": False, "mensaje": "", "direccion": "", "error": ""}

    if not os.path.exists(NOMBRE_ARCHIVO_CLAVES):
        resultado["error"]="No existe keystore.json"
        return None, resultado

    try:
        with open(NOMBRE_ARCHIVO_CLAVES, "r", encoding="utf-8") as f:
            datos=json.load(f)

        # Extraer y verificar checksum
        stored_checksum=datos.pop("checksum", None)
        if stored_checksum:
            # Calcular checksum del JSON sin el campo checksum
            current_json = json.dumps(datos, indent=4).encode('utf-8')
            calculated_checksum=hashlib.sha256(current_json).hexdigest()
            if stored_checksum != calculated_checksum:
                resultado["error"]="Checksum falló → archivo corrupto o modificado"
                return None, resultado

        # Decrypt.
        sal = base64.b64decode(datos["kdf_params"]["salt_b64"])
        nonce = base64.b64decode(datos["cipher_params"]["nonce_b64"])
        texto_cifrado = base64.b64decode(datos["ciphertext_b64"])
        tag = base64.b64decode(datos["tag_b64"])

        kdf = Argon2id(
            salt=sal,
            length=32,
            iterations=datos["kdf_params"]["t_cost"],
            memory_cost=datos["kdf_params"]["m_cost"],
            lanes=datos["kdf_params"]["p"]
        )
        llave_maestra=kdf.derive(contraseña.encode('utf-8'))
        aesgcm=AESGCM(llave_maestra)
        bytes_privados=aesgcm.decrypt(nonce, texto_cifrado + tag, None)

        llave_privada=ed25519.Ed25519PrivateKey.from_private_bytes(bytes_privados)
        bytes_publicos=llave_privada.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        direccion=generar_direccion(bytes_publicos)

        resultado["exito"]=True
        resultado["direccion"]=direccion
        resultado["mensaje"]=f"Billetera desbloqueada → {direccion}"

        if request:
            request.session['billetera_info']={'direccion': direccion}

        # Zeroize
        for i in range(len(bytes_privados)):
            bytes_privados = bytes_privados[:i]+secrets.token_bytes(1) + bytes_privados[i+1:]
        del bytes_privados,llave_maestra

        return llave_privada,resultado

    except Exception as e:
        resultado["error"]="Contraseña incorrecta o archivo dañado"
        return None, resultado
