import albumentations as A
import cv2
import os
import glob
import random

# --- CONFIGURACIÓN ---
# Rutas basadas en tu estructura actual
PATH_POSITIVAS_ORIGINAL = "daset_crudo/positivas"
PATH_NEGATIVAS_ORIGINAL = "daset_crudo/negativas"

PATH_SALIDA_POS = "dataset_final/positivas_4000"
PATH_SALIDA_NEG = "dataset_final/negativas_4000"

CANTIDAD_OBJETIVO = 4000

# Definir transformaciones (Simular posturas, luz, etc.)
transform = A.Compose([
    A.HorizontalFlip(p=0.5),              # Espejo
    A.Rotate(limit=10, p=0.6),            # Rotación leve
    A.RandomBrightnessContrast(p=0.4),    # Luz/Sombra
    A.GaussNoise(p=0.2),                  # Ruido de cámara
    A.Perspective(scale=(0.05, 0.1), p=0.3), # Cambio de perspectiva
    # HOG necesita un tamaño fijo, redimensionamos aquí a 64x128 (estándar peatones)
    A.Resize(height=128, width=64) 
])

def generar_imagenes(origen, destino, tipo):
    print(f"\n--- Generando {tipo} en {destino} ---")
    
    if not os.path.exists(destino):
        os.makedirs(destino)
        
    imagenes = glob.glob(os.path.join(origen, "*.*"))
    print(f"📸 Imágenes originales encontradas: {len(imagenes)}")
    
    if len(imagenes) == 0:
        print("❌ Error: No hay imágenes en la carpeta de origen.")
        return

    count = 0
    # Bucle hasta llegar a 4000
    while count < CANTIDAD_OBJETIVO:
        # Elegir una al azar
        img_path = random.choice(imagenes)
        image = cv2.imread(img_path)
        
        if image is None: continue

        # Transformar
        try:
            augmented = transform(image=image)["image"]
            
            # Guardar con nombre numérico
            nombre = f"{tipo}_{count:05d}.jpg"
            cv2.imwrite(os.path.join(destino, nombre), augmented)
            
            count += 1
            if count % 500 == 0:
                print(f"   Generadas: {count} / {CANTIDAD_OBJETIVO}", end='\r')
        except Exception as e:
            pass

    print(f"\n✅ ¡LISTO! {count} imágenes generadas en {destino}")

# --- MENÚ PRINCIPAL ---
print("1. Generar 4000 POSITIVAS (Peatones)")
print("2. Generar 4000 NEGATIVAS (Fondos/Columnas)")
print("3. Generar TODO")
opcion = input("Elige una opción (1-3): ")

if opcion == '1' or opcion == '3':
    generar_imagenes(PATH_POSITIVAS_ORIGINAL, PATH_SALIDA_POS, "pos")

if opcion == '2' or opcion == '3':
    # Para negativas, a veces no queremos Resize estricto si son fondos grandes,
    # pero para traincascade suele ser útil tenerlas controladas.
    # Usaremos la misma lógica.
    generar_imagenes(PATH_NEGATIVAS_ORIGINAL, PATH_SALIDA_NEG, "neg")