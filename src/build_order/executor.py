"""
Executor del Build Order - Auto-avance basado en estado del juego.

Este modulo compara el estado actual del juego (villagers, recursos)
con los pasos del build order y avanza automaticamente cuando se
cumplen las condiciones.
"""

from typing import Optional, Callable
from dataclasses import dataclass
from enum import Enum

from .build_order import BuildOrder, BuildOrderStep, ActionType
from ..game_detector import GameState


class StepStatus(Enum):
    """Estado de un paso del build order."""
    PENDING = "pending"       # Aun no alcanzado
    CURRENT = "current"       # Paso actual
    READY = "ready"           # Condiciones cumplidas, listo para avanzar
    COMPLETED = "completed"   # Ya ejecutado


@dataclass
class ExecutorState:
    """Estado del executor para la UI."""
    current_step_index: int
    total_steps: int
    current_step: Optional[BuildOrderStep]
    step_status: StepStatus
    progress_percent: float
    villagers_needed: int
    villagers_current: int
    auto_advance_enabled: bool


class BuildOrderExecutor:
    """
    Ejecuta un build order automaticamente basado en el estado del juego.
    
    El executor compara el villager_count del paso actual con el del juego
    y avanza al siguiente paso cuando se cumple la condicion.
    """
    
    def __init__(self):
        self.build_order: Optional[BuildOrder] = None
        self.auto_advance_enabled: bool = True
        self.last_game_state: Optional[GameState] = None
        
        # Callbacks para notificar cambios
        self.on_step_changed: Optional[Callable[[BuildOrderStep], None]] = None
        self.on_step_completed: Optional[Callable[[BuildOrderStep], None]] = None
        self.on_build_order_completed: Optional[Callable[[], None]] = None
    
    def set_build_order(self, build_order: BuildOrder):
        """Carga un build order para ejecutar."""
        self.build_order = build_order
        self.build_order.reset()
        print(f"[Executor] Build order cargado: {build_order.name}")
    
    def set_auto_advance(self, enabled: bool):
        """Habilita/deshabilita el avance automatico."""
        self.auto_advance_enabled = enabled
        print(f"[Executor] Auto-avance: {'ON' if enabled else 'OFF'}")
    
    def update(self, game_state: GameState) -> bool:
        """
        Actualiza el executor con el nuevo estado del juego.
        
        Args:
            game_state: Estado actual del juego (villagers, recursos, etc.)
            
        Returns:
            True si se avanzo al siguiente paso
        """
        if not self.build_order:
            return False
        
        self.last_game_state = game_state
        
        current_step = self.build_order.get_current_step()
        if not current_step:
            # Build order completado
            return False
        
        # Verificar si se cumplen las condiciones para avanzar
        if self.auto_advance_enabled and self._should_advance(current_step, game_state):
            self._advance_step()
            return True
        
        return False
    
    def _should_advance(self, step: BuildOrderStep, state: GameState) -> bool:
        """
        Determina si se debe avanzar al siguiente paso.
        
        Logica principal: avanzar cuando villager_count >= paso.villager_count
        
        Tambien considera:
        - Pasos con el mismo villager_count (avanzar inmediatamente)
        - Acciones especiales como advance_age
        """
        # Condicion principal: villagers
        if state.villager_count >= step.villager_count:
            # Verificar si el siguiente paso tiene el mismo villager_count
            next_step = self._get_next_step()
            if next_step and next_step.villager_count == step.villager_count:
                # Hay multiples pasos para el mismo villager_count
                # Avanzar al siguiente
                return True
            
            # Solo avanzar si superamos el villager_count actual
            if state.villager_count > step.villager_count:
                return True
        
        return False
    
    def _get_next_step(self) -> Optional[BuildOrderStep]:
        """Obtiene el siguiente paso sin avanzar."""
        if not self.build_order:
            return None
        
        next_index = self.build_order.current_step_index + 1
        if next_index < len(self.build_order.steps):
            return self.build_order.steps[next_index]
        return None
    
    def _advance_step(self):
        """Avanza al siguiente paso del build order."""
        if not self.build_order:
            return
        
        current = self.build_order.get_current_step()
        if current:
            print(f"[Executor] Completado: {current}")
            if self.on_step_completed:
                self.on_step_completed(current)
        
        self.build_order.advance_step()
        
        new_current = self.build_order.get_current_step()
        if new_current:
            print(f"[Executor] Siguiente: {new_current}")
            if self.on_step_changed:
                self.on_step_changed(new_current)
        else:
            # Build order completado
            print("[Executor] Build order completado!")
            if self.on_build_order_completed:
                self.on_build_order_completed()
    
    def advance_manually(self):
        """Avanza manualmente al siguiente paso (ignora condiciones)."""
        self._advance_step()
    
    def go_back(self):
        """Retrocede al paso anterior."""
        if self.build_order and self.build_order.current_step_index > 0:
            self.build_order.current_step_index -= 1
            current = self.build_order.get_current_step()
            if current:
                current.completed = False
                print(f"[Executor] Retrocedido a: {current}")
                if self.on_step_changed:
                    self.on_step_changed(current)
    
    def get_state(self) -> Optional[ExecutorState]:
        """Obtiene el estado actual del executor para la UI."""
        if not self.build_order:
            return None
        
        current_step = self.build_order.get_current_step()
        villagers_current = self.last_game_state.villager_count if self.last_game_state else 0
        villagers_needed = current_step.villager_count if current_step else 0
        
        # Determinar status del paso actual
        if not current_step:
            status = StepStatus.COMPLETED
        elif villagers_current >= villagers_needed:
            status = StepStatus.READY
        else:
            status = StepStatus.CURRENT
        
        return ExecutorState(
            current_step_index=self.build_order.current_step_index,
            total_steps=len(self.build_order.steps),
            current_step=current_step,
            step_status=status,
            progress_percent=self.build_order.get_progress_percentage(),
            villagers_needed=villagers_needed,
            villagers_current=villagers_current,
            auto_advance_enabled=self.auto_advance_enabled
        )
