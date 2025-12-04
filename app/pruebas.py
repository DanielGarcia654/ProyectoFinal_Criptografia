import unittest
import os
import json
import base64
import shutil
from unittest.mock import patch
from cryptography.hazmat.primitives import serialization
import billetera
import transaccion
import verificador

class TestWalletCrypto(unittest.TestCase):
    
    def setUp(self):
        "Prepara el entorno limpio antes de cada prueba."
        billetera.NOMBRE_ARCHIVO_CLAVES="test_keystore.json"
        verificador.ARCHIVO_NONCES="test_nonces.json"
        if os.path.exists("test_keystore.json"):os.remove("test_keystore.json")
        if os.path.exists("test_nonces.json"):os.remove("test_nonces.json")
        if os.path.exists("test_tx.json"):os.remove("test_tx.json")

    def tearDown(self):
        "Limpia la basura después de cada prueba"
        if os.path.exists("test_keystore.json"):os.remove("test_keystore.json")
        if os.path.exists("test_nonces.json"):os.remove("test_nonces.json")
        if os.path.exists("test_tx.json"):os.remove("test_tx.json")
        if os.path.exists("test_tx_fake.json"):os.remove("test_tx_fake.json")

    def test_canonicalizacion(self):
        "Prueba que el JSON se ordene correctamente"
        data1={"b": 1, "a": 2}
        data2={"a": 2, "b": 1}
        canon1=transaccion.canonicalizar_json(data1)
        canon2=transaccion.canonicalizar_json(data2)
        self.assertEqual(canon1,canon2)

    @patch('builtins.input',return_value="password_test_123")
    def test_firma_y_verificacion(self, mock_input):
        "Prueba una transacción válida con datos reales."

        billetera.crear_billetera()
        llave=billetera.cargar_billetera()
        bytes_publicos=llave.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        mi_direccion_real=billetera.generar_direccion(bytes_publicos)

        tx = {
            "from":mi_direccion_real, 
            "to":"0xDestinoPrueba", 
            "value":100,
            "nonce":1,         
            "timestamp":"HOY"
        }
        tx_bytes=transaccion.canonicalizar_json(tx)
        
        firma=llave.sign(tx_bytes)
        firma_b64=base64.b64encode(firma).decode('utf-8')
        
        paquete={
            "tx":tx,
            "signature_b64": firma_b64,
            "pubkey_b64":base64.b64encode(bytes_publicos).decode('utf-8')
        }
        
        with open("test_tx.json", "w") as f:
            json.dump(paquete, f)
            
        resultado=verificador.verificar_transaccion("test_tx.json")

        if not resultado:
            print("\nDebug. La verificación falló inesperadamente.")
        self.assertTrue(resultado, "La transacción válida fue rechazada por error.")
        
        paquete["tx"]["value"] =999999 
        with open("test_tx_fake.json","w") as f:
            json.dump(paquete, f)
            
        resultado_fake= verificador.verificar_transaccion("test_tx_fake.json")
        self.assertFalse(resultado_fake, "El ataque de modificación debió ser rechazado.")

    def test_vectores_dorados(self):
        "Genera vectores validos"
        print("\nVectores que sirven para el pdf")
        with patch('builtins.input', return_value="password_test_123"):
            billetera.crear_billetera()
            llave=billetera.cargar_billetera()
            bytes_publicos = llave.public_key().public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw
            )
            addr = billetera.generar_direccion(bytes_publicos)
            
            for i in range(1, 4):
                tx={"from":addr, "to":"0xBob", "val":i, "nonce":i}
                tx_bytes=transaccion.canonicalizar_json(tx)
                firma=llave.sign(tx_bytes)
                print(f"Vector #{i}:")
                print(f" JSON: {tx}")
                print(f" SIG:  {base64.b64encode(firma).decode('utf-8')[:20]}...")

if __name__=='__main__':
    unittest.main()