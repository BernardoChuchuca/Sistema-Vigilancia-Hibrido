# 🛡️ Sistema de Videovigilancia Híbrido: C++ & Deep Learning

![Status](https://img.shields.io/badge/Estado-Terminado-green)
![Lenguaje](https://img.shields.io/badge/C%2B%2B-OpenCV-blue)
![Lenguaje](https://img.shields.io/badge/Python-PyTorch-yellow)

Este proyecto implementa un sistema de seguridad inteligente que resuelve el problema de los falsos positivos mediante una **Arquitectura Híbrida Desacoplada**. Combina la velocidad de procesamiento de **C++** para la detección en tiempo real con la potencia analítica de **Python (Deep Learning)** para la validación biométrica de amenazas.

## 📐 Arquitectura del Sistema

El sistema sigue el patrón de diseño **Productor-Consumidor**, comunicando dos módulos independientes a través de **Sockets TCP/IP** para minimizar la latencia.

![Diagrama de Arquitectura](diagrama_final.jpg)
*(Asegúrate de subir tu imagen 'diagrama_final.jpg' al repositorio para que se vea aquí)*

### 1. Módulo Centinela (C++ - Productor)
* **Responsabilidad:** Vigilancia 24/7 y filtrado rápido.
* **Tecnología:** OpenCV (C++17) + Multithreading.
* **Algoritmo:** Detector LBP (Local Binary Patterns) en Cascada, entrenado con un dataset propio de 8,000 imágenes.
* **Función:** Detecta movimiento, graba el video en un hilo secundario y envía una señal de disparo ('ANALIZAR') al servidor.

### 2. Módulo Cerebro (Python - Consumidor)
* **Responsabilidad:** Inteligencia Artificial y Notificación.
* **Tecnología:** PyTorch + Sockets BSD.
* **Modelo:** Keypoint R-CNN (ResNet-50) pre-entrenado.
* **Validación Biométrica:** Analiza la varianza del movimiento del esqueleto humano para distinguir personas reales de fotografías o estatuas.
* **Salida:** Envía alertas multimedia (Foto, Video y Análisis) a un Bot de Telegram.

---

## 🚀 Características Clave

* **Comunicación IPC Eficiente:** Uso de Sockets locales (Puerto 65432) en lugar de lectura/escritura de archivos de texto, reduciendo el desgaste del disco y la latencia.
* **Dataset Propio:** Entrenamiento realizado con muestras positivas de *Pascal VOC* y negativas de *Lorem Picsum* mediante scripts de *Data Engineering*.
* **Rendimiento Optimizado:**
    * **C++:** Mantiene >30 FPS constantes durante la vigilancia.
    * **Python:** Inferencia bajo demanda (solo se activa con amenazas potenciales).
* **Telemetría:** Monitoreo en tiempo real de uso de RAM, FPS y Nivel de Confianza del modelo.

---

## 🛠️ Instalación y Requisitos

### Pre-requisitos
* **Sistema Operativo:** Linux (Probado en Ubuntu) o Windows.
* **C++:** Compilador GCC/Clang y librería **OpenCV 4.x** instalada.
* **Python 3.8+:** Con las siguientes librerías:

```bash
pip install torch torchvision opencv-python pyTelegramBotAPI psutil numpy
