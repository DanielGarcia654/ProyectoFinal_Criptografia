import json
import time
import base64
import os
import datetime
from billetera import cargar_billetera,generar_direccion
from cryptography.hazmat.primitives import serialization
import secrets #Para zeroize secrets

CARPETA_SALIDA = "outbox"

def obtener_tiempo_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()
    
def canonicalizar_json(datos):
    cadena_json=json.dumps(datos,sort_keys=True,separators=(',', ':'))
    return cadena_json.encode('utf-8')
    
def crear_y_firmar_transaccion(contraseña, destinatario, monto, nonce,solicitud=None):
    "Version adaptada para GUI"
    resultado={"exito":False,"mensaje": "","archivo": "", "firma_preview": "","error": ""}

    llave_privada,res_carga=cargar_billetera(contraseña=contraseña)
    if not llave_privada:
        resultado["error"]=res_carga.get("error","No se pudo cargar la billetera")
        return resultado
    bytes_publicos=llave_privada.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )
    mi_direccion=generar_direccion(bytes_publicos)
    llave_pub_b64=base64.b64encode(bytes_publicos).decode('utf-8')
    try:
        nonce_entero=int(nonce)
    except ValueError:
        resultado["error"]="Nonce debe ser un número entero válido."
        print(resultado["error"])
        return resultado
    
    datos_tx={
        "from": mi_direccion,
        "to": destinatario,
        "value": monto,
        "nonce": nonce_entero,
        "gas_limit": 21000,
        "data_hex": "",
        "timestamp": obtener_tiempo_iso()
    }
    bytes_a_firmar=canonicalizar_json(datos_tx)
    bytes_firma=llave_privada.sign(bytes_a_firmar)
    firma_b64=base64.b64encode(bytes_firma).decode('utf-8')
    transaccion_final = {
        "tx": tx_datos,
        "sig_scheme": "Ed25519",
        "signature_b64": firma_b64,
        "pubkey_b64": llave_pub_b64
    }
    nombre_archivo=f"tx_{tx_datos['from'][:6]}_{nonce}.json"
    ruta_archivo=os.path.join(CARPETA_SALIDA, nombre_archivo)
    
    try:
        with open(ruta_archivo,"w") as f:
            json.dump(transaccion_final, f, indent=4)
        resultado["exito"]=True
        resultado["mensaje"]=f"\nÉxito. Transacción firmada y enviada al Outbox."
        resultado["archivo"]=ruta_archivo
        resultado["firma_preview"]=f"{firma_b64[:20]}..."
        resultado["mensaje"] += f"\nArchivo: {ruta_archivo}\nFirma: {resultado['firma_preview']}"

        if solicitud:
            solicitud.session['tx_info']={'archivo': ruta_archivo,'firma_preview': resultado['firma_preview']}
        #Sobrescribe bytes_privados de cargar_billetera y derivados
        #llave_privada es objeto; para full zeroize,overwrite private_bytes
        bytes_privados_temp=llave_privada.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption()
        )
        for i in range(len(bytes_privados_temp)):
            byte_aleatorio=secrets.randbelow(256).to_bytes(1,'big')
            bytes_privados_temp=bytes_privados_temp[:i]+byte_aleatorio+bytes_privados_temp[i+1:]
        del bytes_privados_temp,bytes_firma
        
    except IOError as e:
        resultado["error"]=f"Error al guardar transaccion: {e}"
    return resultado
