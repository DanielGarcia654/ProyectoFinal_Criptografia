import sys
import os
import customtkinter as ctk
from tkinter import messagebox, simpledialog  

import billetera, transaccion, verificador

ctk.set_appearance_mode("dark") 
ctk.set_default_color_theme("blue")  

class AppCryptoWallet:
    def __init__(self):
        self.app = ctk.CTk()
        self.app.title("Proyecto Cripto-Wallet")
        self.app.geometry("950x720")
        self.app.resizable(False, False)
        
        self.title_label = ctk.CTkLabel(
            self.app, 
            text="¡Bienvenido a Crypto-Wallet!", 
            font=ctk.CTkFont(size=25, weight="bold")
        )
        self.title_label.pack(pady=30)
        
        self.instr_label = ctk.CTkLabel(
            self.app,
            text="Selecciona una opción:",
            font=ctk.CTkFont(size=16)
        )
        self.instr_label.pack(pady=10)
        
        # Botón 1: Crear nueva billetera
        self.btn1 = ctk.CTkButton(
            self.app,
            text="1. Crear nueva billetera (init)",
            command=self.opcion1,
            width=300,
            height=40,
            corner_radius=10
        )
        self.btn1.pack(pady=15)
        
        # Botón 2: Ver dirección y llaves
        self.btn2 = ctk.CTkButton(
            self.app,
            text="2. Ver mi dirección y llaves (load)",
            command=self.opcion2,
            width=300,
            height=40,
            corner_radius=10
        )
        self.btn2.pack(pady=15)
        
        # Botón 3: Crear y firmar transacción
        self.btn3 = ctk.CTkButton(
            self.app,
            text="3. Crear y firmar transacción (sign)\n(NOTA: Copia el archivo de outbox a inbox)",
            command=self.opcion3,
            width=300,
            height=40,
            corner_radius=10
        )
        self.btn3.pack(pady=15)
        
        # Botón 4: Procesar inbox
        self.btn4 = ctk.CTkButton(
            self.app,
            text="4. Procesar inbox (verify and receive)",
            command=self.opcion4,
            width=300,
            height=40,
            corner_radius=10
        )
        self.btn4.pack(pady=15)
        
        # Botón 5: Salir
        self.btn5 = ctk.CTkButton(
            self.app,
            text="5. Salir",
            command=self.opcion5,
            width=300,
            height=40,
            fg_color="red",
            hover_color="darkred",
            corner_radius=10
        )
        self.btn5.pack(pady=30)
    
    def opcion1(self):
        dialogo = ctk.CTkInputDialog(text="Define una contraseña segura:", title="Crear Billetera")
        contraseña = dialogo.get_input()
        if not contraseña:
            messagebox.showwarning("Advertencia", "Se debe generar una contraseña obligatoriamente.")
            return
        try:
            resultado = billetera.crear_billetera(contraseña=contraseña)
            if resultado["exito"]:
                messagebox.showinfo("Éxito", resultado["mensaje"])
            else:
                messagebox.showerror("Error", resultado["error"])
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear billetera: {str(e)}")
    
    def opcion2(self):
        contraseña = simpledialog.askstring("Contraseña", "Ingresa tu contraseña para desbloquear:", show='*')
        if not contraseña:
            return  
        try:
            llave, resultado = billetera.cargar_billetera(contraseña=contraseña)
            if resultado["exito"]:
                messagebox.showinfo("Éxito", resultado["mensaje"])
            else:
                messagebox.showerror("Error", resultado["error"])
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar billetera: {str(e)}")
    
    def opcion3(self):
        # Primero, pide contraseña para cargar billetera
        contraseña = simpledialog.askstring("Contraseña", "Ingresa tu contraseña para desbloquear:", show='*')
        if not contraseña:
            messagebox.showwarning("Advertencia", "Se necesita contraseña para crear transacción.")
            return
        
        # Diálogos para inputs de transacción
        destinatario = simpledialog.askstring("Transacción", "Dirección de destino (to):")
        if not destinatario:
            return
        monto = simpledialog.askstring("Transacción", "Cantidad a enviar (value):")
        if not monto:
            return
        nonce = simpledialog.askstring("Transacción", "Nonce (número de operación, ej. 1):")
        if not nonce:
            return
        
        try:
            resultado = transaccion.crear_y_firmar_transaccion(
                contraseña=contraseña,
                destinatario=destinatario,
                monto=monto,
                nonce=nonce
            )
            if resultado["exito"]:
                mensaje = resultado["mensaje"] + "\n\nNOTA: Copia el archivo de outbox a inbox para procesar."
                messagebox.showinfo("Éxito", mensaje)
            else:
                messagebox.showerror("Error", resultado["error"])
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear transacción: {str(e)}")
    
    def opcion4(self):
        try:
            resultado = verificador.procesar_inbox()
            if resultado["exito"]:
                messagebox.showinfo("Éxito", resultado["mensaje"])
            else:
                messagebox.showerror("Error", resultado["error"])
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar inbox: {str(e)}")
    
    def opcion5(self):
        self.app.destroy()
        sys.exit()
    
    def run(self):
        self.app.mainloop()

if __name__ == "__main__":
    app = AppCryptoWallet()
    app.run()