"""
Game state data structure
"""
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


# Tasas de recolección por aldeano por minuto (aproximadas)
GATHER_RATES = {
    'food_farm': 24,      # Granja
    'food_sheep': 33,     # Ovejas
    'food_berries': 24,   # Bayas
    'food_boar': 40,      # Jabalí
    'wood': 20,           # Madera
    'gold': 20,           # Oro
    'stone': 17           # Piedra
}


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
    
    # Villagers por recurso
    food_villagers: int = 0
    wood_villagers: int = 0
    gold_villagers: int = 0
    stone_villagers: int = 0
    
    # Game info
    age: str = "Dark"  # "Dark", "Feudal", "Castle", "Imperial"
    game_time: Optional[int] = None  # seconds since game start
    
    # Metadata
    last_updated: float = field(default_factory=lambda: datetime.now().timestamp())
    is_valid: bool = False  # Whether the state has been populated
    
    def update_timestamp(self):
        """Update the last_updated timestamp"""
        self.last_updated = datetime.now().timestamp()
    
    def get_income_per_minute(self) -> dict:
        """
        Calcula el income estimado por minuto basado en aldeanos.
        Usa tasa promedio de granja para food.
        """
        return {
            'food': self.food_villagers * GATHER_RATES['food_farm'],
            'wood': self.wood_villagers * GATHER_RATES['wood'],
            'gold': self.gold_villagers * GATHER_RATES['gold'],
            'stone': self.stone_villagers * GATHER_RATES['stone']
        }
    
    def __str__(self) -> str:
        return (f"GameState(vills={self.villager_count}, "
                f"pop={self.population}/{self.max_population}, "
                f"F={self.food}({self.food_villagers}), "
                f"W={self.wood}({self.wood_villagers}), "
                f"G={self.gold}({self.gold_villagers}), "
                f"S={self.stone}({self.stone_villagers}), "
                f"age={self.age})")

