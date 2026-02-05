"""
Build Order data structure for Age of Empires II
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from enum import Enum


class ResourceType(Enum):
    """Types of resources in AOE II"""
    FOOD = "food"
    WOOD = "wood"
    GOLD = "gold"
    STONE = "stone"
    SHEEP = "sheep"
    BERRIES = "berries"
    DEER = "deer"
    BOAR = "boar"


class ActionType(Enum):
    """Types of actions in a build order"""
    ASSIGN_RESOURCE = "assign_resource"
    BUILD = "build"
    TRAIN = "train"
    RESEARCH = "research"
    LURE_BOAR = "lure_boar"
    ADVANCE_AGE = "advance_age"


@dataclass
class BuildOrderStep:
    """Single step in a build order"""
    villager_count: int  # At what villager count this step happens
    action: ActionType
    description: str
    
    # Optional parameters depending on action type
    resource: Optional[ResourceType] = None
    building: Optional[str] = None
    unit: Optional[str] = None
    tech: Optional[str] = None
    count: int = 1  # How many villagers to assign
    
    # UI metadata
    notes: Optional[str] = None
    important: bool = False  # Highlight this step
    
    completed: bool = False  # Tracking completion
    
    def __str__(self) -> str:
        return f"[{self.villager_count}] {self.description}"


@dataclass
class BuildOrder:
    """Complete build order"""
    name: str
    description: str
    civilization: str = "any"  # "any" or specific civ name
    
    # Steps in order
    steps: List[BuildOrderStep] = field(default_factory=list)
    
    # Metadata
    author: Optional[str] = None
    target_age: str = "Feudal"  # Dark, Feudal, Castle, Imperial
    max_villagers: int = 25
    strategy: Optional[str] = None  # e.g., "Scout Rush", "Archers", "Fast Castle"
    
    # Runtime tracking
    current_step_index: int = 0
    
    def get_current_step(self) -> Optional[BuildOrderStep]:
        """Get the current active step"""
        if self.current_step_index < len(self.steps):
            return self.steps[self.current_step_index]
        return None
    
    def get_next_steps(self, count: int = 3) -> List[BuildOrderStep]:
        """Get the next N steps"""
        start = self.current_step_index + 1
        end = min(start + count, len(self.steps))
        return self.steps[start:end]
    
    def advance_step(self):
        """Move to the next step"""
        if self.current_step_index < len(self.steps):
            self.steps[self.current_step_index].completed = True
            self.current_step_index += 1
    
    def reset(self):
        """Reset build order to beginning"""
        self.current_step_index = 0
        for step in self.steps:
            step.completed = False
    
    def get_progress_percentage(self) -> float:
        """Calculate completion percentage"""
        if not self.steps:
            return 0.0
        return (self.current_step_index / len(self.steps)) * 100
