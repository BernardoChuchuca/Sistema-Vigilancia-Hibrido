import telebot
import cv2
import torch
import torchvision
from torchvision import transforms as T
import os
import time
import numpy as np
import socket
import psutil  # <--- NUEVO: Para cumplir la rúbrica (Memoria RAM)

# --- TUS DATOS ---
TOKEN = '8423789623:AAE6cBtrgfUnfSkj-VwOI3YeXDpYNYAWZGw' 
CHAT_ID = '1183446307'
bot = telebot.TeleBot(TOKEN)

# --- RUTAS ---
ARCHIVO_VIDEO_ORIGINAL = "build/alerta.mp4"
ARCHIVO_FOTO_ORIGINAL = "build/captura_original.jpg"
ARCHIVO_SALIDA_VIDEO = "build/salida_postura.mp4"
ARCHIVO_SALIDA_FOTO = "build/captura_postura.jpg"

# --- CONFIGURACIÓN CUDA ---
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"--- 🚀 CEREBRO VERIFICADOR: {device} ---")

# Cargar Modelo Keypoint R-CNN
print("Cargando modelo neuronal... (Esto puede tardar un poco)")
model = torchvision.models.detection.keypointrcnn_resnet50_fpn(pretrained=True)
model.to(device)
model.eval()
transform = T.Compose([T.ToTensor()])

# --- CONFIGURACIÓN DEL SERVIDOR SOCKET (API INTERNA) ---
HOST = '127.0.0.1'
PORT = 65432        

print(f"--- 📡 INICIANDO SERVIDOR SOCKET EN {HOST}:{PORT} ---")
print("Esperando conexión directa desde C++...")

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()

