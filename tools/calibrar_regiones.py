"""
Herramienta visual para calibrar regiones de la UI.
Permite ajustar las coordenadas de population, food, villagers, etc.
"""

import time
import sys
import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))

import mss
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QListWidget, QMessageBox, QScrollArea,
    QSplitter, QFrame
)
from PyQt6.QtCore import Qt, QRect, QPoint
from PyQt6.QtGui import QPixmap, QImage, QPainter, QPen, QColor, QKeyEvent, QAction
import cv2


class ImagenCalib(QLabel):
    """Widget que muestra la captura y permite editar regiones."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.imagen_np = None  # Imagen original
        self.regiones = {}     # Diccionario de regiones {nombre: rect}
        self.region_sel = None # Nombre de region seleccionada
        
        self.inicio_drag = None
        self.rect_drag = None
        self.arrastrando = False
        
    def set_imagen(self, img_np):
        self.imagen_np = img_np.copy()
        self.update_view()
        
    def set_regiones(self, regiones):
        self.regiones = regiones
        self.update_view()
        
    def seleccionar_region(self, nombre):
        self.region_sel = nombre
        self.update_view()
        
    def update_view(self):
        if self.imagen_np is None:
            return
            
        # Dibujar sobre imagen
        img_draw = self.imagen_np.copy()
        
        # Dibujar todas las regiones
        for nombre, r in self.regiones.items():
            x, y, w, h = r['x'], r['y'], r['width'], r['height']
            
            color = (0, 255, 0) # Verde default
            grosor = 1
            
            if nombre == self.region_sel:
                color = (0, 255, 255) # Cian seleccionado
                grosor = 2
            
            cv2.rectangle(img_draw, (x, y), (x+w, y+h), color, grosor)
            # Texto
            cv2.putText(img_draw, nombre, (x, y-5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
        
        # Dibujar rectangulo de arrastre
        if self.arrastrando and self.rect_drag:
            x, y, w, h = self.rect_drag
            cv2.rectangle(img_draw, (x, y), (x+w, y+h), (0, 0, 255), 2)
            
        # Mostrar en Qt
        rgb = cv2.cvtColor(img_draw, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qimg = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)
        self.setPixmap(QPixmap.fromImage(qimg))
        self.setFixedSize(w, h)
        
    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            if self.region_sel:
                self.inicio_drag = e.pos()
                self.arrastrando = True
                
    def mouseMoveEvent(self, e):
        if self.arrastrando and self.inicio_drag:
            curr = e.pos()
            x = min(self.inicio_drag.x(), curr.x())
            y = min(self.inicio_drag.y(), curr.y())
            w = abs(self.inicio_drag.x() - curr.x())
            h = abs(self.inicio_drag.y() - curr.y())
            self.rect_drag = (x, y, w, h)
            self.update_view()
            
    def mouseReleaseEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton and self.arrastrando:
            self.arrastrando = False
            if self.rect_drag and self.region_sel:
                # Actualizar region
                x, y, w, h = self.rect_drag
                self.regiones[self.region_sel] = {
                    'x': x, 'y': y, 'width': w, 'height': h
                }
                self.rect_drag = None
                self.update_view()
                # Notificar al padre
                self.parent().parent().parent().parent().actualizar_valores_ui()


class VentanaCalibracion(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calibrador de Regiones - Age of Empires II")
        self.resize(1200, 800)
        
        self.sct = mss.mss()
        self.config_path = PROJECT_ROOT / "config" / "calibration.json"
        self.monitor_idx = 1
        
        # Cargar config
        self.cargar_config()
        
        self._init_ui()
        self.refrescar_captura()
        
    def cargar_config(self):
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = {"resolution": "1920x1080", "ui_positions": {}}
            
        self.regiones = self.data.get("ui_positions", {})
        
    def guardar_config(self):
        self.data["ui_positions"] = self.regiones
        with open(self.config_path, 'w') as f:
            json.dump(self.data, f, indent=4)
        QMessageBox.information(self, "Guardado", "Configuración guardada correctamente")
        
    def _init_ui(self):
        # Widget central con Splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(splitter)
        
        # Panel Izquierdo (Controles)
        panel_izq = QFrame()
        panel_izq.setFrameShape(QFrame.Shape.StyledPanel)
        layout_izq = QVBoxLayout(panel_izq)
        
        layout_izq.addWidget(QLabel("<b>Regiones Disponibles:</b>"))
        
        self.lista_regiones = QListWidget()
        self.lista_regiones.addItems(sorted(self.regiones.keys()))
        self.lista_regiones.currentItemChanged.connect(self.on_region_changed)
        layout_izq.addWidget(self.lista_regiones)
        
        # Coordenadas manuales
        self.lbl_coords = QLabel("Selecciona region...")
        layout_izq.addWidget(self.lbl_coords)
        
        layout_izq.addStretch()
        
        btn_add = QPushButton("➕ Agregar Región")
        btn_add.clicked.connect(self.nueva_region)
        layout_izq.addWidget(btn_add)
        
        btn_refresh = QPushButton("🔄 Nueva Captura (R)")
        btn_refresh.clicked.connect(self.refrescar_captura)
        layout_izq.addWidget(btn_refresh)
        
        btn_save = QPushButton("💾 Guardar Cambios (Ctrl+S)")
        btn_save.setStyleSheet("background-color: #2e7d32; color: white; font-weight: bold;")
        btn_save.clicked.connect(self.guardar_config)
        layout_izq.addWidget(btn_save)
        
        splitter.addWidget(panel_izq)
        
        # Panel Derecho (Imagen)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True) # Para que se centre
        self.img_widget = ImagenCalib()
        scroll.setWidget(self.img_widget)
        splitter.addWidget(scroll)
        
        # Proporciones
        splitter.setSizes([300, 900])
        
    def refrescar_captura(self):
        monitor = self.sct.monitors[self.monitor_idx]
        # Capturamos solo la parte superior si es full HD (para optimizar)
        # O toda la pantalla si queremos ver todo
        img = np.array(self.sct.grab(monitor))
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        
        # Recortar solo parte superior para zoom? No, mostremos todo 
        # pero quizas croppeado arriba para no scrollear tanto
        # Age UI esta arriba usualmente (top 100px)
        
        # Para facilitar, mostramos solo los primeros 200px de altura
        # que es donde esta la info de recursos
        h, w = img.shape[:2]
        if h > 200:
            img = img[:200, :]
            
        self.img_widget.set_imagen(img)
        self.img_widget.set_regiones(self.regiones)
        
    def on_region_changed(self, current, previous):
        if current:
            nombre = current.text()
            self.img_widget.seleccionar_region(nombre)
            self.actualizar_valores_ui()
            
    def actualizar_valores_ui(self):
        nombre = self.img_widget.region_sel
        if nombre and nombre in self.regiones:
            r = self.regiones[nombre]
            self.lbl_coords.setText(
                f"Region: {nombre}\n"
                f"X: {r['x']}  |  Y: {r['y']}\n"
                f"W: {r['width']} | H: {r['height']}"
            )
            
    def nueva_region(self):
        # TODO: Dialogo para nombre
        pass
        
    def keyPressEvent(self, e):
        if e.key() == Qt.Key.Key_R:
            self.refrescar_captura()
        elif e.modifiers() & Qt.KeyboardModifier.ControlModifier and e.key() == Qt.Key.Key_S:
            self.guardar_config()


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Dark Theme
    app.setStyleSheet("""
        QMainWindow { background-color: #2b2b2b; color: #ffffff; }
        QLabel { color: #ffffff; }
        QListWidget { background-color: #3c3c3c; color: #ffffff; border: 1px solid #555; }
        QPushButton { background-color: #404040; color: #ffffff; padding: 5px; border: 1px solid #555; }
        QPushButton:hover { background-color: #505050; }
    """)
    
    win = VentanaCalibracion()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    time.sleep(1)
    main()
