# AoE II Strategy Overlay

Overlay transparente para Age of Empires II Definitive Edition que muestra build orders en tiempo real sobre el juego.

![Version](https://img.shields.io/badge/version-0.1.0--MVP-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

## Características (MVP)

**Implementado:**
- Overlay transparente que se mantiene siempre visible
- Visualización de build orders paso a paso
- Color coding: paso actual (azul), completado (verde), importante (naranja)
- Selector de build orders desde interfaz
- Draggable - mueve el overlay arrastrándolo
- Hotkey F8 para mostrar/ocultar
- Diseño moderno con tema oscuro

**Próxima Version:**
- Automatización de la apertura (hasta 25 aldeanos)
- Detección automática del estado del juego
- Detección de civilización
- Análisis de unidades enemigas y counters
- Métricas avanzadas (idle TC time, APM, etc.)

## Requisitos del Sistema

- Windows 10/11
- Python 3.8 o superior
- Age of Empires II: Definitive Edition
- Equipo que cumpla requisitos mínimos de AOE II DE

## Instalación

### 1. Clonar o descargar el proyecto

```bash
cd c:\Users\fede4\OneDrive\Documents\Proyectos\StratOverlayAoEII
```

### 2. Crear entorno virtual (recomendado)

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Instalar dependencias

```powershell
pip install -r requirements.txt
```

## Uso

### Iniciar el Overlay

```powershell
python main.py
```

### Controles

| Tecla/Acción | Función |
|-------------|---------|
| **F8** | Mostrar/ocultar overlay |
| **Arrastrar header** | Mover overlay por la pantalla |
| **Dropdown** | Seleccionar build order |
| **Next Step →** | Avanzar manualmente al siguiente paso |
| **🔄** | Recargar build orders desde carpeta |
| **✕** | Cerrar aplicación |

### Durante el Juego

1. Inicia el overlay con `python main.py`
2. Selecciona un build order del dropdown
3. Inicia tu partida en AOE II DE
4. Presiona **F8** si necesitas ocultar/mostrar el overlay
5. Arrastra el overlay a una posición cómoda en tu pantalla
6. Sigue los pasos mientras juegas
7. Usa "Next Step" para marcar pasos completados manualmente

**Nota:** En futuras versiones, el avance será automático al detectar el progreso en el juego.

## Crear Build Orders Personalizados

Los build orders se almacenan en la carpeta `build_orders/` como archivos JSON.

### Formato JSON

```json
{
  "name": "Nombre del Build Order",
  "description": "Descripción breve de la estrategia",
  "civilization": "any",
  "author": "Tu Nombre",
  "target_age": "Feudal",
  "max_villagers": 21,
  "strategy": "Scout Rush",
  "steps": [
    {
      "villager_count": 1,
      "action": "assign_resource",
      "resource": "sheep",
      "count": 3,
      "description": "3 aldeanos a ovejas"
    },
    {
      "villager_count": 4,
      "action": "build",
      "building": "House",
      "description": "Construir casa",
      "important": true
    }
  ]
}
```

### Campos Disponibles

#### Build Order (nivel raíz):
- `name`: Nombre del build order
- `description`: Descripción
- `civilization`: "any" o nombre de civilización específica
- `target_age`: "Dark", "Feudal", "Castle", "Imperial"
- `max_villagers`: Número máximo de aldeanos en la apertura
- `strategy`: Tipo de estrategia (ej: "Scout Rush", "Archers")
- `author`: Autor del build order (opcional)

#### Step (cada paso):
- `villager_count`: En qué población ocurre este paso
- `action`: Tipo de acción (ver tipos abajo)
- `description`: Texto descriptivo del paso
- `count`: Cantidad de aldeanos a asignar (default: 1)
- `important`: `true` para resaltar el paso en naranja (opcional)
- `notes`: Notas adicionales (opcional)

#### Tipos de Acción:
- `assign_resource`: Asignar aldeanos a recurso
  - Requiere: `resource` (sheep, wood, gold, stone, berries, boar, deer)
- `build`: Construir edificio
  - Requiere: `building` (nombre del edificio)
- `train`: Entrenar unidad
  - Requiere: `unit` (nombre de la unidad)
- `research`: Investigar tecnología
  - Requiere: `tech` (nombre de la tecnología)
- `lure_boar`: Atraer jabalí
- `advance_age`: Subir de edad

### Ejemplos Incluidos

- `scout_rush.json` - Scout Rush estándar a Feudal (21 vills)
- `archer_rush.json` - Archer Rush a Feudal (23 vills)

## Desarrollo

### Agregar Nuevas Características

El proyecto está diseñado de forma modular:

- **Build Orders**: Modificar `src/build_order/`
- **UI del Overlay**: Modificar `src/overlay/`
- **Detección de Juego**: Agregar en `src/game_detector/`
- **Automatización**: Agregar en `src/automation/` (futuro)

### Roadmap de Features

#### Phase 2: Automatización
- [ ] Input simulation con PyAutoGUI
- [ ] Auto-seguir build order hasta completar apertura
- [ ] Sistema de decisiones básico

#### Phase 3: Detección de Civilización
- [ ] Reconocer civilización al inicio
- [ ] Cargar build orders específicos por civ
- [ ] Ajustes automáticos de estrategia

#### Phase 4: Análisis Enemigo
- [ ] Detectar composición de unidades enemigas
- [ ] Sugerir counter units
- [ ] Sistema de alertas

#### Phase 5: Métricas Avanzadas
- [ ] Idle TC time tracker
- [ ] Villager idle time
- [ ] APM counter
- [ ] Score de eficiencia

## Solución de Problemas

### El overlay no aparece
- Verifica que instalaste PyQt6: `pip install PyQt6`
- Ejecuta con permisos de administrador si es necesario

### El overlay no se queda encima del juego
- Asegúrate de que AOE II esté en modo **Ventana** o **Borderless Fullscreen**
- Fullscreen exclusivo no permite overlays

### Los build orders no se cargan
- Verifica que los archivos JSON estén en `build_orders/`
- Valida que el JSON sea correcto (usa un validador online)
- Presiona el botón 🔄 para recargar

### El hotkey F8 no funciona
- Algunas aplicaciones capturan F8, prueba cambiar en futuras versiones
- Verifica que el overlay esté en foco al presionar F8

## Licencia

MIT License - Libre para usar, modificar y distribuir.

## Contribuciones

¡Contribuciones son bienvenidas! Si quieres agregar:
- Nuevos build orders
- Mejoras visuales
- Nuevas características

Siéntete libre de crear un fork o enviar sugerencias.

## Soporte

Para problemas o sugerencias, abre un issue en el repositorio del proyecto.

---

**Hecho por @FNT138**
