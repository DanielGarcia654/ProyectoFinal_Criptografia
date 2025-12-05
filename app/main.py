import sys
import os
import datetime
import json
import shutil
import customtkinter as ctk
from tkinter import messagebox
import billetera
import transaccion
import verificador


ctk.set_appearance_mode("dark") 
ctk.set_default_color_theme("blue")  
ARCHIVO_REGISTROS="crypto_wallet_logs.txt"

class AppBilleteraCrypto:
    def __init__(self):
        self.direccion_actual=None
        self.app = ctk.CTk()
        self.app.title("Billetera-Crypto Almacenamiento Frío - GUI Completa")
        self.app.geometry("950x720")
        
        # Barra lateral 
        self.barra_lateral=ctk.CTkFrame(self.app,width=220,corner_radius=10)
        self.barra_lateral.pack(side="left", fill="y", padx=10, pady=10)
        ctk.CTkLabel(self.barra_lateral, text="Billetera-Crypto", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)
        self.etiqueta_estado = ctk.CTkLabel(self.barra_lateral, text="Sin billetera cargada", font=ctk.CTkFont(size=12))
        self.etiqueta_estado.pack(pady=10)
        ctk.CTkLabel(self.barra_lateral, text=f"Registros: {os.path.abspath(ARCHIVO_REGISTROS)}", 
                    font=ctk.CTkFont(size=9), text_color="gray").pack(pady=5)

        # Botones principales
        ctk.CTkButton(self.barra_lateral, text="1. Crear billetera", command=self.opcion1, width=200).pack(pady=8, padx=20)
        ctk.CTkButton(self.barra_lateral, text="2. Cargar billetera", command=self.opcion2, width=200).pack(pady=8, padx=20)
        ctk.CTkButton(self.barra_lateral, text="3. Enviar TX (auto-copia)", command=self.enviar_tx_auto, 
                     width=200, fg_color="#1f6aa5", hover_color="#144870").pack(pady=15, padx=20)
        ctk.CTkButton(self.barra_lateral, text="4. Procesar bandeja", command=self.opcion4, width=200).pack(pady=8, padx=20)
        
        # BOTÓN VER LOGS
        ctk.CTkButton(self.barra_lateral, text="Ver Registros", command=self.ver_registros, 
                     width=200, fg_color="#d10a0a", hover_color="#0fe32f").pack(pady=10, padx=20)

        ctk.CTkButton(self.barra_lateral, text="Salir", command=self.app.destroy, 
                     width=200, fg_color="darkred").pack(pady=30, padx=20)

        # Principal con pestañas
        area_principal=ctk.CTkFrame(self.app)
        area_principal.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        self.vista_pestanas=ctk.CTkTabview(area_principal)
        self.vista_pestanas.pack(fill="both", expand=True, pady=10)
        self.vista_pestanas.add("Salida")
        self.vista_pestanas.add("Entrada")
        self.vista_pestanas.add("Verificados")
        self.marcos = {}
        for pestana in ["Salida", "Entrada", "Verificados"]:
            marco = ctk.CTkScrollableFrame(self.vista_pestanas.tab(pestana))
            marco.pack(fill="both", expand=True, padx=10, pady=10)
            self.marcos[pestana.lower()] = marco
        self.refrescar_carpetas()
        self.agregar_registro("Aplicación iniciada")

    ## def actualizar_estado
    
    def opcion1(self): ###
        contraseña = simpledialog.askstring("Contraseña", "Define una contraseña segura para tu billetera:", show='*')
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
    
    def opcion2(self): ###
        contraseña = simpledialog.askstring("Contraseña", "Ingresa tu contraseña para desbloquear:", show='*')
        if not contraseña:
            return  # O avisa si quieres
        try:
            llave, resultado = billetera.cargar_billetera(contraseña=contraseña)
            if resultado["exito"]:
                messagebox.showinfo("Éxito", resultado["mensaje"])
            else:
                messagebox.showerror("Error", resultado["error"])
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar billetera: {str(e)}")
    


    #### def enviar_tx_auto
    
    def opcion4(self):
        resultado = verificador.procesar_inbox()
        if resultado["exito"]:
            self.agregar_registro(f"Bandeja procesada: {resultado['validos']} válidos, {resultado['invalidos']} rechazados")
            messagebox.showinfo("Éxito", resultado["mensaje"])
        else:
            messagebox.showerror("Error", resultado["error"])
        self.refrescar_carpetas()
    
    def run(self):
        self.app.mainloop()

if __name__ == "__main__":
    app = AppBilleteraCrypto()
    app.ejecutar()
