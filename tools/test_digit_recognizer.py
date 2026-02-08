"""
Script de prueba para el reconocedor de digitos.
Captura pantalla y prueba el reconocimiento en cada region.
"""

import sys
from pathlib import Path
import time

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))

import cv2
import json
from src.game_detector import ScreenCapture, DigitRecognizer


def main():
    print("=" * 50)
    print("  Test de Reconocedor de Digitos")
    print("=" * 50)
    
    templates_dir = PROJECT_ROOT / "assets" / "digit_templates"
    config_path = PROJECT_ROOT / "config" / "calibration.json"
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    calibration = config.get("ui_positions", {})
    
    print(f"\nCalibracion: {config.get('resolution', '?')}")
    
    # Crear reconocedor
    recognizer = DigitRecognizer(str(templates_dir), confianza_minima=0.6)
    
    print(f"Templates: {recognizer.templates_disponibles()}")
    
    capture = ScreenCapture(fps_limit=5)
    
    # Delay para cambiar al juego
    print("\n*** CAMBIA A LA VENTANA DEL JUEGO ***")
    for i in range(5, 0, -1):
        print(f"  Capturando en {i}...", end="\r")
        time.sleep(1)
    print("\nCapturando...          ")
    
    screenshot = capture.capture_top_bar(height=150)
    
    debug_dir = PROJECT_ROOT / "debug"
    debug_dir.mkdir(exist_ok=True)
    
    print("\nResultados:")
    print("-" * 40)
    
    regiones = ["villager_count", "population", "food", "wood", "gold", "stone"]
    
    for nombre in regiones:
        if nombre not in calibration:
            print(f"  {nombre:16}: sin calibracion")
            continue
        
        cfg = calibration[nombre]
        x, y = cfg["x"], cfg["y"]
        w, h = cfg["width"], cfg["height"]
        
        region = screenshot[y:y+h, x:x+w]
        cv2.imwrite(str(debug_dir / f"region_{nombre}.png"), region)
        
        if nombre == "population":
            actual, maximo = recognizer.reconocer_poblacion(region)
            if actual is not None:
                print(f"  {nombre:16}: {actual}/{maximo}")
            else:
                print(f"  {nombre:16}: ---")
        else:
            resultado = recognizer.reconocer_numero(region)
            if resultado is not None:
                print(f"  {nombre:16}: {resultado}")
            else:
                print(f"  {nombre:16}: ---")
    
    print("-" * 40)
    print(f"\nRegiones en: {debug_dir}")


if __name__ == "__main__":
    main()
