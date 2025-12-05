import json
import time
import base64
import os
import datetime
import billetera
from cryptography.hazmat.primitives import serialization

CARPETA_OUTBOX = "outbox"

def obtener_tiempo_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()
    
def canonicalizar_json(datos):
    json_string = json.dumps(datos, sort_keys=True, separators=(',', ':'))
    return json_string.encode('utf-8')
    
def crear_y_firmar_transaccion(contraseña=None, destinatario=None, monto=None, nonce=None):
    if contraseña is None:
        contraseña = input("Ingresa tu contraseña para desbloquear: ")
    
    if destinatario is None:
        destinatario = input("Direccion de destino (to): ")
    if monto is None:
        monto = input("Cantidad a enviar(value): ")
    if nonce is None:
        nonce = input("Nonce(numero de operacion,ej.1): ")
    
    resultado = {"exito": False, "mensaje": "", "archivo": "", "firma_preview": "", "error": ""}

    print("Creador de Transacciones")
    
    llave_privada, res_carga = billetera.cargar_billetera(contraseña=contraseña)
    if not llave_privada:
        resultado["error"] = res_carga.get("error", "No se pudo cargar la billetera.")
        print(resultado["error"])
        return resultado

    bytes_publicos = llave_privada.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )
    mi_direccion = billetera.generar_direccion(bytes_publicos)
    pubkey_b64 = base64.b64encode(bytes_publicos).decode('utf-8')
    
    try:
        nonce_int = int(nonce)
    except ValueError:
        resultado["error"] = "Nonce debe ser un número entero válido."
        print(resultado["error"])
        return resultado
    
    tx_datos = {
        "from": mi_direccion,
        "to": destinatario,
        "value": monto,
        "nonce": nonce_int,
        "gas_limit": 21000,
        "data_hex": "",
        "timestamp": obtener_tiempo_iso()
    }
    
    bytes_para_firmar = canonicalizar_json(tx_datos)
    print(f"*Datos canonicos a firmar: {bytes_para_firmar}")
    
    firma_bytes = llave_privada.sign(bytes_para_firmar)
    firma_b64 = base64.b64encode(firma_bytes).decode('utf-8')
    
    transaccion_final = {
        "tx": tx_datos,
        "sig_scheme": "Ed25519",
        "signature_b64": firma_b64,
        "pubkey_b64": pubkey_b64
    }
    
    nombre_archivo = f"tx_{tx_datos['from'][:6]}_{nonce}.json"
    ruta_archivo = os.path.join(CARPETA_OUTBOX, nombre_archivo)
    
    try:
        with open(ruta_archivo, "w") as f:
            json.dump(transaccion_final, f, indent=4)
            
        resultado["exito"] = True
        resultado["mensaje"] = f"\nÉxito. Transacción firmada y enviada al Outbox."
        resultado["archivo"] = ruta_archivo
        resultado["firma_preview"] = f"{firma_b64[:20]}..."
        resultado["mensaje"] += f"\nArchivo: {ruta_archivo}\nFirma: {resultado['firma_preview']}"
        
        print(resultado["mensaje"])
        
    except IOError as e:
        resultado["error"] = f"Error al guardar transaccion: {e}"
        print(resultado["error"])

    return resultado

if __name__ == "__main__":
    crear_y_firmar_transaccion()
