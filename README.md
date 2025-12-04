<div align="center">

# 🪙 Proyecto Final de Criptografía 

### Facultad de Ingeniería UNAM | Semestre 2026-1
<!-- 
![Criptografía](https://img.shields.io/badge/Materia-Criptograf%C3%ADa-blue?style=for-the-badge)
![Semestre](https://img.shields.io/badge/Semestre-2026--1-green?style=for-the-badge)
![UNAM](https://img.shields.io/badge/UNAM-Facultad%20de%20Ingenier%C3%ADa-gold?style=for-the-badge) 
-->

</div>

---

## 📋 Descripción

Este es el **proyecto final** para la materia de **Criptografía** del semestre 2026-1.

**Crypto-Wallet** es una implementación completa de una **billetera criptográfica fría (cold wallet)** para criptomonedas basadas en cuentas, desarrollada desde cero utilizando primitivas criptográficas fundamentales.

### ¿Qué es una Cold Wallet?

Una billetera fría es un sistema de almacenamiento de criptomonedas que mantiene las llaves privadas completamente **offline y aisladas de la red**, maximizando la seguridad contra ataques remotos. A diferencia de las "hot wallets" conectadas permanentemente a internet, las cold wallets solo firman transacciones localmente, exportando únicamente el resultado firmado.

### Características Principales

Este proyecto implementa las **primitivas criptográficas fundamentales** de una billetera profesional:

- 🔐 **Gestión Segura de Llaves**: Generación de pares Ed25519, almacenamiento encriptado con AES-256-GCM y derivación de claves mediante Argon2id
- ✍️ **Firma Digital Determinista**: Canonicalización de transacciones en JSON y firma criptográfica verificable
- ✅ **Verificación Completa**: Validación de firmas digitales, detección de ataques de replay y comprobación de integridad
- 🪙 **Sistema de Direcciones**: Derivación de direcciones estilo Ethereum mediante SHA-256
- 🧪 **Simulación Local**: Carpetas inbox/outbox que emulan el envío/recepción sin requerir blockchain real

### Enfoque del Proyecto

El objetivo es dominar los **fundamentos criptográficos** mediante una implementación práctica que cumpla estándares de seguridad profesionales:
- Sin frameworks de wallet predefinidos — implementación desde cero
- Uso exclusivo de primitivas criptográficas auditadas (Ed25519, AES-256-GCM, Argon2id)
- Manejo seguro de secretos en memoria y protección contra vulnerabilidades comunes
- Suite completa de pruebas unitarias con vectores de prueba dorados

---

## 👥 Equipo de Desarrollo

<table align="center">
  <tr>
    <td align="center">
      <b>👨‍💻 Garcia Cerda Gerardo Daniel</b>
    </td>
  </tr>
  <tr>
    <td align="center">
      <b>👨‍💻 Hernandez Ruiz Leny Javier</b>
    </td>
  </tr>
  <tr>
    <td align="center">
      <b>👨‍💻 Silverio Martinez Andres</b>
    </td>
  </tr>
  <tr>
    <td align="center">
      <b>👨‍💻 Rios Valdes Oscar</b>
    </td>
  </tr>
</table>


---

## 🎯 Objetivo del Proyecto

Implementar desde cero las **funciones criptográficas centrales** de una billetera fría (cold wallet) para una criptomoneda basada en cuentas. El proyecto incluye:

### Componentes Principales

- 🔑 **Almacenamiento Seguro de Llaves**  
  Diseñar e implementar un sistema de almacenamiento encriptado para proteger las llaves privadas, utilizando esquemas de derivación de claves (KDF) y cifrado autenticado.

- ✍️ **Firma de Transacciones**  
  Desarrollar el mecanismo para firmar transacciones utilizando criptografía de curva elíptica (Ed25519), garantizando autenticidad e integridad.

- ✅ **Verificación de Firmas**  
  Implementar la validación criptográfica de transacciones recibidas, incluyendo protección contra ataques de replay mediante sistemas de nonces.

- 🪙 **Gestión de Direcciones**  
  Derivar direcciones criptográficas a partir de llaves públicas utilizando funciones hash seguras (SHA-256).

### Alcance

> [!NOTE]
> Este proyecto simula el envío y recepción de transacciones **localmente**, sin requerir conexión a red ni actualizaciones de estado de blockchain. Se enfoca en los aspectos criptográficos fundamentales de una billetera fría.

### Conceptos Criptográficos Aplicados

- 🔑 Generación de pares de llaves asimétricas (Ed25519)
- 🔒 Cifrado autenticado (AES-256-GCM)
- 🧂 Derivación de claves con Argon2id
- 📝 Firma digital y verificación
- 🛡️ Protección contra ataques de replay
- 🔗 Canonicalización de datos para integridad

---

## 🚀 Instalación

```bash
# Clona este repositorio
git clone https://github.com/DanielGarcia654/ProyectoFinal_Criptografia.git

# Navega al directorio del proyecto
cd ProyectoFinal

# Instala las dependencias
pip install cryptography customtkinter
py -m pip install customtkinter packaging
```


---

## 💡 Uso

Para instrucciones detalladas de uso, instalación y ejemplos prácticos, consulta la **[Guía de Uso Completa](GUIA_USO.md)**.

### Inicio Rápido

```bash
# Ejecutar con interfaz gráfica
python app/main.py
```

La guía incluye:
- 📘 Configuración paso a paso
- 💼 Ejemplos prácticos completos
- 🔧 Solución de problemas
- ❓ Preguntas frecuentes
- 🎯 Mejores prácticas de seguridad

---

## 📚 Tecnologías y Herramientas

- **Python 3.x** - Lenguaje de programación principal
- **cryptography** - Librería de primitivas criptográficas
  - Ed25519 para firma digital
  - AES-256-GCM para cifrado autenticado
  - Argon2id para derivación de claves
- **CustomTkinter** - Interfaz gráfica moderna
- **unittest** - Framework de pruebas

---

## 📝 Documentación

La documentación completa del proyecto incluye:
- Análisis de seguridad criptográfica
- Diagramas de arquitectura
- Vectores de prueba

---

## 📄 Licencia

Este proyecto es desarrollado con fines académicos para la **Facultad de Ingeniería de la UNAM**.

---
--->
<div align="center">

**Universidad Nacional Autónoma de México**  
**Facultad de Ingeniería**  
**Criptografía | 2026-1**

---

</div>
