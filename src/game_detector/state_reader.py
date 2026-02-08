"""
Lector de estado del juego - Interfaz principal para leer estado de AoE II.

Este módulo orquesta la captura de pantalla y el reconocimiento de dígitos
para extraer el estado actual del juego (villagers, recursos, población).

El lector corre en un thread separado para no bloquear la UI del overlay.
"""
import json
from typing import Optional
import threading
import time
from pathlib import Path
from PyQt6.QtCore import QObject, pyqtSignal

from .game_state import GameState
from .screen_capture import ScreenCapture
from .digit_recognizer import DigitRecognizer


class StateReader(QObject):
    """
    Clase principal para leer el estado del juego desde capturas de pantalla.
    
    Ejecuta en un thread separado para no bloquear la UI.
    Emite señales Qt cuando hay actualizaciones o errores.
    
    Uso típico:
        reader = StateReader(fps=5)
        reader.load_calibration(calibration_data)
        reader.state_updated.connect(mi_callback)
        reader.start()
    """
    
    # Señales Qt para comunicación con la UI
    state_updated = pyqtSignal(GameState)  # Emitida cuando hay nuevo estado
    detection_error = pyqtSignal(str)       # Emitida cuando hay error
    
    def __init__(self, fps: int = 5):
        """
        Inicializa el lector de estado.
        
        Args:
            fps: Frecuencia de actualización (capturas por segundo)
        """
        super().__init__()
        
        # Componentes de captura y reconocimiento
        self.capture = ScreenCapture(fps_limit=fps)
        self.digit_recognizer: Optional[DigitRecognizer] = None
        
        # Estado actual y anterior (para fallback)
        self.current_state = GameState()
        self.previous_state = GameState()
        
        # Control del thread
        self.is_running = False
        self.update_thread: Optional[threading.Thread] = None
        
        # Datos de calibración (posiciones de UI)
        self.calibration = {
            'villager_count': None,  # {"x": int, "y": int, "width": int, "height": int}
            'population': None,
            'food': None,
            'wood': None,
            'gold': None,
            'stone': None
        }
        
        self.is_calibrated = False
        
        # Intentar cargar calibración desde archivo
        self._cargar_calibracion_default()
        
        # Intentar inicializar reconocedor de dígitos
        self._inicializar_reconocedor()
    
    def _cargar_calibracion_default(self):
        """
        Intenta cargar calibración desde config/calibration.json
        """
        ruta_config = Path(__file__).parent.parent.parent / "config" / "calibration.json"
        
        if ruta_config.exists():
            try:
                with open(ruta_config, 'r') as f:
                    data = json.load(f)
                
                if "ui_positions" in data:
                    self.calibration = data["ui_positions"]
                    self.is_calibrated = True
                    print(f"[StateReader] Calibración cargada desde {ruta_config}")
            except Exception as e:
                print(f"[StateReader] Error cargando calibración: {e}")
    
    def _inicializar_reconocedor(self):
        """
        Inicializa el reconocedor de dígitos con templates del proyecto.
        """
        ruta_templates = Path(__file__).parent.parent.parent / "assets" / "digit_templates"
        
        if ruta_templates.exists():
            self.digit_recognizer = DigitRecognizer(str(ruta_templates))
            print("[StateReader] Reconocedor de dígitos inicializado")
        else:
            print(f"[StateReader] AVISO: No se encontró {ruta_templates}")
            print("[StateReader] Ejecutar tools/capturar_templates.py para crear templates")
    
    def load_calibration(self, calibration_data: dict):
        """
        Carga datos de calibración para posiciones de UI.
        
        Args:
            calibration_data: Diccionario con posiciones de elementos UI
                Formato: {"villager_count": {"x": 420, "y": 22, "width": 26, "height": 26}, ...}
        """
        self.calibration = calibration_data
        self.is_calibrated = True
    
    def start(self):
        """
        Inicia el loop de lectura en un thread en segundo plano.
        """
        if self.is_running:
            return
        
        if not self.is_calibrated:
            self.detection_error.emit("No calibrado. Ejecutar calibración primero.")
            return
        
        if self.digit_recognizer is None:
            self.detection_error.emit("Sin templates. Ejecutar tools/capturar_templates.py")
            return
        
        self.is_running = True
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()
        print("[StateReader] Iniciado")
    
    def stop(self):
        """
        Detiene el loop de lectura.
        """
        self.is_running = False
        if self.update_thread:
            self.update_thread.join(timeout=2.0)
        
        # Limpiar recursos de captura (mss no es thread-safe)
        if self.capture.mss is not None:
            try:
                self.capture.mss.close()
            except:
                pass
            self.capture.mss = None
        
        print("[StateReader] Detenido")
    
    def _update_loop(self):
        """
        Loop principal que corre en thread separado.
        Captura pantalla y actualiza estado periódicamente.
        """
        while self.is_running:
            try:
                self._update_state()
                time.sleep(0.2)  # ~5 Hz
            except Exception as e:
                self.detection_error.emit(f"Error: {str(e)}")
                time.sleep(1.0)  # Back-off en error
    
    def _extraer_region(self, screenshot, nombre_region: str):
        """
        Extrae una región de la captura según calibración.
        """
        config = self.calibration.get(nombre_region)
        if config is None:
            return None
        
        # Validar que config es un diccionario
        if not isinstance(config, dict):
            return None
        
        x = config.get("x", 0)
        y = config.get("y", 0)
        w = config.get("width", 50)
        h = config.get("height", 30)
        
        # Extraer región
        return screenshot[y:y+h, x:x+w].copy()
    
    def _update_state(self):
        """
        Captura pantalla y actualiza el estado del juego.
        Lee cada region de UI y reconoce los numeros.
        Si falla, mantiene el valor anterior (fallback).
        """
        # Capturar barra superior de la pantalla
        screenshot = self.capture.capture_top_bar(height=150)
        
        # Guardar estado anterior para fallback
        self.previous_state = self.current_state
        
        # Crear nuevo estado
        new_state = GameState()
        
        # --- Leer contador de villagers ---
        villager_region = self._extraer_region(screenshot, 'villager_count')
        if villager_region is not None and self.digit_recognizer:
            valor = self.digit_recognizer.reconocer_numero(villager_region)
            if valor is not None and 0 < valor < 200:
                new_state.villager_count = valor
            else:
                new_state.villager_count = self.previous_state.villager_count
        
        # --- Leer poblacion (formato XX/YY) ---
        pop_region = self._extraer_region(screenshot, 'population')
        if pop_region is not None and self.digit_recognizer:
            actual, maximo = self.digit_recognizer.reconocer_poblacion(pop_region)
            if actual is not None:
                new_state.population = actual
                new_state.max_population = maximo or self.previous_state.max_population
            else:
                new_state.population = self.previous_state.population
                new_state.max_population = self.previous_state.max_population
        
        # --- Leer recursos ---
        for recurso in ['food', 'wood', 'gold', 'stone']:
            region = self._extraer_region(screenshot, recurso)
            if region is not None and self.digit_recognizer:
                valor = self.digit_recognizer.reconocer_numero(region)
                if valor is not None and 0 <= valor < 100000:
                    setattr(new_state, recurso, valor)
                else:
                    setattr(new_state, recurso, getattr(self.previous_state, recurso))
        
        # Marcar estado como valido
        new_state.is_valid = True
        new_state.update_timestamp()
        
        # Actualizar estado actual
        self.current_state = new_state
        
        # Emitir senal para la UI
        self.state_updated.emit(new_state)
    
    def get_current_state(self) -> GameState:
        """
        Retorna el estado más reciente.
        
        Returns:
            GameState con datos actuales
        """
        return self.current_state
    
    def manual_capture(self) -> GameState:
        """
        Captura manual única (sin iniciar loop).
        Útil para testing y debugging.
        
        Returns:
            GameState con datos de la captura
        """
        self._update_state()
        return self.current_state
