"""
Reconocedor de dígitos usando Template Matching.

Este módulo implementa reconocimiento de números en capturas de pantalla
usando comparación directa contra templates de cada dígito (0-9).

Ventajas sobre OCR:
- No requiere binarización (funciona con cualquier color de texto)
- Más robusto ante variaciones de fuente del juego
- Resultados consistentes para fuentes conocidas
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class ResultadoDigito:
    """
    Resultado de reconocer un solo dígito.
    
    Attributes:
        digito: Valor numérico reconocido (0-9)
        confianza: Nivel de confianza del match (0.0 a 1.0)
        posicion_x: Posición X donde se encontró el dígito en la imagen
    """
    digito: int
    confianza: float
    posicion_x: int


class DigitRecognizer:
    """
    Reconocedor de dígitos usando template matching.
    
    Carga templates de dígitos (0-9) para diferentes colores de texto
    y los compara contra regiones de imagen para reconocer números.
    
    Ejemplo de uso:
        recognizer = DigitRecognizer("assets/digit_templates")
        numero = recognizer.reconocer_numero(region_imagen, color="cyan")
    """
    
    # Colores soportados para templates
    COLORES_SOPORTADOS = ["white", "cyan", "yellow"]
    
    def __init__(
        self, 
        templates_dir: str, 
        confianza_minima: float = 0.75,
        metodo_matching: int = cv2.TM_CCOEFF_NORMED
    ):
        """
        Inicializa el reconocedor cargando templates desde disco.
        
        Args:
            templates_dir: Directorio raíz de templates (ej: "assets/digit_templates")
            confianza_minima: Umbral mínimo para considerar un match válido (0.0-1.0)
            metodo_matching: Método de OpenCV para template matching
        """
        self.templates_dir = Path(templates_dir)
        self.confianza_minima = confianza_minima
        self.metodo_matching = metodo_matching
        
        # Cache de templates: {color: {digito: imagen}}
        self.templates: Dict[str, Dict[int, np.ndarray]] = {}
        
        # Cargar templates disponibles
        self._cargar_templates()
    
    def _cargar_templates(self):
        """
        Carga todos los templates disponibles desde el directorio.
        
        Los templates se organizan en subcarpetas por color:
        templates_dir/
            white/
                0.png, 1.png, ..., 9.png
            cyan/
                0.png, ...
        """
        for color in self.COLORES_SOPORTADOS:
            dir_color = self.templates_dir / color
            
            if not dir_color.exists():
                continue
            
            self.templates[color] = {}
            
            for digito in range(10):
                ruta_template = dir_color / f"{digito}.png"
                
                if ruta_template.exists():
                    # Cargar en escala de grises para matching más rápido
                    template = cv2.imread(str(ruta_template), cv2.IMREAD_GRAYSCALE)
                    
                    if template is not None:
                        self.templates[color][digito] = template
        
        # Log de templates cargados
        for color, digitos in self.templates.items():
            if digitos:
                lista_digitos = sorted(digitos.keys())
                print(f"[DigitRecognizer] Cargados templates {color}: {lista_digitos}")
    
    def templates_disponibles(self, color: str) -> List[int]:
        """
        Retorna lista de dígitos disponibles para un color.
        
        Args:
            color: Color a consultar ("white", "cyan", "yellow")
            
        Returns:
            Lista de dígitos disponibles (ej: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        """
        if color not in self.templates:
            return []
        return sorted(self.templates[color].keys())
    
    def tiene_templates_completos(self, color: str) -> bool:
        """
        Verifica si hay templates para todos los dígitos 0-9.
        
        Args:
            color: Color a verificar
            
        Returns:
            True si hay templates para 0, 1, 2, ..., 9
        """
        return self.templates_disponibles(color) == list(range(10))
    
    def _encontrar_digito(
        self, 
        region: np.ndarray, 
        template: np.ndarray
    ) -> Tuple[float, int]:
        """
        Busca un template de dígito en una región.
        
        Args:
            region: Imagen donde buscar (escala de grises)
            template: Template del dígito a buscar
            
        Returns:
            Tupla (confianza máxima, posición X del mejor match)
        """
        # Verificar que la región sea más grande que el template
        if (region.shape[0] < template.shape[0] or 
            region.shape[1] < template.shape[1]):
            return (0.0, -1)
        
        # Ejecutar template matching
        resultado = cv2.matchTemplate(region, template, self.metodo_matching)
        _, max_val, _, max_loc = cv2.minMaxLoc(resultado)
        
        return (max_val, max_loc[0])
    
    def _detectar_digitos_en_region(
        self, 
        region: np.ndarray, 
        color: str
    ) -> List[ResultadoDigito]:
        """
        Detecta todos los dígitos presentes en una región.
        
        Usa Non-Maximum Suppression (NMS) para evitar detecciones duplicadas.
        
        Args:
            region: Imagen de la región a analizar
            color: Color de los templates a usar
            
        Returns:
            Lista de ResultadoDigito ordenada por posición X
        """
        if color not in self.templates:
            return []
        
        # Convertir a escala de grises si es necesario
        if len(region.shape) == 3:
            region_gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
        else:
            region_gray = region
        
        # Lista para acumular todas las detecciones
        detecciones = []
        
        # Probar cada template de dígito
        for digito, template in self.templates[color].items():
            # Verificar tamaño
            if (region_gray.shape[0] < template.shape[0] or 
                region_gray.shape[1] < template.shape[1]):
                continue
            
            # Template matching
            resultado = cv2.matchTemplate(
                region_gray, template, self.metodo_matching
            )
            
            # Encontrar todos los matches por encima del umbral
            ubicaciones = np.where(resultado >= self.confianza_minima)
            
            for pt in zip(*ubicaciones[::-1]):  # x, y
                confianza = resultado[pt[1], pt[0]]
                detecciones.append(ResultadoDigito(
                    digito=digito,
                    confianza=float(confianza),
                    posicion_x=pt[0]
                ))
        
        if not detecciones:
            return []
        
        # Aplicar Non-Maximum Suppression simple
        # Agrupar detecciones cercanas y quedarse con la de mayor confianza
        detecciones_filtradas = self._aplicar_nms(detecciones, distancia_minima=5)
        
        # Ordenar por posición X (izquierda a derecha)
        detecciones_filtradas.sort(key=lambda d: d.posicion_x)
        
        return detecciones_filtradas
    
    def _aplicar_nms(
        self, 
        detecciones: List[ResultadoDigito], 
        distancia_minima: int
    ) -> List[ResultadoDigito]:
        """
        Aplica Non-Maximum Suppression para eliminar detecciones duplicadas.
        
        Cuando hay múltiples detecciones cerca (< distancia_minima píxeles),
        mantiene solo la de mayor confianza.
        
        Args:
            detecciones: Lista de todas las detecciones
            distancia_minima: Distancia mínima entre detecciones válidas
            
        Returns:
            Lista filtrada de detecciones
        """
        if not detecciones:
            return []
        
        # Ordenar por confianza descendente
        ordenadas = sorted(detecciones, key=lambda d: d.confianza, reverse=True)
        
        resultado = []
        posiciones_usadas = []
        
        for det in ordenadas:
            # Verificar si hay una detección cercana ya aceptada
            es_duplicado = False
            for pos in posiciones_usadas:
                if abs(det.posicion_x - pos) < distancia_minima:
                    es_duplicado = True
                    break
            
            if not es_duplicado:
                resultado.append(det)
                posiciones_usadas.append(det.posicion_x)
        
        return resultado
    
    def reconocer_numero(
        self, 
        region: np.ndarray, 
        color: str = "white"
    ) -> Optional[int]:
        """
        Reconoce un número completo en una región de imagen.
        
        Detecta todos los dígitos visibles en la región, los ordena
        de izquierda a derecha, y los combina para formar el número.
        
        Args:
            region: Recorte de imagen conteniendo el número
            color: Color del texto ("white", "cyan", "yellow")
            
        Returns:
            Número reconocido, o None si no se detectó nada válido
        
        Ejemplo:
            Si la región contiene "127", retorna el entero 127.
        """
        if region is None or region.size == 0:
            return None
        
        # Detectar dígitos individuales
        digitos = self._detectar_digitos_en_region(region, color)
        
        if not digitos:
            return None
        
        # Combinar dígitos en orden (izq a der) para formar el número
        numero_str = "".join(str(d.digito) for d in digitos)
        
        try:
            return int(numero_str)
        except ValueError:
            return None
    
    def reconocer_poblacion(
        self, 
        region: np.ndarray, 
        color: str = "white"
    ) -> Tuple[Optional[int], Optional[int]]:
        """
        Reconoce población en formato "actual/máximo" (ej: "15/20").
        
        Detecta todos los dígitos y los divide en dos grupos
        basándose en un gap significativo (donde estaría la barra "/").
        
        Args:
            region: Recorte de imagen con "XX/YY"
            color: Color del texto
            
        Returns:
            Tupla (población_actual, población_máxima)
            Retorna (None, None) si no se puede reconocer
        """
        if region is None or region.size == 0:
            return (None, None)
        
        digitos = self._detectar_digitos_en_region(region, color)
        
        if len(digitos) < 2:
            return (None, None)
        
        # Encontrar el gap más grande entre dígitos consecutivos
        # Ese gap debería ser donde está la barra "/"
        max_gap = 0
        indice_gap = 0
        
        for i in range(len(digitos) - 1):
            gap = digitos[i + 1].posicion_x - digitos[i].posicion_x
            if gap > max_gap:
                max_gap = gap
                indice_gap = i
        
        # Dividir en dos grupos
        grupo_actual = digitos[:indice_gap + 1]
        grupo_maximo = digitos[indice_gap + 1:]
        
        if not grupo_actual or not grupo_maximo:
            return (None, None)
        
        # Formar números
        actual_str = "".join(str(d.digito) for d in grupo_actual)
        maximo_str = "".join(str(d.digito) for d in grupo_maximo)
        
        try:
            return (int(actual_str), int(maximo_str))
        except ValueError:
            return (None, None)


def crear_reconocedor_default() -> DigitRecognizer:
    """
    Crea un reconocedor con la configuración por defecto del proyecto.
    
    Busca templates en assets/digit_templates/ relativo al directorio del proyecto.
    
    Returns:
        Instancia configurada de DigitRecognizer
    """
    # Encontrar directorio del proyecto
    ruta_modulo = Path(__file__).parent
    ruta_proyecto = ruta_modulo.parent.parent
    ruta_templates = ruta_proyecto / "assets" / "digit_templates"
    
    return DigitRecognizer(str(ruta_templates))
