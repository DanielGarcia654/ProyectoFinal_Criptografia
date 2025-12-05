import json
import base64
import os
import shutil
import datetime
from cryptography.hazmat.primitives.asymmetric import ed25519
from billetera import generar_direccion 

CARPETA_ENTRADA="inbox"
CARPETA_VERIFICADOS="verified"
ARCHIVO_NONCES="base_datos_nonces.json"
LIBRETA_DIRECCIONES="address_book.json"  

def cargar_rastreador_nonces():
    if not os.path.exists(ARCHIVO_NONCES):
        return {}
    try:
        with open(ARCHIVO_NONCES,"r") as f:
            return json.load(f)
    except:
        return {}

def guardar_rastreador_nonces(datos):
    with open(ARCHIVO_NONCES,"w") as f:
        json.dump(datos, f, indent=4)

def cargar_libreta_direcciones():
    "Carga libreta de direcciones JSON (minimo:nombre y ultima vez por direccion)"
    if not os.path.exists(LIBRETA_DIRECCIONES):
        return {}
    try:
        with open(LIBRETA_DIRECCIONES,"r") as f:
            return json.load(f)
    except:
        return {}

def guardar_libreta_direcciones(datos):
    "Guarda libreta de direcciones JSON."
    with open(LIBRETA_DIRECCIONES,"w") as f:
        json.dump(datos, f, indent=4)

def canonicalizar_json(datos):
    "JSON Canónico: llaves ordenadas, UTF-8, sin espacios (documentado para reproducibilidad)"
    cadena_json=json.dumps(datos, sort_keys=True, separators=(',', ':'))
    return cadena_json.encode('utf-8')

def verificar_transaccion(ruta_archivo):
    "Verificación detallada: Retorna dict con 'valido' y 'razon' (cumple specs para razones detalladas), incluye recomputar canónico/resumen, verificar firma, coincidencia de dirección"
    resultado={"valido": False, "razon": "", "direccion": ""}
    try:
        with open(ruta_archivo, "r") as f:
            paquete=json.load(f)
        datos_tx=paquete["tx"]
        firma_b64=paquete["signature_b64"]
        pubkey_b64=paquete["pubkey_b64"]
        remitente=datos_tx["from"]
        nonce_entrante=datos_tx["nonce"]
        nonces_db=cargar_rastreador_nonces()
        ultimo_nonce=nonces_db.get(remitente, -1) 
        
        if nonce_entrante<=ultimo_nonce:
            resultado["razon"]=f"Ataque de repetición: nonce {nonce_entrante} <= ultimo {ultimo_nonce}"
            return resultado
        bytes_publicos=base64.b64decode(pubkey_b64)
        llave_publica=ed25519.Ed25519PublicKey.from_public_bytes(bytes_publicos)
        direccion_calculada=generar_direccion(bytes_publicos)
        
        if direccion_calculada != remitente:
            resultado["razon"]=f"Discrepancia de dirección: calculada {direccion_calculada} != tx.from {remitente}"
            return resultado
        bytes_mensaje = canonicalizar_json(datos_tx)
        bytes_firma = base64.b64decode(firma_b64)
        
        try:
            llave_publica.verify(bytes_firma, bytes_mensaje)
        except:
            resultado["razon"]="Mala firma: Verificación fallida"
            return resultado

        # Si llega aquí: Válido
        nonces_db[remitente] = nonce_entrante
        guardar_rastreador_nonces(nonces_db)
        resultado["valido"] = True
        resultado["razon"] = "valido"
        resultado["direccion"] = remitente

    except json.JSONDecodeError:
        resultado["razon"]="Mal formato: JSON inválido"
    except KeyError as e:
        resultado["razon"]=f"Mal formato: Falta clave {str(e)}"
    except base64.binascii.Error:
        resultado["razon"]="Mal formato: base64 inválido (firma/pubkey)"
    except ValueError as e:
        resultado["razon"]=f"Mal formato: {str(e)}"
    except Exception as e:
        resultado["razon"]=f"Error inesperado: {str(e)}"
    return resultado

def procesar_inbox(solicitud=None):
    "Retorna dict con resumen.Usa razones detalladas de verificar_transaccion. Actualiza libreta si válido"
    resultado={"exito": True, "mensaje": "", "procesados": 0, "validos": 0, "invalidos": 0, "error": ""}

    if not os.path.exists(CARPETA_ENTRADA):
        os.mkdir(CARPETA_ENTRADA)
    if not os.path.exists(CARPETA_VERIFICADOS):
        os.mkdir(CARPETA_VERIFICADOS)

    try:
        archivos = os.listdir(CARPETA_ENTRADA)
        procesados = 0
        validos = 0
        invalidos = 0
        razones_invalidos = []  

        for nombre in archivos:
            if not nombre.endswith(".json"):
                continue
            ruta_completa=os.path.join(CARPETA_ENTRADA, nombre)
            dict_es_valida=verificar_transaccion(ruta_completa)
            if dict_es_valida["valido"]:
                ruta_destino=os.path.join(CARPETA_VERIFICADOS, nombre)
                shutil.move(ruta_completa, ruta_destino)
                validos += 1
                # Actualiza libreta de direcciones
                libreta=cargar_libreta_direcciones()
                direc=dict_es_valida["direccion"]
                libreta[direc]={
                    "nombre": libreta.get(direc, {}).get("nombre", "Desconocido"),
                    "ultima_vez": datetime.datetime.now(datetime.timezone.utc).isoformat()
                }
                guardar_libreta_direcciones(libreta)
            else:
                os.remove(ruta_completa)
                invalidos += 1
                razones_invalidos.append(f"{nombre}: {dict_es_valida['razon']}")
            procesados += 1
        if procesados == 0:
            resultado["mensaje"]="No hay archivos nuevos en la Bandeja de Entrada."
        else:
            msg_invalido = f"\nRazones inválidos: {', '.join(razones_invalidos)}" if razones_invalidos else ""
            resultado["mensaje"]=f"Procesamiento completado.\nArchivos procesados: {procesados}\nVálidos (movidos a Verified): {validos}\nInválidos (eliminados): {invalidos}{msg_invalido}"
        resultado["procesados"]=procesados
        resultado["validos"]=validos
        resultado["invalidos"]=invalidos
        if solicitud:
            solicitud.session['inbox_resumen'] = resultado

    except Exception as e:
        resultado["exito"]=False
        resultado["error"]=f"Error durante procesamiento: {str(e)}"
    return resultado
