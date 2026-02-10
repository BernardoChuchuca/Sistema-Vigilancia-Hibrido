# 🛡️ Sistema de Videovigilancia Híbrido (C++ & Python)

Este proyecto implementa un sistema de seguridad inteligente que combina la velocidad de **C++** para la detección en tiempo real con la potencia de **Python (Deep Learning)** para la validación biométrica de amenazas.

![Arquitectura del Sistema](diagrama_final.jpg)

##  Características Principales

* **Arquitectura Desacoplada:** Patrón Productor-Consumidor comunicado vía **Sockets TCP/IP**.
* **Módulo Centinela (C++):** Detección de movimiento ultrarrápida usando **LBP Cascade** (Entrenado con dataset propio de 8,000 imágenes).
* **Módulo Cerebro (Python):** Validación de postura humana mediante **Keypoint R-CNN (PyTorch)**.
* **Filtro Anti-Falsos Positivos:** Análisis de varianza de movimiento para distinguir humanos reales de fotografías o estatuas.
* **Alertas Multimedia:** Envío de evidencia (Foto + Video + Análisis) a **Telegram** en tiempo real.

##  Tecnologías Utilizadas

* **Lenguajes:** C++17, Python 3.9
* **Visión Artificial:** OpenCV 4.5 (C++ & Python)
* **Inteligencia Artificial:** PyTorch, Torchvision
* **Comunicación:** Sockets BSD (TCP/IP Localhost:65432)
* **Herramientas:** CMake, Albumentations (Data Augmentation)

##  Pre-requisitos

### Para el Módulo C++ (Linux/Windows)
* Compilador GCC o MSVC compatible con C++17.
* Librería OpenCV 4.x instalada y configurada.

### Para el Módulo Python
Instalar las dependencias necesarias:
```bash
pip install torch torchvision opencv-python pyTelegramBotAPI psutil numpy
