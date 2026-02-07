"""
Script de prueba para el reconocedor de dígitos.

Uso:
1. Primero capturar templates con: python tools/capturar_templates.py
2. Luego ejecutar este test: python tools/test_digit_recognizer.py

El script captura la pantalla y muestra qué números detecta en cada región.
"""

import sys
from pathlib import Path

# Agregar directorio raíz al path
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))

import cv2
import json
from src.game_detector import ScreenCapture, DigitRecognizer


def main():
    print("=" * 50)
    print("  Test de Reconocedor de Dígitos")
    print("=" * 50)
    
    # Verificar que existan templates
    templates_dir = PROJECT_ROOT / "assets" / "digit_templates"
    if not templates_dir.exists():
        print(f"\n❌ No se encontró {templates_dir}")
        print("   Ejecutar primero: python tools/capturar_templates.py")
        return
    
    # Cargar calibración
    config_path = PROJECT_ROOT / "config" / "calibration.json"
    if not config_path.exists():
        print(f"\n❌ No se encontró {config_path}")
        return
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    calibration = config.get("ui_positions", {})
    print(f"\n📍 Calibración cargada para {config.get('resolution', 'desconocida')}")
    
    # Inicializar componentes
    print("\n🔧 Inicializando...")
    capture = ScreenCapture(fps_limit=5)
    recognizer = DigitRecognizer(str(templates_dir), confianza_minima=0.7)
    
    # Mostrar templates cargados
    print("\n📦 Templates disponibles:")
    for color in ["white", "cyan", "yellow"]:
        digitos = recognizer.templates_disponibles(color)
        if digitos:
            print(f"   {color}: {digitos}")
        else:
            print(f"   {color}: (ninguno)")
    
    # Capturar pantalla
    print("\n📸 Capturando pantalla...")
    screenshot = capture.capture_top_bar(height=150)
    
    # Probar reconocimiento en cada región
    print("\n🔍 Resultados de reconocimiento:")
    print("-" * 40)
    
    regiones = [
        ("villager_count", "cyan"),
        ("population", "white"),
        ("food", "white"),
        ("wood", "white"),
        ("gold", "white"),
        ("stone", "white"),
    ]
    
    for nombre, color in regiones:
        if nombre not in calibration:
            print(f"   {nombre}: sin calibración")
            continue
        
        cfg = calibration[nombre]
        x, y = cfg["x"], cfg["y"]
        w, h = cfg["width"], cfg["height"]
        
        # Extraer región
        region = screenshot[y:y+h, x:x+w]
        
        # Reconocer
        if nombre == "population":
            resultado = recognizer.reconocer_poblacion(region, color=color)
            display = f"{resultado[0]}/{resultado[1]}" if resultado[0] else "---"
        else:
            resultado = recognizer.reconocer_numero(region, color=color)
            display = str(resultado) if resultado is not None else "---"
        
        print(f"   {nombre:16}: {display}")
        
        # Guardar región para debug
        debug_path = PROJECT_ROOT / "debug" / f"region_{nombre}.png"
        debug_path.parent.mkdir(exist_ok=True)
        cv2.imwrite(str(debug_path), region)
    
    print("-" * 40)
    print(f"\n💾 Regiones guardadas en: {PROJECT_ROOT / 'debug'}")
    print("\n✅ Test completado")


if __name__ == "__main__":
    main()
