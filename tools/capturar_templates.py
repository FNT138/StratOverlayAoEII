"""
Herramienta interactiva para capturar templates de dígitos desde Age of Empires II DE.

Uso:
1. Abrir el juego y posicionarse en una partida donde se vean los números
2. Ejecutar este script: python tools/capturar_templates.py
3. Usar los controles para capturar cada dígito

Controles:
- Clic izquierdo: Seleccionar esquina inicial del recorte
- Clic derecho: Seleccionar esquina final y mostrar preview
- 0-9: Guardar el recorte actual como template del dígito correspondiente
- C: Cambiar color (white -> cyan -> yellow -> white)
- R: Refrescar captura de pantalla
- Q: Salir

El script guarda los templates en assets/digit_templates/{color}/{digito}.png
"""

import cv2
import numpy as np
import mss
from pathlib import Path
import sys

# Agregar el directorio raíz al path para importar módulos del proyecto
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))


class CapturadorTemplates:
    """
    Herramienta visual para capturar templates de dígitos.
    Permite seleccionar regiones de la pantalla y guardarlas como templates.
    """
    
    # Colores disponibles para los templates
    COLORES = ["white", "cyan", "yellow"]
    
    def __init__(self):
        """Inicializa el capturador con estado inicial."""
        self.sct = mss.mss()
        self.monitor = self.sct.monitors[1]  # Monitor principal
        
        # Estado de selección
        self.punto_inicio = None
        self.punto_fin = None
        self.recorte_actual = None
        
        # Color actual para guardar templates
        self.indice_color = 0
        self.color_actual = self.COLORES[0]
        
        # Captura inicial
        self.screenshot = self._capturar_pantalla()
        
        # Directorio de salida
        self.dir_templates = PROJECT_ROOT / "assets" / "digit_templates"
        
        # Nombre de la ventana
        self.nombre_ventana = "Capturador de Templates - AoE II"
        self.nombre_preview = "Preview del Recorte"
    
    def _capturar_pantalla(self) -> np.ndarray:
        """
        Captura la pantalla completa.
        
        Returns:
            Imagen en formato BGR (OpenCV)
        """
        screenshot = self.sct.grab(self.monitor)
        img = np.array(screenshot)
        # Convertir BGRA a BGR
        return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    
    def _mouse_callback(self, evento, x, y, flags, param):
        """
        Callback para eventos del mouse.
        
        Clic izquierdo: Define punto de inicio
        Clic derecho: Define punto final y muestra preview
        """
        if evento == cv2.EVENT_LBUTTONDOWN:
            self.punto_inicio = (x, y)
            self.punto_fin = None
            self.recorte_actual = None
            print(f"Punto inicio: {x}, {y}")
            
        elif evento == cv2.EVENT_RBUTTONDOWN:
            if self.punto_inicio is not None:
                self.punto_fin = (x, y)
                self._extraer_recorte()
                print(f"Punto fin: {x}, {y}")
    
    def _extraer_recorte(self):
        """
        Extrae el recorte actual basado en los puntos seleccionados.
        Normaliza las coordenadas para que funcione sin importar el orden de selección.
        """
        if self.punto_inicio is None or self.punto_fin is None:
            return
        
        # Normalizar coordenadas (asegurar que x1 < x2 y y1 < y2)
        x1 = min(self.punto_inicio[0], self.punto_fin[0])
        y1 = min(self.punto_inicio[1], self.punto_fin[1])
        x2 = max(self.punto_inicio[0], self.punto_fin[0])
        y2 = max(self.punto_inicio[1], self.punto_fin[1])
        
        # Extraer región
        self.recorte_actual = self.screenshot[y1:y2, x1:x2].copy()
        
        # Mostrar preview ampliado
        if self.recorte_actual.size > 0:
            # Escalar para mejor visualización (mínimo 100px de ancho)
            h, w = self.recorte_actual.shape[:2]
            escala = max(4, 100 // max(w, 1))
            preview = cv2.resize(
                self.recorte_actual, 
                (w * escala, h * escala), 
                interpolation=cv2.INTER_NEAREST
            )
            cv2.imshow(self.nombre_preview, preview)
    
    def _guardar_template(self, digito: int):
        """
        Guarda el recorte actual como template para el dígito especificado.
        
        Args:
            digito: Número del 0 al 9
        """
        if self.recorte_actual is None:
            print("⚠️  No hay recorte seleccionado. Usa clic izq + clic der para seleccionar.")
            return
        
        # Crear directorio si no existe
        dir_color = self.dir_templates / self.color_actual
        dir_color.mkdir(parents=True, exist_ok=True)
        
        # Guardar imagen
        ruta = dir_color / f"{digito}.png"
        cv2.imwrite(str(ruta), self.recorte_actual)
        print(f"✅ Guardado: {ruta}")
    
    def _cambiar_color(self):
        """Cambia al siguiente color en la lista."""
        self.indice_color = (self.indice_color + 1) % len(self.COLORES)
        self.color_actual = self.COLORES[self.indice_color]
        print(f"🎨 Color actual: {self.color_actual}")
    
    def _dibujar_interfaz(self, img: np.ndarray) -> np.ndarray:
        """
        Dibuja elementos de interfaz sobre la imagen.
        
        Args:
            img: Imagen base
            
        Returns:
            Imagen con interfaz dibujada
        """
        display = img.copy()
        
        # Dibujar rectángulo de selección si hay puntos definidos
        if self.punto_inicio is not None:
            cv2.circle(display, self.punto_inicio, 5, (0, 255, 0), -1)
            
            if self.punto_fin is not None:
                cv2.rectangle(display, self.punto_inicio, self.punto_fin, (0, 255, 0), 2)
        
        # Mostrar información en la esquina
        info = [
            f"Color: {self.color_actual}",
            "Controles:",
            "  Clic izq: Punto inicio",
            "  Clic der: Punto fin",
            "  0-9: Guardar digito",
            "  C: Cambiar color",
            "  R: Refrescar",
            "  Q: Salir"
        ]
        
        y = 30
        for linea in info:
            cv2.putText(display, linea, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.6, (0, 255, 0), 2)
            y += 25
        
        return display
    
    def ejecutar(self):
        """
        Ejecuta el bucle principal de la herramienta.
        """
        print("=" * 50)
        print("  Capturador de Templates de Dígitos")
        print("  Para Age of Empires II: Definitive Edition")
        print("=" * 50)
        print(f"\nTemplates se guardarán en: {self.dir_templates}")
        print(f"Color inicial: {self.color_actual}")
        print("\nAbre el juego y posiciónate donde se vean los números.")
        print("Presiona R para refrescar la captura.\n")
        
        # Crear ventana y configurar callback del mouse
        cv2.namedWindow(self.nombre_ventana, cv2.WINDOW_NORMAL)
        cv2.setMouseCallback(self.nombre_ventana, self._mouse_callback)
        
        # Redimensionar ventana para que quepa en pantalla
        cv2.resizeWindow(self.nombre_ventana, 1280, 720)
        
        while True:
            # Dibujar interfaz
            display = self._dibujar_interfaz(self.screenshot)
            cv2.imshow(self.nombre_ventana, display)
            
            # Procesar teclas
            key = cv2.waitKey(1) & 0xFF
            
            # Q para salir
            if key == ord('q') or key == ord('Q'):
                break
            
            # R para refrescar captura
            elif key == ord('r') or key == ord('R'):
                self.screenshot = self._capturar_pantalla()
                print("🔄 Captura refrescada")
            
            # C para cambiar color
            elif key == ord('c') or key == ord('C'):
                self._cambiar_color()
            
            # 0-9 para guardar dígitos
            elif ord('0') <= key <= ord('9'):
                digito = key - ord('0')
                self._guardar_template(digito)
        
        # Limpiar
        cv2.destroyAllWindows()
        print("\n¡Captura finalizada!")
        
        # Mostrar resumen de templates guardados
        self._mostrar_resumen()
    
    def _mostrar_resumen(self):
        """Muestra un resumen de los templates guardados."""
        print("\n📊 Resumen de templates:")
        
        for color in self.COLORES:
            dir_color = self.dir_templates / color
            if dir_color.exists():
                templates = list(dir_color.glob("*.png"))
                digitos = [t.stem for t in templates]
                if digitos:
                    print(f"  {color}: {', '.join(sorted(digitos))}")
                else:
                    print(f"  {color}: (vacío)")
            else:
                print(f"  {color}: (no existe)")


def main():
    """Punto de entrada principal."""
    capturador = CapturadorTemplates()
    capturador.ejecutar()


if __name__ == "__main__":
    main()
