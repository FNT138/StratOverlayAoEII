"""
Reconocedor de digitos usando Template Matching.

ESTRATEGIA: Usar solo templates "white" para todo, ya que en escala de grises
los digitos de cualquier color claro (blanco, cyan, amarillo, verde) se ven similares.
El matching se hace por forma/brillo, no por color.
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class ResultadoDigito:
    """Resultado de reconocer un solo digito."""
    digito: int
    confianza: float
    posicion_x: int


class DigitRecognizer:
    """
    Reconocedor de digitos usando template matching.
    Usa templates en escala de grises para matchear por forma, no por color.
    """
    
    def __init__(
        self, 
        templates_dir: str, 
        confianza_minima: float = 0.6,
        metodo_matching: int = cv2.TM_CCOEFF_NORMED
    ):
        self.templates_dir = Path(templates_dir)
        self.confianza_minima = confianza_minima
        self.metodo_matching = metodo_matching
        
        # Templates en escala de grises: {digito: imagen}
        self.templates: Dict[int, np.ndarray] = {}
        
        self._cargar_templates()
    
    def _cargar_templates(self):
        """
        Carga templates desde la carpeta 'white'.
        Los convierte a escala de grises y los usa para todo.
        """
        # Priorizar white, luego cyan, luego yellow
        for color in ["white", "cyan", "yellow"]:
            dir_color = self.templates_dir / color
            if not dir_color.exists():
                continue
            
            for digito in range(10):
                if digito in self.templates:
                    continue  # Ya tenemos este digito
                
                ruta = dir_color / f"{digito}.png"
                if ruta.exists():
                    template = cv2.imread(str(ruta), cv2.IMREAD_GRAYSCALE)
                    if template is not None:
                        self.templates[digito] = template
        
        if self.templates:
            print(f"[DigitRecognizer] Templates cargados: {sorted(self.templates.keys())}")
        else:
            print("[DigitRecognizer] ADVERTENCIA: No se cargaron templates")
    
    def templates_disponibles(self, color: str = None) -> List[int]:
        """Retorna lista de digitos disponibles."""
        return sorted(self.templates.keys())
    
    def tiene_templates_completos(self, color: str = None) -> bool:
        """Verifica si hay templates 0-9."""
        return self.templates_disponibles() == list(range(10))
    
    def _detectar_digitos_en_region(self, region: np.ndarray) -> List[ResultadoDigito]:
        """
        Detecta todos los digitos en una region usando template matching.
        """
        if region is None or region.size == 0:
            return []
        
        # Convertir a escala de grises
        if len(region.shape) == 3:
            gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
        else:
            gray = region.copy()
        
        detecciones = []
        
        for digito, template in self.templates.items():
            # Verificar que el template cabe en la region
            if gray.shape[0] < template.shape[0] or gray.shape[1] < template.shape[1]:
                continue
            
            # Template matching
            result = cv2.matchTemplate(gray, template, self.metodo_matching)
            
            # Encontrar todos los matches buenos
            locations = np.where(result >= self.confianza_minima)
            
            for pt in zip(*locations[::-1]):  # pt = (x, y)
                conf = float(result[pt[1], pt[0]])
                detecciones.append(ResultadoDigito(
                    digito=digito,
                    confianza=conf,
                    posicion_x=pt[0]
                ))
        
        if not detecciones:
            return []
        
        # Non-Maximum Suppression: quedarse con el mejor match en cada posicion
        return self._aplicar_nms(detecciones, distancia_minima=8)
    
    def _aplicar_nms(self, detecciones: List[ResultadoDigito], 
                      distancia_minima: int) -> List[ResultadoDigito]:
        """Elimina detecciones duplicadas, quedandose con la de mayor confianza."""
        if not detecciones:
            return []
        
        # Ordenar por confianza descendente
        ordenadas = sorted(detecciones, key=lambda d: d.confianza, reverse=True)
        
        resultado = []
        posiciones_usadas = []
        
        for det in ordenadas:
            es_duplicado = False
            for pos in posiciones_usadas:
                if abs(det.posicion_x - pos) < distancia_minima:
                    es_duplicado = True
                    break
            
            if not es_duplicado:
                resultado.append(det)
                posiciones_usadas.append(det.posicion_x)
        
        # Ordenar por posicion X (izquierda a derecha)
        resultado.sort(key=lambda d: d.posicion_x)
        return resultado
    
    def reconocer_numero(self, region: np.ndarray, color: str = None) -> Optional[int]:
        """
        Reconoce un numero en una region de imagen.
        El parametro 'color' se ignora (se usa matching por forma).
        """
        if region is None or region.size == 0:
            return None
        
        digitos = self._detectar_digitos_en_region(region)
        
        if not digitos:
            return None
        
        numero_str = "".join(str(d.digito) for d in digitos)
        
        try:
            return int(numero_str)
        except ValueError:
            return None
    
    def reconocer_poblacion(self, region: np.ndarray, 
                             color: str = None) -> Tuple[Optional[int], Optional[int]]:
        """
        Reconoce poblacion en formato 'XX/YY'.
        Detecta digitos y los divide por el gap mas grande (donde esta la barra).
        """
        if region is None or region.size == 0:
            return (None, None)
        
        digitos = self._detectar_digitos_en_region(region)
        
        if len(digitos) < 2:
            return (None, None)
        
        # Encontrar el gap mas grande (donde esta la "/")
        max_gap = 0
        indice_gap = 0
        
        for i in range(len(digitos) - 1):
            gap = digitos[i + 1].posicion_x - digitos[i].posicion_x
            if gap > max_gap:
                max_gap = gap
                indice_gap = i
        
        grupo1 = digitos[:indice_gap + 1]
        grupo2 = digitos[indice_gap + 1:]
        
        if not grupo1 or not grupo2:
            return (None, None)
        
        try:
            actual = int("".join(str(d.digito) for d in grupo1))
            maximo = int("".join(str(d.digito) for d in grupo2))
            return (actual, maximo)
        except ValueError:
            return (None, None)


def crear_reconocedor_default() -> DigitRecognizer:
    """Crea reconocedor con configuracion por defecto."""
    ruta = Path(__file__).parent.parent.parent / "assets" / "digit_templates"
    return DigitRecognizer(str(ruta))
