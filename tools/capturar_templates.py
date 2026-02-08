"""
Herramienta para capturar templates de dígitos desde Age of Empires II DE.
Versión simplificada - captura la barra superior sin escalar para máxima precisión.

Uso:
1. Abrir el juego y posicionarse en una partida
2. Ejecutar: python tools/capturar_templates.py
3. Seleccionar dígitos y guardarlos
"""

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))

import mss
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QComboBox, QMessageBox, QScrollArea
)
from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QPixmap, QImage, QPainter, QPen, QColor, QKeyEvent
import cv2


class ImagenCaptura(QLabel):
    """Widget que muestra la captura y permite seleccionar región."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.imagen_np = None  # Imagen original en numpy (BGR)
        self.inicio = None
        self.fin = None
        self.arrastrando = False
    
    def set_imagen(self, img_np: np.ndarray):
        """Establece la imagen (numpy BGR) a mostrar a escala 1:1."""
        self.imagen_np = img_np.copy()
        
        # Convertir BGR -> RGB para Qt
        rgb = cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        
        # Crear QPixmap
        qimg = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)
        self.setPixmap(QPixmap.fromImage(qimg))
        self.setFixedSize(w, h)
        
        # Limpiar selección
        self.inicio = None
        self.fin = None
    
    def get_recorte(self) -> np.ndarray:
        """Retorna el recorte seleccionado."""
        if self.imagen_np is None or self.inicio is None or self.fin is None:
            return None
        
        x1, x2 = sorted([self.inicio.x(), self.fin.x()])
        y1, y2 = sorted([self.inicio.y(), self.fin.y()])
        
        # Limitar a bordes
        h, w = self.imagen_np.shape[:2]
        x1, x2 = max(0, x1), min(w, x2)
        y1, y2 = max(0, y1), min(h, y2)
        
        if x2 <= x1 or y2 <= y1:
            return None
        
        return self.imagen_np[y1:y2, x1:x2].copy()
    
    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self.inicio = e.pos()
            self.fin = e.pos()
            self.arrastrando = True
            self.update()
    
    def mouseMoveEvent(self, e):
        if self.arrastrando:
            self.fin = e.pos()
            self.update()
    
    def mouseReleaseEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self.fin = e.pos()
            self.arrastrando = False
            self.update()
            # Notificar
            parent = self.parent()
            while parent and not hasattr(parent, 'actualizar_preview'):
                parent = parent.parent()
            if parent:
                parent.actualizar_preview()
    
    def paintEvent(self, e):
        super().paintEvent(e)
        if self.inicio and self.fin:
            p = QPainter(self)
            p.setPen(QPen(QColor(0, 255, 0), 2))
            p.drawRect(QRect(self.inicio, self.fin))


class VentanaCaptura(QMainWindow):
    """Ventana principal."""
    
    COLORES = ["white", "cyan", "yellow"]
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Capturador de Templates - Barra Superior")
        
        self.sct = mss.mss()
        self.monitor = self.sct.monitors[1]
        
        self.color_actual = "white"
        self.dir_templates = PROJECT_ROOT / "assets" / "digit_templates"
        
        self._init_ui()
        self.refrescar()
    
    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Controles superiores
        fila1 = QHBoxLayout()
        
        fila1.addWidget(QLabel("Color:"))
        self.combo = QComboBox()
        self.combo.addItems(self.COLORES)
        self.combo.currentTextChanged.connect(lambda c: setattr(self, 'color_actual', c))
        fila1.addWidget(self.combo)
        
        fila1.addSpacing(20)
        
        btn_ref = QPushButton("🔄 Refrescar (R)")
        btn_ref.clicked.connect(self.refrescar)
        fila1.addWidget(btn_ref)
        
        fila1.addStretch()
        
        self.lbl_info = QLabel("Selecciona un dígito con el mouse")
        fila1.addWidget(self.lbl_info)
        
        layout.addLayout(fila1)
        
        # Área de imagen con scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(False)
        self.img_widget = ImagenCaptura()
        scroll.setWidget(self.img_widget)
        scroll.setMinimumHeight(200)
        layout.addWidget(scroll)
        
        # Preview y botones
        fila2 = QHBoxLayout()
        
        # Preview
        self.lbl_preview = QLabel("Preview")
        self.lbl_preview.setFixedSize(120, 80)
        self.lbl_preview.setStyleSheet("background: #333; border: 1px solid #555;")
        self.lbl_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fila2.addWidget(self.lbl_preview)
        
        fila2.addSpacing(20)
        
        # Botones dígitos
        fila2.addWidget(QLabel("Guardar:"))
        for i in range(10):
            btn = QPushButton(str(i))
            btn.setFixedSize(35, 35)
            btn.clicked.connect(lambda _, d=i: self.guardar(d))
            fila2.addWidget(btn)
        
        fila2.addStretch()
        
        layout.addLayout(fila2)
        
        # Estado templates
        self.lbl_estado = QLabel()
        self.lbl_estado.setStyleSheet("color: #888; font-size: 11px;")
        layout.addWidget(self.lbl_estado)
        self._actualizar_estado()
        
        self.resize(1000, 400)
    
    def refrescar(self):
        """Captura solo la barra superior (150px) a escala 1:1."""
        region = {
            "left": self.monitor["left"],
            "top": self.monitor["top"],
            "width": self.monitor["width"],
            "height": 150  # Solo barra superior
        }
        screenshot = self.sct.grab(region)
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        
        self.img_widget.set_imagen(img)
        self.lbl_info.setText(f"Captura: {img.shape[1]}x{img.shape[0]} px")
    
    def actualizar_preview(self):
        """Muestra el recorte seleccionado."""
        recorte = self.img_widget.get_recorte()
        if recorte is None or recorte.size == 0:
            return
        
        # Ampliar para preview
        h, w = recorte.shape[:2]
        if w > 0 and h > 0:
            escala = min(100 // w, 60 // h, 8)
            escala = max(escala, 1)
            grande = cv2.resize(recorte, (w * escala, h * escala), 
                               interpolation=cv2.INTER_NEAREST)
            
            rgb = cv2.cvtColor(grande, cv2.COLOR_BGR2RGB)
            h2, w2, ch = rgb.shape
            qimg = QImage(rgb.data, w2, h2, ch * w2, QImage.Format.Format_RGB888)
            self.lbl_preview.setPixmap(QPixmap.fromImage(qimg))
            
            self.lbl_info.setText(f"Selección: {w}x{h} px")
    
    def guardar(self, digito: int):
        """Guarda el recorte como template."""
        recorte = self.img_widget.get_recorte()
        if recorte is None or recorte.size == 0:
            QMessageBox.warning(self, "Error", "Selecciona una región primero")
            return
        
        path = self.dir_templates / self.color_actual
        path.mkdir(parents=True, exist_ok=True)
        
        archivo = path / f"{digito}.png"
        cv2.imwrite(str(archivo), recorte)
        
        self.lbl_info.setText(f"✅ {self.color_actual}/{digito}.png guardado")
        self._actualizar_estado()
    
    def _actualizar_estado(self):
        lineas = []
        for color in self.COLORES:
            d = self.dir_templates / color
            if d.exists():
                nums = sorted([f.stem for f in d.glob("*.png")])
                lineas.append(f"{color}: {', '.join(nums) if nums else '(vacío)'}")
            else:
                lineas.append(f"{color}: (vacío)")
        self.lbl_estado.setText("  |  ".join(lineas))
    
    def keyPressEvent(self, e: QKeyEvent):
        k = e.key()
        if k in (Qt.Key.Key_Q, Qt.Key.Key_Escape):
            self.close()
        elif k == Qt.Key.Key_R:
            self.refrescar()
        elif k == Qt.Key.Key_C:
            idx = (self.COLORES.index(self.color_actual) + 1) % 3
            self.combo.setCurrentIndex(idx)
        elif Qt.Key.Key_0 <= k <= Qt.Key.Key_9:
            self.guardar(k - Qt.Key.Key_0)


def main():
    print("Iniciando capturador de templates...")
    print(f"Templates en: {PROJECT_ROOT / 'assets' / 'digit_templates'}\n")
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet("""
        QMainWindow, QWidget { background: #2b2b2b; color: #fff; }
        QPushButton { background: #3c3c3c; border: 1px solid #555; 
                      border-radius: 3px; padding: 5px; }
        QPushButton:hover { background: #4a4a4a; }
        QComboBox { background: #3c3c3c; border: 1px solid #555; padding: 3px; }
    """)
    
    v = VentanaCaptura()
    v.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