while True:
    conn = None
    try:
        # 1. Esperar señal de C++
        conn, addr = server_socket.accept()
        print(f"\n>> 🔗 CONEXIÓN RECIBIDA de {addr}")
        
        data = conn.recv(1024).decode('utf-8')
        
        if "ANALIZAR" in data:
            print(">> 📨 Señal 'ANALIZAR' recibida.")
            
            # 2. Esperar a que el archivo exista (Sincronización con disco)
            archivo_encontrado = False
            for i in range(10): # 10 intentos de 0.5s
                if os.path.exists(ARCHIVO_VIDEO_ORIGINAL):
                    print(f"   💾 Video capturado detectado en disco.")
                    archivo_encontrado = True
                    break
                else:
                    print(f"   ⏳ Esperando transferencia de archivo... ({i+1}/10)")
                    time.sleep(0.5)
            
            if not archivo_encontrado:
                print("⚠️ Error: El archivo de video nunca apareció. Saltando...")
                conn.close()
                continue
                
            time.sleep(0.5) # Pequeña pausa de seguridad

            # 3. Procesamiento de Video e IA
            cap = cv2.VideoCapture(ARCHIVO_VIDEO_ORIGINAL)
            if not cap.isOpened():
                print("❌ Error al abrir el video.")
                conn.close()
                continue

            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            writer = cv2.VideoWriter(ARCHIVO_SALIDA_VIDEO, cv2.VideoWriter_fourcc(*'mp4v'), 20.0, (width, height))
            
            # Variables para lógica de validación
            historial_nariz_x = [] 
            historial_nariz_y = []
            mejor_frame = None
            max_confianza_detectada = 0.0
            max_puntos_detectados = 0

            print("   🧠 Analizando posturas con PyTorch...")
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret: break
                
                # Inferencia
                img_tensor = transform(frame).to(device).unsqueeze(0)
                with torch.no_grad():
                    output = model(img_tensor)[0]
                
                scores = output['scores'].cpu().numpy()
                keypoints = output['keypoints'].cpu().numpy()
                
                # Dibujar esqueleto si hay confianza
                if len(scores) > 0 and scores[0] > 0.7:
                    # Guardamos métricas para el reporte
                    if scores[0] > max_confianza_detectada:
                        max_confianza_detectada = scores[0]
                        max_puntos_detectados = sum(1 for kp in keypoints[0] if kp[2] > 0.5)
                        mejor_frame = frame.copy() # Guardamos la mejor foto para Telegram

                    # Lógica de Varianza (Movimiento de nariz)
                    kp_nariz = keypoints[0][0] # Punto 0 es la nariz
                    if kp_nariz[2] > 0.7:
                        historial_nariz_x.append(kp_nariz[0])
                        historial_nariz_y.append(kp_nariz[1])

                    # Dibujar en el video
                    for kp in keypoints[0]:
                        x, y, v = kp
                        if v > 0.5: 
                            cv2.circle(frame, (int(x), int(y)), 4, (0, 255, 0), -1)

                writer.write(frame)
            
            cap.release()
            writer.release()
            
            # 4. Cálculo de Varianza (Anti-Falsos Positivos)
            es_humano_real = False
            movimiento = 0.0
            if len(historial_nariz_x) > 5:
                movimiento = np.std(historial_nariz_x) + np.std(historial_nariz_y)
                # Umbral: si se mueve más de 0.3 pixeles promedio, está vivo
                if movimiento > 0.3: 
                    es_humano_real = True

            # 5. IMPRESIÓN DE MÉTRICAS (RÚBRICA 10%)
            process = psutil.Process(os.getpid())
            memoria_mb = process.memory_info().rss / 1024 / 1024
            
            print(f"\n📊 --- REPORTE TÉCNICO DE INFERENCIA ---")
            print(f"   💾 Uso de Memoria RAM: {memoria_mb:.2f} MB")
            print(f"   🎯 Confianza Máxima (Score): {max_confianza_detectada:.4f}")
            print(f"   🦴 Puntos Clave Detectados: {max_puntos_detectados}/17")
            print(f"   ⚡ Varianza de Movimiento: {movimiento:.4f}")
            print(f"   🤖 VEREDICTO: {'✅ HUMANO REAL' if es_humano_real else '❌ ESTATUA/FOTO'}")
            print("------------------------------------------\n")

            # 6. Notificación a Telegram
            if es_humano_real:
                print("🚀 Enviando alerta multimedia a Telegram...")
                
                # A. Foto Original (C++)
                if os.path.exists(ARCHIVO_FOTO_ORIGINAL):
                    with open(ARCHIVO_FOTO_ORIGINAL, 'rb') as f:
                        bot.send_photo(CHAT_ID, f, caption="🚨 ALERTA: Movimiento Detectado (Centinela C++)")
                
                # B. Foto Analizada (Skeleton)
                if mejor_frame is not None:
                    cv2.imwrite(ARCHIVO_SALIDA_FOTO, mejor_frame)
                    with open(ARCHIVO_SALIDA_FOTO, 'rb') as f:
                        bot.send_photo(CHAT_ID, f, caption=f"🦴 ANÁLISIS BIOMÉTRICO\nConfianza: {max_confianza_detectada:.2f}\nKeypoints: {max_puntos_detectados}")
                
                # C. Video Evidencia
                with open(ARCHIVO_SALIDA_VIDEO, 'rb') as f:
                    bot.send_video(CHAT_ID, f, caption=f"🧠 EVIDENCIA VIDEO\nValidación: Positiva")
                
                print(">> ✅ Notificación enviada con éxito.")
            else:
                print("❌ Falsa alarma descartada (Poca varianza o confianza baja).")
                # Limpieza de archivos basura
                try:
                    if os.path.exists(ARCHIVO_VIDEO_ORIGINAL): os.remove(ARCHIVO_VIDEO_ORIGINAL)
                    if os.path.exists(ARCHIVO_FOTO_ORIGINAL): os.remove(ARCHIVO_FOTO_ORIGINAL)
                    if os.path.exists(ARCHIVO_SALIDA_VIDEO): os.remove(ARCHIVO_SALIDA_VIDEO)
                except:
                    pass

        conn.close() 

    except Exception as e:
        print(f"❌ Error crítico en el servidor: {e}")
        if conn: conn.close()