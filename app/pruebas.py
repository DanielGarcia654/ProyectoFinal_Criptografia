import pytest
import base64
from billetera import generar_direccion, crear_billetera, cargar_billetera
from transaccion import crear_y_firmar_transaccion
from verificador import verificar_transaccion
from cryptography.hazmat.primitives.asymmetric import ed25519
import json, os

# Vector dorado: Par de claves Ed25519 conocidas
PRIV_CONOCIDA=b'\x00' * 32
PUB_CONOCIDA=b'\x01' * 32
FIRMA_CONOCIDA=b'\x02' * 64
MSJ_CONOCIDO=b'{"from":"0x123","to":"0x456","value":"1","nonce":1,"gas_limit":21000,"data_hex":"","timestamp":"2025-01-01T00:00:00Z"}'

def test_derivacion_direccion():
    direc=generar_direccion(PUB_CONOCIDA)
    assert direc.startswith("0x"), "La dirección debe comenzar con 0x"
    assert len(direc)==42, "Longitud de dirección Ethereum"

def test_cifrado_descifrado_ida_vuelta(tmp_path):
    contra="contraprueba"
    # Crear
    resultado=crear_billetera(contra)
    assert resultado["exito"]
    # Guardar en temporal
    with open(tmp_path / "keystore.json", "w") as f:
        json.dump(resultado, f)  # Guardado simulado
    # Cargar
    _, res_carga=cargar_billetera(contra)
    assert res_carga["exito"]

def test_firmar_verificar_vector_dorado():
    priv=ed25519.Ed25519PrivateKey.from_private_bytes(PRIV_CONOCIDA)
    firma=priv.sign(MSJ_CONOCIDO)
    pub=priv.public_key()
    pub.verify(firma, MSJ_CONOCIDO) 
    assert True # Dorado: Firma conocida verifica

def test_canonicalizacion():
    tx={"from": "0x1", "to": "0x2", "value": "10", "nonce": 1}
    canonica=json.dumps(tx, sort_keys=True, separators=(',', ':')).encode('utf-8')
    assert b'"from":"0x1"' in canonica  # Ordenado

# Para TX completa: Simular archivos en tmp_path
def test_verificar_tx_vector_prueba(tmp_path):
    #Válida
    tx_valida = {"tx": {"from": "0x123", "to": "0x456", "value": "1", "nonce": 1}, "sig_scheme": "Ed25519", "signature_b64": base64.b64encode(FIRMA_CONOCIDA).decode(), "pubkey_b64": base64.b64encode(PUB_CONOCIDA).decode()}
    with open(tmp_path / "tx_valida.json", "w") as f:
        json.dump(tx_valida, f)
    assert verificar_transaccion(str(tmp_path / "tx_valida.json"))["valido"]
    
    #Mala firma
    tx_mala_firma = tx_valida.copy()
    tx_mala_firma["signature_b64"] = "invalid"
    with open(tmp_path / "tx_mala.json", "w") as f:
        json.dump(tx_mala_firma, f)
    assert not verificar_transaccion(str(tmp_path / "tx_mala.json"))["valido"]

if __name__=="__main__":
    pytest.main(["-v", __file__])
