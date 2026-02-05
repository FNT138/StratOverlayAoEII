"""
Game state data structure
"""
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class GameState:
    """Represents the current state of the game"""
    
    # Population
    villager_count: int = 0
    population: int = 0
    max_population: int = 0
    
    # Resources
    food: int = 0
    wood: int = 0
    gold: int = 0
    stone: int = 0
    
    # Game info
    age: str = "Dark"  # "Dark", "Feudal", "Castle", "Imperial"
    game_time: Optional[int] = None  # seconds since game start
    
    # Metadata
    last_updated: float = field(default_factory=lambda: datetime.now().timestamp())
    is_valid: bool = False  # Whether the state has been populated
    
    def update_timestamp(self):
        """Update the last_updated timestamp"""
        self.last_updated = datetime.now().timestamp()
    
    def __str__(self) -> str:
        return (f"GameState(vills={self.villager_count}, "
                f"pop={self.population}/{self.max_population}, "
                f"F={self.food}, W={self.wood}, G={self.gold}, S={self.stone}, "
                f"age={self.age})")
